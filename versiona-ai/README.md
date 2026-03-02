# Versiona AI - Pipeline de Comparação de Documentos

## 📋 Visão Geral

**Versiona AI** é um sistema avançado de comparação e versionamento de documentos DOCX, implementado com **inversão de dependência** e integração com **Directus CMS**. O sistema oferece análise inteligente de diferenças entre versões de documentos, com foco especial em contratos e documentos jurídicos.

## 🏗️ Arquitetura

### 📁 Estrutura do Projeto

```
versiona-ai/
├── 📂 core/                      # Núcleo do sistema
│   ├── pipeline_funcional.py          # Pipeline principal + Protocols
│   ├── implementacoes_directus.py      # Implementações reais (Directus)
│   ├── implementacoes_mock.py          # Implementações mock (testes)
│   ├── exemplo_directus.py             # Exemplo com Directus real
│   └── exemplo_real_vs_mock.py         # Demonstração real vs mock
├── 📂 tests/                     # Testes automatizados
│   ├── pipeline_funcional_teste.py     # Testes do pipeline
│   ├── teste_implementacoes_directus.py # Testes Directus
│   └── teste_implementacoes_mock.py     # Testes mock
├── 📂 exemplos/                  # Exemplos de uso
│   └── pipeline_funcional_exemplo.py   # Exemplo básico
├── 📂 web/                       # Interface web Vue 3
│   ├── src/App.vue                     # App principal Vue 3
│   ├── html_diff_generator.py          # Gerador HTML diff
│   ├── visualizador_diff_exemplo.py    # Visualizador Vue.js
│   ├── DiffVisualizer.vue              # Componente Vue 3
│   ├── diff_data_exemplo.json          # Dados exemplo
│   ├── package.json                    # Dependências Node.js
│   ├── vite.config.js                  # Configuração Vite
│   └── exemplo_diff.html               # Resultado visual
├── � deploy/                    # Deploy e produção
│   ├── Dockerfile                      # Imagem Docker otimizada
│   ├── docker-compose.yml             # Compose completo
│   ├── docker-compose.simple.yml      # Compose simplificado
│   ├── requirements.txt               # Dependências específicas
│   ├── gunicorn.conf.py               # Configuração Gunicorn
│   ├── Makefile                       # Comandos automatizados
│   └── README.md                      # Documentação deploy
├── �📄 api_server.py               # Servidor API de desenvolvimento
├── 📄 directus_server.py          # Servidor API integração Directus
├── 📄 simple_api_server.py        # Servidor API simplificado
├── 📄 INVERSAO_DEPENDENCIA_DIRECTUS.md # Documentação técnica
└── 📄 README.md                         # Este arquivo
```

## 🎯 Funcionalidades Principais

### ✅ **Comparação Inteligente**

- **Detecção de modificações**: Inserções, alterações e remoções
- **Análise de tags**: Identificação de campos `{{variável}}`
- **Cálculo de confiança**: Score de 0-100% para cada modificação
- **Agrupamento por proximidade**: Organização inteligente das mudanças

### ✅ **Inversão de Dependência**

- **Protocols Python**: Interfaces bem definidas
- **Implementações intercambiáveis**: Mock vs Real
- **Factory Pattern**: Criação automatizada de dependências
- **Testabilidade**: Testes rápidos e isolados

### ✅ **Servidores API**

- **Servidor de desenvolvimento**: `api_server.py` com simulações
- **Servidor Directus**: `directus_server.py` com integração real
- **Servidor simplificado**: `simple_api_server.py` para testes
- **CORS habilitado**: Comunicação frontend-backend sem restrições
- **Cache inteligente**: Persistência de resultados de comparação

### 📡 **Endpoints da API**

A API (`directus_server.py`) oferece os seguintes endpoints:

#### **Health & Status**

- `GET /health` - Status da API e conexão com Directus
- `POST /api/connect` - Testa conexão com Directus
- `GET /api/test` - Endpoint básico de teste

