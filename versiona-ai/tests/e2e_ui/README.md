# Testes E2E via Interface de Usuário

Testes end-to-end que validam o fluxo completo do usuário através da interface do Directus, garantindo que a Task 010 (vinculação cláusulas-modificações) funciona na prática.

## 🎯 Objetivo

Validar que usuários conseguem:
1. ✅ Criar/processar versões de contrato
2. ✅ Visualizar modificações vinculadas às cláusulas corretas
3. ✅ Navegar e filtrar modificações por cláusula
4. ✅ Completar fluxo sem erros ou confusão

## 🏗️ Arquitetura

### Abordagem Híbrida

**Directus SDK** (validações rápidas de dados):
- Setup de dados de teste
- Validação de foreign keys
- Consultas de estado do sistema

**Playwright** (testes críticos de UI):
- Login no Directus Admin
- Navegação e interação com formulários
- Validação de elementos visuais
- Screenshots de evidências

### Stack do Docker Compose

```
┌─────────────┐
│ Test Runner │──┐
│ (Playwright)│  │
└─────────────┘  │
                 ├─> ┌──────────┐
┌─────────────┐  │   │ Directus │
│  API Server │──┼──>│   CMS    │
│ (Versiona)  │  │   └──────────┘
└─────────────┘  │         │
                 │         ▼
                 │   ┌──────────┐
                 └──>│PostgreSQL│
                     └──────────┘
```

## 🚀 Uso Rápido

### Executar todos os testes

```bash
make e2e-ui-test
```

### Executar apenas testes de UI (Playwright)

```bash
make e2e-ui-test-playwright
```

### Executar apenas validações de dados (SDK)

```bash
make e2e-ui-test-sdk
```

### Modo desenvolvimento (sem rebuild)

```bash
make e2e-ui-up      # Subir stack
make e2e-ui-shell   # Shell interativo no test-runner
pytest tests/e2e_ui/ -v -s --headed  # Rodar com browser visível
```

### Ver logs em tempo real

```bash
make e2e-ui-logs
```

### Limpar ambiente

```bash
make e2e-ui-down
```

## 📁 Estrutura de Arquivos

```
tests/e2e_ui/
├── README.md                          # Este arquivo
├── conftest.py                        # Fixtures pytest
├── Dockerfile.ui-test                 # Container do test runner
├── pyproject.toml                     # Dependências (Playwright, SDK)
├── seed/
│   ├── 01-schema.sql                  # Schema do banco
│   ├── 02-modelo-contrato.sql         # Modelo com cláusulas
│   └── 03-usuarios.sql                # Usuários de teste
├── fixtures/
│   ├── contrato-modelo.docx           # Documento modelo
│   └── contrato-versao-alterada.docx  # Versão modificada
├── test_ui_directus_login.py          # Testes de autenticação
├── test_ui_processar_versao.py        # Testes de criação/processamento
├── test_ui_visualizar_modificacoes.py # CRÍTICO - Task 010
└── test_sdk_validacoes_dados.py       # Validações via SDK
```

## 🧪 Testes Implementados

### 1. Autenticação (`test_ui_directus_login.py`)
- ✅ Login com credenciais válidas
- ✅ Navegação para dashboard

### 2. Processamento (`test_ui_processar_versao.py`)
- ✅ Criar versão via formulário
- ✅ Upload de documento DOCX
- ✅ Aguardar processamento (polling)
- ✅ Validar status "concluído"

### 3. Visualização - **CRÍTICO** (`test_ui_visualizar_modificacoes.py`)
- ✅ Navegar para lista de modificações
- ✅ **Verificar campo `clausula` preenchido**
- ✅ **Validar nome da cláusula exibido (não apenas ID)**
- ✅ **Navegar de modificação → cláusula**
- ✅ Filtrar modificações por cláusula específica

### 4. Validações de Dados (`test_sdk_validacoes_dados.py`)
- ✅ Foreign keys válidos (`clausula_id` aponta para registro real)
- ✅ Consistência entre UI e banco
- ✅ Cobertura de 100% das modificações vinculadas

## 🔧 Configuração

### Variáveis de Ambiente

Arquivo `.env.e2e.ui` (criado automaticamente):

```bash
# Directus
DIRECTUS_URL=http://directus:8055
DIRECTUS_ADMIN_EMAIL=admin@test.local
DIRECTUS_ADMIN_PASSWORD=TestPassword123!
DIRECTUS_TOKEN=test-token-123

# API
API_URL=http://api-server:8001

# Postgres
POSTGRES_USER=directus
POSTGRES_PASSWORD=directus
POSTGRES_DB=directus_test

# Playwright
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_SLOW_MO=0
```

### Seed de Dados

O seed SQL cria automaticamente:
- 1 modelo de contrato "Modelo Teste Task 010"
- 10 cláusulas típicas (1.0 a 10.0)
- 1 usuário admin de teste
- Permissões configuradas

## 📊 Métricas de Sucesso

| Métrica | Meta | Atual |
|---------|------|-------|
| Coverage do fluxo crítico | 100% | - |
| Tempo de execução | < 5min | - |
| Taxa de falsos positivos | < 1% | - |
| Testes passando | 100% | - |

## 🐛 Troubleshooting

### Erro: "Connection refused" no Directus

```bash
# Verificar se Directus subiu
docker-compose -f docker-compose.ui-test.yml logs directus

# Aumentar timeout do healthcheck
# Editar docker-compose.ui-test.yml -> healthcheck.start_period
```

### Erro: "Element not found" no Playwright

```bash
# Rodar com browser visível para debug
pytest tests/e2e_ui/test_ui_*.py -v -s --headed --slowmo 1000

# Gerar trace para análise
pytest tests/e2e_ui/ --tracing=on
```

### Erro: Seed não aplicado

```bash
# Recriar banco do zero
docker-compose -f docker-compose.ui-test.yml down -v
make e2e-ui-test
```

### Testes lentos (> 10min)

```bash
# Rodar apenas validações SDK (sem UI)
pytest tests/e2e_ui/test_sdk_*.py -v

# Ou configurar Playwright headless
export PLAYWRIGHT_HEADLESS=true
```

## 📸 Screenshots e Evidências

Screenshots são salvos automaticamente em:
- `test-results/screenshots/` (em caso de falha)
- `test-results/traces/` (traces completos para replay)

Ver falha:
```bash
playwright show-trace test-results/traces/test-*.zip
```

## 🔗 Referências

- [Task 010](../../TASKS/task-010-processamento-de-versoes-nao-esta-relacionadno-a-claulua-a-modificacao.md)
- [Directus API Docs](https://docs.directus.io/reference/introduction/)
- [Playwright Python](https://playwright.dev/python/docs/intro)

## 📝 Notas de Implementação

### Por que Híbrido?

**Apenas Playwright:**
- ❌ Muito lento (5-10min por suite)
- ❌ Flaky (dependente de timing)
- ✅ Valida UI real

**Apenas SDK:**
- ✅ Rápido (< 2min)
- ✅ Determinístico
- ❌ Não valida UI

**Híbrido (escolhido):**
- ✅ Rápido (2-4min)
- ✅ Valida dados E interface
- ✅ Menor manutenção
- SDK para 80% (setup, validações)
- Playwright para 20% crítico (UI task-010)

### Limitações Conhecidas

1. **Não testa autenticação SSO**: Apenas login direto
2. **Não testa mobile**: Apenas desktop viewport
3. **Não testa múltiplos browsers**: Apenas Chromium
4. **Não testa acessibilidade**: Fora do escopo inicial

Essas limitações podem ser endereçadas em iterações futuras se necessário.
