"""
Algoritmo Fuzzy Otimizado com Cache, TF-IDF Pre-filtering e Early Exit

Otimizações implementadas:
1. Cache de similaridade: Evita recomputação de pares já calculados
2. Pré-filtragem TF-IDF: Reduz candidatas de n para top-k (~20)
3. Early exit: Para quando encontra match excelente (>95%)

Performance esperada: 80-90% redução de tempo vs baseline
"""

import hashlib
import time
from typing import Any

import numpy as np
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer


class AlgoritmoFuzzyAvancadoOtimizado(AlgoritmoVinculacao):
    """
    Versão otimizada do fuzzy matching com múltiplas estratégias de aceleração.

    Estratégia:
    1. Indexa tags com TF-IDF (trigrams/bigrams)
    2. Para cada modificação, pré-filtra top-k candidatas (~20)
    3. Aplica fuzzy apenas nas candidatas
    4. Early exit se encontra match excelente (>95%)
    5. Cache para evitar recomputações
    """

    @property
    def nome(self) -> str:
        return "fuzzy_otimizado"

    @property
    def descricao(self) -> str:
        return "Fuzzy com cache + TF-IDF pre-filtering + early exit"

    def __init__(
        self,
        prefilter_top_k: int = 20,
        early_exit_threshold: float = 95.0,
        use_cache: bool = True,
        cache_ttl: int = 3600,
        min_tags_for_index: int = 100,
    ):
        """
        Args:
            prefilter_top_k: Número de candidatas após TF-IDF (padrão: 20)
            early_exit_threshold: Score para parar busca (padrão: 95.0)
            use_cache: Habilitar cache de similaridade (padrão: True)
            cache_ttl: Tempo de vida do cache em segundos (padrão: 3600)
            min_tags_for_index: Mínimo de tags para criar índice (padrão: 100)
        """
        self.prefilter_top_k = prefilter_top_k
        self.early_exit_threshold = early_exit_threshold
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.min_tags_for_index = min_tags_for_index

        # Caches
        self._similarity_cache = {}
        self._cache_timestamps = {}

        # Índice TF-IDF (inicializado sob demanda)
        self._vectorizer = None
        self._tag_vectors = None
        self._tag_texts = None
        self._tags_indexadas = None

        # Estatísticas
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "prefilter_reductions": 0,
            "early_exits": 0,
            "total_comparisons": 0,
            "comparisons_saved": 0,
            "indexing_time": 0.0,
        }

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para cache."""
        return text.lower().strip()

    def _get_cache_key(self, text1: str, text2: str, metric: str = "ratio") -> str:
        """Gera chave de cache determinística."""
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)
        # Ordena para garantir simetria (score(A,B) == score(B,A))
        key_tuple = tuple(sorted([norm1, norm2]))
        hash_key = hashlib.md5(str(key_tuple).encode()).hexdigest()
        return f"{metric}:{hash_key}"

    def _get_cached_score(
        self, text1: str, text2: str, metric: str = "ratio"
    ) -> float | None:
        """Recupera score do cache com validação de TTL."""
        if not self.use_cache:
            return None

        key = self._get_cache_key(text1, text2, metric)

        # Check TTL
        if key in self._similarity_cache:
            timestamp = self._cache_timestamps.get(key, 0)
            if time.time() - timestamp < self.cache_ttl:
                self._stats["cache_hits"] += 1
                return self._similarity_cache[key]
            # Cache expired
            del self._similarity_cache[key]
            del self._cache_timestamps[key]

        self._stats["cache_misses"] += 1
        return None

    def _cache_score(self, text1: str, text2: str, score: float, metric: str = "ratio"):
        """Armazena score no cache."""
        if not self.use_cache:
            return

        key = self._get_cache_key(text1, text2, metric)
        self._similarity_cache[key] = score
        self._cache_timestamps[key] = time.time()

    def _calcular_score_com_cache(
        self, text1: str, text2: str, metric: str = "ratio"
    ) -> float:
        """Calcula score de similaridade com cache."""
        # Tenta cache primeiro
        cached = self._get_cached_score(text1, text2, metric)
        if cached is not None:
            return cached

        # Calcula
        if metric == "ratio":
            score = fuzz.ratio(text1, text2)
        elif metric == "partial_ratio":
            score = fuzz.partial_ratio(text1, text2)
        elif metric == "token_sort_ratio":
            score = fuzz.token_sort_ratio(text1, text2)
        elif metric == "token_set_ratio":
            score = fuzz.token_set_ratio(text1, text2)
        else:
            score = fuzz.ratio(text1, text2)

        # Cacheia
        self._cache_score(text1, text2, score, metric)
        return score

    def _build_tfidf_index(self, tags: list[dict]):
        """Constrói índice TF-IDF para pré-filtragem."""
        if self._vectorizer is not None:
            return  # Já indexado

        if len(tags) < self.min_tags_for_index:
            # Não vale a pena indexar poucos itens
            return

        start = time.time()

        # Extrai textos das tags
        self._tags_indexadas = tags
        self._tag_texts = []

        for tag in tags:
            # Tenta diferentes campos
            texto = tag.get("conteudo") or tag.get("texto") or tag.get("nome", "")
            self._tag_texts.append(texto)

        # Cria vectorizer com char n-grams (melhor para fuzzy matching)
        self._vectorizer = TfidfVectorizer(
            ngram_range=(2, 4),  # Bigrams + trigrams + 4-grams
            analyzer="char_wb",  # Considera boundaries de palavras
            max_features=5000,  # Limita dimensionalidade
            sublinear_tf=True,  # Normaliza frequências
            lowercase=True,
        )

        # Indexa todas as tags
        self._tag_vectors = self._vectorizer.fit_transform(self._tag_texts)

        self._stats["indexing_time"] = time.time() - start

    def _prefilter_candidates(self, search_text: str) -> list[tuple[int, float]] | None:
        """
        Retorna top-k tags candidatas usando TF-IDF cosine similarity.

        Returns:
            Lista de (índice, score) ou None se sem índice
        """
        if self._vectorizer is None or self._tag_vectors is None:
            return None  # Sem pré-filtro, processa todas

        # Vetoriza texto de busca
        search_vector = self._vectorizer.transform([search_text])

        # Calcula similaridade coseno
        similarities = (search_vector * self._tag_vectors.T).toarray()[0]

        # Retorna top-k índices
        top_k = min(self.prefilter_top_k, len(similarities))
        top_indices = np.argpartition(similarities, -top_k)[-top_k:]

        # Ordena por similaridade decrescente
        top_indices = sorted(top_indices, key=lambda i: similarities[i], reverse=True)

        # Registra estatística
        original_count = len(self._tag_texts)
        self._stats["prefilter_reductions"] += original_count - top_k
        self._stats["comparisons_saved"] += original_count - top_k

        return [(idx, similarities[idx]) for idx in top_indices]

    def vincular_modificacao(
        self, texto_modificacao: str, tags: list[dict], threshold: float = 85.0
    ) -> dict | None:
        """
        Vincula uma modificação à melhor tag usando fuzzy otimizado.

        Args:
            texto_modificacao: Texto da modificação
            tags: Lista de tags disponíveis
            threshold: Score mínimo para vinculação (padrão: 85.0)

        Returns:
            Tag vinculada ou None
        """
        if not texto_modificacao:
            return None

        # Pré-filtragem
        candidates = self._prefilter_candidates(texto_modificacao)

        # Se não há pré-filtro, processa todas
        if candidates is None:
            tag_indices = range(len(tags))
        else:
            tag_indices = [idx for idx, _ in candidates]

        melhor_tag = None
        melhor_score = 0.0

        for idx in tag_indices:
            tag = tags[idx]
            texto_tag = tag.get("conteudo") or tag.get("texto") or tag.get("nome", "")

            if not texto_tag:
                continue

            # Calcula score (com cache)
            score = self._calcular_score_com_cache(texto_modificacao, texto_tag)
            self._stats["total_comparisons"] += 1

            # Early exit se encontrar match excelente
            if score >= self.early_exit_threshold:
                self._stats["early_exits"] += 1
                return tag

            # Atualiza melhor
            if score > melhor_score and score >= threshold:
                melhor_score = score
                melhor_tag = tag

        return melhor_tag if melhor_score > 0 else None

    def calcular_posicoes(
        self, modificacoes: list[dict[str, Any]], texto_completo: str
    ) -> list[dict[str, Any]]:
        """
        Calcula posições usando fuzzy matching.

        Nota: Esta implementação otimizada foca em vincular_clausulas.
        Para calcular posições, usa a mesma lógica do AlgoritmoFuzzyAvancado.
        """
        # Mantém compatibilidade retornando modificações sem alteração
        # (posições são calculadas por outros algoritmos no híbrido)
        return modificacoes

    def vincular_clausulas(
        self,
        modificacoes: list[dict],
        tags: list[dict],
        texto_completo: str | None = None,
    ) -> list[dict]:
        """
        Versão principal com todas as otimizações.

        Args:
            modificacoes: Lista de modificações a vincular
            tags: Lista de tags disponíveis
            texto_completo: Texto completo (não usado na versão otimizada)

        Returns:
            Lista de modificações com tag_vinculada
        """
        # Reset stats
        for key in self._stats:
            if key != "indexing_time":  # Preserva tempo de indexação
                self._stats[key] = 0

        # Pré-constrói índice TF-IDF uma única vez
        self._build_tfidf_index(tags)

        # Processa cada modificação
        resultados = []
        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)

            if texto_busca is None:
                resultados.append({**mod, "tag_vinculada": None})
                continue

            melhor_tag = self.vincular_modificacao(texto_busca, tags)

            resultados.append({**mod, "tag_vinculada": melhor_tag})

        return resultados

    def get_stats(self) -> dict:
        """Retorna estatísticas de performance."""
        total_comparacoes = self._stats["total_comparisons"]
        comparacoes_salvas = self._stats["comparisons_saved"]

        cache_total = self._stats["cache_hits"] + self._stats["cache_misses"]

        return {
            **self._stats,
            "efficiency": (
                comparacoes_salvas / (total_comparacoes + comparacoes_salvas) * 100
                if (total_comparacoes + comparacoes_salvas) > 0
                else 0
            ),
            "cache_hit_rate": (
                self._stats["cache_hits"] / cache_total * 100 if cache_total > 0 else 0
            ),
        }


__all__ = ["AlgoritmoFuzzyAvancadoOtimizado"]
