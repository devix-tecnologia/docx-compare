#!/usr/bin/env python3
"""
Script para capturar dados da versão 99090886-7f43-45c9-bfe4-ec6eddd6cde0 do Directus
e salvar como fixture para testes reproduzíveis.

Uso:
    cd versiona-ai/tests/sample/versao-99090886
    python capture_fixture.py
"""

import json
import sys
from pathlib import Path

import requests

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Configuração
VERSAO_ID = "99090886-7f43-45c9-bfe4-ec6eddd6cde0"
OUTPUT_DIR = Path(__file__).parent


def capture_data():
    """Captura todos os dados necessários do Directus."""
    print(f"🔍 Capturando dados da versão {VERSAO_ID}...")

    # 1. Processar versão para obter resultado completo
    print("📥 Processando versão (simula POST /api/process)...")
    response = requests.post(
        "http://localhost:8001/api/process",
        json={"versao_id": VERSAO_ID},
        headers={"Content-Type": "application/json"},
    )

    if response.status_code != 200:
        print(f"❌ Erro ao processar versão: {response.status_code}")
        print(response.text)
        return False

    result = response.json()

    # Salvar resultado completo do processamento
    with open(OUTPUT_DIR / "resultado_processamento.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("✅ Resultado do processamento salvo: resultado_processamento.json")

    # 2. Extrair métricas de vinculação
    metrics = result.get("vinculacao_metrics", {})
    with open(OUTPUT_DIR / "vinculacao_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print("✅ Métricas de vinculação salvas: vinculacao_metrics.json")

    # 3. Extrair modificações detalhadas
    modificacoes = result.get("modificacoes", [])
    with open(OUTPUT_DIR / "modificacoes_processadas.json", "w", encoding="utf-8") as f:
        json.dump(modificacoes, f, indent=2, ensure_ascii=False)
    print(
        f"✅ Modificações processadas salvas ({len(modificacoes)} items): modificacoes_processadas.json"
    )

    # 4. Criar resumo para testes
    resumo = {
        "versao_id": VERSAO_ID,
        "data_captura": result.get("created_at"),
        "metricas": {
            "total_modificacoes": len(modificacoes),
            "vinculadas": metrics.get("vinculadas", 0),
            "revisao_manual": metrics.get("revisao_manual", 0),
            "nao_vinculadas": metrics.get("nao_vinculadas", 0),
            "taxa_sucesso": metrics.get("taxa_sucesso", 0),
            "taxa_cobertura": metrics.get("taxa_cobertura", 0),
            "tags_mapeadas": metrics.get("tags_mapeadas", 0),
        },
        "qualidade": {
            "similaridade": metrics.get("similaridade", 0),
            "metodo_usado": metrics.get("metodo_usado", ""),
        },
        "arquivos_gerados": [
            "resultado_processamento.json",
            "vinculacao_metrics.json",
            "modificacoes_processadas.json",
            "test_expectations.json",
        ],
    }

    with open(OUTPUT_DIR / "fixture_summary.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)

    # 5. Criar expectativas para testes
    expectations = {
        "description": "Expectativas mínimas para teste de regressão da versão 99090886",
        "versao_id": VERSAO_ID,
        "min_vinculacao_taxa": 40.0,  # Mínimo de 40% de vinculação
        "min_cobertura_taxa": 45.0,  # Mínimo de 45% de cobertura
        "min_similaridade": 0.90,  # Mínimo de 90% de similaridade
        "metodo_esperado": "conteudo",  # Deve usar método conteúdo
        "baseline": {
            "vinculadas": metrics.get("vinculadas", 0),
            "revisao_manual": metrics.get("revisao_manual", 0),
            "nao_vinculadas": metrics.get("nao_vinculadas", 0),
            "taxa_sucesso": metrics.get("taxa_sucesso", 0),
            "taxa_cobertura": metrics.get("taxa_cobertura", 0),
        },
        "note": "Estes valores são baseados no resultado do commit e4cc120 (conteúdo + fuzzy matching)",
    }

    with open(OUTPUT_DIR / "test_expectations.json", "w", encoding="utf-8") as f:
        json.dump(expectations, f, indent=2, ensure_ascii=False)
    print("✅ Expectativas de teste salvas: test_expectations.json")

    # 6. Criar README
    readme_content = f"""# Fixture: Versão 99090886-7f43-45c9-bfe4-ec6eddd6cde0

## Descrição

Esta fixture contém dados reais capturados do Directus para a versão `{VERSAO_ID}`.
Os dados foram capturados após a implementação do método de conteúdo + fuzzy matching (commit e4cc120).

## Arquivos

- `resultado_processamento.json`: Resultado completo do processamento da versão
- `vinculacao_metrics.json`: Métricas detalhadas de vinculação
- `modificacoes_processadas.json`: Lista completa de modificações com vinculações
- `test_expectations.json`: Expectativas mínimas para testes de regressão
- `fixture_summary.json`: Resumo da captura
- `README.md`: Este arquivo

## Métricas Capturadas

- **Total de modificações**: {len(modificacoes)}
- **Vinculadas**: {metrics.get("vinculadas", 0)} ({metrics.get("taxa_sucesso", 0):.1f}%)
- **Revisão manual**: {metrics.get("revisao_manual", 0)} ({metrics.get("revisao_manual", 0) / len(modificacoes) * 100:.1f}%)
- **Não vinculadas**: {metrics.get("nao_vinculadas", 0)} ({metrics.get("nao_vinculadas", 0) / len(modificacoes) * 100:.1f}%)
- **Taxa de cobertura**: {metrics.get("taxa_cobertura", 0):.1f}%
- **Similaridade**: {metrics.get("similaridade", 0):.2%}
- **Método usado**: {metrics.get("metodo_usado", "N/A")}

## Uso em Testes

```python
import json
from pathlib import Path

# Carregar fixture
fixture_dir = Path(__file__).parent / "versao-99090886"
with open(fixture_dir / "test_expectations.json") as f:
    expectations = json.load(f)

# Executar teste
result = process_versao(expectations["versao_id"])

# Validar contra expectativas
assert result["vinculacao_metrics"]["taxa_sucesso"] >= expectations["min_vinculacao_taxa"]
assert result["vinculacao_metrics"]["taxa_cobertura"] >= expectations["min_cobertura_taxa"]
assert result["vinculacao_metrics"]["similaridade"] >= expectations["min_similaridade"]
```

## Atualização

Para atualizar esta fixture:

```bash
cd versiona-ai/tests/sample/versao-99090886
python capture_fixture.py
```

## Data da Captura

{result.get("created_at", "N/A")}
"""

    with open(OUTPUT_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ README criado: README.md")

    print("\n" + "=" * 60)
    print("✅ CAPTURA COMPLETA!")
    print("=" * 60)
    print("📊 Resumo:")
    print(f"   - Versão: {VERSAO_ID}")
    print(f"   - Modificações: {len(modificacoes)}")
    print(
        f"   - Vinculadas: {metrics.get('vinculadas', 0)} ({metrics.get('taxa_sucesso', 0):.1f}%)"
    )
    print(f"   - Cobertura: {metrics.get('taxa_cobertura', 0):.1f}%")
    print(f"   - Similaridade: {metrics.get('similaridade', 0):.2%}")
    print(f"   - Método: {metrics.get('metodo_usado', 'N/A')}")
    print(f"\n📁 Arquivos salvos em: {OUTPUT_DIR}")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = capture_data()
    sys.exit(0 if success else 1)
