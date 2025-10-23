# 📊 API Endpoints: Parâmetro Mock Implementado

## 🎯 Resumo da Implementação

Agora **TODOS** os endpoints da API suportam o parâmetro `mock` para alternar entre dados simulados e reais:

### ✅ Endpoints Atualizados

#### 1. **POST /api/process** - Processamento de Versões

```bash
# Modo mock
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "versao_001", "mock": true}'

# Modo real (default)
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "10f99b61-dd4a-4041-9753-4fa88e359830", "mock": false}'
```

#### 2. **GET /api/versoes** - Lista de Versões

```bash
# Modo mock via query parameter
curl "http://localhost:8000/api/versoes?mock=true"

# Modo real (default)
curl "http://localhost:8000/api/versoes"
```

#### 3. **POST /api/versoes** - Lista de Versões (alternativo)

```bash
# Modo mock via JSON
curl -X POST http://localhost:8000/api/versoes \
  -H "Content-Type: application/json" \
  -d '{"mock": true}'

# Modo real
curl -X POST http://localhost:8000/api/versoes \
  -H "Content-Type: application/json" \
  -d '{"mock": false}'
```

## 📋 Comportamentos por Modo

### 🔧 Mock Mode (`mock=true`)

- **Versões Mock**: `versao_001`, `versao_002`
- **Dados**: Simulados, consistentes, ideais para demos
- **Performance**: Rápida, sem dependências externas
- **Uso**: Desenvolvimento, testes, apresentações

### 🔍 Real Mode (`mock=false` ou omitido)

- **Versões Reais**: IDs do Directus (ex: `10f99b61-dd4a-4041-9753-4fa88e359830`)
- **Dados**: Do Directus real, com arquivos DOCX
- **Performance**: Dependente da rede e Directus
- **Uso**: Produção, processamento real

## 🎭 Exemplos de Teste Completo

### Teste de Listagem

```bash
# 1. Listar versões mock
curl "http://localhost:8000/api/versoes?mock=true"
# Resposta: {"mode": "mock", "versoes": [...]}

# 2. Listar versões reais
curl "http://localhost:8000/api/versoes"
# Resposta: {"mode": "real", "versoes": [...]} ou erro se falhar
```

### Teste de Processamento

```bash
# 1. Processar mock
curl -X POST http://localhost:8000/api/process \
  -d '{"versao_id": "versao_001", "mock": true}'
# Resposta: {"mode": "mock", "id": "...", ...}

# 2. Processar real
curl -X POST http://localhost:8000/api/process \
  -d '{"versao_id": "10f99b61-dd4a-4041-9753-4fa88e359830", "mock": false}'
# Resposta: {"mode": "real", "id": "...", ...} ou erro se não encontrar
```

## 🔄 Fluxo de Trabalho Recomendado

### Para Desenvolvimento/Demo:

1. Use `mock=true` para dados consistentes
2. IDs mock: `versao_001`, `versao_002`
3. Dados sempre disponíveis

### Para Produção:

1. Use `mock=false` (ou omita)
2. IDs reais do Directus
3. Processamento completo de arquivos

## 🛡️ Tratamento de Erros

### Mock Mode:

- ❌ ID inexistente → `"Versão mock {id} não encontrada"`
- ✅ Sempre funciona para IDs válidos

### Real Mode:

- ❌ Directus indisponível → `"Versão {id} não encontrada no Directus (HTTP {code})"`
- ❌ ID inexistente → `"Versão {id} não encontrada no Directus (HTTP 404)"`
- ✅ Processamento completo quando disponível

## 📈 Status da Implementação

- ✅ **Parâmetro mock** em todos endpoints
- ✅ **Consistência** entre endpoints
- ✅ **Flexibilidade** GET vs POST
- ✅ **Indicador de modo** na resposta
- ✅ **Tratamento de erros** claro
- ✅ **Separação limpa** mock vs real
- ✅ **Documentação completa**

## 🎉 Resultado Final

O sistema agora oferece **total flexibilidade** para alternar entre dados mock e reais em todos os endpoints, mantendo comportamento consistente e previsível!
