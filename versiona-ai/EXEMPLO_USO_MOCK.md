# Guia de Uso: Parâmetro Mock na API de Processamento

## 📋 Visão Geral

A função de processamento agora aceita um parâmetro `mock` que permite alternar entre:

- **mock=true**: Dados simulados para demonstração
- **mock=false** (ou não informado): Processamento real de documentos do Directus

## 🔧 Como Usar

### Endpoint

```
POST /api/process
Content-Type: application/json
```

### 1. Modo Mock (Dados Simulados)

```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "versao_001", "mock": true}'
```

**Resultado:**

- Usa dados pré-definidos para demonstração
- Geração rápida de diff com conteúdo exemplo
- Ideal para testes e apresentações

### 2. Modo Real (Processamento Completo)

```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "versao_001", "mock": false}'
```

**Resultado:**

- Busca dados reais do Directus
- Baixa arquivos DOCX quando disponíveis
- Processa documentos usando `docx_utils.py`
- Fallback para dados baseados em metadados

### 3. Modo Padrão (Real por Default)

```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "versao_001"}'
```

**Resultado:** Mesmo comportamento que `mock=false`

## 📊 Diferenças na Resposta

### Campos Comuns

```json
{
  "id": "uuid-gerado",
  "versao_id": "versao_001",
  "versao_data": {...},
  "original": "texto original",
  "modified": "texto modificado",
  "diff_html": "html com diferenças",
  "created_at": "timestamp",
  "url": "http://localhost:8000/view/{id}",
  "mode": "mock" | "real"
}
```

### Campo Indicador

- `"mode": "mock"` - Dados simulados
- `"mode": "real"` - Processamento real

## 🎯 Casos de Uso

### Mock Mode (mock=true)

- ✅ Demonstrações e apresentações
- ✅ Testes de interface
- ✅ Desenvolvimento frontend
- ✅ Validação de API

### Real Mode (mock=false)

- ✅ Processamento produtivo
- ✅ Comparação de documentos reais
- ✅ Análise de diferenças de contratos
- ✅ Operação normal do sistema

## 🔄 Processamento Real: Fluxo Completo

1. **Busca no Directus**: Tenta obter versão com IDs dos arquivos
2. **Download**: Baixa arquivos DOCX do Directus
3. **Extração**: Usa `docx_utils.convert_docx_to_text()`
4. **Fallback**: Se falhar, usa conteúdo baseado em metadados
5. **Diff**: Gera comparação HTML completa

## 🛡️ Tratamento de Erros

- Falha na conexão Directus → Usa mock como fallback
- Arquivos não encontrados → Usa conteúdo baseado em metadados
- Erro na extração de texto → Fallback seguro
- Versão inexistente → Retorna erro claro

## 📈 Exemplo de Teste Completo

```bash
# Teste mock
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "versao_001", "mock": true}'

# Teste real
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "versao_001", "mock": false}'

# Visualizar resultado
curl "http://localhost:8000/view/{diff_id}"
```

## ✅ Status da Implementação

- ✅ Parâmetro `mock` implementado
- ✅ Modo mock funcional
- ✅ Modo real com fallbacks
- ✅ Processamento DOCX real
- ✅ Integração com `docx_utils.py`
- ✅ Indicador de modo na resposta
- ✅ Documentação completa
