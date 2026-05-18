# Testes E2E do DiffVisualizer

## ✅ Status

O DiffVisualizer está **100% funcional** e pronto para testes Playwright!

### Componentes Verificados

1. **POST /api/process**: Processa documentos e retorna diff_id
2. **GET /view/{diff_id}**: Serve interface Vue.js do visualizador
3. **GET /api/data/{diff_id}**: API JSON com dados das modificações
4. **GET /assets/\***: Assets estáticos (JS e CSS)

## 🚀 Como Executar os Testes

### 1. Teste de Integração Simples (Python)

```bash
cd /Users/sidarta/repositorios/docx-compare/versiona-ai
uv run python test_diff_viewer_integration.py
```

Este teste verifica:

- ✅ Processamento de versão
- ✅ Visualizador HTML
- ✅ API de dados
- ✅ Assets estáticos

### 2. Testes E2E com Playwright

Os testes estão em: `tests/e2e_ui/test_diff_visualizer.py`

```bash
# Dentro do container de testes
pytest tests/e2e_ui/test_diff_visualizer.py -v
```

**Fixtures disponíveis:**

- `diff_id`: Processa uma versão e retorna o diff_id para usar nos testes

**Testes implementados:**

1. `test_visualizador_carrega_interface`: Verifica carregamento da interface
2. `test_visualizador_exibe_modificacoes`: Verifica exibição das modificações
3. `test_visualizador_exibe_metricas`: Verifica exibição das métricas
4. `test_api_dados_retorna_json_valido`: Valida resposta da API
5. `test_visualizador_assets_carregam`: Verifica carregamento de assets

## 🔧 Configuração para Playwright

### URLs para Testes

**Dentro do Docker Compose:**

```python
# No container test-runner, usar a URL interna
page.goto("http://api-server:8001/view/{diff_id}")
```

**De fora do Docker:**

```python
# Para testes locais
page.goto("http://localhost:8011/view/{diff_id}")
```

### Exemplo de Teste Básico

```python
def test_visualizador_basico(page: Page):
    # 1. Processar versão
    response = requests.post(
        "http://api-server:8001/api/process",
        json={"versao_id": "2573b998-63d0-4471-ad85-db6f860c3721"},
        timeout=120
    )

    diff_id = response.json()["diff_id"]

    # 2. Abrir visualizador
    page.goto(f"http://api-server:8001/view/{diff_id}")

    # 3. Aguardar carregamento
    page.wait_for_selector("#app", timeout=10000)

    # 4. Verificar título
    expect(page).to_have_title("Versiona AI - Visualizador de Diff")

    # 5. Verificar variáveis JavaScript
    versao_id = page.evaluate("window.VERSAO_ID")
    assert versao_id == diff_id
```

## 📊 Resultados Esperados

### Processamento Bem-Sucedido

```json
{
  "diff_id": "e59b1ea1-4895-4879-ba53-a295bfa937b9",
  "success": true,
  "metodo": "AST_PANDOC",
  "metricas": {
    "total_modificacoes": 2,
    "alteracoes": 0,
    "insercoes": 2,
    "remocoes": 0
  },
  "modificacoes": [...],
  "url": "http://localhost:8001/view/e59b1ea1-4895-4879-ba53-a295bfa937b9"
}
```

### API de Dados

```json
{
  "diff_id": "e59b1ea1-4895-4879-ba53-a295bfa937b9",
  "metodo": "AST_PANDOC",
  "metricas": {...},
  "modificacoes": [
    {
      "tipo": "INSERCAO",
      "conteudo": {"novo": "a) Multa de 2% ..."},
      "posicao": {"linha": 1, "coluna": 1},
      "confianca": 0.9,
      "css_class": "diff-insercao"
    }
  ],
  "success": true,
  "total_blocos": 100
}
```

## ⚠️ Notas Importantes

### Timeouts

O processamento de documentos pode demorar mais de 30 segundos. Use timeouts adequados:

```python
# Para requests
response = requests.post(..., timeout=120)

# Para Playwright
page.wait_for_load_state("networkidle", timeout=15000)
```

### Seletores CSS

Os seletores CSS no arquivo de teste são genéricos. Ajuste conforme sua implementação Vue.js:

```python
# Exemplo: ajustar seletores
modificacoes = page.locator(".diff-insercao, .diff-alteracao, .diff-remocao")
metricas = page.locator("text=/Total.*modificações/i")
```

### Variáveis JavaScript Injetadas

O backend injeta estas variáveis no HTML:

```javascript
window.VERSAO_ID = "e59b1ea1-4895-4879-ba53-a295bfa937b9";
window.LOAD_FROM_API = true;
```

Use `page.evaluate()` para acessá-las nos testes.

## 🐛 Troubleshooting

### Timeout no Processamento

Se o processamento demora muito:

1. Aumente o timeout: `timeout=180`
2. Verifique logs: `docker logs e2e-ui-api`
3. Use versões com documentos menores para testes rápidos

### Assets Não Carregam

Se JavaScript/CSS não carregar:

1. Verificar: `curl -I http://localhost:8011/assets/index-*.js`
2. Verificar build Vue.js: `versiona-ai/web/dist/`
3. Verificar logs do Flask para erros de CORS

### Interface Não Exibe Modificações

Se o visualizador carregar mas não mostrar modificações:

1. Abrir DevTools do browser no Playwright
2. Verificar chamadas de rede para `/api/data/{diff_id}`
3. Verificar console JavaScript por erros

## 📝 Próximos Passos

1. Executar testes Playwright completos
2. Validar seletores CSS conforme implementação Vue.js
3. Adicionar testes de interatividade (cliques, filtros, etc)
4. Adicionar testes de diferentes tipos de modificações (ALTERACAO, REMOCAO)
5. Adicionar testes de responsividade mobile

## 🔗 Arquivos Relacionados

- **Teste integração simples**: `test_diff_viewer_integration.py`
- **Testes Playwright**: `tests/e2e_ui/test_diff_visualizer.py`
- **Backend Flask**: `directus_server.py`
- **Frontend Vue.js**: `web/dist/`
- **Docker Compose**: `docker-compose.ui-test.yml`
