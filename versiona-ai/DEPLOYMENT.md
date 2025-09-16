# 🚀 Deployment Versiona AI - Caprover

Este guia contém todas as instruções para fazer deploy da API Versiona AI usando Docker e Caprover.

## 📦 Build e Push da Imagem

### 1. Preparar ambiente local
```bash
cd versiona-ai/
cp .env.production .env  # Configurar variáveis de produção
```

### 2. Build e push automático
```bash
./build-and-push.sh
```

Este script irá:
- ✅ Fazer build da imagem Docker otimizada
- ✅ Taggar com versão timestamp e latest
- ✅ Fazer push para `docker-registry.de.vix.br`
- ✅ Limpar imagens antigas locais

## 🏗️ Deploy no Caprover

### Opção 1: Deploy via Registry (Recomendado)

1. **Criar nova app no Caprover**
   - Nome: `versiona-ai`
   - Tipo: `Deploy via ImageName`

2. **Configurar imagem**
   ```
   docker-registry.de.vix.br/versiona-ai:latest
   ```

3. **Configurar variáveis de ambiente**
   ```
   DIRECTUS_BASE_URL=https://contract.devix.co
   DIRECTUS_TOKEN=seu_token_aqui
   FLASK_PORT=8001
   FLASK_ENV=production
   FLASK_DEBUG=false
   ```

4. **Configurar porta**
   - Container Port: `8001`
   - Enable HTTPS: ✅

### Opção 2: Deploy via Dockerfile

1. **Fazer upload do código**
   - Fazer zip da pasta `versiona-ai/`
   - Upload no Caprover com `captain-definition`

2. **Configurar variáveis antes do deploy**

## 🔧 Configurações do Caprover

### Variáveis de Ambiente Obrigatórias
```bash
DIRECTUS_BASE_URL=https://contract.devix.co
DIRECTUS_TOKEN=seu_token_directus_aqui
```

### Variáveis Opcionais
```bash
FLASK_PORT=8001
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=sua_chave_secreta_aqui
LOG_LEVEL=INFO
```

### Health Check
- **URL**: `/health`
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3

## 📊 Monitoramento

### Endpoints importantes
- `GET /health` - Status da aplicação
- `GET /api/versoes` - Lista de versões
- `GET /version/{id}` - Visualizar versão específica

### Logs
```bash
# Ver logs no Caprover
captain logs versiona-ai --follow

# Ou via Docker
docker logs versiona-ai --follow
```

## 🔄 Atualizações

### Update via Registry
1. Fazer build local: `./build-and-push.sh`
2. No Caprover: clicar em "Force Update"

### Update via Git
1. Fazer push do código
2. Re-deploy via upload no Caprover

## 🐛 Troubleshooting

### Problema: Container não inicia
- ✅ Verificar variáveis de ambiente
- ✅ Verificar logs do container
- ✅ Testar conexão com Directus

### Problema: Health check falhando
- ✅ Verificar se porta 8001 está correta
- ✅ Testar endpoint `/health` manualmente
- ✅ Verificar network do Caprover

### Problema: Erro de conexão Directus
- ✅ Validar `DIRECTUS_TOKEN`
- ✅ Verificar conectividade com `https://contract.devix.co`
- ✅ Testar endpoint `/api/connect`

## 📋 Checklist de Deploy

- [ ] Build da imagem executado com sucesso
- [ ] Push para registry concluído
- [ ] App criada no Caprover
- [ ] Variáveis de ambiente configuradas
- [ ] Health check funcionando
- [ ] HTTPS habilitado
- [ ] DNS configurado (se necessário)
- [ ] Logs sem erros
- [ ] Endpoints principais testados

## 🎯 URLs de Produção

Após deploy bem-sucedido:

- **Health Check**: `https://versiona-ai.devix.co/health`
- **API Versões**: `https://versiona-ai.devix.co/api/versoes`
- **Exemplo**: `https://versiona-ai.devix.co/version/c2b1dfa0-c664-48b8-a5ff-84b70041b428`

---

## 📞 Suporte

Em caso de problemas:
1. Verificar logs do container
2. Testar health check
3. Validar configurações de rede
4. Contatar equipe DevOps Devix
