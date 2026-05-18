"""
Testes de borda extensivos para o algoritmo de produção (baseline).

FOCO: Modificações sequenciais que alteram posições de tags subsequentes.
Cenários críticos que podem causar bugs de vinculação.
"""

import sys
from pathlib import Path

# Setup path
tests_dir = Path(__file__).parent.parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

import pytest
from algoritmos.producao.algoritmo import AlgoritmoProducao


@pytest.fixture
def algoritmo():
    """Instância do algoritmo de produção"""
    return AlgoritmoProducao()


class TestModificacoesSequenciais:
    """
    Testes para modificações sequenciais que alteram posições.

    PROBLEMA: Modificação 1 altera o texto, então posições de tags/modificações
    seguintes ficam desatualizadas.
    """

    def test_insercao_desloca_tags_seguintes(self, algoritmo):
        """
        INSERCAO no início desloca TODAS as tags para frente.

        Texto original: "Cláusula 1. Cláusula 2."
        Após INSERCAO "Preâmbulo. " no início: "Preâmbulo. Cláusula 1. Cláusula 2."

        Tag 2 estava em [12-23], agora está em [12+11-23+11] = [23-34]
        """
        texto_original = "Cláusula 1. Cláusula 2."
        texto_modificado = "Preâmbulo. Cláusula 1. Cláusula 2."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Cláusula 1",
                "texto": "Cláusula 1.",
                # Posições NO TEXTO ORIGINAL
                "posicao_inicio": 0,
                "posicao_fim": 11,
            },
            {
                "id": "tag_2",
                "titulo": "Cláusula 2",
                "texto": "Cláusula 2.",
                # Posições NO TEXTO ORIGINAL
                "posicao_inicio": 12,
                "posicao_fim": 23,
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Preâmbulo. "},
                # Sem posição - algoritmo precisa calcular
            },
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Cláusula 1."},
                # Esta modificação está na tag_1
            },
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Cláusula 2."},
                # Esta modificação está na tag_2
            },
        ]

        # O texto passado é o MODIFICADO (após todas as mudanças)
        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto_modificado)

        # Modificação 1: "Preâmbulo." não deve vincular a nenhuma tag
        assert resultado[0].get("tag_vinculada") is None, (
            "Preâmbulo não deve vincular - está antes de todas as tags"
        )

        # Modificação 2: "Cláusula 1." deve vincular a tag_1
        assert resultado[1].get("tag_vinculada") is not None, (
            "Cláusula 1 deve vincular a tag_1"
        )
        assert resultado[1]["tag_vinculada"]["id"] == "tag_1"

        # Modificação 3: "Cláusula 2." deve vincular a tag_2
        assert resultado[2].get("tag_vinculada") is not None, (
            "Cláusula 2 deve vincular a tag_2"
        )
        assert resultado[2]["tag_vinculada"]["id"] == "tag_2"

    def test_remocao_desloca_tags_seguintes_para_tras(self, algoritmo):
        """
        REMOCAO no início desloca tags seguintes para TRÁS.

        Texto original: "Preâmbulo desnecessário. Cláusula 1."
        Após REMOCAO: "Cláusula 1."

        Tag 1 estava em [25-36], após remoção fica em [0-11]
        """
        texto_original = "Preâmbulo desnecessário. Cláusula 1."
        texto_modificado = "Cláusula 1."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Cláusula 1",
                "texto": "Cláusula 1.",
                # Posição NO TEXTO ORIGINAL
                "posicao_inicio": 25,
                "posicao_fim": 36,
            },
        ]

        modificacoes = [
            {
                "tipo": "REMOCAO",
                "conteudo": {"original": "Preâmbulo desnecessário. "},
            },
        ]

        # REMOCAO não está no texto modificado, então não calcula posição
        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto_modificado)

        # REMOCAO não deve vincular (não está no texto)
        assert resultado[0].get("tag_vinculada") is None


