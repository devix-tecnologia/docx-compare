"""
Algoritmo Híbrido de Vinculação de Cláusulas

Combina múltiplas estratégias em cascata para maximizar performance e cobertura:
1. Overlap direto (se tem posições)
2. Regex (padrões estruturados)
3. Fuzzy (similaridade textual)
4. ML (semântica) - opcional

Meta: Score ≥90, Taxa ≥95%, Precisão ≥95%
"""

from typing import Any

from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao
from algoritmos.fuzzy.algoritmo import AlgoritmoFuzzyAvancado
from algoritmos.regex.algoritmo import AlgoritmoRegex


class AlgoritmoHibrido(AlgoritmoVinculacao):
    """
    Algoritmo híbrido que combina estratégias em cascata:
    - Overlap: para modificações com posições conhecidas
    - Regex: para padrões estruturados (valores, datas, IDs)
    - Fuzzy: para texto livre com variações (parametrizável)
    - ML: (opcional) para paráfrases e semântica
    """

    def __init__(
        self,
        usar_fuzzy: bool | None = None,
        limiar_complexidade_fuzzy: int = 10000,
    ):
        """
        Inicializa sub-algoritmos e estatísticas.
        
        Args:
            usar_fuzzy: Se True, sempre usa fuzzy. Se False, nunca usa.
                       Se None (padrão), decide automaticamente baseado em complexidade.
            limiar_complexidade_fuzzy: Limite de (modificações × tags) acima do qual
                                      fuzzy é desabilitado automaticamente.
                                      Padrão: 10.000 comparações.
        """
        # Instanciar sub-algoritmos
        self._alg_regex = AlgoritmoRegex()
        self._alg_fuzzy = AlgoritmoFuzzyAvancado()

        # Configuração de uso do fuzzy
        self._usar_fuzzy = usar_fuzzy
        self._limiar_complexidade_fuzzy = limiar_complexidade_fuzzy
        self._fuzzy_desabilitado_auto = False  # Flag para rastreamento

        # Thresholds configuráveis
        self._thresholds = {
            "overlap": 0.5,  # 50% de overlap mínimo
            "fuzzy": 0.85,  # 85% de similaridade
            "ml": 0.80,  # 80% de confiança semântica
        }

        # Estatísticas de uso
        self._stats = {
            "overlap": 0,
            "regex": 0,
            "fuzzy": 0,
            "fuzzy_desabilitado": 0,  # Quantas vezes fuzzy foi pulado
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
        self,
        modificacoes: list[dict[str, Any]],
        texto_completo: str,
        usar_fuzzy_override: bool | None = None,
    ) -> list[dict[str, Any]]:
        """
        Calcula posições usando estratégias em cascata:
        1. Regex (rápido e preciso para padrões estruturados)
        2. Fuzzy (busca aproximada para texto livre) - se habilitado
        3. Busca exata (fallback)

        Args:
            modificacoes: Lista de modificações
            texto_completo: Texto completo
            usar_fuzzy_override: Se fornecido, sobrescreve self._usar_fuzzy para esta chamada

        Retorna modificações com posicao_inicio, posicao_fim e _estrategia_posicao.
        """
        # Decidir se usa fuzzy (com override ou default)
        usar_fuzzy = (
            usar_fuzzy_override if usar_fuzzy_override is not None else self._usar_fuzzy
        )

        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            if not texto_busca:
                resultado.append(
                    {
                        **mod,
                        "posicao_inicio": None,
                        "posicao_fim": None,
                        "_estrategia_posicao": None,
                    }
                )
                continue

            posicao = None
            estrategia_posicao = None

            # 1. Tentar REGEX primeiro (mais rápido e preciso)
            try:
                resultado_regex = self._alg_regex.calcular_posicoes(
                    [mod], texto_completo
                )
                if (
                    resultado_regex
                    and resultado_regex[0].get("posicao_inicio") is not None
                ):
                    posicao = (
                        resultado_regex[0]["posicao_inicio"],
                        resultado_regex[0]["posicao_fim"],
                    )
                    estrategia_posicao = "regex"
            except Exception:
                pass  # Regex pode falhar, continuar

            # 2. Se regex falhou, tentar FUZZY (se habilitado explicitamente)
            if posicao is None and usar_fuzzy is True:
                try:
                    resultado_fuzzy = self._alg_fuzzy.calcular_posicoes(
                        [mod], texto_completo
                    )
                    if (
                        resultado_fuzzy
                        and resultado_fuzzy[0].get("posicao_inicio") is not None
                    ):
                        posicao = (
                            resultado_fuzzy[0]["posicao_inicio"],
                            resultado_fuzzy[0]["posicao_fim"],
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
                resultado.append(
                    {
                        **mod,
                        "posicao_inicio": posicao[0],
                        "posicao_fim": posicao[1],
                        "_estrategia_posicao": estrategia_posicao,
                    }
                )
            else:
                resultado.append(
                    {
                        **mod,
                        "posicao_inicio": None,
                        "posicao_fim": None,
                        "_estrategia_posicao": None,
                    }
                )

        return resultado

    def vincular_clausulas(
        self,
        modificacoes: list[dict[str, Any]],
        tags: list[dict[str, Any]],
        texto_completo: str,
    ) -> list[dict[str, Any]]:
        """
        Vincula modificações a tags usando estratégia em cascata:
        1. Calcular posições (já usa regex → fuzzy internamente)
        2. OVERLAP: se tem posição válida, tentar buscar_tag_por_posicao
        3. REGEX: se overlap falhou mas regex achou posição, usar regex para vincular
        4. FUZZY: se regex falhou, usar fuzzy (se habilitado)
        5. ML: (opcional) último recurso para casos difíceis
        6. NONE: se tudo falhar

        Retorna modificações com tag_vinculada, _estrategia_usada e _score_vinculacao.
        """
        # Decidir se usa fuzzy baseado em complexidade
        num_modificacoes = len(modificacoes)
        num_tags = len(tags)
        complexidade = num_modificacoes * num_tags
        
        usar_fuzzy_nesta_execucao = self._usar_fuzzy
        if usar_fuzzy_nesta_execucao is None:
            # Auto-detectar: desabilitar se complexidade > limiar
            usar_fuzzy_nesta_execucao = complexidade <= self._limiar_complexidade_fuzzy
            if not usar_fuzzy_nesta_execucao:
                self._fuzzy_desabilitado_auto = True
                print(f"⚠️  Fuzzy desabilitado automaticamente: {num_modificacoes} modificações × {num_tags} tags = {complexidade:,} comparações (limiar: {self._limiar_complexidade_fuzzy:,})")
        
        # Primeiro, calcular posições (passando flag para controlar fuzzy lá também)
        mods_com_posicao = self.calcular_posicoes(
            modificacoes, texto_completo, usar_fuzzy_override=usar_fuzzy_nesta_execucao
        )

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

            # 3. FUZZY: se regex falhou ou posição veio do fuzzy (e se habilitado)
            if tag_vinculada is None and usar_fuzzy_nesta_execucao:
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
            elif tag_vinculada is None and not usar_fuzzy_nesta_execucao:
                self._stats["fuzzy_desabilitado"] += 1

            # 5. Nenhuma estratégia funcionou
            if tag_vinculada is None:
                self._stats["nao_vinculada"] += 1

            # Adicionar aos resultados
            resultado.append(
                {
                    **mod,
                    "tag_vinculada": tag_vinculada,
                    "_estrategia_usada": estrategia_usada,
                    "_score_vinculacao": score_vinculacao,
                }
            )

        return resultado

    def obter_estatisticas(self) -> dict[str, dict[str, Any]]:
        """
        Retorna estatísticas de uso das estratégias.

        Returns:
            Dict com count e percentage de cada estratégia.
        """
        total = sum(self._stats.values()) or 1

        return {
            estrategia: {"count": count, "percentage": round(100 * count / total, 2)}
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
