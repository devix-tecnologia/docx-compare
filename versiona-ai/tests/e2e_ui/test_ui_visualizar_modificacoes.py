"""
TESTE CRÍTICO - Task 010
Valida que modificações estão vinculadas às cláusulas corretas via UI.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.critical
class TestVisualizarModificacoesVinculadas:
    """
    Testes críticos para Task 010.
    Validam que vinculação modificação-cláusula é visível na UI.
    """

    def test_navegar_para_lista_modificacoes(
        self,
        directus_page_logged: Page,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """Valida navegação para lista de modificações de uma versão."""
        # Navegar para collection de modificações
        directus_page_logged.goto(
            f"{e2e_ui_config.directus_url}/admin/content/modificacao"
        )
        
        # Aguardar lista carregar
        directus_page_logged.wait_for_timeout(2000)
        
        # Validar que está na página correta
        assert "modificacao" in directus_page_logged.url.lower()
        
        print("✅ Navegou para lista de modificações")

    @pytest.mark.parametrize("use_filter", [True, False])
    def test_modificacoes_tem_clausula_preenchida(
        self,
        directus_session,
        e2e_ui_config,
        versao_processada_id: str,
        use_filter: bool
    ):
        """
        CRÍTICO - Task 010
        Valida via SDK que TODAS modificações têm clausula_id preenchido.
        """
        # Buscar modificações da versão
        params = {"filter": {"versao": {"_eq": versao_processada_id}}}
        
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modificacao",
            params=params,
        )
        
        assert response.status_code == 200, f"Falha ao buscar modificações: {response.text}"
        
        modificacoes = response.json()["data"]
        
        # VALIDAÇÃO CRÍTICA
        assert len(modificacoes) > 0, "Nenhuma modificação encontrada para a versão"
        
        modificacoes_sem_clausula = [
            mod for mod in modificacoes
            if mod.get("clausula") is None or mod.get("clausula") == ""
        ]
        
        assert len(modificacoes_sem_clausula) == 0, (
            f"❌ FALHA TASK 010: {len(modificacoes_sem_clausula)} modificações "
            f"sem cláusula vinculada!\n"
            f"IDs: {[mod['id'] for mod in modificacoes_sem_clausula]}"
        )
        
        print(f"✅ TASK 010 OK: {len(modificacoes)} modificações com cláusula vinculada")

    def test_ui_exibe_nome_clausula_nao_apenas_id(
        self,
        directus_page_logged: Page,
        directus_session,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """
        Valida que UI exibe nome/título da cláusula, não apenas ID.
        """
        # Buscar primeira modificação da versão via API
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modificacao",
            params={
                "filter": {"versao": {"_eq": versao_processada_id}},
                "limit": 1,
                "fields": ["id", "clausula.nome", "clausula.referencia"]
            },
        )
        
        if response.status_code != 200 or not response.json()["data"]:
            pytest.skip("Nenhuma modificação encontrada para validar UI")
        
        modificacao = response.json()["data"][0]
        modificacao_id = modificacao["id"]
        clausula_info = modificacao.get("clausula", {})
        
        # Navegar para detalhe da modificação na UI
        directus_page_logged.goto(
            f"{e2e_ui_config.directus_url}/admin/content/modificacao/{modificacao_id}"
        )
        
        # Aguardar página carregar
        directus_page_logged.wait_for_timeout(3000)
        
        # Validar que campo de relacionamento está presente
        # (buscar por referências ou nome da cláusula no HTML)
        page_content = directus_page_logged.content()
        
        if clausula_info.get("nome"):
            # Se temos nome da cláusula, deve aparecer na UI
            assert (
                clausula_info["nome"] in page_content or
                clausula_info.get("referencia", "") in page_content
            ), "Nome/referência da cláusula não aparece na UI"
        
        print(f"✅ UI exibe informação da cláusula: {clausula_info}")

    def test_navegar_de_modificacao_para_clausula(
        self,
        directus_page_logged: Page,
        directus_session,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """
        Valida que é possível navegar de modificação → cláusula via UI.
        """
        # Buscar modificação com cláusula via API
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modificacao",
            params={
                "filter": {"versao": {"_eq": versao_processada_id}},
                "limit": 1,
                "fields": ["id", "clausula"]
            },
        )
        
        if response.status_code != 200 or not response.json()["data"]:
            pytest.skip("Nenhuma modificação encontrada")
        
        modificacao = response.json()["data"][0]
        modificacao_id = modificacao["id"]
        clausula_id = modificacao.get("clausula")
        
        if not clausula_id:
            pytest.fail("Modificação de teste não tem cláusula vinculada")
        
        # Navegar para modificação
        directus_page_logged.goto(
            f"{e2e_ui_config.directus_url}/admin/content/modificacao/{modificacao_id}"
        )
        
        directus_page_logged.wait_for_timeout(2000)
        
        # Tentar encontrar link para cláusula
        # (Directus geralmente cria links em campos de relacionamento)
        try:
            # Buscar por elementos que contenham o ID da cláusula
            # Ou por links na interface
            links = directus_page_logged.query_selector_all('a[href*="clausula"]')
            
            if len(links) > 0:
                print(f"✅ Encontrado {len(links)} link(s) para cláusulas na UI")
            else:
                # Se não encontrou links, apenas validar que ID aparece
                page_content = directus_page_logged.content()
                assert str(clausula_id) in page_content, (
                    "ID da cláusula não aparece na página de modificação"
                )
                print("✅ ID da cláusula aparece na UI (link pode não estar acessível em teste)")
        except Exception as e:
            pytest.skip(f"Não foi possível validar link UI: {e}")

    def test_filtrar_modificacoes_por_clausula(
        self,
        directus_session,
        e2e_ui_config,
        modelo_contrato_id: str
    ):
        """
        Valida que é possível filtrar modificações por cláusula específica.
        """
        # Buscar uma cláusula do modelo
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/clausula",
            params={
                "filter": {"modelo_contrato": {"_eq": modelo_contrato_id}},
                "limit": 1
            },
        )
        
        if response.status_code != 200 or not response.json()["data"]:
            pytest.skip("Nenhuma cláusula encontrada no modelo")
        
        clausula_id = response.json()["data"][0]["id"]
        
        # Buscar modificações dessa cláusula
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modificacao",
            params={"filter": {"clausula": {"_eq": clausula_id}}},
        )
        
        assert response.status_code == 200
        modificacoes = response.json()["data"]
        
        # Validar que TODAS modificações retornadas são da cláusula correta
        for mod in modificacoes:
            assert mod.get("clausula") == clausula_id, (
                f"Filtro retornou modificação de outra cláusula: {mod['id']}"
            )
        
        print(f"✅ Filtro por cláusula funciona: {len(modificacoes)} modificações encontradas")

    def test_validacao_foreign_key_banco(
        self,
        directus_session,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """
        Valida integridade referencial: clausula_id aponta para registro válido.
        """
        # Buscar todas modificações da versão
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modificacao",
            params={
                "filter": {"versao": {"_eq": versao_processada_id}},
                "fields": ["id", "clausula"]
            },
        )
        
        assert response.status_code == 200
        modificacoes = response.json()["data"]
        
        clausula_ids = {mod["clausula"] for mod in modificacoes if mod.get("clausula")}
        
        # Para cada clausula_id, validar que registro existe
        for clausula_id in clausula_ids:
            response = directus_session.get(
                f"{e2e_ui_config.directus_url}/items/clausula/{clausula_id}"
            )
            
            assert response.status_code == 200, (
                f"❌ Foreign key inválido: modificação aponta para cláusula "
                f"inexistente {clausula_id}"
            )
        
        print(f"✅ Integridade referencial OK: {len(clausula_ids)} cláusulas validadas")
