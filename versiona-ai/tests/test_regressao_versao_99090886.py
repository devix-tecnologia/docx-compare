"""
Teste de regressão da versão 99090886-7f43-45c9-bfe4-ec6eddd6cde0

Este teste garante que o processamento desta versão mantém qualidade mínima
usando dados reais capturados do Directus como fixture.

Baseline estabelecido no commit e4cc120 (conteúdo + fuzzy matching):
- Vinculadas: 23/55 (41.8%)
- Cobertura: 45.5% (incluindo revisão manual)
- Similaridade: 91.34%
- Método: conteúdo
"""

import json
import sys
from pathlib import Path

import pytest

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import requests

# Configuração
FIXTURE_DIR = Path(__file__).parent / "sample" / "versao-99090886"
API_URL = "http://localhost:8001"


@pytest.fixture
def expectations():
    """Carrega expectativas mínimas do teste."""
    with open(FIXTURE_DIR / "test_expectations.json") as f:
        return json.load(f)


@pytest.fixture
def baseline_metrics():
    """Carrega métricas baseline capturadas."""
    with open(FIXTURE_DIR / "vinculacao_metrics.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def resultado_processamento():
    """
    Processa a versão UMA ÚNICA VEZ e compartilha resultado entre todos os testes.

    Isso evita processar 5 vezes (reduz de ~5 minutos para ~1 minuto).
    
    Para testes rápidos offline, use a fixture salva:
    pytest --use-saved-fixture
    """
    import os
    
    # Opção para usar fixture salva (mais rápido para testes offline)
    if os.environ.get("USE_SAVED_FIXTURE") == "1":
        print("\n📦 Usando fixture salva (modo offline)")
        with open(FIXTURE_DIR / "resultado_processamento.json") as f:
            return json.load(f)
    
    versao_id = "99090886-7f43-45c9-bfe4-ec6eddd6cde0"

    print(f"\n🔄 Processando versão {versao_id} (executado 1x para todos os testes)...")
    print("⏳ Isso pode demorar 2-5 minutos (download + diff + vinculação)...")

    response = requests.post(
        f"{API_URL}/api/process",
        json={"versao_id": versao_id},
        headers={"Content-Type": "application/json"},
        timeout=600,  # 10 minutos - processamento completo pode demorar
    )

    assert response.status_code == 200, f"Erro ao processar: {response.status_code}"

    result = response.json()
    print("✅ Processamento concluído!")
    print(
        f"   Vinculadas: {result['vinculacao_metrics']['vinculadas']}/{result['vinculacao_metrics']['total_modificacoes']}"
    )
    print(f"   Taxa: {result['vinculacao_metrics']['taxa_sucesso']:.1f}%")

    return result


def test_servidor_disponivel():
    """Verifica se o servidor está rodando."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        assert response.status_code == 200, "Servidor não está disponível"
    except requests.exceptions.ConnectionError:
        pytest.skip("Servidor não está rodando. Inicie com: python directus_server.py")


def test_processamento_versao_99090886_taxa_minima(
    expectations, resultado_processamento
):
    """
    Teste de regressão: garante taxa mínima de vinculação.

    Requisitos mínimos:
    - Taxa de sucesso ≥ 40%
    - Taxa de cobertura ≥ 45%
    - Similaridade ≥ 90%
    - Método usado: conteúdo
    """
    metrics = resultado_processamento.get("vinculacao_metrics", {})

    # Validações contra expectativas mínimas
    assert metrics["taxa_sucesso"] >= expectations["min_vinculacao_taxa"], (
        f"Taxa de vinculação ({metrics['taxa_sucesso']:.1f}%) abaixo do mínimo ({expectations['min_vinculacao_taxa']:.1f}%)"
    )

    assert metrics["taxa_cobertura"] >= expectations["min_cobertura_taxa"], (
        f"Taxa de cobertura ({metrics['taxa_cobertura']:.1f}%) abaixo do mínimo ({expectations['min_cobertura_taxa']:.1f}%)"
    )

    assert metrics["similaridade"] >= expectations["min_similaridade"], (
        f"Similaridade ({metrics['similaridade']:.2%}) abaixo do mínimo ({expectations['min_similaridade']:.2%})"
    )

    assert metrics["metodo_usado"] == expectations["metodo_esperado"], (
        f"Método usado ({metrics['metodo_usado']}) diferente do esperado ({expectations['metodo_esperado']})"
    )


def test_processamento_versao_99090886_nao_regredir(
    baseline_metrics, resultado_processamento
):
    """
    Teste de regressão: garante que não houve piora em relação ao baseline.

    Nenhuma métrica deve piorar mais de 5% em relação ao baseline.
    """
    metrics = resultado_processamento.get("vinculacao_metrics", {})

    # Tolerância de 5% de variação (pode ter pequenas diferenças por ordem de processamento)
    tolerancia = 0.95  # 95% do baseline

    assert metrics["vinculadas"] >= baseline_metrics["vinculadas"] * tolerancia, (
        f"Vinculadas caíram: {metrics['vinculadas']} vs baseline {baseline_metrics['vinculadas']}"
    )

    assert metrics["taxa_sucesso"] >= baseline_metrics["taxa_sucesso"] * tolerancia, (
        f"Taxa de sucesso caiu: {metrics['taxa_sucesso']:.1f}% vs baseline {baseline_metrics['taxa_sucesso']:.1f}%"
    )

    assert (
        metrics["taxa_cobertura"] >= baseline_metrics["taxa_cobertura"] * tolerancia
    ), (
        f"Taxa de cobertura caiu: {metrics['taxa_cobertura']:.1f}% vs baseline {baseline_metrics['taxa_cobertura']:.1f}%"
    )

    assert metrics["similaridade"] >= baseline_metrics["similaridade"] * tolerancia, (
        f"Similaridade caiu: {metrics['similaridade']:.2%} vs baseline {baseline_metrics['similaridade']:.2%}"
    )


def test_processamento_versao_99090886_modificacoes_validas(resultado_processamento):
    """
    Teste de integridade: verifica se modificações foram criadas corretamente.
    
    - Se fixture salva: valida estrutura dos dados salvos
    - Se API real: busca modificações do Directus para validar
    """
    modificacoes = resultado_processamento.get("modificacoes", [])

    # Se não tem modificações na resposta, buscar do Directus (API real)
    if not modificacoes:
        versao_id = "99090886-7f43-45c9-bfe4-ec6eddd6cde0"
        response = requests.get(
            f"{API_URL}/api/versoes/{versao_id}/modificacoes",
            timeout=30,
        )
        
        assert response.status_code == 200, (
            f"Erro ao buscar modificações do Directus: {response.status_code}"
        )
        
        modificacoes = response.json()

    # Deve ter modificações
    assert len(modificacoes) > 0, "Nenhuma modificação foi criada"

    # Cada modificação deve ter estrutura válida
    for mod in modificacoes:
        # Estrutura da fixture: {metodo_inferencia, modificacao, score, tag}
        # Estrutura do Directus: {id, tipo, conteudo, vinculacao, ...}
        if "modificacao" in mod:
            # Fixture capturada
            mod_data = mod["modificacao"]
            assert "id" in mod_data, f"Modificação sem ID: {mod_data}"
            assert "tipo" in mod_data, f"Modificação sem tipo: {mod_data}"
        else:
            # Directus direto
            assert "id" in mod, f"Modificação sem ID: {mod}"
            assert "tipo" in mod, f"Modificação sem tipo: {mod}"
        
        # Validar score de vinculação
        score = mod.get("score") or (mod.get("vinculacao") or {}).get("score")
        if score is not None:
            assert score >= 0.0 and score <= 1.0, f"Score inválido: {score}"


def test_processamento_versao_99090886_tags_mapeadas(resultado_processamento):
    """
    Teste de mapeamento de tags: todas as tags devem ser mapeadas.
    """
    metrics = resultado_processamento.get("vinculacao_metrics", {})

    # Todas as tags devem ser mapeadas (100 tags no modelo)
    assert metrics["tags_mapeadas"] == 100, (
        f"Nem todas as tags foram mapeadas: {metrics['tags_mapeadas']}/100"
    )


def test_comparacao_com_fixture_salva(baseline_metrics, resultado_processamento):
    """
    Teste de reprodutibilidade: compara resultado com fixture salva.

    Este teste garante que o processamento é determinístico.
    """
    metrics = resultado_processamento.get("vinculacao_metrics", {})

    # Valores devem ser exatos (ou muito próximos, considerando ordem de float)
    assert abs(metrics["vinculadas"] - baseline_metrics["vinculadas"]) <= 1, (
        f"Vinculadas divergem: {metrics['vinculadas']} vs {baseline_metrics['vinculadas']}"
    )

    assert abs(metrics["nao_vinculadas"] - baseline_metrics["nao_vinculadas"]) <= 1, (
        f"Não vinculadas divergem: {metrics['nao_vinculadas']} vs {baseline_metrics['nao_vinculadas']}"
    )

    # Similaridade pode ter pequena variação por arredondamento
    assert abs(metrics["similaridade"] - baseline_metrics["similaridade"]) < 0.01, (
        f"Similaridade diverge: {metrics['similaridade']:.4f} vs {baseline_metrics['similaridade']:.4f}"
    )


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])
