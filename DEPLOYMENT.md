# 🚀 Deployment Guide - Processador Automático de Versões

Este guia mostra como fazer o deploy da aplicação usando Docker para produção.

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Acesso ao Directus configurado
- Pandoc instalado (já incluído na imagem Docker)

## 🐳 Deployment com Docker

### 1. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```bash
# Configurações do Directus
DIRECTUS_BASE_URL=https://contract.devix.co
DIRECTUS_TOKEN=your-actual-directus-token
DIRECTUS_EMAIL=your-email@company.com
DIRECTUS_PASSWORD=your-password

# Configurações da aplicação
CHECK_INTERVAL=60          # Intervalo entre verificações (segundos)
REQUEST_TIMEOUT=30         # Timeout das requisições HTTP (segundos)
VERBOSE_MODE=false         # Logs detalhados (true/false)
DRY_RUN=false             # Modo teste sem alterações (true/false)
```

### 2. Build e Deploy

#### Opção A: Docker Compose (Recomendado)

```bash
# Build e start
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Verificar status
curl http://localhost:5005/health
```

#### Opção B: Docker Manual

```bash
# Build da imagem
docker build -t docx-compare .

# Executar container
docker run -d \
  --name docx-compare-processor \
  -p 5005:5005 \
  --env-file .env \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/outputs:/app/outputs \
  --restart unless-stopped \
  docx-compare
```

### 3. Monitoramento

#### Endpoints Disponíveis

- **Health Check**: `GET http://localhost:5005/health`
- **Status**: `GET http://localhost:5005/status`
- **Resultados**: `GET http://localhost:5005/outputs/<filename>`

#### Verificar Status

```bash
# Health check
curl http://localhost:5005/health

# Status detalhado
curl http://localhost:5005/status

# Logs em tempo real
docker-compose logs -f docx-compare
```

## 🔧 Configurações de Produção

### Servidor WSGI

A aplicação usa **Gunicorn** como servidor WSGI para produção:

- **Workers**: `CPU cores * 2 + 1`
- **Timeout**: 300 segundos
- **Keep-alive**: 60 segundos
- **Max requests**: 1000 por worker

### Recursos da Aplicação

- **Processamento automático** em background
- **Encerramento gracioso** com sinais SIGTERM/SIGINT
- **Health checks** para monitoramento
- **Logs estruturados** para análise
- **Volumes persistentes** para resultados

### Variáveis de Ambiente Disponíveis

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DIRECTUS_BASE_URL` | - | URL base do Directus |
| `DIRECTUS_TOKEN` | - | Token de acesso ao Directus |
| `CHECK_INTERVAL` | 60 | Intervalo entre verificações (s) |
| `REQUEST_TIMEOUT` | 30 | Timeout HTTP (s) |
| `VERBOSE_MODE` | false | Logs detalhados |
| `DRY_RUN` | false | Modo teste sem alterações |
| `RESULTS_DIR` | results | Diretório de resultados |

## 🔒 Segurança

### Usuário Não-Root

A aplicação roda com usuário não-root (`appuser`) para segurança.

### Volumes

```bash
# Resultados persistentes
./results:/app/results

# Outputs acessíveis via web
./outputs:/app/outputs
```

### Health Checks

```bash
# Docker Compose inclui health check automático
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5005/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 📊 Monitoramento e Logs

### Logs Estruturados

```bash
# Ver logs em tempo real
docker-compose logs -f

# Logs de uma data específica
docker-compose logs --since "2024-01-01T00:00:00Z"

# Logs filtrados por nível
docker-compose logs | grep ERROR
```

### Métricas Disponíveis

A aplicação expõe métricas via endpoints:

- **Health**: Status geral da aplicação
- **Status**: Estado do processador e estatísticas
- **Resultados**: Acesso aos arquivos processados

## 🚀 Comandos Úteis

```bash
# Restart da aplicação
docker-compose restart

# Update da aplicação
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Limpeza
docker-compose down -v  # Remove volumes
docker system prune -a  # Limpeza geral

# Backup dos resultados
tar -czf backup-results-$(date +%Y%m%d).tar.gz results/
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro de conectividade com Directus**
   ```bash
   # Verificar configurações
   curl -H "Authorization: Bearer $DIRECTUS_TOKEN" $DIRECTUS_BASE_URL/items/versao?limit=1
   ```

2. **Container não inicia**
   ```bash
   # Verificar logs de inicialização
   docker-compose logs docx-compare
   ```

3. **Erro de permissões**
   ```bash
   # Verificar proprietário dos volumes
   chown -R 1000:1000 results/ outputs/
   ```

### Logs de Debug

Para debug detalhado, configure:

```bash
# No .env
VERBOSE_MODE=true
DRY_RUN=true  # Para teste sem alterações
```

## 🔄 Atualização

Para atualizar a aplicação:

```bash
# 1. Parar o serviço
docker-compose down

# 2. Atualizar código
git pull origin main

# 3. Rebuild e restart
docker-compose build --no-cache
docker-compose up -d

# 4. Verificar saúde
curl http://localhost:5005/health
```