class TestSobreposicao:
    """Testes para modificações que se sobrepõem ou tocam tags."""

    def test_modificacao_dentro_de_tag(self, algoritmo):
        """
        Modificação que é substring da tag deve vincular.

        Caso: modificação "O prazo é de 24 meses" é substring da cláusula completa.
        """
        # Texto APÓS a modificação
        texto_modificado = "Cláusula 1 - O prazo é de 24 meses."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Cláusula Prazo",
                # Tag contém quase o mesmo texto (pequena diferença: 12 vs 24)
                "texto": "Cláusula 1 - O prazo é de 12 meses.",
                "posicao_inicio": 0,
                "posicao_fim": 35,
            },
        ]

        # Modificação é substring significativa (alta similaridade)
        modificacoes = [
            {
                "tipo": "ALTERACAO",
                "conteudo": {"novo": "O prazo é de 24 meses"},  # Substring maior
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto_modificado)

        # partial_ratio deve ser alto (substring match)
        # "O prazo é de 24 meses" vs "Cláusula 1 - O prazo é de 12 meses."
        # partial: ~94% (substring match)
        assert resultado[0].get("tag_vinculada") is not None, (
            "Modificação substring da tag deve vincular por partial_ratio!"
        )
        assert resultado[0]["tag_vinculada"]["id"] == "tag_1"

    def test_modificacao_span_multiplas_tags(self, algoritmo):
        """
        Modificação que afeta múltiplas tags.

        Deve vincular à tag com maior overlap.
        """
        texto = "Cláusula 1. Cláusula 2. Cláusula 3."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Cláusula 1",
                "texto": "Cláusula 1.",
                "posicao_inicio": 0,
                "posicao_fim": 11,
            },
            {
                "id": "tag_2",
                "titulo": "Cláusula 2",
                "texto": "Cláusula 2.",
                "posicao_inicio": 12,
                "posicao_fim": 23,
            },
            {
                "id": "tag_3",
                "titulo": "Cláusula 3",
                "texto": "Cláusula 3.",
                "posicao_inicio": 24,
                "posicao_fim": 35,
            },
        ]

        modificacoes = [
            {
                "tipo": "ALTERACAO",
                # Modificação que span tags 1 e 2
                "conteudo": {"novo": "Cláusula 1. Cláusula 2."},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Deve vincular a alguma tag (preferencialmente a com maior overlap)
        assert resultado[0].get("tag_vinculada") is not None


class TestCasosLimite:
    """Testes para casos limite e edge cases."""

    def test_texto_duplicado_na_tag(self, algoritmo):
        """
        Tag com texto que se repete.

        Ex: "Item 1. Item 1." - modificação pode bater em qualquer ocorrência.
        """
        texto = "Item 1. Item 1. Conclusão."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Itens duplicados",
                "texto": "Item 1. Item 1.",
                "posicao_inicio": 0,
                "posicao_fim": 15,
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Item 1."},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Deve vincular (mesmo com duplicação)
        assert resultado[0].get("tag_vinculada") is not None
        assert resultado[0]["tag_vinculada"]["id"] == "tag_1"

    def test_modificacao_vazia(self, algoritmo):
        """Modificação sem conteúdo."""
        texto = "Texto normal."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Tag 1",
                "texto": "Texto normal.",
                "posicao_inicio": 0,
                "posicao_fim": 13,
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": ""},  # Vazio
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Modificação vazia não deve vincular
        assert resultado[0].get("tag_vinculada") is None

    def test_tag_sem_texto(self, algoritmo):
        """Tag sem conteúdo (campo texto vazio)."""
        texto = "Texto qualquer."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Tag sem conteúdo",
                "texto": "",  # Vazio
                "posicao_inicio": 0,
                "posicao_fim": 0,
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Texto qualquer."},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Não deve vincular a tag sem texto
        assert resultado[0].get("tag_vinculada") is None

    def test_posicoes_tags_invertidas(self, algoritmo):
        """
        Tags com posições invertidas (fim < inicio).

        Possível bug nos dados.
        """
        texto = "Texto normal."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Tag com posição invertida",
                "texto": "Texto normal.",
                "posicao_inicio": 13,  # Fim
                "posicao_fim": 0,  # Início (INVERTIDO)
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Texto normal."},
            },
        ]

        # Não deve dar erro
        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Comportamento: pode vincular por fuzzy (ignora posições ruins)
        # Ou não vincular (depende da implementação)
        assert len(resultado) == 1

    def test_modificacoes_consecutivas_mesma_posicao(self, algoritmo):
        """
        Múltiplas modificações na mesma posição.

        Ex: Duas inserções consecutivas no mesmo lugar.
        """
        texto = "Início. Inserção A. Inserção B. Fim."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Bloco de inserções",
                "texto": "Inserção A. Inserção B.",
                "posicao_inicio": 8,
                "posicao_fim": 31,
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Inserção A. "},
            },
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Inserção B. "},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Ambas devem vincular à mesma tag
        assert resultado[0].get("tag_vinculada") is not None
        assert resultado[0]["tag_vinculada"]["id"] == "tag_1"

        assert resultado[1].get("tag_vinculada") is not None
        assert resultado[1]["tag_vinculada"]["id"] == "tag_1"