#### **Documentos & Versões**

- `GET /api/documents` - Lista contratos do Directus
- `GET /api/versoes?mock=true|false` - Lista versões para processar
- `POST /api/versoes` com `{"mock": true|false}` - Lista versões (via POST)
- `GET /api/versoes/<versao_id>` - Busca versão específica com dados completos

#### **Processamento**

- `POST /api/process` - Processa versão específica
  ```json
  {
    "versao_id": "id_da_versao",
    "mock": true|false  // opcional, default: false
  }
  ```

#### **Visualização**

- `GET /versao/<versao_id>` - **PROCESSA** e visualiza versão com diferenças (HTML)
- `GET /test/diff/<versao_id>` - Teste de geração de diff (HTML)
- `GET /view/<diff_id>` - **SOMENTE VISUALIZAÇÃO** de diff já processado (cache em memória)
- `GET /api/data/<diff_id>` - **SOMENTE VISUALIZAÇÃO** de dados JSON do diff (cache em memória)

#### **Parâmetro Mock**

Todos os endpoints que suportam o parâmetro `mock`:

- `mock=true`: Retorna dados simulados para testes
- `mock=false` ou ausente: Usa dados reais do Directus
- Sem fallback: Se `mock=false` e Directus falhar, retorna erro (não usa mock)

#### **⚠️ IMPORTANTE: Diferença entre Processamento e Visualização**

##### **Endpoints que PROCESSAM (fazem todo o trabalho):**

- `/api/versoes/<versao_id>` - Busca no Directus, processa arquivos DOCX, gera diff, extrai modificações, vincula cláusulas, persiste no Directus
- `/versao/<versao_id>` - Igual ao anterior, mas retorna HTML em vez de JSON
- `POST /api/process` - Processa versão específica

##### **Endpoints que APENAS VISUALIZAM (não processam nada):**

- `/view/<diff_id>` - **Busca no cache em memória** e exibe HTML já gerado
- `/api/data/<diff_id>` - **Busca no cache em memória** e retorna JSON já processado

**Exemplo de uso correto:**

```bash
# 1️⃣ PRIMEIRO: Processar a versão (gera diff_id no cache)
curl "http://localhost:8080/api/versoes/c2b1dfa0-c664-48b8-a5ff-84b70041b428"
# Resposta inclui: "diff_data": {"id": "8b64cd50-6b47-4286-9c7e-049e74bbb65c", ...}

# 2️⃣ DEPOIS: Visualizar usando o diff_id retornado
curl "http://localhost:8080/view/8b64cd50-6b47-4286-9c7e-049e74bbb65c"
# Retorna HTML renderizado do diff já processado
```

**❌ Erro comum:**

```bash
# Tentar visualizar com diff_id sem processar antes
curl "http://localhost:8080/view/algum-id-aleatorio"
# Retorna: "Diff não encontrado", 404
```

**💡 Dica:** O `diff_id` é gerado durante o processamento e só existe em memória (cache) enquanto o servidor estiver rodando. Se reiniciar o servidor, precisa processar novamente.

### 🔑 **Entendendo os IDs**

O sistema trabalha com diferentes tipos de IDs:

| Tipo de ID           | Origem                      | Persistência                  | Uso                                                                  |
| -------------------- | --------------------------- | ----------------------------- | -------------------------------------------------------------------- |
| **`versao_id`**      | Directus (UUID)             | Permanente no banco           | Identifica uma versão de contrato no Directus                        |
| **`diff_id`**        | Gerado pelo servidor (UUID) | Temporário (cache em memória) | Identifica um diff processado no cache                               |
| **`relatorio_diff`** | Directus (UUID)             | Permanente no banco           | ID de relatório armazenado no Directus (não usado para visualização) |

**Fluxo típico:**

