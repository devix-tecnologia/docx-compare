"""
TDD — Task 015: falha silenciosa ao persistir modificações.

Comportamento esperado:
  - Quando _atualizar_versao_com_modificacoes falha (Directus rejeita o write
    aninhado com INVALID_FOREIGN_KEY ou qualquer HTTP 4xx/5xx), a versão deve
    ter seu status atualizado para "erro" via PATCH separado e simples.
  - Quando a persistência é bem-sucedida, o status NÃO deve ser alterado para
    "erro".
  - A observação gravada junto ao status "erro" deve conter a mensagem de erro
    truncada a 200 caracteres (evitar payloads gigantes).

Valores válidos de status da versão (Directus):
  draft | processar | em_processamento | concluido | erro | fechada
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from directus_server import DirectusAPI

VERSAO_ID = "aaaaaaaa-0000-0000-0000-000000000001"
ERRO_DIRECTUS = (
    'HTTP 400: {"errors":[{"message":"Invalid foreign key '
    '"59a034cc-e29d-4ed2-8989-4a945582d215" for field \\"clausula\\" '
    'in collection \\"modificacao\\".","extensions":{"code":"INVALID_FOREIGN_KEY"}}]}'
)


@pytest.fixture
def api():
    instance = DirectusAPI()
    instance.repo = Mock()
    instance.repo.atualizar_status_versao.return_value = {
        "success": True,
        "status_code": 200,
        "data": {},
    }
    return instance


# ===========================================================================
# Método: _persistir_modificacoes_com_fallback
# ===========================================================================


class TestPersistirModificacoesComFallback:
    """
    Testa o método que tenta persistir modificações e, em caso de falha,
    atualiza o status da versão para "erro" via PATCH separado.
    """

    def test_sucesso_nao_chama_status_erro(self, api):
        """Quando a persistência funciona, atualizar_status_versao NÃO deve ser chamado."""
        with patch.object(
            api,
            "_atualizar_versao_com_modificacoes",
            return_value={"success": True, "modificacoes_criadas": 3},
        ):
            api._persistir_modificacoes_com_fallback(
                VERSAO_ID, [{"categoria": "ALTERACAO"}]
            )

        for c in api.repo.atualizar_status_versao.call_args_list:
            status = c.kwargs.get("status") or (c.args[1] if len(c.args) > 1 else None)
            assert status != "erro", (
                "atualizar_status_versao('erro') não deve ser chamado em caso de sucesso"
            )

    def test_falha_chama_status_erro(self, api):
        """Quando a persistência falha, atualizar_status_versao('erro') deve ser chamado."""
        with patch.object(
            api,
            "_atualizar_versao_com_modificacoes",
            return_value={"success": False, "error": ERRO_DIRECTUS, "status_code": 400},
        ):
            api._persistir_modificacoes_com_fallback(
                VERSAO_ID, [{"categoria": "ALTERACAO"}]
            )

        api.repo.atualizar_status_versao.assert_called_once()
        kwargs = api.repo.atualizar_status_versao.call_args
        status_passado = kwargs.kwargs.get("status") or kwargs.args[1]
        assert status_passado == "erro"

    def test_falha_inclui_observacao_com_erro(self, api):
        """A observação deve conter parte da mensagem de erro para diagnóstico."""
        with patch.object(
            api,
            "_atualizar_versao_com_modificacoes",
            return_value={"success": False, "error": ERRO_DIRECTUS, "status_code": 400},
        ):
            api._persistir_modificacoes_com_fallback(VERSAO_ID, [])

        kwargs = api.repo.atualizar_status_versao.call_args
        observacao = kwargs.kwargs.get("observacao") or (
            kwargs.args[2] if len(kwargs.args) > 2 else None
        )
        assert observacao is not None, "observacao deve ser preenchida"
        assert "INVALID_FOREIGN_KEY" in observacao or "400" in observacao

    def test_observacao_truncada_a_200_chars(self, api):
        """Mensagem de erro muito longa deve ser truncada para caber na observação."""
        erro_longo = "A" * 500
        with patch.object(
            api,
            "_atualizar_versao_com_modificacoes",
            return_value={"success": False, "error": erro_longo, "status_code": 400},
        ):
            api._persistir_modificacoes_com_fallback(VERSAO_ID, [])

        kwargs = api.repo.atualizar_status_versao.call_args
        observacao = kwargs.kwargs.get("observacao") or (
            kwargs.args[2] if len(kwargs.args) > 2 else None
        )
        assert len(observacao) <= 200, (
            f"observacao deve ter no máximo 200 chars, tem {len(observacao)}"
        )

    def test_falha_retorna_success_false(self, api):
        """O método deve retornar indicador de falha quando a persistência falha."""
        with patch.object(
            api,
            "_atualizar_versao_com_modificacoes",
            return_value={"success": False, "error": ERRO_DIRECTUS, "status_code": 400},
        ):
            resultado = api._persistir_modificacoes_com_fallback(VERSAO_ID, [])

        assert resultado["success"] is False

    def test_sucesso_retorna_success_true(self, api):
        """O método deve repassar o resultado de sucesso."""
        with patch.object(
            api,
            "_atualizar_versao_com_modificacoes",
            return_value={"success": True, "modificacoes_criadas": 2},
        ):
            resultado = api._persistir_modificacoes_com_fallback(VERSAO_ID, [])

        assert resultado["success"] is True

    def test_versao_id_correto_no_fallback(self, api):
        """O fallback de status deve usar o mesmo versao_id da persistência."""
        outro_id = "bbbbbbbb-1111-1111-1111-000000000002"
        with patch.object(
            api,
            "_atualizar_versao_com_modificacoes",
            return_value={
                "success": False,
                "error": "erro qualquer",
                "status_code": 500,
            },
        ):
            api._persistir_modificacoes_com_fallback(outro_id, [])

        kwargs = api.repo.atualizar_status_versao.call_args
        versao_id_passado = kwargs.kwargs.get("versao_id") or kwargs.args[0]
        assert versao_id_passado == outro_id
