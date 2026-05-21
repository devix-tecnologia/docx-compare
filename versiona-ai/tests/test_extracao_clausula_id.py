"""
Testes para investigar a origem do clausula_id atribuído às modificações.

Contexto (Task 015):
  Ao persistir modificações, o Directus retorna INVALID_FOREIGN_KEY para o campo
  `clausula`. A hipótese é que o ID sendo gravado pode ser o ID da TAG
  (modelo_contrato_tag.id) em vez do ID da CLÁUSULA (clausula.id).

Estrutura retornada pelo Directus para `tags.clausulas.*`:
  {
    "id":              "<CLAUSULA_UUID>",   ← ID próprio da cláusula (queremos este)
    "tag":             "<TAG_UUID>",        ← FK de volta à tag (NÃO queremos este)
    "modelo_contrato": "<MODELO_UUID>",
    "numero":          "3.3",
    "nome":            "Cláusula 3ª - 3.3",
    "status":          "published"
  }

O Directus retorna sempre este único formato — não há variações ou fallbacks.
Os testes verificam que o código extrai `id` (clausula) e não confunde com
`tag` (FK de volta ao tag) nem com o `tag_id` do objeto TagMapeada.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from directus_server import DirectusAPI, TagMapeada

# IDs intencionalmente distintos para detectar confusão entre entidades
TAG_UUID = "aaaaaaaa-0000-0000-0000-000000000001"  # ID do tag (modelo_contrato_tag)
CLAUSULA_UUID = "bbbbbbbb-1111-1111-1111-000000000002"  # ID da cláusula
MODELO_UUID = "cccccccc-2222-2222-2222-000000000003"  # ID do modelo

# Reproduz o ID problemático reportado no log do task-015
CLAUSULA_UUID_PROBLEMA = "59a034cc-e29d-4ed2-8989-4a945582d215"


@pytest.fixture
def api():
    with patch("directus_server.requests") as mock_requests:
        mock_requests.get.return_value = MagicMock(status_code=200, json=lambda: {})
        mock_requests.post.return_value = MagicMock(status_code=200, json=lambda: {})
        yield DirectusAPI()


def _vincula_uma_mod(api, tag_mapeada, modificacao):
    """
    Executa o pipeline completo de vinculação (incluindo aplicar_tag) mockando
    _inferir_posicoes_via_conteudo_com_contexto para retornar o TagMapeada pronto.
    Retorna a modificação enriquecida com clausula_id (se houver).
    """
    with patch.object(
        api,
        "_inferir_posicoes_via_conteudo_com_contexto",
        return_value=[tag_mapeada],
    ):
        retorno = api._vincular_modificacoes_clausulas_novo(
            modificacoes=[modificacao],
            tags_modelo=[{"tag_nome": tag_mapeada.tag_nome}],  # dummy, não será usado
            texto_com_tags="texto dummy",
            texto_original="texto dummy",
        )

    # _vincular_modificacoes_clausulas_novo retorna modificacoes enriquecidas
    modificacoes_enriquecidas = retorno.get("modificacoes", [])
    if modificacoes_enriquecidas:
        return modificacoes_enriquecidas[0]
    return modificacao


def _make_tag(clausula_id, clausula_numero="3.3"):
    """
    Cria TagMapeada com o único formato que o Directus retorna para
    `contrato.modelo_contrato.tags.clausulas.*`:
      {
        "id":              "<CLAUSULA_UUID>",
        "tag":             "<TAG_UUID>",
        "modelo_contrato": "<MODELO_UUID>",
        "numero":          "3.3",
        "nome":            "...",
        "status":          "published"
      }
    """
    return TagMapeada(
        tag_id=TAG_UUID,
        tag_nome="CLAUSULA-3-3",
        posicao_inicio_original=0,
        posicao_fim_original=200,
        clausulas=[
            {
                "id": clausula_id,  # ID próprio da cláusula ← queremos este
                "tag": TAG_UUID,  # FK de volta ao tag ← NÃO deve ser usado
                "modelo_contrato": MODELO_UUID,
                "numero": clausula_numero,
                "nome": f"Cláusula {clausula_numero}",
                "status": "published",
            }
        ],
        score_inferencia=1.0,
        metodo="offset",
    )


def _make_mod_dentro_da_tag():
    return {
        "tipo": "ALTERACAO",
        "conteudo": {"original": "texto original", "novo": "texto alterado"},
        "posicao_inicio": 50,
        "posicao_fim": 100,
    }


# ===========================================================================
# Extração correta do clausula_id
# ===========================================================================


class TestExtracaoClausulaId:
    """
    Verifica que o código extrai o campo `id` da cláusula (ID próprio da entidade)
    e não confunde com o campo `tag` (FK de volta ao tag) nem com o tag_id
    do TagMapeada.
    """

    def test_extrai_id_da_clausula_e_nao_da_tag(self, api):
        """
        CRÍTICO: clausulas[0]["id"] deve ser o ID da cláusula.
        clausulas[0]["tag"] é o FK de volta ao tag — não deve ser usado.
        """
        tag = _make_tag(CLAUSULA_UUID)
        mod = _make_mod_dentro_da_tag()

        resultado = _vincula_uma_mod(api, tag, mod)

        assert resultado.get("clausula_id") == CLAUSULA_UUID, (
            f"clausula_id deveria ser {CLAUSULA_UUID} (campo 'id' da cláusula), "
            f"mas foi {resultado.get('clausula_id')} — possível confusão com "
            f"o campo 'tag' (FK) ou o tag_id do TagMapeada ({TAG_UUID})"
        )

    def test_clausula_id_nao_e_o_tag_uuid(self, api):
        """O clausula_id extraído nunca deve ser igual ao tag_id do TagMapeada."""
        tag = _make_tag(CLAUSULA_UUID)
        mod = _make_mod_dentro_da_tag()

        resultado = _vincula_uma_mod(api, tag, mod)

        assert resultado.get("clausula_id") != TAG_UUID, (
            "BUG: clausula_id foi definido com o ID do tag (campo 'tag' ou tag_id), "
            "não com o ID da cláusula"
        )

    def test_clausula_numero_extraido_da_clausula(self, api):
        """clausula_numero deve vir do campo 'numero' da cláusula."""
        tag = _make_tag(CLAUSULA_UUID, clausula_numero="3.3")
        mod = _make_mod_dentro_da_tag()

        resultado = _vincula_uma_mod(api, tag, mod)

        assert resultado.get("clausula_numero") == "3.3"

    def test_reproducao_caso_task_015(self, api):
        """
        Reproduz exatamente o cenário do log do task-015.
        O ID da tag é diferente do ID da cláusula — se o código confundir
        os dois, o FK inválido será gravado no Directus.
        """
        tag = TagMapeada(
            tag_id=TAG_UUID,  # tag com ID diferente da clausula
            tag_nome="CLAUSULA-3-3",
            posicao_inicio_original=0,
            posicao_fim_original=200,
            clausulas=[
                {
                    "id": CLAUSULA_UUID_PROBLEMA,  # ID da cláusula (o problemático)
                    "tag": TAG_UUID,  # FK de volta ao tag (diferente!)
                    "modelo_contrato": MODELO_UUID,
                    "numero": "3.3",
                    "nome": "Cláusula 3ª",
                    "status": "published",
                }
            ],
            score_inferencia=1.0,
            metodo="offset",
        )
        mod = _make_mod_dentro_da_tag()

        resultado = _vincula_uma_mod(api, tag, mod)

        assert resultado.get("clausula_id") == CLAUSULA_UUID_PROBLEMA, (
            f"clausula_id deveria ser {CLAUSULA_UUID_PROBLEMA}, "
            f"mas foi {resultado.get('clausula_id')}"
        )
        assert resultado.get("clausula_id") != TAG_UUID, (
            "BUG DETECTADO: clausula_id foi setado com o ID do tag, não da cláusula"
        )
