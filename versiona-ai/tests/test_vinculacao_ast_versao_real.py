"""
Teste de regressão para vinculação de cláusulas em processamento AST.

PROBLEMA IDENTIFICADO (2026-05-16):
- Versão 2573b998-63d0-4471-ad85-db6f860c3721 processada com AST
- 2 modificações detectadas (INSERÇÃO)
- 85/100 tags mapeadas corretamente
- 271 cláusulas disponíveis no modelo
- PROBLEMA: posicao_inicio e posicao_fim são NULL nas modificações
- RESULTADO: 0% de vinculação (0/2 modificações vinculadas)

OBJETIVO:
- Garantir que modificações AST tenham posições calculadas
- Garantir vinculação automática de cláusulas baseada em posições
- Meta: >= 50% de vinculação (pelo menos 1/2 modificações)

FIXTURE:
- Versão real do Directus (backup restaurado no E2E)
- Processamento real via API
"""

import time

import pytest
import requests

# ==============================================================================
# CONSTANTES DA VERSÃO REAL
# ==============================================================================

VERSAO_ID = "2573b998-63d0-4471-ad85-db6f860c3721"
CONTRATO_ID = "f7435867-8e6e-4798-a00f-f6edc23ae0f2"
MODELO_ID = "48b43d38-76b4-47a2-93a4-4216ad57defc"
ARQUIVO_ID = "92f80aec-275c-4917-9d7c-4ba31a065561"

# URLs dos serviços E2E
API_BASE_URL = "http://localhost:8011"
DIRECTUS_BASE_URL = "http://localhost:8065"

# Tokens de autenticação
API_TOKEN = "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"
ADMIN_TOKEN = "test-static-token-12345"


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def api_headers():
    """Headers para autenticação na API"""
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


@pytest.fixture
def directus_headers():
    """Headers para autenticação no Directus"""
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


@pytest.fixture
def limpar_modificacoes_versao(directus_headers):
    """
    Limpa modificações existentes antes do teste para garantir estado limpo.
    Executa ANTES do teste.
    """
    # Buscar modificações existentes
    response = requests.get(
        f"{DIRECTUS_BASE_URL}/items/modificacao",
        headers=directus_headers,
        params={"filter[versao][_eq]": VERSAO_ID},
    )

    if response.status_code == 200:
        data = response.json()
        modificacoes = data.get("data", [])

        # Deletar cada modificação
        for mod in modificacoes:
            requests.delete(
                f"{DIRECTUS_BASE_URL}/items/modificacao/{mod['id']}",
                headers=directus_headers,
            )

    yield  # Teste executa aqui

    # Cleanup não necessário pois queremos manter resultado do teste


@pytest.fixture
def versao_data(directus_headers):
    """Dados da versão do Directus"""
    response = requests.get(
        f"{DIRECTUS_BASE_URL}/items/versao/{VERSAO_ID}",
        headers=directus_headers,
        params={
            "fields": "id,versao,status,origem,contrato.id,contrato.modelo_contrato"
        },
    )

    assert response.status_code == 200, f"Falha ao buscar versão: {response.text}"
    return response.json()["data"]


# ==============================================================================
# TESTES
# ==============================================================================


