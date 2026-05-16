# 🧪 Testes E2E (End-to-End)

Suite de testes end-to-end para validar o fluxo completo de processamento de versões no ambiente de produção.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Configuração](#configuração)
- [Executando os Testes](#executando-os-testes)
- [Estrutura de Testes](#estrutura-de-testes)
- [Ambientes](#ambientes)
- [CI/CD](#cicd)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

Os testes E2E validam:

- ✅ **Health checks** - Servidor está rodando e respondendo
- ✅ **API endpoints** - Endpoints retornam dados na estrutura esperada
- ✅ **Integração Directus** - Comunicação com CMS está funcional
- ✅ **Processamento mock** - Lógica de processamento sem efeitos colaterais
- ✅ **Performance** - Servidor aguenta carga moderada
- ✅ **Tratamento de erros** - Validação de cenários de falha

## 📦 Requisitos

### Local

```bash
# Python 3.13+
python --version

# UV package manager
uv --version

# Dependências do projeto
uv sync
```

### Docker (recomendado)

```bash
# Docker e Docker Compose
docker --version
docker-compose --version
```

## ⚙️ Configuração

### 1. Arquivo de Ambiente

Copie e configure o `.env.e2e`:

```bash
cp .env.e2e.example .env.e2e
```

Edite o arquivo com suas credenciais:

```env
# URL base da API (local ou remota)
E2E_BASE_URL=http://localhost:8001

# Directus CMS
E2E_DIRECTUS_URL=https://contract.devix.co
E2E_DIRECTUS_TOKEN=your-directus-token-here

# Timeouts (segundos)
E2E_TIMEOUT=30

# CUIDADO: Apenas para testes em produção
E2E_ALLOW_PRODUCTION=false
```

### 2. Markers de Teste

Configure markers no `pytest.ini` (já incluído):

```ini
[pytest]
markers =
    e2e: Testes end-to-end
    integration: Testes de integração
    slow: Testes que demoram mais de 5s
```

## 🚀 Executando os Testes

### Opção 1: Local (requer servidor rodando)

```bash
# 1. Iniciar servidor em outra janela
make dev-server

# 2. Executar testes E2E
make e2e-test

# Ou diretamente com pytest
uv run pytest tests/e2e/ -v -s
```

### Opção 2: Docker Compose (recomendado)

```bash
# Executar tudo automaticamente (build + run + cleanup)
make e2e-test-docker

# Ou manualmente
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
docker-compose -f docker-compose.test.yml down
```

### Opção 3: CI/CD

```bash
# Modo CI (sem interação, retorna exit code)
make e2e-ci
```

### Testes Seletivos

```bash
# Apenas health checks
uv run pytest tests/e2e/ -k "TestHealthCheck" -v

# Apenas testes rápidos (exclui @slow)
uv run pytest tests/e2e/ -m "not slow" -v

# Apenas testes de integração
uv run pytest tests/e2e/ -m "integration" -v

# Apenas um teste específico
uv run pytest tests/e2e/test_processamento_completo_remoto.py::TestHealthCheck::test_server_is_reachable -v
```

## 🏗️ Estrutura de Testes

```
tests/e2e/
├── __init__.py                               # Package marker
├── conftest.py                               # Fixtures pytest compartilhadas
├── test_processamento_completo_remoto.py     # Testes do fluxo completo
├── Dockerfile.test                           # Container para test runner
└── README.md                                 # Esta documentação

tests/fixtures/
└── directus_mock_server.py                   # Mock do Directus (futuro)
```

### Classes de Teste

#### `TestHealthCheck`

Testes básicos de conectividade:

- `test_server_is_reachable` - Servidor responde
- `test_health_endpoint_returns_valid_data` - Health check retorna JSON válido

#### `TestProcessamentoCompleto`

Testes do fluxo de processamento:

- `test_processar_versao_mock` - Mock mode sem efeitos colaterais
- `test_processar_versao_uuid_invalido` - Validação de UUID
- `test_processar_versao_inexistente` - Tratamento de 404

#### `TestDirectusIntegration`

Testes de integração com Directus (opcionais):

- `test_directus_connectivity` - Ping no Directus
- `test_directus_read_versoes` - Leitura da collection

#### `TestPerformanceReliability`

Testes de carga e resiliência:

- `test_multiplas_requisicoes_sequenciais` - Processamento em sequência
- `test_timeout_handling` - Validação de timeouts

## 🌍 Ambientes

### Local (http://localhost:8001)

```bash
# .env.e2e
E2E_BASE_URL=http://localhost:8001
E2E_ALLOW_PRODUCTION=false
```

### Staging/QA

```bash
# .env.e2e
E2E_BASE_URL=https://staging.example.com
E2E_ALLOW_PRODUCTION=false
```

### Produção ⚠️

```bash
# .env.e2e
E2E_BASE_URL=https://ignai-contract-ia.paas.node10.de.vix.br
E2E_ALLOW_PRODUCTION=true  # CUIDADO!

# Executar com flag adicional
uv run pytest tests/e2e/ --e2e-production -v
```

**⚠️ ATENÇÃO:** Testes em produção podem modificar dados reais. Use apenas em modo mock ou com dados de teste isolados.

## 🔄 CI/CD

### GitHub Actions (exemplo)

```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run E2E Tests
        run: make e2e-ci
        env:
          E2E_DIRECTUS_TOKEN: ${{ secrets.DIRECTUS_TOKEN }}

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results/
```

## 📊 Relatórios

```bash
# Gerar relatório HTML
make e2e-test-docker

# Abrir relatório
make e2e-test-report

# Relatórios salvos em:
# - test-results/junit.xml     (XML para CI)
# - test-results/report.html   (HTML para humanos)
```

## 🐛 Troubleshooting

### Erro: "Servidor não está acessível"

```bash
# Verificar se servidor está rodando
curl http://localhost:8001/health

# Iniciar servidor
make dev-server
```

### Erro: "Production environment blocked"

```bash
# Confirmar que é intencional
echo "E2E_ALLOW_PRODUCTION=true" >> .env.e2e

# Executar com flag
uv run pytest tests/e2e/ --e2e-production
```

### Erro: "Directus not connected"

```bash
# Verificar token no .env.e2e
echo $E2E_DIRECTUS_TOKEN

# Testar conectividade manual
curl -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  https://contract.devix.co/server/ping
```

### Docker não builda

```bash
# Limpar cache
docker-compose -f docker-compose.test.yml down -v
docker system prune -f

# Rebuild
make e2e-test-docker
```

### Testes lentos

```bash
# Rodar apenas testes rápidos
uv run pytest tests/e2e/ -m "not slow"

# Aumentar timeout no .env.e2e
E2E_TIMEOUT=60
```

## 🎓 Boas Práticas

### ✅ DO

- Execute testes E2E antes de deploy
- Use modo mock para desenvolvimento rápido
- Mantenha .env.e2e fora do git (use .env.e2e.example)
- Documente novos casos de teste
- Use markers (`@pytest.mark.slow`) adequadamente

### ❌ DON'T

- Nunca commite tokens reais no repositório
- Evite testes E2E em produção sem supervisão
- Não use sleep() explícito (use fixtures com retry)
- Não crie testes que dependem de ordem de execução
- Evite hardcoded UUIDs (use fixtures ou factories)

## 📚 Recursos Adicionais

- [Pytest Documentation](https://docs.pytest.org/)
- [Requests Library](https://requests.readthedocs.io/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Directus API Docs](https://docs.directus.io/reference/introduction.html)

## 🤝 Contribuindo

Para adicionar novos testes:

1. Crie nova classe de teste em `test_processamento_completo_remoto.py`
2. Use fixtures do `conftest.py` (api_client, directus_client)
3. Adicione markers apropriados (`@pytest.mark.slow`, etc)
4. Documente comportamento esperado
5. Atualize este README se necessário

---

**Versão:** 1.0.0
**Última atualização:** 2024-01-10
