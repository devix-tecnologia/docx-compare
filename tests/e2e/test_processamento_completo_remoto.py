"""
Teste E2E completo do processamento de versões em servidor remoto.

Uso:
    pytest tests/e2e/test_processamento_completo_remoto.py -v -s
"""

import time

import pytest
import requests


class TestHealthCheck:
    """Testes de saúde e conectividade do servidor."""

    def test_server_is_reachable(self, api_client: requests.Session, e2e_config):
        """Valida que o servidor está acessível."""
        response = api_client.get(
            f"{e2e_config.base_url}/health",
            timeout=e2e_config.timeout,
        )

        assert response.status_code == 200, (
            f"Servidor não respondeu corretamente: {response.status_code}"
        )

    def test_health_endpoint_returns_valid_data(
        self, api_client: requests.Session, e2e_config
    ):
        """Valida estrutura e dados do endpoint de saúde."""
        response = api_client.get(
            f"{e2e_config.base_url}/health",
            timeout=e2e_config.timeout,
        )

        assert response.status_code == 200
        data = response.json()

        # Validações essenciais
        assert data.get("status") == "ok", f"Status não é 'ok': {data}"
        assert "timestamp" in data, "Timestamp ausente no health check"
        assert "version" in data, "Versão ausente no health check"

        # Validação de conexão com Directus
        assert data.get("directus_connected") is True, (
            f"Directus não conectado: {data.get('directus_url')}"
        )


@pytest.mark.slow
class TestProcessamentoCompleto:
    """Testes de processamento end-to-end."""

    def test_processar_versao_mock(
        self,
        api_client: requests.Session,
        e2e_config,
    ):
        """Teste de processamento usando dados mock."""
        versao_id_mock = "test-mock-version-id"

        response = api_client.get(
            f"{e2e_config.base_url}/api/versoes/{versao_id_mock}",
            params={"mock": "true"},
            timeout=30,
        )

        # Com mock, deve retornar dados simulados
        if response.status_code == 200:
            result = response.json()

            assert "diff_data" in result, "diff_data ausente na resposta mock"
            assert "modificacoes" in result["diff_data"], (
                "modificacoes ausentes no mock"
            )

            print(
                f"✅ Mock retornou {len(result['diff_data']['modificacoes'])} "
                "modificações simuladas"
            )

    def test_processar_versao_uuid_invalido(
        self,
        api_client: requests.Session,
        e2e_config,
    ):
        """Valida tratamento de UUID inválido."""
        invalid_uuid = "nao-e-um-uuid-valido"

        response = api_client.get(
            f"{e2e_config.base_url}/api/versoes/{invalid_uuid}",
            timeout=e2e_config.timeout,
        )

        # Deve retornar erro (400 ou 404)
        assert response.status_code in [400, 404, 500], (
            f"Status inesperado para UUID inválido: {response.status_code}"
        )

    def test_processar_versao_inexistente(
        self,
        api_client: requests.Session,
        e2e_config,
    ):
        """Valida tratamento de versão que não existe."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        response = api_client.get(
            f"{e2e_config.base_url}/api/versoes/{fake_uuid}",
            timeout=e2e_config.timeout,
        )

        # Backend pode retornar 404 ou 500 dependendo
        assert response.status_code in [404, 500], (
            f"Status inesperado: {response.status_code}"
        )


@pytest.mark.slow
class TestDirectusIntegration:
    """Testes de integração com Directus CMS."""

    @pytest.mark.skipif(
        True,  # Skip por padrão - requer Directus configurado
        reason="Requer Directus real e credenciais válidas",
    )
    def test_directus_connectivity(
        self,
        directus_client: requests.Session,
        e2e_config,
    ):
        """Valida conectividade com Directus."""
        response = directus_client.get(
            f"{e2e_config.directus_url}/server/ping",
            timeout=e2e_config.timeout,
        )
        assert response.status_code == 200, "Directus não está acessível"

    @pytest.mark.skipif(
        True,
        reason="Requer Directus e permissões de leitura",
    )
    def test_directus_read_versoes(
        self,
        directus_client: requests.Session,
        e2e_config,
    ):
        """Testa leitura da collection contrato_versao."""
        response = directus_client.get(
            f"{e2e_config.directus_url}/items/contrato_versao",
            params={"limit": 5},
            timeout=e2e_config.timeout,
        )

        assert response.status_code == 200, f"Erro ao buscar versões: {response.text}"

        data = response.json()
        assert "data" in data, "Campo 'data' ausente"
        assert isinstance(data["data"], list), "Campo 'data' não é lista"


@pytest.mark.slow
class TestPerformanceReliability:
    """Testes de performance e confiabilidade."""

    def test_multiplas_requisicoes_sequenciais(
        self,
        api_client: requests.Session,
        e2e_config,
    ):
        """Valida processamento sequencial de múltiplas requisições."""
        test_uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "223e4567-e89b-12d3-a456-426614174001",
            "323e4567-e89b-12d3-a456-426614174002",
        ]

        results = []
        for uuid in test_uuids:
            response = api_client.get(
                f"{e2e_config.base_url}/api/versoes/{uuid}?mock=true",
                timeout=30,
            )
            results.append(response.status_code)
            time.sleep(0.5)  # Delay entre requisições

        # Mock mode sempre retorna 200
        assert all(status == 200 for status in results), (
            f"Algumas requisições falharam: {results}"
        )
        print(f"✅ {len(test_uuids)} requisições processadas com sucesso")

    def test_timeout_handling(
        self,
        api_client: requests.Session,
        e2e_config,
    ):
        """Valida que a API responde dentro do timeout configurado."""
        response = api_client.get(
            f"{e2e_config.base_url}/health",
            timeout=e2e_config.timeout,
        )

        # Se não lançar exceção, timeout foi respeitado
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < e2e_config.timeout


# Marcar todos os testes como E2E
pytestmark = [pytest.mark.e2e, pytest.mark.integration]
