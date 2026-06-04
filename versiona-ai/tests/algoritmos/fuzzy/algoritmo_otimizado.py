"""
Algoritmo Fuzzy Otimizado com Cache, TF-IDF Pre-filtering e Early Exit

Otimizações implementadas:
1. Cache de similaridade: Evita recomputação de pares já calculados
2. Pré-filtragem TF-IDF: Reduz candidatas de n para top-k (~20)
3. Early exit: Para quando encontra match excelente (>95%)

Performance esperada: 80-90% redução de tempo vs baseline
"""

import hashlib
import re
import time
import unicodedata
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
        prefilter_top_k: int = 50,
        early_exit_threshold: float = 85.0,
        use_cache: bool = True,
        cache_ttl: int = 3600,
        min_tags_for_index: int = 100,
    ):
        """
        Args:
            prefilter_top_k: Número de candidatas após TF-IDF (padrão: 50)
            early_exit_threshold: Score para parar busca (padrão: 85.0)
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

        Usa a implementação padrão do AlgoritmoFuzzyAvancado (sliding window).
        As otimizações (cache, TF-IDF, early exit) são aplicadas em vincular_clausulas.
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)

            # Buscar posição com fuzzy matching apenas se houver texto
            if texto_busca is None:
                resultado.append({**mod})
                continue

            inicio, fim, score = self._buscar_posicao_com_sliding_window(
                texto_busca, texto_completo
            )

            if inicio >= 0:
                resultado.append(
                    {
                        **mod,
                        "posicao_inicio": inicio,
                        "posicao_fim": fim,
                        "_fuzzy_score": score,
                    }
                )
            else:
                resultado.append(
                    {
                        **mod,
                        "posicao_inicio": None,
                        "posicao_fim": None,
                        "_fuzzy_score": 0.0,
                    }
                )

        return resultado

    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza texto removendo acentos, espaços extras e normalizando números.

        Args:
            texto: Texto a normalizar

        Returns:
            Texto normalizado
        """
        if not texto:
            return ""

        # Remover acentos
        texto_sem_acento = unicodedata.normalize("NFKD", texto)
        texto_sem_acento = "".join(
            [c for c in texto_sem_acento if not unicodedata.combining(c)]
        )

        # Normalizar espaços múltiplos
        texto_normalizado = re.sub(r"\s+", " ", texto_sem_acento)

        # Normalizar números (remover formatação)
        texto_normalizado = re.sub(
            r"(\d)\.(\d{3})", r"\1\2", texto_normalizado
        )  # 1.000 -> 1000
        texto_normalizado = re.sub(
            r"(\d),(\d{2})\b", r"\1.\2", texto_normalizado
        )  # 10,50 -> 10.50

        return texto_normalizado.strip().lower()

    def _calcular_threshold_dinamico(self, texto: str) -> float:
        """
        Calcula threshold baseado no tamanho do texto.

        Textos curtos precisam de threshold mais alto para evitar falsos positivos.

        Args:
            texto: Texto para análise

        Returns:
            Threshold entre 0 e 100
        """
        tamanho = len(texto)

        if tamanho < 20:
            return 90.0  # Muito curto: alta precisão
        elif tamanho < 100:
            return 85.0  # Médio: balanceado
        else:
            return 80.0  # Longo: mais flexível

    def _calcular_score_composto(self, texto1: str, texto2: str) -> float:
        """
        Calcula score usando múltiplas métricas e retorna o máximo.

        Args:
            texto1: Primeiro texto
            texto2: Segundo texto

        Returns:
            Score entre 0 e 100
        """
        if not texto1 or not texto2:
            return 0.0

        # Normalizar ambos os textos
        t1_norm = self._normalizar_texto(texto1)
        t2_norm = self._normalizar_texto(texto2)

        if not t1_norm or not t2_norm:
            return 0.0

        # Calcular múltiplas métricas
        scores = [
            fuzz.ratio(t1_norm, t2_norm),
            fuzz.partial_ratio(t1_norm, t2_norm),
            fuzz.token_sort_ratio(t1_norm, t2_norm),
            fuzz.token_set_ratio(t1_norm, t2_norm),
        ]

        # Retornar o melhor score
        return max(scores)

    def _buscar_posicao_com_sliding_window(
        self, texto_busca: str, texto_completo: str, window_size: int | None = None
    ) -> tuple[int, int, float]:
        """
        Busca a melhor posição usando sliding window com fuzzy matching.

        Args:
            texto_busca: Texto a buscar
            texto_completo: Texto onde buscar
            window_size: Tamanho da janela (None = tamanho do texto_busca * 1.5)

        Returns:
            Tupla (inicio, fim, score) ou (-1, -1, 0.0) se não encontrado
        """
        if not texto_busca or not texto_completo:
            return (-1, -1, 0.0)

        # Primeiro tentar match exato
        texto_busca_norm = self._normalizar_texto(texto_busca)
        texto_completo_norm = self._normalizar_texto(texto_completo)

        pos_exata = texto_completo_norm.find(texto_busca_norm)
        if pos_exata != -1:
            # Encontrar posição no texto original
            inicio = self._mapear_posicao_normalizada_para_original(
                pos_exata, texto_completo
            )
            fim = inicio + len(texto_busca)
            return (inicio, fim, 100.0)

        # Se não encontrou exato, usar sliding window
        if window_size is None:
            window_size = int(len(texto_busca) * 1.5)

        threshold = self._calcular_threshold_dinamico(texto_busca)
        melhor_score = 0.0
        melhor_posicao = (-1, -1)

        # Deslizar janela pelo texto
        for i in range(len(texto_completo) - window_size + 1):
            janela = texto_completo[i : i + window_size]
            score = self._calcular_score_composto(texto_busca, janela)

            if score > melhor_score and score >= threshold:
                melhor_score = score
                melhor_posicao = (i, i + window_size)

        if melhor_posicao[0] == -1:
            return (-1, -1, 0.0)

        return (melhor_posicao[0], melhor_posicao[1], melhor_score)

    def _mapear_posicao_normalizada_para_original(
        self, pos_norm: int, texto_original: str
    ) -> int:
        """
        Mapeia posição no texto normalizado para o texto original.

        Args:
            pos_norm: Posição no texto normalizado
            texto_original: Texto original

        Returns:
            Posição no texto original
        """
        contador = 0
        for i, char in enumerate(texto_original):
            char_norm = self._normalizar_texto(char)
            if char_norm:
                if contador == pos_norm:
                    return i
                contador += 1
        return len(texto_original)

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
