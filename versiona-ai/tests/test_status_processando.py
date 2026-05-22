"""
Testes TDD para a transição de status "em_processamento" em process_versao.

Garante que:
- Status "em_processamento" é setado ANTES do processamento começar
- Status "erro" é setado quando processamento falha
- Modo mock=True não altera status (sem efeito colateral)
- Observação de erro é truncada para evitar payloads grandes
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from directus_server import DirectusAPI


@pytest.fixture
def api():
    """DirectusAPI com repositório mockado."""
    instance = DirectusAPI()
    instance.repo = Mock()
    instance.repo.atualizar_status_versao.return_value = {
        "success": True,
        "status_code": 200,
        "data": {},
    }
    instance.repo.get_versao_para_processar.return_value = None
    return instance


@pytest.fixture
def versao_data_minimal():
    """Dados mínimos de versão para testes."""
    return {"id": "v123", "arquivo": "file-1", "contrato": {}}


class TestProcessVersaoStatusEmProcessamento:
    """Testa transições de status em process_versao()."""

    def test_seta_em_processamento_antes_de_processar(self, api, versao_data_minimal):
        """atualizar_status_versao('em_processamento') deve ser chamado ANTES de _process_versao_com_ast."""
        api.repo.get_versao_para_processar.return_value = versao_data_minimal

        call_order = []

        def track_status(*args, **kwargs):
            call_order.append(f"status_{kwargs.get('status', '?')}")
            return {"success": True, "status_code": 200, "data": {}}

        api.repo.atualizar_status_versao = Mock(side_effect=track_status)

        with patch.object(api, "_process_versao_com_ast") as mock_ast:

            def track_ast(versao_id, versao_data):
                call_order.append("ast")
                return {"resultado": "ok"}

            mock_ast.side_effect = track_ast
            api.process_versao("v123", mock=False, use_ast=True)

        assert "status_em_processamento" in call_order, (
            "atualizar_status_versao('em_processamento') não foi chamado"
        )
        assert "ast" in call_order, "_process_versao_com_ast não foi chamado"
        assert call_order.index("status_em_processamento") < call_order.index("ast"), (
            "status 'em_processamento' deve ser setado ANTES do processamento AST"
        )

    def test_nao_seta_em_processamento_se_mock_true(self, api):
        """Com mock=True, atualizar_status_versao NÃO deve ser chamado."""
        # mock=True busca versão via _get_mock_versao_by_id (não usa repo)
        # Se versão mock não existe, retorna erro sem chamar repo
        result = api.process_versao("versao-inexistente-no-mock", mock=True)

        api.repo.atualizar_status_versao.assert_not_called()

    def test_seta_erro_se_get_versao_falha(self, api):
        """Se get_versao_para_processar lança exceção, status deve ir para 'erro'."""
        api.repo.get_versao_para_processar.side_effect = Exception("Directus offline")

        result = api.process_versao("v123", mock=False)

        assert "error" in result

        calls = api.repo.atualizar_status_versao.call_args_list
        erro_calls = [c for c in calls if c.kwargs.get("status") == "erro"]
        assert len(erro_calls) >= 1, (
            "atualizar_status_versao('erro') deve ser chamado quando get_versao_para_processar falha"
        )

    def test_seta_erro_se_processamento_ast_falha(self, api, versao_data_minimal):
        """Se _process_versao_com_ast lança exceção, status deve ir para 'erro'."""
        api.repo.get_versao_para_processar.return_value = versao_data_minimal

        with patch.object(
            api, "_process_versao_com_ast", side_effect=Exception("Pandoc falhou")
        ):
            result = api.process_versao("v123", mock=False, use_ast=True)

        assert "error" in result

        calls = api.repo.atualizar_status_versao.call_args_list
        erro_calls = [c for c in calls if c.kwargs.get("status") == "erro"]
        assert len(erro_calls) >= 1, (
            "atualizar_status_versao('erro') deve ser chamado quando _process_versao_com_ast falha"
        )

    def test_observacao_erro_truncada_em_500_chars(self, api):
        """Observação de erro não deve ultrapassar 500 chars para evitar payloads grandes."""
        mensagem_longa = "E" * 1000
        api.repo.get_versao_para_processar.side_effect = Exception(mensagem_longa)

        api.process_versao("v123", mock=False)

        calls = api.repo.atualizar_status_versao.call_args_list
        erro_calls = [c for c in calls if c.kwargs.get("status") == "erro"]
        assert len(erro_calls) >= 1

        observacao = erro_calls[0].kwargs.get("observacao", "")
        assert (
            len(observacao) <= 560
        ), (  # margem para prefixo "Erro no processamento: "
            f"Observação de erro muito longa: {len(observacao)} chars (esperado <= 560)"
        )

    def test_nao_seta_erro_se_mock_true_e_falha(self, api):
        """Com mock=True, mesmo em caso de falha, atualizar_status_versao não é chamado."""
        with patch(
            "directus_server._get_mock_versao_by_id",
            side_effect=Exception("mock error"),
        ):
            result = api.process_versao("v123", mock=True)

        api.repo.atualizar_status_versao.assert_not_called()

    def test_em_processamento_nao_interrompe_se_falha_ao_setar(
        self, api, versao_data_minimal
    ):
        """Falha ao setar 'em_processamento' não deve interromper o processamento."""
        api.repo.get_versao_para_processar.return_value = versao_data_minimal
        api.repo.atualizar_status_versao.return_value = {
            "success": False,
            "status_code": 500,
            "error": "Directus indisponível",
        }

        ast_foi_chamado = []
        with patch.object(api, "_process_versao_com_ast") as mock_ast:
            mock_ast.side_effect = lambda *a, **kw: (
                ast_foi_chamado.append(True),
                {"resultado": "ok"},
            )[1]
            api.process_versao("v123", mock=False, use_ast=True)

        assert ast_foi_chamado, (
            "Processamento deve continuar mesmo se falhar ao setar status 'em_processamento'"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