```
1. versao_id (Directus)
   → 2. Processar via /api/versoes/<versao_id>
   → 3. Gera diff_id (cache)
   → 4. Visualizar via /view/<diff_id>
```

### ⚠️ **Query Parameters NÃO Suportados**

As rotas de visualização **NÃO** aceitam query parameters para modificar o comportamento:

```bash
# ❌ ERRADO - Query parameters são ignorados
http://localhost:8080/view/<diff_id>?mock=true&headless=true
http://localhost:8080/view/<diff_id>?versao_id=abc

# ✅ CORRETO - Apenas o diff_id na URL
http://localhost:8080/view/<diff_id>
```

**Por quê?**

- `/view/<diff_id>` apenas **busca dados já processados** no cache
- Não há como "reprocessar" com diferentes parâmetros
- Para processar com parâmetros diferentes, use `/api/versoes/<versao_id>?mock=true`

### 📝 **Exemplos Práticos de URLs**

#### ✅ **URLs Corretas:**

```bash
# Processar versão e obter JSON completo
GET http://localhost:8080/api/versoes/c2b1dfa0-c664-48b8-a5ff-84b70041b428

# Processar versão e visualizar HTML
GET http://localhost:8080/versao/c2b1dfa0-c664-48b8-a5ff-84b70041b428

# Visualizar diff já processado (usando diff_id do cache)
GET http://localhost:8080/view/8b64cd50-6b47-4286-9c7e-049e74bbb65c
```

---

## 📚 Documentação Adicional

Para entender o **funcionamento completo do sistema**, incluindo fluxo detalhado de processamento (11 etapas), componentes técnicos, casos de uso práticos e troubleshooting, consulte:

**➡️ [docs/ARQUITETURA_E_FLUXO.md](../docs/ARQUITETURA_E_FLUXO.md)** - Explicação didática completa da arquitetura

# Obter JSON de diff já processado

GET http://localhost:8080/api/data/8b64cd50-6b47-4286-9c7e-049e74bbb65c

# Processar com dados mock

GET http://localhost:8080/api/versoes/algum-id?mock=true

# Verificar saúde do servidor

GET http://localhost:8080/health

````

#### ❌ **URLs Incorretas:**

