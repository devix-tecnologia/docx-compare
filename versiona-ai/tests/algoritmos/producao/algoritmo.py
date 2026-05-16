"""
Adapter do algoritmo de produção (directus_server.py) para interface comum.

Este algoritmo serve como BASELINE para comparação com novas estratégias.
"""

import sys
from pathlib import Path

# Adicionar paths necessários
tests_dir = Path(__file__).parent.parent.parent
versiona_dir = tests_dir.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))
if str(versiona_dir) not in sys.path:
    sys.path.insert(0, str(versiona_dir))

from difflib import SequenceMatcher

from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao


class AlgoritmoProducao(AlgoritmoVinculacao):
    """
    Algoritmo atualmente em produção (directus_server.py).

    Estratégia:
    - Busca simples de texto com str.find()
    - Fuzzy matching com difflib (threshold 85%)
    - Método baseado em conteúdo (não offset)
    """

    @property
    def nome(self) -> str:
        return "producao"

    @property
    def descricao(self) -> str:
        return "Algoritmo atual de produção (baseline) - busca simples + fuzzy matching"

    def calcular_posicoes(self, modificacoes: list[dict], texto: str) -> list[dict]:
        """
        Implementação baseada em _calcular_posicoes_modificacoes() do directus_server.py
        """
        for mod in modificacoes:
            tipo = mod.get("tipo")
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)

            if not texto_busca:
                continue

            # Para INSERCAO/ALTERACAO: buscar no texto modificado
            if tipo in ["INSERCAO", "ALTERACAO"]:
                pos = texto.find(texto_busca)
                if pos != -1:
                    mod["posicao_inicio"] = pos
                    mod["posicao_fim"] = pos + len(texto_busca)

            # Para REMOCAO: não está no texto modificado
            # (algoritmo atual retorna None)

        return modificacoes

    def vincular_clausulas(
        self, modificacoes: list[dict], tags: list[dict], texto: str
    ) -> list[dict]:
        """
        Implementação baseada em _vincular_modificacoes_clausulas_novo() do directus_server.py

        Usa método de conteúdo com fuzzy matching.
        """
        for mod in modificacoes:
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")

            if pos_inicio is None or pos_fim is None:
                mod["tag_vinculada"] = None
                continue

            # Extrair texto da modificação
            texto_modificacao = UtilitariosVinculacao.extrair_texto_busca(mod)
            if not texto_modificacao:
                mod["tag_vinculada"] = None
                continue

            # Buscar melhor tag por conteúdo (fuzzy) ou posição
            melhor_tag = self._buscar_melhor_tag_fuzzy(
                texto_modificacao, pos_inicio, pos_fim, tags
            )

            mod["tag_vinculada"] = melhor_tag

        return modificacoes

    def _buscar_melhor_tag_fuzzy(
        self,
        texto_modificacao: str,
        pos_inicio: int,
        pos_fim: int,
        tags: list[dict],
    ) -> dict | None:
        """
        Busca melhor tag usando fuzzy matching (threshold 85%) ou overlap de posição.

        Baseado em _vincular_modificacoes_clausulas_novo() do directus_server.py
        """
        melhor_tag = None
        melhor_score = 0.0
        threshold = 0.85

        for tag in tags:
            tag_texto = tag.get("texto", "")
            tag_inicio = tag.get("posicao_inicio")
            tag_fim = tag.get("posicao_fim")

            # Método 1: Fuzzy matching de conteúdo
            # Checar se a modificação está DENTRO do texto da tag
            if tag_texto and texto_modificacao in tag_texto:
                # Se texto modificação é substring, é match perfeito
                melhor_tag = tag
                melhor_score = 1.0
                break
            elif tag_texto:
                similarity = SequenceMatcher(None, texto_modificacao, tag_texto).ratio()

                if similarity > melhor_score:
                    melhor_score = similarity
                    if similarity >= threshold:
                        melhor_tag = tag

            # Método 2: Overlap de posição (fallback)
            if tag_inicio is not None and tag_fim is not None:
                overlap = UtilitariosVinculacao.calcular_overlap(
                    pos_inicio, pos_fim, tag_inicio, tag_fim
                )

                # Se tem overlap significativo e não achou por fuzzy
                if overlap > 0.5 and melhor_score < threshold:
                    melhor_tag = tag
                    melhor_score = overlap

        return melhor_tag


# Para importação direta
__all__ = ["AlgoritmoProducao"]
