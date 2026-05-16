"""
Algoritmo de vinculação baseado em fuzzy matching avançado com RapidFuzz.

Estratégia:
- Múltiplas métricas de similaridade (ratio, partial_ratio, token_sort, token_set)
- Threshold dinâmico baseado no tamanho do texto
- Normalização avançada (acentos, espaços, números)
- Sliding window para busca de posição
- Score composto (max das métricas)
"""

from typing import Any, Optional
import re
import unicodedata
from rapidfuzz import fuzz
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao


class AlgoritmoFuzzyAvancado(AlgoritmoVinculacao):
    """
    Algoritmo de vinculação usando fuzzy matching avançado com RapidFuzz.
    
    Features:
    - Normalização robusta de texto
    - Múltiplas métricas de similaridade
    - Threshold dinâmico por tamanho
    - Sliding window para posições precisas
    """
    
    @property
    def nome(self) -> str:
        return "fuzzy"
    
    @property
    def descricao(self) -> str:
        return "Fuzzy matching avançado com RapidFuzz - múltiplas métricas + threshold dinâmico"
    
    def __init__(self):
        pass
    
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
        texto_sem_acento = unicodedata.normalize('NFKD', texto)
        texto_sem_acento = ''.join([c for c in texto_sem_acento if not unicodedata.combining(c)])
        
        # Normalizar espaços múltiplos
        texto_normalizado = re.sub(r'\s+', ' ', texto_sem_acento)
        
        # Normalizar números (remover formatação)
        texto_normalizado = re.sub(r'(\d)\.(\d{3})', r'\1\2', texto_normalizado)  # 1.000 -> 1000
        texto_normalizado = re.sub(r'(\d),(\d{2})\b', r'\1.\2', texto_normalizado)  # 10,50 -> 10.50
        
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
            fuzz.token_set_ratio(t1_norm, t2_norm)
        ]
        
        # Retornar o melhor score
        return max(scores)
    
    def _buscar_posicao_com_sliding_window(
        self, texto_busca: str, texto_completo: str, window_size: Optional[int] = None
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
            inicio = self._mapear_posicao_normalizada_para_original(pos_exata, texto_completo)
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
            janela = texto_completo[i:i + window_size]
            score = self._calcular_score_composto(texto_busca, janela)
            
            if score > melhor_score and score >= threshold:
                melhor_score = score
                melhor_posicao = (i, i + window_size)
        
        if melhor_posicao[0] == -1:
            return (-1, -1, 0.0)
        
        return (melhor_posicao[0], melhor_posicao[1], melhor_score)
    
    def _mapear_posicao_normalizada_para_original(self, pos_norm: int, texto_original: str) -> int:
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
    
    def calcular_posicoes(
        self, modificacoes: list[dict[str, Any]], texto_completo: str
    ) -> list[dict[str, Any]]:
        """
        Calcula posições das modificações no texto completo usando fuzzy matching.
        
        Args:
            modificacoes: Lista de modificações
            texto_completo: Texto completo onde buscar
            
        Returns:
            Lista de modificações com posicao_inicio e posicao_fim
        """
        resultado = []
        
        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            
            # Buscar posição com fuzzy matching
            inicio, fim, score = self._buscar_posicao_com_sliding_window(texto_busca, texto_completo)
            
            if inicio >= 0:
                resultado.append({
                    **mod,
                    "posicao_inicio": inicio,
                    "posicao_fim": fim,
                    "_fuzzy_score": score,
                })
            else:
                resultado.append({
                    **mod,
                    "posicao_inicio": None,
                    "posicao_fim": None,
                    "_fuzzy_score": 0.0,
                })
        
        return resultado
    
    def vincular_clausulas(
        self,
        modificacoes: list[dict[str, Any]],
        tags: list[dict[str, Any]],
        texto_completo: str
    ) -> list[dict[str, Any]]:
        """
        Vincula modificações a tags usando fuzzy matching.
        
        Args:
            modificacoes: Lista de modificações
            tags: Lista de tags com posicao_inicio e posicao_fim
            texto_completo: Texto completo
            
        Returns:
            Lista de modificações com tag_vinculada
        """
        # Primeiro calcular posições
        mods_com_posicao = self.calcular_posicoes(modificacoes, texto_completo)
        
        resultado = []
        
        for mod in mods_com_posicao:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")
            
            tag = None
            
            # 1. Tentar overlap se tem posição
            if pos_inicio is not None:
                tag = UtilitariosVinculacao.buscar_tag_por_posicao(
                    pos_inicio, pos_fim, tags
                )
            
            # 2. Se não achou, tentar fuzzy matching direto com tags
            if tag is None:
                melhor_tag = None
                melhor_score = 0.0
                threshold = self._calcular_threshold_dinamico(texto_busca)
                
                for t in tags:
                    tag_texto = t.get("texto", "")
                    score = self._calcular_score_composto(texto_busca, tag_texto)
                    
                    if score > melhor_score and score >= threshold:
                        melhor_score = score
                        melhor_tag = t
                
                tag = melhor_tag
            
            resultado.append({
                **mod,
                "tag_vinculada": tag,  # Armazenar objeto completo, não só ID
            })
        
        return resultado
