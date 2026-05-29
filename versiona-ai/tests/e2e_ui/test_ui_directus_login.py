"""
Testes E2E de autenticação no Directus Admin UI.
"""

from playwright.sync_api import Page, expect


class TestDirectusLogin:
    """Testes de login e autenticação."""

    def test_login_page_loads(self, page: Page, e2e_ui_config):
        """Valida que página de login carrega corretamente."""
        page.goto(f"{e2e_ui_config.directus_url}/admin/login")

        # Aguardar formulário de login
        page.wait_for_selector('input[type="email"]', timeout=10000)

        # Validar elementos do formulário
        expect(page.locator('input[type="email"]')).to_be_visible()
        expect(page.locator('input[type="password"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()

    def test_login_with_valid_credentials(self, page: Page, e2e_ui_config):
        """Valida login com credenciais válidas."""
        page.goto(f"{e2e_ui_config.directus_url}/admin/login")

        # Aguardar formulário
        page.wait_for_selector('input[type="email"]', timeout=10000)

        # Preencher credenciais
        page.fill('input[type="email"]', e2e_ui_config.admin_email)
        page.fill('input[type="password"]', e2e_ui_config.admin_password)

        # Clicar em login
        page.click('button[type="submit"]')

        # Aguardar redirecionamento para dashboard
        page.wait_for_url("**/admin/**", timeout=15000)

        # Validar que não está mais na página de login
        assert "login" not in page.url.lower(), (
            "Ainda na página de login após submissão"
        )

        print(f"✅ Login bem-sucedido: {page.url}")

    def test_login_with_invalid_credentials(self, page: Page, e2e_ui_config):
        """Valida que login com credenciais inválidas falha."""
        page.goto(f"{e2e_ui_config.directus_url}/admin/login")

        # Aguardar formulário
        page.wait_for_selector('input[type="email"]', timeout=10000)

        # Preencher credenciais inválidas
        page.fill('input[type="email"]', "usuario@invalido.com")
        page.fill('input[type="password"]', "senhaErrada123")

        # Clicar em login
        page.click('button[type="submit"]')

        # Aguardar mensagem de erro (tempo suficiente para UI processar)
        page.wait_for_timeout(2000)

        # Validar que ainda está na página de login
        assert "login" in page.url.lower(), (
            "Não deveria ter feito login com credenciais inválidas"
        )

        print("✅ Login corretamente rejeitado para credenciais inválidas")

    def test_navigate_to_dashboard(self, directus_page_logged: Page):
        """Valida navegação para dashboard após login."""
        # Página já vem autenticada (fixture directus_page_logged)

        # Validar que está no admin
        assert "/admin" in directus_page_logged.url, "Não está no painel admin"

        # Tentar encontrar elementos típicos do dashboard Directus
        # (pode variar conforme versão do Directus)
        directus_page_logged.wait_for_timeout(2000)

        print(f"✅ Dashboard carregado: {directus_page_logged.url}")
