"""
Módulo base com interface comum e utilitários para algoritmos de vinculação.

Todos os algoritmos devem herdar de AlgoritmoVinculacao e implementar:
- calcular_posicoes(): Calcula posicao_inicio/posicao_fim das modificações
- vincular_clausulas(): Vincula modificações às tags
"""

import sys
from pathlib import Path

# Adicionar tests/ ao path para importar framework
tests_dir = Path(__file__).parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from framework_comparacao import AlgoritmoVinculacao


class UtilitariosVinculacao:
    """Utilitários comuns para algoritmos de vinculação"""

    @staticmethod
    def extrair_texto_busca(modificacao: dict) -> str | None:
        """
        Extrai o texto a buscar de uma modificação.

        Args:
            modificacao: Dict com tipo e conteudo

        Returns:
            Texto a buscar no documento ou None
        """
        tipo = modificacao.get("tipo")
        conteudo = modificacao.get("conteudo", {})

        if tipo == "INSERCAO":
            return conteudo.get("novo")
        elif tipo == "ALTERACAO":
            # Para alteração, buscar pelo texto novo
            return conteudo.get("novo")
        elif tipo == "REMOCAO":
            # Para remoção, buscar pelo texto original
            return conteudo.get("original")

        return None

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """
        Normaliza texto para comparação (minúsculas, sem espaços extras).

        Args:
            texto: Texto a normalizar

        Returns:
            Texto normalizado
        """
        return " ".join(texto.lower().split())

    @staticmethod
    def calcular_overlap(
        pos_inicio_a: int,
        pos_fim_a: int,
        pos_inicio_b: int,
        pos_fim_b: int,
    ) -> float:
        """
        Calcula porcentagem de sobreposição do intervalo A em relação ao intervalo B.

        IMPORTANTE: Retorna quanto do intervalo A (modificação) está contido no intervalo B (tag).
        Isso é diferente do Jaccard Index (interseção/união).

        Args:
            pos_inicio_a, pos_fim_a: Intervalo A (tipicamente a modificação)
            pos_inicio_b, pos_fim_b: Intervalo B (tipicamente a tag)

        Returns:
            Porcentagem de sobreposição de A em B (0.0 a 1.0)

        Exemplo:
            - A: 100→120 (20 chars)
            - B: 90→150 (60 chars)
            - Intersecção: 100→120 = 20 chars
            - Overlap = 20/20 = 1.0 (100% de A está em B)
        """
        if pos_fim_a < pos_inicio_b or pos_fim_b < pos_inicio_a:
            return 0.0  # Sem sobreposição

        # Calcular interseção
        inicio_intersecao = max(pos_inicio_a, pos_inicio_b)
        fim_intersecao = min(pos_fim_a, pos_fim_b)
        tamanho_intersecao = fim_intersecao - inicio_intersecao

        # Calcular quanto de A está em B
        tamanho_a = pos_fim_a - pos_inicio_a

        if tamanho_a == 0:
            return 0.0

        # Retorna porcentagem de A que está dentro de B
        return tamanho_intersecao / tamanho_a

    @staticmethod
    def buscar_tag_por_posicao(
        posicao_inicio: int, posicao_fim: int, tags: list[dict]
    ) -> dict | None:
        """
        Busca tag que melhor sobrepõe com a posição fornecida.

        Args:
            posicao_inicio: Início da modificação
            posicao_fim: Fim da modificação
            tags: Lista de tags disponíveis

        Returns:
            Tag com maior sobreposição ou None
        """
        melhor_tag = None
        melhor_overlap = 0.0

        for tag in tags:
            tag_inicio = tag.get("posicao_inicio")
            tag_fim = tag.get("posicao_fim")

            if tag_inicio is None or tag_fim is None:
                continue

            overlap = UtilitariosVinculacao.calcular_overlap(
                posicao_inicio, posicao_fim, tag_inicio, tag_fim
            )

            if overlap > melhor_overlap:
                melhor_overlap = overlap
                melhor_tag = tag

        # Retornar apenas se houver sobreposição significativa (>10%)
        if melhor_overlap > 0.1:
            return melhor_tag

        return None


__all__ = ["AlgoritmoVinculacao", "UtilitariosVinculacao"]
