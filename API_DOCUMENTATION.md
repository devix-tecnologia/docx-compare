# API de Comparação de Documentos DOCX

Esta API oferece um serviço para comparar documentos DOCX usando integração com Directus.

## 🚀 Instalação e Configuração

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
DIRECTUS_BASE_URL=https://your-directus-instance.com
DIRECTUS_TOKEN=your-directus-token-here
```

### 3. Executar a API
```bash
python api_server.py
```

A API estará disponível em `http://localhost:5000`

## 📊 Endpoints

### GET /health
Verifica se a API está funcionando.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-02T10:30:00.000Z",
  "service": "docx-compare-api"
}
```

### GET /config
Retorna a configuração atual da API.

**Resposta:**
```json
{
  "directus_base_url": "https://your-directus-instance.com",
  "results_directory": "results",
  "lua_filter_path": "comments_html_filter_direct.lua",
  "lua_filter_exists": true,
  "max_file_size_mb": 50.0
}
```

### POST /compare
Compara dois documentos DOCX usando IDs do Directus.

**Body (JSON):**
```json
{
  "original_file_id": "550e8400-e29b-41d4-a716-446655440000",
  "modified_file_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Resposta de Sucesso:**
```json
{
  "success": true,
  "result_url": "http://localhost:5000/results/comparison_result_uuid.html",
  "original_file": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "documento_original.docx",
    "size_bytes": 45632
  },
  "modified_file": {
    "id": "550e8400-e29b-41d4-a716-446655440001", 
    "filename": "documento_modificado.docx",
    "size_bytes": 47821
  },
  "statistics": {
    "total_additions": 8,
    "total_deletions": 6,
    "total_modifications": 3
  },
  "modifications": [
    {
      "original": "( ) Em caso de prestação de serviços",
      "modified": "( x ) Em caso de prestação de serviços"
    }
  ],
  "generated_at": "2025-09-02T10:30:00.000Z"
}
```

**Resposta de Erro:**
```json
{
  "success": false,
  "error": "Erro ao baixar arquivo do Directus: 404",
  "timestamp": "2025-09-02T10:30:00.000Z"
}
```

### GET /results/<filename>
Serve o arquivo HTML com o resultado da comparação.

## 🧪 Testando a API

Execute o script de teste:
```bash
python test_api.py
```

Ou use curl:
```bash
# Teste de saúde
curl http://localhost:5000/health

# Teste de comparação
curl -X POST http://localhost:5000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "original_file_id": "seu-uuid-original",
    "modified_file_id": "seu-uuid-modificado"
  }'
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `DIRECTUS_BASE_URL` | URL base do Directus | - |
| `DIRECTUS_TOKEN` | Token de acesso ao Directus | - |
| `RESULTS_DIR` | Diretório para salvar resultados | `results` |
| `LUA_FILTER_PATH` | Caminho do filtro Lua | `comments_html_filter_direct.lua` |
| `FLASK_HOST` | Host do Flask | `0.0.0.0` |
| `FLASK_PORT` | Porta do Flask | `5000` |
| `FLASK_DEBUG` | Modo debug | `True` |
| `MAX_FILE_SIZE` | Tamanho máximo de arquivo (bytes) | `52428800` (50MB) |

### Limitações

- Apenas arquivos `.docx` são suportados
- Tamanho máximo de arquivo: 50MB (configurável)
- Resultados são mantidos indefinidamente (considere implementar limpeza automática)

## 🚨 Tratamento de Erros

A API retorna os seguintes códigos de erro:

- `400` - Bad Request (payload inválido, UUID malformado)
- `404` - Not Found (arquivo não encontrado no Directus)
- `500` - Internal Server Error (erro de processamento)

## 🔐 Segurança

- Configure o token do Directus com permissões mínimas necessárias
- Em produção, use HTTPS
- Considere implementar rate limiting
- Valide e sanitize todas as entradas

## 📝 Exemplo de Uso

```python
import requests

# Comparar dois documentos
response = requests.post('http://localhost:5000/compare', json={
    'original_file_id': 'uuid-do-arquivo-original',
    'modified_file_id': 'uuid-do-arquivo-modificado'
})

if response.status_code == 200:
    result = response.json()
    print(f"Resultado disponível em: {result['result_url']}")
    print(f"Total de modificações: {result['statistics']['total_modifications']}")
else:
    print(f"Erro: {response.json()['error']}")
```