class TestThresholdDinamico:
    """Testes para o threshold dinâmico baseado no tamanho do texto."""

    def test_texto_muito_curto_threshold_alto(self, algoritmo):
        """Texto < 20 chars: threshold 90%"""
        texto = "A"

        tags = [
            {
                "id": "tag_1",
                "titulo": "Tag A",
                "texto": "A",
                "posicao_inicio": 0,
                "posicao_fim": 1,
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "A"},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Match perfeito: deve vincular
        assert resultado[0].get("tag_vinculada") is not None

    def test_texto_medio_threshold_medio(self, algoritmo):
        """Texto 20-100 chars: threshold 85%"""
        texto = "Este é um texto de tamanho médio para testar o threshold."

        tags = [
            {
                "id": "tag_1",
                "titulo": "Texto médio",
                "texto": "Este é um texto de tamanho médio para testar o threshold.",
                "posicao_inicio": 0,
                "posicao_fim": len(texto),
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": texto},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        assert resultado[0].get("tag_vinculada") is not None

    def test_texto_longo_threshold_baixo(self, algoritmo):
        """Texto > 100 chars: threshold 80%"""
        texto = (
            "Este é um texto muito longo que deve usar um threshold mais "
            "flexível de 80% para permitir pequenas variações e ainda assim "
            "conseguir fazer a vinculação corretamente mesmo com templates."
        )

        tags = [
            {
                "id": "tag_1",
                "titulo": "Texto longo",
                "texto": texto,
                "posicao_inicio": 0,
                "posicao_fim": len(texto),
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": texto},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        assert resultado[0].get("tag_vinculada") is not None


class TestMetricasRapidFuzz:
    """Testes específicos para as 4 métricas do RapidFuzz."""

    def test_token_set_ratio_ignora_duplicatas(self, algoritmo):
        """
        token_set_ratio ignora tokens duplicados.

        "a b c c c" vs "a b c" = 100%
        """
        texto = "palavra palavra palavra"

        tags = [
            {
                "id": "tag_1",
                "titulo": "Com duplicatas",
                "texto": "palavra palavra palavra",
                "posicao_inicio": 0,
                "posicao_fim": len(texto),
            },
        ]

        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "palavra"},  # Só uma vez
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Deve vincular (token_set_ratio é alta)
        assert resultado[0].get("tag_vinculada") is not None

    def test_partial_ratio_detecta_substring(self, algoritmo):
        """
        partial_ratio detecta quando modificação é substring da tag.
        """
        tag_texto = "Cláusula 1 - O objeto deste contrato é a prestação de serviços."
        mod_texto = "prestação de serviços"

        texto = tag_texto

        tags = [
            {
                "id": "tag_1",
                "titulo": "Cláusula completa",
                "texto": tag_texto,
                "posicao_inicio": 0,
                "posicao_fim": len(tag_texto),
            },
        ]

        modificacoes = [
            {
                "tipo": "ALTERACAO",
                "conteudo": {"novo": mod_texto},
            },
        ]

        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

        # Substring deve vincular (partial_ratio detecta)
        assert resultado[0].get("tag_vinculada") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
