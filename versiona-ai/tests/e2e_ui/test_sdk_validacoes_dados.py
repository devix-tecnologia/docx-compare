"""
Validações de dados via Directus SDK (sem UI).
Testes rápidos focados em integridade de dados.
"""

import pytest


class TestValidacoesDadosSDK:
    """Validações de dados via API Directus."""

    def test_modelo_contrato_existe(
        self,
        directus_session,
        e2e_ui_config,
        modelo_contrato_id: str
    ):
        """Valida que modelo de contrato de teste existe."""
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modelo_contrato/{modelo_contrato_id}"
        )

        assert response.status_code == 200
        modelo = response.json()["data"]

        assert modelo["nome"] == "Modelo Teste Task 010"
        print(f"✅ Modelo encontrado: {modelo['nome']}")

    def test_modelo_tem_clausulas(
        self,
        directus_session,
        e2e_ui_config,
        modelo_contrato_id: str
    ):
        """Valida que modelo tem cláusulas cadastradas."""
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/clausula",
            params={"filter": {"modelo_contrato": {"_eq": modelo_contrato_id}}},
        )

        assert response.status_code == 200
        clausulas = response.json()["data"]

        assert len(clausulas) >= 5, f"Modelo deve ter >= 5 cláusulas, tem {len(clausulas)}"

        print(f"✅ Modelo tem {len(clausulas)} cláusulas")

    def test_clausulas_tem_referencia_unica(
        self,
        directus_session,
        e2e_ui_config,
        modelo_contrato_id: str
    ):
        """Valida que cada cláusula tem referência única (ex: 1.0, 2.0)."""
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/clausula",
            params={
                "filter": {"modelo_contrato": {"_eq": modelo_contrato_id}},
                "fields": ["id", "referencia"]
            },
        )

        assert response.status_code == 200
        clausulas = response.json()["data"]

        referencias = [c["referencia"] for c in clausulas]

        # Validar unicidade
        assert len(referencias) == len(set(referencias)), (
            "Existem referências duplicadas"
        )

        print(f"✅ {len(referencias)} referências únicas: {referencias[:5]}...")

    def test_directus_health_check(
        self,
        directus_session,
        e2e_ui_config
    ):
        """Valida que Directus está saudável."""
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/server/health"
        )

        assert response.status_code == 200
        print("✅ Directus health check: OK")

    def test_api_versiona_health_check(
        self,
        api_session,
        e2e_ui_config
    ):
        """Valida que API Versiona está saudável."""
        response = api_session.get(
            f"{e2e_ui_config.api_url}/health"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data.get("directus_connected") is True

        print(f"✅ API Versiona health: {data['status']}")

    def test_consistencia_ids_modificacao_clausula(
        self,
        directus_session,
        e2e_ui_config,
        versao_processada_id: str
    ):
        """
        Valida consistência: IDs de cláusulas nas modificações
        correspondem a registros reais.
        """
        # Buscar modificações
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/modificacao",
            params={
                "filter": {"versao": {"_eq": versao_processada_id}},
                "fields": ["id", "clausula"]
            },
        )

        assert response.status_code == 200
        modificacoes = response.json()["data"]

        if not modificacoes:
            pytest.skip("Versão não tem modificações para validar")

        # Coletar IDs únicos de cláusulas
        clausula_ids = {
            mod["clausula"] for mod in modificacoes
            if mod.get("clausula")
        }

        # Buscar todas cláusulas em uma query
        response = directus_session.get(
            f"{e2e_ui_config.directus_url}/items/clausula",
            params={"filter": {"id": {"_in": list(clausula_ids)}}},
        )

        assert response.status_code == 200
        clausulas_existentes = response.json()["data"]

        # Validar que todos IDs existem
        ids_existentes = {c["id"] for c in clausulas_existentes}

        assert clausula_ids == ids_existentes, (
            f"IDs inconsistentes - Esperados: {clausula_ids}, "
            f"Existentes: {ids_existentes}"
        )

        print(f"✅ Consistência OK: {len(clausula_ids)} cláusulas validadas")
