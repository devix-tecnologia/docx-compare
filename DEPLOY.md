# 🚀 Deploy para CapRover

Script automatizado para fazer deploy da aplicação no CapRover.

## 📋 Pré-requisitos

1. **CapRover CLI instalado:**

   ```bash
   npm install -g caprover
   ```

2. **Variáveis configuradas no `.env`:**

   ```bash
   CAPROVER_URL=https://captain.paas.node10.de.vix.br
   CAPROVER_APP_NAME=ignai-contract-ia
   CAPROVER_APP_TOKEN=seu_token_aqui
   ```

   > **Nota:** O script usa automaticamente a imagem `docker-registry.de.vix.br/versiona-ai-minimal:latest`
   > ou a versão específica gerada pelo build.

## 🔑 Como obter o App Token

1. Acesse: https://captain.paas.node10.de.vix.br/
2. Entre na aplicação `ignai-contract-ia`
3. Vá em **Deployment** → **App Token**
4. Clique em **Show Token**
5. Copie o token e adicione no `.env`

## 🚀 Como usar

### Deploy simples (sem rebuild):

```bash
./deploy-caprover.sh
```

O script irá perguntar se você quer fazer build antes. Digite `n` para não fazer build.

### Deploy com build automático:

Quando o script perguntar, digite `s` para fazer build antes do deploy.

Ou você pode fazer o build manualmente antes:

```bash
./versiona-ai/build-minimal.sh
./deploy-caprover.sh
```

## 📊 O que o script faz

1. ✅ Verifica se o arquivo `.env` existe
2. ✅ Carrega as variáveis de ambiente
3. ✅ Valida se todas as variáveis obrigatórias estão configuradas
4. ✅ Pergunta se deve fazer build da imagem
5. ✅ Se sim, faz build e **captura automaticamente a versão gerada** (ex: `20251008-100153`)
6. ✅ Usa a imagem específica buildada (ou `:latest` se não fez build)
7. ✅ Faz o deploy no CapRover usando o App Token
8. ✅ Mostra os endpoints da aplicação

### 🎯 Comportamento Inteligente

- **Com build (`s`)**: Usa a imagem específica que foi buildada (ex: `versiona-ai-minimal:20251008-100153`)
- **Sem build (`n`)**: Usa automaticamente `:latest` do registry

Isso garante que você sempre faz deploy da imagem que acabou de buildar, evitando inconsistências!

> **Imagem padrão:** `docker-registry.de.vix.br/versiona-ai-minimal:latest` > **Registry:** `docker-registry.de.vix.br`

## 🌐 Endpoints após deploy

- **Health Check**: https://ignai-contract-ia.paas.node10.de.vix.br/health
- **Frontend**: https://ignai-contract-ia.paas.node10.de.vix.br/
- **API**: https://ignai-contract-ia.paas.node10.de.vix.br/api/

## 🔧 Troubleshooting

### Erro: "CAPROVER_APP_TOKEN não definida"

Configure o token no arquivo `.env`:

```bash
CAPROVER_APP_TOKEN=seu_token_real_aqui
```

### Erro: "caprover: command not found"

Instale o CapRover CLI:

```bash
npm install -g caprover
```

### Erro no deploy

Verifique:

- ✅ Token está correto
- ✅ Imagem Docker existe no registry
- ✅ Aplicação existe no CapRover
- ✅ URL do CapRover está correta

## 📝 Exemplo de uso completo

```bash
# 1. Configure o token no .env
vim .env  # Adicione o CAPROVER_APP_TOKEN

# 2. Execute o deploy
./deploy-caprover.sh

# 3. Quando perguntar se quer fazer build, digite:
# - 's' para SIM (faz build + deploy)
# - 'n' para NÃO (só deploy)

# 4. Aguarde o deploy concluir
# ✅ Deploy concluído com sucesso!
```

## 🎯 Variáveis de ambiente no CapRover

Não esqueça de configurar no CapRover:

```
DIRECTUS_TOKEN=seu_token_directus
DIRECTUS_BASE_URL=https://contract.devix.co
FLASK_PORT=8001
```