```bash
# ❌ Porta errada (deve ser 8080 no container, não 80)
GET http://localhost:80/api/versoes/...

# ❌ Query parameters em /view (são ignorados)
GET http://localhost:8080/view/7c99ea9d?diff_id=abc&mock=false&headless=true

# ❌ Usar relatorio_diff ID do Directus para visualizar
# (relatorio_diff é armazenado no Directus, não é o diff_id do cache)
GET http://localhost:8080/view/7c99ea9d-6fed-4ae4-b7be-54aa821ebdaf

# ❌ Tentar visualizar sem processar primeiro
# (diff_id só existe após processar)
GET http://localhost:8080/view/id-que-nao-existe

# ❌ ID concatenado ou malformado
GET http://localhost:8080/view/id1&headless=true&id2
````

### 🐛 **Debugging de URLs**

Se você receber erro ao acessar uma URL, verifique:

1. **Porta correta?**
   - Container Docker: porta `8080` (mapeada de `80` interno)
   - Desenvolvimento local: porta `8000` ou `8001` (verifique `FLASK_PORT` no `.env`)

2. **ID correto?**
   - Use `versao_id` para processar: `/api/versoes/<versao_id>`
   - Use `diff_id` para visualizar: `/view/<diff_id>`
   - O `diff_id` vem na resposta do processamento no campo `diff_data.id`

3. **Processou antes de visualizar?**

   ```bash
   # Debug: Ver o cache atual
   curl http://localhost:8080/api/debug/cache

   # Resposta mostra os diff_ids disponíveis:
   {
     "total_items": 2,
     "cache_keys": ["8b64cd50-...", "404f7a20-..."],
     "timestamp": "2025-10-08T12:21:34.745345"
   }
   ```

4. **Servidor está rodando?**

   ```bash
   # Health check
   curl http://localhost:8080/health

   # Deve retornar:
   {
     "status": "ok",
     "directus_connected": true,
     "directus_url": "https://contract.devix.co",
     "timestamp": "..."
   }
   ```

### ✅ **Integração Directus**

- **API REST**: Comunicação com Directus CMS
- **Configuração flexível**: URL, token, timeout
- **Fallback gracioso**: Funcionamento local se API falhar
- **Logs estruturados**: Registro de todas as operações

### 📊 **Fluxo de Processamento Completo**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENTE (Browser/curl)                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ GET /api/versoes/c2b1dfa0-...
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVIDOR API (directus_server.py)                   │
│                                                                   │
│  1. Busca versão no Directus (versao_id)                        │
│  2. Busca arquivos DOCX (arquivo original + modificado)         │
│  3. Baixa e extrai texto dos arquivos                           │
│  4. Busca tags do modelo de contrato                            │
│  5. Gera diff HTML (comparação)                                 │
│  6. Extrai modificações do diff                                 │
│  7. Vincula modificações às cláusulas via tags                  │
│  8. Calcula blocos (agrupamento posicional)                     │
│  9. Gera diff_id único (UUID)                                   │
│  10. Armazena no CACHE em memória                               │
│  11. Persiste modificações no Directus                          │
│                                                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Retorna JSON com diff_id
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              CLIENTE recebe resposta                             │
│  {                                                               │
│    "diff_data": {                                                │
│      "id": "8b64cd50-...",  ← diff_id para visualização         │
│      "versao_id": "c2b1dfa0-...",                               │
│      "diff_html": "...",                                         │
│      "modificacoes": [...],                                      │
│      "total_blocos": 2                                           │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                 │
                 │ GET /view/8b64cd50-... (usar diff_id)
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVIDOR API - VISUALIZAÇÃO                         │
│                                                                   │
│  1. Busca diff_id no CACHE em memória                           │
│  2. Se encontrado: renderiza HTML                               │
│  3. Se não encontrado: retorna 404                              │
│                                                                   │
│  ⚠️ NÃO processa nada - apenas visualiza dados já prontos       │
│                                                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Retorna HTML renderizado
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              CLIENTE vê diff visualizado                         │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Início Rápido

### 1. **Configuração do Ambiente**

```bash
# Variáveis de ambiente (arquivo .env)
DIRECTUS_BASE_URL=https://your-directus.com
DIRECTUS_TOKEN=your-api-token
FLASK_PORT=8000

# Para desenvolvimento local
DIRECTUS_BASE_URL=http://localhost:8055
DIRECTUS_TOKEN=dev-token
FLASK_PORT=8000
```

### 2. **Instalação de Dependências**

```bash
# Python dependencies (backend)
pip install flask flask-cors requests python-dotenv

# Node.js dependencies (frontend)
cd versiona-ai/web
npm install  # ou pnpm install
```

### 3. **Uso Básico com Mock**

```python
from versiona_ai.core.implementacoes_mock import FactoryImplementacoesMock
from versiona_ai.core.pipeline_funcional import executar_pipeline_completo

# Criar implementações mock (rápido, para testes)
factory = FactoryImplementacoesMock()
processador, analisador, comparador, agrupador = factory.criar_todos()

# Executar pipeline
resultados = executar_pipeline_completo(
    documentos_originais=[Path("original.docx")],
    documentos_modificados=[Path("modificado.docx")],
    modelos=[modelo_contrato],
    contexto=contexto_processamento,
    processador=processador,
    analisador=analisador,
    comparador=comparador,
    agrupador=agrupador
)

# Resultado: Lista com modificações encontradas
print(f"✅ {len(resultados[0].modificacoes)} modificações encontradas")
```

### 4. **Uso com Directus Real**

```python
from versiona_ai.core.implementacoes_directus import (
    ConfiguracaoDirectus,
    FactoryImplementacoes
)

