"""
Fixtures e configuração para testes E2E em servidor remoto.

Uso:
    # Rodar contra desenvolvimento local
    pytest tests/e2e/ -v

    # Rodar contra staging
    E2E_BASE_URL=https://staging.example.com pytest tests/e2e/ -v

    # Rodar contra produção (com flag explícita)
    E2E_BASE_URL=https://ignai-contract-ia.paas.node10.de.vix.br \
    E2E_ALLOW_PRODUCTION=true \
    pytest tests/e2e/ -v --e2e-production
"""

import os
import uuid
from dataclasses import dataclass

import pytest
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
load_dotenv(".env.e2e", override=False)  # Não sobrescrever env vars do Docker


@dataclass
class E2EConfig:
    """Configuração centralizada para testes E2E."""

    base_url: str
    directus_url: str
    directus_token: str
    timeout: int = 30
    allow_production: bool = False
    cleanup_after_test: bool = True

    def __post_init__(self):
        """Validações de segurança."""
        # Prevenir execução acidental em produção
        production_indicators = ["prod", "production", "paas.node10"]
        is_production = any(
            ind in self.base_url.lower() for ind in production_indicators
        )

        if is_production and not self.allow_production:
            raise RuntimeError(
                f"🚨 BLOQUEIO DE SEGURANÇA: Tentativa de rodar E2E em produção!\n"
                f"   URL: {self.base_url}\n"
                f"   Para permitir, defina: E2E_ALLOW_PRODUCTION=true\n"
                f"   E adicione flag: --e2e-production"
            )


def pytest_addoption(parser):
    """Adiciona opções customizadas ao pytest."""
    parser.addoption(
        "--e2e-production",
        action="store_true",
        default=False,
        help="Permite rodar testes E2E em ambiente de produção (use com cuidado!)",
    )
    parser.addoption(
        "--e2e-no-cleanup",
        action="store_true",
        default=False,
        help="Não limpar dados de teste após execução (útil para debug)",
    )


@pytest.fixture(scope="session")
def e2e_config(request) -> E2EConfig:
    """Fixture de configuração global para testes E2E."""
    allow_production = os.getenv(
        "E2E_ALLOW_PRODUCTION", "false"
    ).lower() == "true" or request.config.getoption("--e2e-production")

    cleanup_after_test = not request.config.getoption("--e2e-no-cleanup")

    config = E2EConfig(
        base_url=os.getenv("E2E_BASE_URL", "http://localhost:8001"),
        directus_url=os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co"),
        directus_token=os.getenv("DIRECTUS_TOKEN", ""),
        timeout=int(os.getenv("E2E_TIMEOUT", "30")),
        allow_production=allow_production,
        cleanup_after_test=cleanup_after_test,
    )

    # Validar configuração
    if not config.directus_token:
        pytest.skip("DIRECTUS_TOKEN não configurado")

    return config


@pytest.fixture(scope="session")
def api_client(e2e_config: E2EConfig) -> requests.Session:
    """Cliente HTTP reutilizável com timeout e retry."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    # Adapter com retry para resiliência
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


@pytest.fixture
def directus_client(e2e_config: E2EConfig) -> requests.Session:
    """Cliente autenticado para comunicação direta com Directus."""
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {e2e_config.directus_token}",
            "Content-Type": "application/json",
        }
    )
    return session


@pytest.fixture
def test_marker() -> str:
    """Marcador único para identificar dados criados por este teste."""
    return f"e2e-test-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def cleanup_tracker():
    """Rastreia recursos criados durante o teste para limpeza posterior."""
    resources = {"versoes": [], "modelos": [], "clausulas": []}

    yield resources

    # Limpeza automática seria feita aqui se necessário
    # (implementação depende da estratégia de cleanup)


@pytest.fixture(autouse=True)
def e2e_test_marker(request):
    """Marca automaticamente todos os testes E2E."""
    if "e2e" not in request.keywords:
        request.node.add_marker(pytest.mark.e2e)
