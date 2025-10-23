# Fixture: Versão 99090886-7f43-45c9-bfe4-ec6eddd6cde0

## Descrição

Esta fixture contém dados reais capturados do Directus para a versão `99090886-7f43-45c9-bfe4-ec6eddd6cde0`.
Os dados foram capturados após a implementação do método de conteúdo + fuzzy matching (commit e4cc120).

## Arquivos

- `resultado_processamento.json`: Resultado completo do processamento da versão
- `vinculacao_metrics.json`: Métricas detalhadas de vinculação
- `modificacoes_processadas.json`: Lista completa de modificações com vinculações
- `test_expectations.json`: Expectativas mínimas para testes de regressão
- `fixture_summary.json`: Resumo da captura
- `README.md`: Este arquivo

## Métricas Capturadas

- **Total de modificações**: 55
- **Vinculadas**: 23 (41.8%)
- **Revisão manual**: 2 (3.6%)
- **Não vinculadas**: 30 (54.5%)
- **Taxa de cobertura**: 45.5%
- **Similaridade**: 91.34%
- **Método usado**: conteudo

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

2025-10-12T18:13:53.353264