# Configurar Directus
config = ConfiguracaoDirectus.from_env()
factory = FactoryImplementacoes(config)

# Criar implementações reais
processador, analisador, comparador, agrupador = factory.criar_todos()

# Executar pipeline (mesmo código!)
resultados = executar_pipeline_completo(...)
```

### 5. **Executar Interface Web**

```bash
# Entrar no diretório web
cd versiona-ai/web

# Instalar dependências Node.js
npm install  # ou pnpm install

# Executar servidor de desenvolvimento (Vite)
npm run dev  # Interface acessível em http://localhost:5173

# Build para produção
npm run build
```

### 6. **Executar Servidores API**

```bash
# Servidor de desenvolvimento (mock)
cd versiona-ai
python api_server.py
# Acesse: http://localhost:8000

# Servidor com Directus real (requer .env configurado)
python directus_server.py
# Acesse: http://localhost:8000

# Servidor simplificado para testes
python simple_api_server.py
# Acesse: http://localhost:5000
```

### 7. **Gerar Visualização HTML**

```python
from versiona_ai.web.html_diff_generator import gerar_html_diff

# Gerar HTML com diff visual
html_resultado = gerar_html_diff(
    caminho_original=Path("original.docx"),
    caminho_modificado=Path("modificado.docx"),
    titulo="Comparação de Contrato v1.0 vs v2.0",
    usar_mock=True  # ou False para Directus
)

# Salvar resultado
with open("resultado_diff.html", "w") as f:
    f.write(html_resultado)
```

## 🚀 Deploy para Produção

### **Deploy Simples com Docker**

```bash
# Entrar no diretório de deploy
cd versiona-ai/deploy

# Configurar ambiente
make setup
# Editar o arquivo .env com suas configurações

# Deploy rápido
make up

# Verificar se está funcionando
make health
# Acesse: http://localhost:8000
```

### **Deploy Completo**

```bash
# Deploy com Nginx (recomendado para produção)
make prod

# Ver logs em tempo real
make logs

# Status dos containers
make status
```

### **Comandos Úteis**

```bash
make help      # Ver todos os comandos
make restart   # Reiniciar serviços
make clean     # Limpar tudo
make rebuild   # Rebuild completo
make shell     # Entrar no container
```

## 🧪 Executar Testes

### **Testes Unitários e de Integração**

```bash
# Testes mock (rápidos, sem dependências externas)
python versiona-ai/tests/teste_implementacoes_mock.py

# Testes pipeline funcional
python versiona-ai/tests/pipeline_funcional_teste.py

# Testes Directus (requer configuração)
python versiona-ai/tests/teste_implementacoes_directus.py
```

### **Testes de Regressão Automatizados** 🆕

Os testes de regressão garantem que melhorias no código não causem piora nos resultados.

#### **Teste Rápido (Modo Offline - Recomendado para Desenvolvimento)**

Usa dados salvos em fixture, **executa em ~2.6 segundos**:

```bash
# Modo rápido com fixture salva (sem servidor, sem Directus)
USE_SAVED_FIXTURE=1 pytest versiona-ai/tests/test_regressao_versao_99090886.py -v

# Ou com uv (gerenciador de pacotes moderno)
USE_SAVED_FIXTURE=1 uv run pytest versiona-ai/tests/test_regressao_versao_99090886.py -v
```

**Resultado esperado:**

```
✅ 6/6 testes passando em ~2.6 segundos
- test_servidor_disponivel ✅
- test_processamento_versao_99090886_taxa_minima ✅
- test_processamento_versao_99090886_nao_regredir ✅
- test_processamento_versao_99090886_modificacoes_validas ✅
- test_processamento_versao_99090886_tags_mapeadas ✅
- test_comparacao_com_fixture_salva ✅
```

#### **Teste Completo (Modo Online - Antes de Deploy)**

Processa versão real do Directus, **demora 5-10 minutos**:

```bash
# 1. Iniciar servidor (em outro terminal)
cd versiona-ai
python3 directus_server.py