@pytest.mark.skip(reason="Requer ambiente E2E com Directus rodando em localhost:8065")
def test_vinculacao_clausulas_versao_real_ast(
    api_headers, directus_headers, limpar_modificacoes_versao, versao_data
):
    """
    Teste RED → GREEN para vinculação de cláusulas em processamento AST.

    ESTADO ATUAL (RED):
    - posicao_inicio = NULL
    - posicao_fim = NULL
    - clausula = NULL
    - Taxa de vinculação: 0%

    ESTADO ESPERADO (GREEN):
    - posicao_inicio != NULL (calculado do AST)
    - posicao_fim != NULL (calculado do AST)
    - clausula != NULL (vinculado automaticamente)
    - Taxa de vinculação: >= 50% (pelo menos 1/2)
    """

    # ===== ARRANGE =====
    print(f"\n🧪 Testando versão {VERSAO_ID}")
    print(f"   Contrato: {versao_data['contrato']['id']}")
    print(f"   Modelo: {versao_data['contrato']['modelo_contrato']}")

    # Verificar que serviços estão disponíveis
    health_check = requests.get(f"{API_BASE_URL}/health")
    assert health_check.status_code == 200, "API não está disponível"

    # ===== ACT =====
    print("\n⚙️  Processando versão via API...")
    response = requests.get(
        f"{API_BASE_URL}/api/versoes/{VERSAO_ID}",
        headers=api_headers,
        timeout=120,  # AST pode demorar
    )

    assert response.status_code == 200, f"Falha ao processar: {response.text}"
    resultado = response.json()

    print(f"   Status: {resultado.get('status')}")
    if resultado.get("message"):
        print(f"   Mensagem: {resultado.get('message')}")

    # Aguardar persistência no banco
    time.sleep(2)

    # ===== ASSERT - Buscar modificações criadas =====
    print("\n🔍 Verificando modificações criadas...")
    mod_response = requests.get(
        f"{DIRECTUS_BASE_URL}/items/modificacao",
        headers=directus_headers,
        params={
            "filter[versao][_eq]": VERSAO_ID,
            "fields": "id,categoria,alteracao,conteudo,posicao_inicio,posicao_fim,clausula,clausula.numero,clausula.nome",
        },
    )

    assert mod_response.status_code == 200, (
        f"Falha ao buscar modificações: {mod_response.text}"
    )
    modificacoes = mod_response.json()["data"]

    print(f"   Total de modificações: {len(modificacoes)}")

    # ===== ASSERT 1: Modificações foram criadas =====
    assert len(modificacoes) > 0, "Nenhuma modificação foi criada"
    assert len(modificacoes) == 2, (
        f"Esperado 2 modificações, obtido {len(modificacoes)}"
    )

    # ===== ASSERT 2: Posições foram calculadas =====
    print("\n📍 Verificando posições das modificações...")
    modificacoes_com_posicao = []
    modificacoes_sem_posicao = []

    for idx, mod in enumerate(modificacoes, 1):
        print(f"\n   Modificação {idx}:")
        print(f"      ID: {mod['id'][:8]}...")
        print(f"      Categoria: {mod['categoria']}")
        print(f"      Posição início: {mod.get('posicao_inicio')}")
        print(f"      Posição fim: {mod.get('posicao_fim')}")
        print(f"      Alteração: {len(mod.get('alteracao', '') or '')} chars")
        print(f"      Conteúdo: {len(mod.get('conteudo', '') or '')} chars")

        if mod.get("posicao_inicio") is not None and mod.get("posicao_fim") is not None:
            modificacoes_com_posicao.append(mod)
        else:
            modificacoes_sem_posicao.append(mod)

    # ASSERT CRÍTICO: Todas modificações devem ter posições
    assert len(modificacoes_sem_posicao) == 0, (
        f"❌ {len(modificacoes_sem_posicao)}/{len(modificacoes)} modificações SEM posição!\n"
        f"   Modificações sem posição: {[m['id'][:8] for m in modificacoes_sem_posicao]}\n"
        f"   PROBLEMA: Processamento AST não calculou posicoes_inicio/posicao_fim"
    )

    print(
        f"\n   ✅ {len(modificacoes_com_posicao)}/{len(modificacoes)} modificações COM posição"
    )

    # ===== ASSERT 3: Cláusulas foram vinculadas =====
    print("\n🔗 Verificando vinculação de cláusulas...")
    modificacoes_vinculadas = []
    modificacoes_nao_vinculadas = []

    for idx, mod in enumerate(modificacoes, 1):
        clausula = mod.get("clausula")

        if clausula and clausula != "":
            print(f"\n   ✅ Modificação {idx} VINCULADA:")
            print(
                f"      Cláusula: {clausula.get('numero') if isinstance(clausula, dict) else clausula}"
            )
            if isinstance(clausula, dict) and clausula.get("nome"):
                print(f"      Nome: {clausula['nome'][:50]}...")
            modificacoes_vinculadas.append(mod)
        else:
            print(f"\n   ❌ Modificação {idx} NÃO VINCULADA")
            modificacoes_nao_vinculadas.append(mod)

    # Calcular taxa de vinculação
    taxa_vinculacao = (len(modificacoes_vinculadas) / len(modificacoes)) * 100
    print(
        f"\n📊 Taxa de vinculação: {taxa_vinculacao:.1f}% ({len(modificacoes_vinculadas)}/{len(modificacoes)})"
    )

    # ASSERT CRÍTICO: Pelo menos 50% devem ser vinculadas
    assert taxa_vinculacao >= 50.0, (
        f"❌ Taxa de vinculação muito baixa: {taxa_vinculacao:.1f}%\n"
        f"   Meta: >= 50%\n"
        f"   Vinculadas: {len(modificacoes_vinculadas)}/{len(modificacoes)}\n"
        f"   PROBLEMA: Vinculação automática não funcionou mesmo com posições corretas"
    )

    print("\n✅ Teste PASSOU! Vinculação funcionando corretamente")


