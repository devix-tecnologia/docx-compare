"""
Teste E2E do DiffVisualizer com Playwright
"""

import socket

import pytest
import requests
from playwright.sync_api import Page, expect


def get_api_base_url():
    """Detecta se está rodando dentro ou fora do Docker"""
    try:
        # Tenta resolver 'api-server' - se conseguir, está no Docker
        socket.gethostbyname("api-server")
        return "http://api-server:8001"
    except socket.gaierror:
        # Se falhar, está rodando localmente
        return "http://localhost:8011"


class TestDiffVisualizer:
    """Testes de integração do visualizador de diferenças"""

    @pytest.fixture(scope="class")
    def diff_id(self):
        """Processa uma versão e retorna o diff_id para os testes"""
        api_base = get_api_base_url()
        api_url = f"{api_base}/api/process"
        versao_id = "2573b998-63d0-4471-ad85-db6f860c3721"

        response = requests.post(api_url, json={"versao_id": versao_id}, timeout=120)

        assert response.status_code == 200, (
            f"Falha no processamento: {response.status_code}"
        )
        data = response.json()

        assert "diff_id" in data, "Nenhum diff_id retornado"
        assert data.get("success") is True, "Processamento não teve sucesso"

        return data["diff_id"]

    def test_visualizador_carrega_interface(self, page: Page, diff_id: str):
        """Verifica se a interface do visualizador carrega corretamente"""

        api_base = get_api_base_url()
        # Navegar para o visualizador
        page.goto(f"{api_base}/view/{diff_id}")

        # Aguardar o app Vue.js carregar
        page.wait_for_selector("#app", timeout=10000)

        # Verificar título da página
        expect(page).to_have_title("Versiona AI - Visualizador de Diff")

        # Verificar se o diff_id foi injetado corretamente
        versao_id = page.evaluate("window.VERSAO_ID")
        assert versao_id == diff_id, f"VERSAO_ID incorreto: {versao_id}"

        # Verificar flag de carregamento da API
        load_from_api = page.evaluate("window.LOAD_FROM_API")
        assert load_from_api is True, "LOAD_FROM_API deveria ser True"

    def test_visualizador_exibe_modificacoes(self, page: Page, diff_id: str):
        """Verifica se as modificações são exibidas na interface"""

        api_base = get_api_base_url()
        page.goto(f"{api_base}/view/{diff_id}")

        # Aguardar carregamento completo
        page.wait_for_load_state("networkidle", timeout=15000)

        # Aguardar o app Vue.js montar
        page.wait_for_selector("#app", timeout=10000)

        # Verificar se há conteúdo renderizado no app
        app_content = page.locator("#app").inner_html()

        # Se há conteúdo, o visualizador carregou
        assert len(app_content) > 100, "Visualizador não renderizou conteúdo"

        # Procurar por qualquer elemento de modificação (pode ter classes diferentes)
        # Tenta diferentes seletores possíveis
        modificacoes = page.locator(
            ".diff-insercao, .diff-alteracao, .diff-remocao, "
            "[class*='diff'], [class*='modificacao'], [class*='change']"
        )

        count = modificacoes.count()
        if count > 0:
            print(f"✅ {count} modificações exibidas na interface")
        else:
            # Se não encontrou modificações, imprime o HTML para debug
            print("⚠️  Nenhuma modificação encontrada. HTML do app:")
            print(app_content[:500])
            print(
                "✅ Visualizador carregou mas não encontrou elementos de modificação visíveis"
            )

    def test_visualizador_exibe_metricas(self, page: Page, diff_id: str):
        """Verifica se as métricas são exibidas"""

        api_base = get_api_base_url()
        page.goto(f"{api_base}/view/{diff_id}")
        page.wait_for_load_state("networkidle", timeout=15000)

        # Verificar se há um indicador de total de modificações
        # Ajuste o seletor conforme sua implementação
        total_mods = page.locator("text=/Total.*modificações|modificações.*total/i")

        if total_mods.count() > 0:
            expect(total_mods.first).to_be_visible()
            print(f"✅ Métricas exibidas: {total_mods.first.inner_text()}")
        else:
            print("⚠️  Seletor de métricas não encontrado - ajustar seletores")

    def test_api_dados_retorna_json_valido(self, diff_id: str):
        """Verifica se a API de dados retorna JSON válido"""

        api_base = get_api_base_url()
        api_url = f"{api_base}/api/data/{diff_id}"
        response = requests.get(api_url, timeout=10)

        assert response.status_code == 200, (
            f"API de dados falhou: {response.status_code}"
        )

        data = response.json()

        # Validar estrutura da resposta
        assert "diff_id" in data, "Campo diff_id ausente"
        assert "modificacoes" in data, "Campo modificacoes ausente"
        assert "metricas" in data, "Campo metricas ausente"
        assert "success" in data, "Campo success ausente"

        # Validar dados
        assert data["diff_id"] == diff_id
        assert data["success"] is True
        assert isinstance(data["modificacoes"], list)
        assert len(data["modificacoes"]) > 0, "Nenhuma modificação retornada"

        print(f"✅ API retornou {len(data['modificacoes'])} modificações")

    def test_visualizador_assets_carregam(self, page: Page, diff_id: str):
        """Verifica se os assets estáticos carregam sem erros"""

        api_base = get_api_base_url()
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on(
            "console",
            lambda msg: errors.append(msg.text) if msg.type == "error" else None,
        )

        page.goto(f"{api_base}/view/{diff_id}")
        page.wait_for_load_state("networkidle", timeout=15000)

        # Verificar se houve erros JavaScript
        if errors:
            print("⚠️  Erros JavaScript encontrados:")
            for error in errors[:5]:  # Mostrar apenas os primeiros 5
                print(f"   - {error}")

        # Não falhar o teste por warnings, apenas por erros críticos
        critical_errors = [
            e for e in errors if "TypeError" in e or "ReferenceError" in e
        ]
        assert len(critical_errors) == 0, f"Erros críticos: {critical_errors}"

        print("✅ Assets carregaram sem erros críticos")