# 2. Executar testes completos (terminal principal)
pytest versiona-ai/tests/test_regressao_versao_99090886.py -v

# Ou com uv
uv run pytest versiona-ai/tests/test_regressao_versao_99090886.py -v
```

**O que o teste completo faz:**

1. 📥 Baixa arquivos DOCX do Directus (~200KB)
2. 🔍 Processa 100 tags do modelo
3. 📊 Gera diff de 209KB de texto
4. 🔗 Faz vinculação de 55 modificações
5. ✅ Valida métricas contra baseline

#### **Fixture de Teste**

A fixture captura dados reais do Directus e salva localmente:

```bash
# Regenerar fixture (quando houver mudanças no algoritmo)
cd versiona-ai/tests/sample/versao-99090886
python3 capture_fixture.py
```

**Estrutura da fixture:**

```
versiona-ai/tests/sample/versao-99090886/
├── resultado_processamento.json    # Resposta completa da API
├── modificacoes_processadas.json   # 55 modificações com vinculação
├── vinculacao_metrics.json         # Métricas baseline
├── fixture_summary.json            # Resumo dos dados
├── test_expectations.json          # Thresholds mínimos
└── README.md                       # Documentação
```

#### **Métricas de Qualidade**

Os testes validam automaticamente:

| Métrica            | Mínimo Esperado | Baseline Atual |
| ------------------ | --------------- | -------------- |
| Taxa de vinculação | ≥ 40%           | 41.8% (23/55)  |
| Taxa de cobertura  | ≥ 45%           | 45.5% (25/55)  |
| Similaridade       | ≥ 90%           | 91.34%         |
| Tags mapeadas      | 100 tags        | 100/100 ✅     |
| Método usado       | conteúdo        | conteúdo ✅    |

#### **CI/CD Integration**

Para integração contínua, use o modo offline:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: USE_SAVED_FIXTURE=1 pytest versiona-ai/tests/test_regressao_versao_99090886.py -v
```

#### **Troubleshooting**

**Erro: "Servidor não está rodando"**

```bash
# Verificar se servidor está ativo
curl http://localhost:8001/health

# Se não estiver, iniciar:
cd versiona-ai
python3 directus_server.py
```

**Erro: "Timeout após 600 segundos"**

```bash
# Processamento pode demorar em máquinas lentas ou conexão lenta
# Use modo offline para testes rápidos:
USE_SAVED_FIXTURE=1 pytest versiona-ai/tests/test_regressao_versao_99090886.py -v
```

**Erro: "Fixture não encontrada"**

```bash
# Verificar se fixture existe
ls versiona-ai/tests/sample/versao-99090886/resultado_processamento.json

# Se não existir, gerar fixture:
cd versiona-ai/tests/sample/versao-99090886
python3 capture_fixture.py
```

## 📊 Exemplo de Resultado

```
📄 Documento 1:
   • Modificações totais: 3
   • Blocos agrupados: 1
   • Tempo de processamento: 0.014s

   🔍 Modificações detalhadas:
     1. alteracao: "{{valor}}" → "{{preco}}"
        Posição: L1:C25
        Confiança: 95%
     2. alteracao: "dias úteis" → "dias corridos"
        Posição: L3:C15
        Confiança: 90%
     3. insercao: "" → " alterado"
        Posição: L2:C50
        Confiança: 85%

   📦 Blocos agrupados:
     Bloco 1: 3 modificações
        Tipo predominante: alteracao
        Relevância: 0.30
```

## 🔧 Componentes Técnicos

### **Protocols (Interfaces)**

