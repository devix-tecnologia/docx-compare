"""
Testes para vinculação de modificações do tipo INSERCAO às cláusulas.

Task 012: Modificações do tipo inserção não estão sendo associadas à cláusula.

Root causes:
1. _vincular_por_sobreposicao_com_score não trata posicao_inicio=None,
   causando TypeError (max(None, int)) que impede vinculação.
2. INSERCAO com posições fora das regiões de tags não tem fallback
   para vincular usando clausula_modificada (número vindo do AST diff).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from directus_server import DirectusAPI, ResultadoVinculacao, TagMapeada


@pytest.fixture
def api():
    with patch("directus_server.requests") as mock_requests:
        mock_requests.get.return_value = MagicMock(status_code=200, json=lambda: {})
        mock_requests.post.return_value = MagicMock(status_code=200, json=lambda: {})
        yield DirectusAPI()


def _make_tag(nome, inicio, fim, clausula_id, clausula_numero, score=1.0):
    """Helper para criar TagMapeada nos testes."""
    return TagMapeada(
        tag_id=f"tag-{nome}",
        tag_nome=nome,
        posicao_inicio_original=inicio,
        posicao_fim_original=fim,
        clausulas=[
            {
                "id": clausula_id,
                "numero": clausula_numero,
                "nome": f"Cláusula {clausula_numero}",
                "status": "published",
            }
        ],
        score_inferencia=score,
        metodo="conteudo",
    )


# ===========================================================================
# Testes de bug: posicao_inicio=None não deve causar TypeError
# ===========================================================================


class TestInsercaoComPosicaoNula:
    """
    INSERCAO e REMOCAO com posicao_inicio=None não podem causar TypeError.
    Bug: max(None, int) levanta TypeError silenciosamente abortando a vinculação.
    """

    def test_insercao_com_posicao_nula_nao_levanta_typeerror(self, api):
        """
        Bug: _vincular_por_sobreposicao_com_score chamava max(None, int)
        quando posicao_inicio=None, causando TypeError.
        """
        tags = [_make_tag("CLAUSULA-1", 0, 100, "cl-1", "1.1")]
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "texto inserido"},
                "posicao_inicio": None,
                "posicao_fim": None,
            }
        ]

        # Não deve levantar TypeError
        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        assert isinstance(resultado, ResultadoVinculacao)
        assert (
            len(resultado.vinculadas)
            + len(resultado.nao_vinculadas)
            + len(resultado.revisao_manual)
            == 1
        )

    def test_remocao_com_posicao_nula_nao_levanta_typeerror(self, api):
        """REMOCAO também tem posicao_inicio=None e não deve causar TypeError."""
        tags = [_make_tag("CLAUSULA-1", 0, 100, "cl-1", "1.1")]
        modificacoes = [
            {
                "tipo": "REMOCAO",
                "conteudo": {"original": "texto removido"},
                "posicao_inicio": None,
                "posicao_fim": None,
            }
        ]

        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        assert isinstance(resultado, ResultadoVinculacao)
        total = (
            len(resultado.vinculadas)
            + len(resultado.nao_vinculadas)
            + len(resultado.revisao_manual)
        )
        assert total == 1

    def test_lista_mista_com_posicoes_nulas_nao_interrompe_loop(self, api):
        """
        Quando há modificações com e sem posições na mesma lista,
        o TypeError em uma não deve impedir o processamento das demais.
        """
        tags = [_make_tag("CLAUSULA-2", 200, 400, "cl-2", "2.1")]
        modificacoes = [
            {
                "tipo": "REMOCAO",
                "conteudo": {"original": "removido"},
                "posicao_inicio": None,
                "posicao_fim": None,
            },
            {
                "tipo": "ALTERACAO",
                "conteudo": {"original": "original", "novo": "novo"},
                "posicao_inicio": 250,
                "posicao_fim": 300,
            },
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "inserido"},
                "posicao_inicio": None,
                "posicao_fim": None,
            },
        ]

        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        total = (
            len(resultado.vinculadas)
            + len(resultado.nao_vinculadas)
            + len(resultado.revisao_manual)
        )
        assert total == 3, "Todas as 3 modificações devem ser processadas"
        # A ALTERACAO com posições válidas dentro da tag deve ser vinculada
        vinculadas_tipos = [
            item["modificacao"]["tipo"] for item in resultado.vinculadas
        ]
        assert "ALTERACAO" in vinculadas_tipos, (
            "ALTERACAO com overlap deve ser vinculada"
        )


# ===========================================================================
# Testes de vinculação positional de INSERCAO
# ===========================================================================


class TestInsercaoComPosicaoValida:
    """INSERCAO com posicao_inicio/posicao_fim dentro de uma tag deve ser vinculada."""

    def test_insercao_dentro_tag_vinculada_automaticamente(self, api):
        """
        INSERCAO com posições que sobrepõem uma tag deve ser vinculada
        (score >= 0.8 → vinculadas).
        """
        tags = [_make_tag("CLAUSULA-3", 100, 500, "cl-3", "3.1")]
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "parágrafo inserido na cláusula 3"},
                "posicao_inicio": 200,
                "posicao_fim": 350,
            }
        ]

        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        # Deve estar em vinculadas ou revisao_manual (score >= 0.5)
        vinculada = len(resultado.vinculadas) > 0 or len(resultado.revisao_manual) > 0
        assert vinculada, "INSERCAO dentro de tag deve ser vinculada"

    def test_insercao_com_sobreposicao_total_na_clausula(self, api):
        """
        INSERCAO completamente dentro da região de uma tag
        deve ter score alto e ir para vinculadas (não revisao_manual).
        """
        # Tag cobre posição 0-1000
        tags = [_make_tag("CLAUSULA-1", 0, 1000, "cl-1", "1.1")]
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "novo parágrafo"},
                "posicao_inicio": 100,
                "posicao_fim": 200,
            }
        ]

        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        assert len(resultado.vinculadas) == 1, (
            "INSERCAO inteiramente dentro da tag deve ir para vinculadas"
        )
        vinculacao = resultado.vinculadas[0]
        assert vinculacao["tag"].tag_nome == "CLAUSULA-1"
        assert vinculacao["score"] >= 0.8


# ===========================================================================
# Testes de fallback por clausula_modificada
# ===========================================================================


class TestInsercaoFallbackClausulaModificada:
    """
    INSERCAO sem sobreposição posicional deve usar clausula_modificada
    (número da cláusula vindo do AST diff) como fallback para vinculação.
    """

    def test_insercao_sem_overlap_usa_clausula_modificada(self, api):
        """
        INSERCAO com posição fora de todas as tags mas com clausula_modificada
        deve ser vinculada via número da cláusula.
        Caso típico: parágrafo novo inserido DEPOIS do conteúdo original da cláusula.
        """
        # Tags cobrem posições 0-200 e 300-500
        tags = [
            _make_tag("CLAUSULA-2", 300, 500, "cl-2", "2.1"),
            _make_tag("CLAUSULA-3", 600, 900, "cl-3", "3.1"),
        ]
        # INSERCAO está em posição 510-590 (entre tags, sem overlap)
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "parágrafo novo entre cláusulas"},
                "posicao_inicio": 510,
                "posicao_fim": 590,
                "clausula_modificada": "2.1",  # Do AST diff - pertence à cláusula 2.1
            }
        ]

        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        # Deve ser vinculada à cláusula 2.1 via fallback
        vinculadas = resultado.vinculadas + resultado.revisao_manual
        assert len(vinculadas) == 1, (
            "INSERCAO com clausula_modificada deve ser vinculada mesmo sem overlap"
        )
        tag_vinculada = vinculadas[0]["tag"]
        assert tag_vinculada.tag_nome == "CLAUSULA-2"

    def test_insercao_sem_overlap_sem_clausula_modificada_fica_nao_vinculada(self, api):
        """
        INSERCAO sem overlap E sem clausula_modificada deve permanecer
        em nao_vinculadas (não há como determinar a cláusula correta).
        """
        tags = [_make_tag("CLAUSULA-1", 0, 100, "cl-1", "1.1")]
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "conteúdo completamente novo"},
                "posicao_inicio": 500,
                "posicao_fim": 600,
                # Sem clausula_modificada
            }
        ]

        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        assert len(resultado.nao_vinculadas) == 1
        assert len(resultado.vinculadas) == 0
        assert len(resultado.revisao_manual) == 0

    def test_insercao_com_posicao_nula_e_clausula_modificada_vinculada(self, api):
        """
        INSERCAO com posicao_inicio=None mas com clausula_modificada
        deve ser vinculada via fallback de número de cláusula.
        Caso típico: texto inserido não encontrado na busca textual.
        """
        tags = [_make_tag("CLAUSULA-4", 400, 700, "cl-4", "4.1")]
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "texto não encontrado na busca"},
                "posicao_inicio": None,
                "posicao_fim": None,
                "clausula_modificada": "4.1",  # Vem do data-clause no diff HTML
            }
        ]

        resultado = api._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags, modificacoes=modificacoes
        )

        # Deve ser vinculada à cláusula 4.1
        vinculadas = resultado.vinculadas + resultado.revisao_manual
        assert len(vinculadas) == 1, (
            "INSERCAO com posicao=None mas clausula_modificada deve ser vinculada"
        )
        tag_vinculada = vinculadas[0]["tag"]
        assert tag_vinculada.tag_nome == "CLAUSULA-4"


# ===========================================================================
# Testes de integração: _vincular_modificacoes_clausulas_novo com INSERCAO
# ===========================================================================


class TestVincularModificacoesNovoComInsercao:
    """
    Testa o método _vincular_modificacoes_clausulas_novo com modificações
    do tipo INSERCAO, garantindo que o fluxo completo funciona.
    """

    def test_insercao_vinculada_no_fluxo_completo(self, api):
        """
        INSERCAO deve ser vinculada no fluxo completo de vinculação
        quando o texto está presente no documento modificado.
        """
        # Texto original (base das tags)
        texto_modificado = (
            "Cláusula 1: texto original da cláusula um. "
            "Parágrafo novo inserido aqui. "
            "Cláusula 2: texto da cláusula dois."
        )
        texto_com_tags = (
            "{{CLAUSULA-1}}Cláusula 1: texto original da cláusula um.{{/CLAUSULA-1}} "
            "{{CLAUSULA-2}}Cláusula 2: texto da cláusula dois.{{/CLAUSULA-2}}"
        )
        tags_modelo = [
            {
                "tag_nome": "CLAUSULA-1",
                "conteudo": "Cláusula 1: texto original da cláusula um.",
                "clausulas": [
                    {
                        "id": "cl-1",
                        "numero": "1.1",
                        "nome": "Cláusula 1",
                        "status": "published",
                    }
                ],
                "posicao_inicio_texto": 14,
                "posicao_fim_texto": 57,
            },
        ]
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Parágrafo novo inserido aqui."},
                "posicao_inicio": 46,
                "posicao_fim": 74,
                "clausula_modificada": "1.1",
            }
        ]

        resultado_vinculacao = api._vincular_modificacoes_clausulas_novo(
            modificacoes=modificacoes,
            tags_modelo=tags_modelo,
            texto_com_tags=texto_com_tags,
            texto_original=texto_modificado,
        )

        assert resultado_vinculacao is not None
        mods = resultado_vinculacao.get("modificacoes", [])
        assert len(mods) == 1
        # A inserção deve ter clausula_id definido
        insercao = mods[0]
        assert insercao.get("clausula_id") is not None, (
            "INSERCAO deve ser vinculada à cláusula no fluxo completo"
        )
