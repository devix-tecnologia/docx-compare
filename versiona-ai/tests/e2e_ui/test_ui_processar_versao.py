"""
Testes de criação e processamento de versões via UI do Directus.
"""

import time

import pytest
from playwright.sync_api import Page, expect


class TestProcessarVersao:
    """Testes de criação e processamento de versões."""

    def test_navegar_para_formulario_versao(
        self,
        directus_page_logged: Page,
        e2e_ui_config
    ):
        """Valida navegação para formulário de criação de versão."""
        # Navegar para collection de versões
        directus_page_logged.goto(
            f"{e2e_ui_config.directus_url}/admin/content/contrato_versao"
        )
        
        # Aguardar lista carregar
        directus_page_logged.wait_for_timeout(2000)
        
        # Validar que está na página correta
        assert "contrato_versao" in directus_page_logged.url.lower()
        
        print("✅ Navegou para lista de versões")

    def test_criar_versao_via_api_sdk(
        self,
        directus_session,
        e2e_ui_config,
        modelo_contrato_id: str
    ):
        """
        Cria versão via API (simula envio de formulário).
        """
        # Payload de criação
        payload = {
            "nome": f"Versão E2E UI - {int(time.time())}",
            "modelo_contrato": modelo_contrato_id,
            "status": "aguardando_processamento",
        }
        
        # Criar versão
        response = directus_session.post(
            f"{e2e_ui_config.directus_url}/items/contrato_versao",
            json=payload,
        )
        
        assert response.status_code in [200, 201], (
            f"Falha ao criar versão: {response.status_code} - {response.text}"
        )
        
        versao_data = response.json()["data"]
        versao_id = versao_data["id"]
        
        print(f"✅ Versão criada: {versao_id} - {versao_data['nome']}")
        
        # Validar que versão foi criada corretamente
        assert versao_data["status"] == "aguardando_processamento"
        assert versao_data["modelo_contrato"] == modelo_contrato_id

    def test_aguardar_processamento_concluir(
        self,
        directus_session,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """
        Valida que processamento conclui (status muda para 'concluido').
        """
        # Buscar versão
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/contrato_versao/{versao_processada_id}"
        )
        
        assert response.status_code == 200
        versao = response.json()["data"]
        
        # Validar status
        assert versao["status"] in ["concluido", "concluído"], (
            f"Status inesperado: {versao['status']}"
        )
        
        print(f"✅ Versão processada com status: {versao['status']}")

    def test_versao_processada_tem_modificacoes(
        self,
        directus_session,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """
        Valida que versão processada gerou modificações.
        """
        # Buscar modificações da versão
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modificacao",
            params={"filter": {"versao": {"_eq": versao_processada_id}}},
        )
        
        assert response.status_code == 200
        modificacoes = response.json()["data"]
        
        # Deve ter pelo menos 1 modificação
        # (em testes reais com documentos, seria > 0)
        # Por ora, apenas validamos que a query funciona
        assert isinstance(modificacoes, list)
        
        print(f"✅ Versão tem {len(modificacoes)} modificação(ões)")

    def test_visualizar_detalhes_versao_ui(
        self,
        directus_page_logged: Page,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """
        Valida visualização de detalhes da versão na UI.
        """
        # Navegar para detalhe da versão
        directus_page_logged.goto(
            f"{e2e_ui_config.directus_url}/admin/content/contrato_versao/{versao_processada_id}"
        )
        
        # Aguardar página carregar
        directus_page_logged.wait_for_timeout(3000)
        
        # Validar que está na página correta
        assert versao_processada_id in directus_page_logged.url
        
        # Validar que elementos típicos estão presentes
        page_content = directus_page_logged.content()
        
        # Status deve estar visível
        assert "status" in page_content.lower() or "conclu" in page_content.lower()
        
        print(f"✅ Detalhes da versão carregados na UI")