@pytest.mark.skip(reason="Requer ambiente E2E com Directus rodando em localhost:8065")
def test_modificacoes_tem_conteudo_valido(
    api_headers, directus_headers, limpar_modificacoes_versao
):
    """
    Teste auxiliar: verificar que modificações têm conteúdo válido.

    Modificações de INSERÇÃO devem ter:
    - campo 'alteracao' preenchido (texto inserido)
    - campo 'conteudo' pode ser vazio (não existe no original)
    """

    # Processar versão
    response = requests.get(
        f"{API_BASE_URL}/api/versoes/{VERSAO_ID}", headers=api_headers, timeout=120
    )

    assert response.status_code == 200

    time.sleep(2)

    # Buscar modificações
    mod_response = requests.get(
        f"{DIRECTUS_BASE_URL}/items/modificacao",
        headers=directus_headers,
        params={
            "filter[versao][_eq]": VERSAO_ID,
            "fields": "id,categoria,alteracao,conteudo",
        },
    )

    assert mod_response.status_code == 200
    modificacoes = mod_response.json()["data"]

    print(f"\n📝 Verificando conteúdo de {len(modificacoes)} modificações...")

    for idx, mod in enumerate(modificacoes, 1):
        categoria = mod.get("categoria")
        alteracao = mod.get("alteracao") or ""
        conteudo = mod.get("conteudo") or ""

        print(f"\n   Modificação {idx} ({categoria}):")
        print(f"      Alteração: {len(alteracao)} chars")
        print(f"      Conteúdo: {len(conteudo)} chars")

        if categoria == "INSERCAO":
            assert len(alteracao) > 0, (
                "Modificação INSERÇÃO deve ter campo 'alteracao' preenchido"
            )

        # Pelo menos um dos campos deve ter conteúdo
        assert len(alteracao) > 0 or len(conteudo) > 0, (
            "Modificação deve ter pelo menos um campo com conteúdo"
        )


# ==============================================================================
# HELPERS PARA DEBUG
# ==============================================================================


@pytest.mark.skip(reason="Requer ambiente E2E com Directus rodando em localhost:8065")
def test_debug_tags_modelo(directus_headers):
    """
    Teste auxiliar para debug: verificar tags do modelo.
    """
    response = requests.get(
        f"{DIRECTUS_BASE_URL}/items/tag",
        headers=directus_headers,
        params={
            "filter[modelo_contrato][_eq]": MODELO_ID,
            "fields": "id,tag_nome,conteudo",
            "limit": 10,
        },
    )

    assert response.status_code == 200
    tags = response.json()["data"]

    print(f"\n🏷️  Tags do modelo (primeiras 10/{len(tags)}):")
    for tag in tags[:10]:
        print(f"   - {tag['tag_nome']}: {len(tag.get('conteudo', ''))} chars")


@pytest.mark.skip(reason="Requer ambiente E2E com Directus rodando em localhost:8065")
def test_debug_clausulas_modelo(directus_headers):
    """
    Teste auxiliar para debug: verificar cláusulas do modelo.
    """
    response = requests.get(
        f"{DIRECTUS_BASE_URL}/items/clausula",
        headers=directus_headers,
        params={
            "filter[modelo_contrato][_eq]": MODELO_ID,
            "fields": "id,numero,nome",
            "limit": 10,
        },
    )

    assert response.status_code == 200
    clausulas = response.json()["data"]

    print("\n📚 Cláusulas do modelo (primeiras 10):")
    for clausula in clausulas[:10]:
        print(f"   - {clausula['numero']}: {clausula['nome'][:50]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