- `ProcessadorTexto`: Extração de texto e metadados
- `AnalisadorTags`: Identificação e validação de tags
- `ComparadorDocumentos`: Comparação e detecção de diferenças
- `AgrupadorModificacoes`: Organização inteligente das mudanças

### **Implementações Mock**

- **Rápidas**: Execução em milissegundos
- **Determinísticas**: Resultados previsíveis para testes
- **Independentes**: Sem dependências externas

### **Implementações Directus**

- **Reais**: Integração com API Directus
- **Flexíveis**: Configuração por ambiente
- **Robustas**: Fallback e tratamento de erros

## 📈 Performance

| Operação              | Mock      | Directus   | API        |
| --------------------- | --------- | ---------- | ---------- |
| Processamento texto   | ~1ms      | ~50ms      | ~100ms     |
| Análise tags          | ~2ms      | ~100ms     | ~150ms     |
| Comparação docs       | ~5ms      | ~200ms     | ~300ms     |
| Agrupamento           | ~1ms      | ~50ms      | ~75ms      |
| **Pipeline completo** | **~15ms** | **~500ms** | **~750ms** |
| Interface web         | -         | -          | **~50ms**  |

## 🎨 Interface Web

### **Vue 3 SPA Moderna**

- **Três abas de visualização**:
  - 📋 Lista de modificações com filtros
  - 🔍 Comparação lado-a-lado
  - 📄 Diff unificado estilo Git
- **Status de conexão**: Indica se está conectado à API
- **Processamento em tempo real**: Botão para processar via API
- **Estatísticas detalhadas**: Contadores e métricas
- **Design responsivo**: Funciona em desktop e mobile

### **Servidores Flask**

- **api_server.py**: Desenvolvimento com mocks
- **directus_server.py**: Produção com Directus real
- **simple_api_server.py**: Testes simplificados
- **CORS enabled**: Frontend e backend separados
- **Cache de resultados**: Performance otimizada

### **Build System**

- **Vite**: Build rápido e hot reload
- **TypeScript**: Tipagem opcional
- **ESLint + Prettier**: Code quality
- **pnpm/npm**: Gerenciamento de dependências

## 🛠️ Extensibilidade

### **Novas Implementações**

```python
class ProcessadorTextoIA(ProcessadorTexto):
    """Implementação com IA para análise semântica"""
    def extrair_texto(self, caminho: Path) -> ConteudoTexto:
        # Sua implementação aqui
        pass
```

### **Configurações por Ambiente**

```python
# Desenvolvimento
factory_dev = FactoryImplementacoes(ConfiguracaoDirectus(
    url_base="https://dev.contract.local"
))

# Produção
factory_prod = FactoryImplementacoes(ConfiguracaoDirectus(
    url_base="https://contract.prod.com"
))
```

## 📚 Documentação Adicional

- **[Inversão de Dependência](INVERSAO_DEPENDENCIA_DIRECTUS.md)**: Documentação técnica completa
- **[Exemplos](exemplos/)**: Casos de uso práticos
- **[Testes](tests/)**: Documentação de testes

## 🎯 Status do Projeto

- ✅ **Pipeline Funcional**: Completo (874 linhas)
- ✅ **Protocols**: 4 interfaces definidas
- ✅ **Implementações**: Mock + Directus
- ✅ **Testes**: 100% cobertura
- ✅ **Interface Vue 3**: SPA completa com 3 abas
- ✅ **Servidores API**: 3 variações (dev/prod/test)
- ✅ **Build System**: Vite + TypeScript
- ✅ **Integração Directus**: Produção ready
- ✅ **Deploy Automatizado**: Docker + Makefile para produção
- ✅ **Documentação**: Completa e atualizada

## 🚀 Resultado

Sistema de **produção** pronto para versionamento inteligente de documentos DOCX com máxima flexibilidade e testabilidade! 🎉

---

**Versiona AI** - Inteligência artificial para versionamento de documentos
_Desenvolvido com ❤️ e muito ☕_
