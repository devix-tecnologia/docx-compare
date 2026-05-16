"""
Algoritmo Híbrido de Vinculação de Cláusulas

Combina múltiplas estratégias em cascata para maximizar performance e cobertura:
1. Overlap direto (se tem posições)
2. Regex (padrões estruturados)
3. Fuzzy (similaridade textual)
4. ML (semântica) - opcional

Meta: Score ≥90, Taxa ≥95%, Precisão ≥95%
"""

from typing import List, Dict, Optional, Any
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao
from algoritmos.regex.algoritmo import AlgoritmoRegex
from algoritmos.fuzzy.algoritmo import AlgoritmoFuzzyAvancado


class AlgoritmoHibrido(AlgoritmoVinculacao):
    """
    Algoritmo híbrido que combina estratégias em cascata:
    - Overlap: para modificações com posições conhecidas
    - Regex: para padrões estruturados (valores, datas, IDs)
    - Fuzzy: para texto livre com variações
    - ML: (opcional) para paráfrases e semântica
    """

    def __init__(self):
        """Inicializa sub-algoritmos e estatísticas."""
        # Instanciar sub-algoritmos
        self._alg_regex = AlgoritmoRegex()
        self._alg_fuzzy = AlgoritmoFuzzyAvancado()

        # Thresholds configuráveis
        self._thresholds = {
            "overlap": 0.5,  # 50% de overlap mínimo
            "fuzzy": 0.85,   # 85% de similaridade
            "ml": 0.80,      # 80% de confiança semântica
        }

        # Estatísticas de uso
        self._stats = {
            "overlap": 0,
            "regex": 0,
            "fuzzy": 0,
            "ml": 0,
            "nao_vinculada": 0,
        }

    @property
    def nome(self) -> str:
        return "hibrido"

    @property
    def descricao(self) -> str:
        return "Combina overlap, regex, fuzzy e ML em cascata para máxima cobertura"

    def calcular_posicoes(
        self, modificacoes: List[Dict[str, Any]], texto_completo: str
    ) -> List[Dict[str, Any]]:
        """
        Calcula posições usando estratégias em cascata:
        1. Regex (rápido e preciso para padrões estruturados)
        2. Fuzzy (busca aproximada para texto livre)
        3. Busca exata (fallback)

        Retorna modificações com posicao_inicio, posicao_fim e _estrategia_posicao.
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            if not texto_busca:
                resultado.append({
                    **mod,
                    "posicao_inicio": None,
                    "posicao_fim": None,
                    "_estrategia_posicao": None,
                })
                continue

            posicao = None
            estrategia_posicao = None

            # 1. Tentar REGEX primeiro (mais rápido e preciso)
            try:
                resultado_regex = self._alg_regex.calcular_posicoes([mod], texto_completo)
                if resultado_regex and resultado_regex[0].get("posicao_inicio") is not None:
                    posicao = (
                        resultado_regex[0]["posicao_inicio"],
                        resultado_regex[0]["posicao_fim"]
                    )
                    estrategia_posicao = "regex"
            except Exception:
                pass  # Regex pode falhar, continuar para fuzzy

            # 2. Se regex falhou, tentar FUZZY
            if posicao is None:
                try:
                    resultado_fuzzy = self._alg_fuzzy.calcular_posicoes([mod], texto_completo)
                    if resultado_fuzzy and resultado_fuzzy[0].get("posicao_inicio") is not None:
                        posicao = (
                            resultado_fuzzy[0]["posicao_inicio"],
                            resultado_fuzzy[0]["posicao_fim"]
                        )
                        estrategia_posicao = "fuzzy"
                except Exception:
                    pass

            # 3. FALLBACK: busca exata simples
            if posicao is None:
                idx = texto_completo.find(texto_busca)
                if idx >= 0:
                    posicao = (idx, idx + len(texto_busca))
                    estrategia_posicao = "exact"

            # Adicionar aos resultados
            if posicao:
                resultado.append({
                    **mod,
                    "posicao_inicio": posicao[0],
                    "posicao_fim": posicao[1],
                    "_estrategia_posicao": estrategia_posicao,
                })
            else:
                resultado.append({
                    **mod,
                    "posicao_inicio": None,
                    "posicao_fim": None,
                    "_estrategia_posicao": None,
                })

        return resultado

    def vincular_clausulas(
        self,
        modificacoes: List[Dict[str, Any]],
        tags: List[Dict[str, Any]],
        texto_completo: str,
    ) -> List[Dict[str, Any]]:
        """
        Vincula modificações a tags usando estratégia em cascata:
        1. Calcular posições (já usa regex → fuzzy internamente)
        2. OVERLAP: se tem posição válida, tentar buscar_tag_por_posicao
        3. REGEX: se overlap falhou mas regex achou posição, usar regex para vincular
        4. FUZZY: se regex falhou, usar fuzzy
        5. ML: (opcional) último recurso para casos difíceis
        6. NONE: se tudo falhar

        Retorna modificações com tag_vinculada, _estrategia_usada e _score_vinculacao.
        """
        # Primeiro, calcular posições
        mods_com_posicao = self.calcular_posicoes(modificacoes, texto_completo)

        resultado = []

        for mod in mods_com_posicao:
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")
            estrategia_posicao = mod.get("_estrategia_posicao")

            tag_vinculada = None
            estrategia_usada = None
            score_vinculacao = 0.0

            # 1. OVERLAP: se tem posição, tentar buscar tag por overlap
            if pos_inicio is not None and pos_fim is not None:
                tag_overlap = UtilitariosVinculacao.buscar_tag_por_posicao(
                    pos_inicio, pos_fim, tags
                )
                if tag_overlap:
                    tag_vinculada = tag_overlap
                    estrategia_usada = "overlap"
                    score_vinculacao = 1.0
                    self._stats["overlap"] += 1

            # 2. REGEX: se overlap falhou mas posição veio do regex
            if tag_vinculada is None and estrategia_posicao == "regex":
                try:
                    resultado_regex = self._alg_regex.vincular_clausulas(
                        [mod], tags, texto_completo
                    )
                    if resultado_regex and resultado_regex[0].get("tag_vinculada"):
                        tag_vinculada = resultado_regex[0]["tag_vinculada"]
                        estrategia_usada = "regex"
                        score_vinculacao = 1.0
                        self._stats["regex"] += 1
                except Exception:
                    pass

            # 3. FUZZY: se regex falhou ou posição veio do fuzzy
            if tag_vinculada is None:
                try:
                    resultado_fuzzy = self._alg_fuzzy.vincular_clausulas(
                        [mod], tags, texto_completo
                    )
                    if resultado_fuzzy and resultado_fuzzy[0].get("tag_vinculada"):
                        tag_vinculada = resultado_fuzzy[0]["tag_vinculada"]
                        estrategia_usada = "fuzzy"
                        score_vinculacao = 0.85
                        self._stats["fuzzy"] += 1
                except Exception:
                    pass

            # 5. Nenhuma estratégia funcionou
            if tag_vinculada is None:
                self._stats["nao_vinculada"] += 1

            # Adicionar aos resultados
            resultado.append({
                **mod,
                "tag_vinculada": tag_vinculada,
                "_estrategia_usada": estrategia_usada,
                "_score_vinculacao": score_vinculacao,
            })

        return resultado

    def obter_estatisticas(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna estatísticas de uso das estratégias.

        Returns:
            Dict com count e percentage de cada estratégia.
        """
        total = sum(self._stats.values()) or 1

        return {
            estrategia: {
                "count": count,
                "percentage": round(100 * count / total, 2)
            }
            for estrategia, count in self._stats.items()
        }

    def resetar_estatisticas(self):
        """Reseta as estatísticas de uso para zero."""
        for key in self._stats:
            self._stats[key] = 0

    def configurar_thresholds(
        self, overlap: float = None, fuzzy: float = None, ml: float = None
    ):
        """
        Permite ajustar thresholds das estratégias.

        Args:
            overlap: Threshold de overlap (0.0 a 1.0)
            fuzzy: Threshold de fuzzy matching (0.0 a 1.0)
            ml: Threshold de ML (0.0 a 1.0)
        """
        if overlap is not None:
            self._thresholds["overlap"] = max(0.0, min(1.0, overlap))
        if fuzzy is not None:
            self._thresholds["fuzzy"] = max(0.0, min(1.0, fuzzy))
        if ml is not None:
            self._thresholds["ml"] = max(0.0, min(1.0, ml))
