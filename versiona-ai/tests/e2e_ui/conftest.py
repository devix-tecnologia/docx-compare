"""
Fixtures e configuração para testes E2E via Interface de Usuário.

Combina Playwright (UI) + Directus SDK (validações de dados).
"""

import os
import time
from dataclasses import dataclass
from typing import Generator

import pytest
import requests
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

# Carregar variáveis de ambiente
load_dotenv()
load_dotenv(".env.e2e.ui", override=False)


@dataclass
class E2EUIConfig:
    """Configuração para testes E2E UI."""

    directus_url: str
    api_url: str
    admin_email: str
    admin_password: str
    directus_token: str
    playwright_headless: bool = True
    playwright_slow_mo: int = 0
    timeout: int = 60


@pytest.fixture(scope="session")
def e2e_ui_config() -> E2EUIConfig:
    """Configuração global para testes E2E UI."""
    return E2EUIConfig(
        directus_url=os.getenv("DIRECTUS_URL", "http://localhost:8055"),
        api_url=os.getenv("API_URL", "http://localhost:8001"),
        admin_email=os.getenv("DIRECTUS_ADMIN_EMAIL", "admin@example.com"),
        admin_password=os.getenv("DIRECTUS_ADMIN_PASSWORD", "TestPassword123!"),
        directus_token=os.getenv("DIRECTUS_TOKEN", ""),
        playwright_headless=os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true",
        playwright_slow_mo=int(os.getenv("PLAYWRIGHT_SLOW_MO", "0")),
        timeout=int(os.getenv("E2E_UI_TIMEOUT", "60")),
    )


@pytest.fixture(scope="session")
def directus_session(e2e_ui_config: E2EUIConfig) -> requests.Session:
    """Cliente HTTP para Directus API (via SDK)."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {e2e_ui_config.directus_token}",
        "Content-Type": "application/json",
    })
    
    # Aguardar Directus estar pronto
    max_retries = 30
    for i in range(max_retries):
        try:
            response = session.get(
                f"{e2e_ui_config.directus_url}/server/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ Directus está pronto: {e2e_ui_config.directus_url}")
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                raise RuntimeError(f"Directus não está acessível após {max_retries} tentativas")
            time.sleep(2)
    
    return session


@pytest.fixture(scope="session")
def api_session(e2e_ui_config: E2EUIConfig) -> requests.Session:
    """Cliente HTTP para API Versiona."""
    session = requests.Session()
    
    # Aguardar API estar pronta
    max_retries = 20
    for i in range(max_retries):
        try:
            response = session.get(
                f"{e2e_ui_config.api_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ API está pronta: {e2e_ui_config.api_url}")
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                raise RuntimeError(f"API não está acessível após {max_retries} tentativas")
            time.sleep(2)
    
    return session


# =================================================================
# Fixtures Playwright
# =================================================================

@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    """Instância Playwright para testes."""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright: Playwright, e2e_ui_config: E2EUIConfig) -> Generator[Browser, None, None]:
    """Browser Chromium configurado."""
    browser = playwright.chromium.launch(
        headless=e2e_ui_config.playwright_headless,
        slow_mo=e2e_ui_config.playwright_slow_mo,
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Contexto de navegação isolado por teste."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Página web para interação."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def directus_page_logged(
    page: Page,
    e2e_ui_config: E2EUIConfig
) -> Generator[Page, None, None]:
    """Página já autenticada no Directus Admin."""
    # Navegar para login
    page.goto(f"{e2e_ui_config.directus_url}/admin/login")
    
    # Aguardar formulário de login
    page.wait_for_selector('input[type="email"]', timeout=10000)
    
    # Preencher credenciais
    page.fill('input[type="email"]', e2e_ui_config.admin_email)
    page.fill('input[type="password"]', e2e_ui_config.admin_password)
    
    # Clicar em login
    page.click('button[type="submit"]')
    
    # Aguardar redirecionamento para dashboard
    page.wait_for_url("**/admin/**", timeout=15000)
    
    print(f"✅ Login realizado no Directus: {e2e_ui_config.admin_email}")
    
    yield page


# =================================================================
# Fixtures de Dados de Teste
# =================================================================

@pytest.fixture(scope="session")
def modelo_contrato_id(directus_session: requests.Session, e2e_ui_config: E2EUIConfig) -> str:
    """ID do modelo de contrato de teste (criado pelo seed)."""
    response = directus_session.get(
        f"{e2e_ui_config.directus_url}/items/modelo_contrato",
        params={"filter": {"nome": {"_eq": "Modelo Teste Task 010"}}},
    )
    
    if response.status_code != 200:
        pytest.skip("Modelo de contrato não encontrado no seed")
    
    data = response.json()
    if not data.get("data"):
        pytest.skip("Modelo de contrato 'Modelo Teste Task 010' não existe")
    
    return data["data"][0]["id"]


@pytest.fixture
def versao_processada_id(
    directus_session: requests.Session,
    e2e_ui_config: E2EUIConfig,
    modelo_contrato_id: str
) -> str:
    """
    Cria uma versão de teste e aguarda processamento.
    Retorna o ID da versão processada.
    """
    # Criar versão via Directus API
    payload = {
        "nome": f"Versão Teste E2E UI - {int(time.time())}",
        "modelo_contrato": modelo_contrato_id,
        "status": "aguardando_processamento",
        "arquivo": None,  # Em testes reais, seria upload de arquivo
    }
    
    response = directus_session.post(
        f"{e2e_ui_config.directus_url}/items/contrato_versao",
        json=payload,
    )
    
    if response.status_code not in [200, 201]:
        pytest.fail(f"Falha ao criar versão: {response.text}")
    
    versao_id = response.json()["data"]["id"]
    
    # Simular processamento (em ambiente real, webhook dispararia)
    # Aqui apenas alteramos status para "concluido"
    directus_session.patch(
        f"{e2e_ui_config.directus_url}/items/contrato_versao/{versao_id}",
        json={"status": "concluido"},
    )
    
    return versao_id


# =================================================================
# Fixtures de Limpeza
# =================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(request):
    """Limpa dados de teste após cada execução (se configurado)."""
    yield
    
    # Cleanup será implementado se necessário
    # Por ora, deixamos dados no banco para debug
    pass


# =================================================================
# Helpers
# =================================================================

def wait_for_element(page: Page, selector: str, timeout: int = 10000):
    """Helper para aguardar elemento com timeout."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
    except Exception as e:
        # Tirar screenshot para debug
        page.screenshot(path=f"test-results/screenshots/error-{int(time.time())}.png")
        raise e


def wait_for_processing(
    directus_session: requests.Session,
    directus_url: str,
    versao_id: str,
    timeout: int = 60
) -> bool:
    """
    Aguarda processamento de versão ficar completo.
    Retorna True se concluído, False se timeout.
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = directus_session.get(
            f"{directus_url}/items/contrato_versao/{versao_id}",
        )
        
        if response.status_code == 200:
            status = response.json()["data"]["status"]
            if status in ["concluido", "concluído"]:
                return True
            elif status == "erro":
                return False
        
        time.sleep(2)
    
    return False
