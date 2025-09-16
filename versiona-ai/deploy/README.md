# 🚀 Deploy do Versiona AI

Este diretório contém todos os arquivos necessários para fazer o deploy do **Versiona AI** em produção usando Docker.

## 📋 Estrutura

```
deploy/
├── 📄 Dockerfile              # Imagem Docker backend Python
├── 📄 Dockerfile.web          # Imagem Docker frontend Vue 3
├── 📄 docker-compose.yml      # Compose completo com Nginx
├── 📄 docker-compose.simple.yml # Compose simplificado
├── 📄 requirements.txt        # Dependências Python específicas
├── 📄 gunicorn.conf.py        # Configuração do Gunicorn
├── 📄 .env.example           # Exemplo de variáveis de ambiente
├── 📂 nginx/                 # Configuração do Nginx
│   └── nginx.conf            # Proxy reverso
└── 📄 README.md              # Este arquivo
```

## 🚀 Deploy Rápido

### 1. **Configurar Variáveis de Ambiente**

```bash
# Copiar e editar o arquivo de ambiente
cp .env.example .env

# Editar com suas configurações
nano .env
```

### 2. **Deploy Simplificado**

```bash
# Usar o compose simplificado (apenas a aplicação)
docker-compose -f docker-compose.simple.yml up -d

# Verificar se está rodando
docker-compose -f docker-compose.simple.yml ps

# Ver logs
docker-compose -f docker-compose.simple.yml logs -f
```

### 3. **Deploy Completo (com Nginx)**

```bash
# Usar o compose completo (aplicação + nginx)
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f versiona-ai
```

## 🔧 Configuração

### **Variáveis de Ambiente Obrigatórias**

```bash
# Directus
DIRECTUS_BASE_URL=https://seu-directus.com
DIRECTUS_TOKEN=seu-token-aqui

# Flask
FLASK_PORT=8000
FLASK_ENV=production
```

### **Portas Expostas**

| Serviço      | Porta | Descrição        |
| ------------ | ----- | ---------------- |
| Frontend Vue | 3000  | Interface web    |
| Backend API  | 8000  | API Flask        |
| Nginx        | 80    | Proxy (completo) |
| Nginx        | 443   | HTTPS (completo) |

## 📊 Monitoramento

### **Health Check**

```bash
# Verificar saúde da API
curl http://localhost:8000/health

# Verificar frontend
curl http://localhost:3000

# Com proxy completo
curl http://localhost/health

# Resposta esperada da API:
# {"status": "healthy", "timestamp": "..."}
```

### **Logs**

```bash
# Logs da API
docker-compose logs versiona-ai-api

# Logs do frontend
docker-compose logs versiona-ai-web

# Logs em tempo real
docker-compose logs -f versiona-ai-api
docker-compose logs -f versiona-ai-web

# Logs do sistema (API)
docker exec versiona-ai-api tail -f /app/logs/gunicorn_access.log
```

## 🛠️ Comandos Úteis

### **Gerenciamento do Container**

```bash
# Parar
docker-compose down

# Reiniciar
docker-compose restart

# Rebuild
docker-compose up -d --build

# Remover tudo
docker-compose down -v --remove-orphans
```

### **Debug**

```bash
# Entrar no container
docker exec -it versiona-ai-prod bash

# Ver variáveis de ambiente
docker exec versiona-ai-prod env

# Testar API internamente
docker exec versiona-ai-prod curl http://localhost:8000/health
```

## 📈 Performance

### **Configuração do Gunicorn**

- **Workers**: `CPU cores * 2 + 1`
- **Timeout**: 30 segundos
- **Max requests**: 1000 por worker
- **Keep-alive**: 2 segundos

### **Recursos Utilizados**

- **CPU**: ~0.5-1.0 core por worker
- **RAM**: ~100-200MB por worker
- **Disco**: Logs rotacionados (max 30MB)

## 🔒 Segurança

### **Boas Práticas Implementadas**

- ✅ **Usuário não-root**: Container roda como `appuser`
- ✅ **Imagem mínima**: Python 3.13-slim
- ✅ **Dependências fixadas**: Versões específicas
- ✅ **Logs limitados**: Rotação automática
- ✅ **Health checks**: Monitoramento automático

### **Configurações Recomendadas**

```bash
# Firewall (exemplo para Ubuntu)
sudo ufw allow 8000/tcp
sudo ufw enable

# Proxy reverso (Nginx externo recomendado)
# SSL/TLS com certificados válidos
# Rate limiting
```

## 🚨 Troubleshooting

### **Problemas Comuns**

| Problema                | Solução                                           |
| ----------------------- | ------------------------------------------------- |
| Port 8000 ocupado       | `docker-compose down` e verificar processos       |
| Token Directus inválido | Verificar `.env` e regenerar token                |
| Build falha             | Verificar conexão internet e limpar cache Docker  |
| Container não inicia    | Verificar logs: `docker-compose logs versiona-ai` |

### **Reset Completo**

```bash
# Parar tudo
docker-compose down -v

# Remover imagens
docker rmi $(docker images "versiona-ai*" -q)

# Rebuild completo
docker-compose up -d --build
```

## 🎯 Status

- ✅ **Dockerfile**: Otimizado para produção
- ✅ **Multi-stage build**: Frontend + Backend
- ✅ **Gunicorn**: Configurado para performance
- ✅ **Health checks**: Monitoramento automático
- ✅ **Logs**: Estruturados e rotacionados
- ✅ **Segurança**: Usuário não-root e deps fixadas

---

🚀 **Deploy pronto para produção!**

_Sistema Versiona AI containerizado e otimizado._
