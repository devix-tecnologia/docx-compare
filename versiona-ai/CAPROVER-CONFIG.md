# Configuração Caprover - Versiona AI

## ⚙️ Variáveis de Ambiente

```bash
# === OBRIGATÓRIAS ===
DIRECTUS_BASE_URL=https://contract.devix.co
DIRECTUS_TOKEN=seu_token_directus_aqui

# === OPCIONAIS ===
FLASK_PORT=8001
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=sua_chave_secreta_segura
LOG_LEVEL=INFO
```

## 🐳 Imagem Docker
```
docker-registry.de.vix.br/versiona-ai:latest
```

## 🌐 Configuração de Rede
- **Container Port**: 8001
- **Enable HTTPS**: ✅ Sim
- **Force HTTPS**: ✅ Sim

## 📊 Health Check
- **Path**: `/health`
- **Port**: 8001
- **Expected Response**: JSON com `"status": "ok"`

## 🔄 Deploy Steps

1. **Criar App no Caprover**
   - Nome: `versiona-ai`
   - Deploy via: `Deploy via ImageName`

2. **Configurar Imagem**
   ```
   docker-registry.de.vix.br/versiona-ai:latest
   ```

3. **Adicionar Variáveis de Ambiente**
   - Ir em "App Configs" → "Environment Variables"
   - Adicionar as variáveis listadas acima

4. **Ativar HTTPS**
   - Ir em "HTTP Settings"
   - Marcar "Enable HTTPS"
   - Marcar "Force HTTPS by redirecting all HTTP traffic to HTTPS"

5. **Deploy**
   - Clicar em "Deploy"
   - Aguardar container inicializar

## 🎯 URLs de Acesso

Após deploy bem-sucedido:

- **API Base**: `https://versiona-ai.sua-instancia.com`
- **Health Check**: `https://versiona-ai.sua-instancia.com/health`
- **Versões**: `https://versiona-ai.sua-instancia.com/api/versoes`
- **Exemplo**: `https://versiona-ai.sua-instancia.com/version/c2b1dfa0-c664-48b8-a5ff-84b70041b428`
