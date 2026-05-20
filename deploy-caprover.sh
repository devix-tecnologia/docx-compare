#!/bin/bash

# Script de Deploy para CapRover
# Lê configurações do arquivo .env

set -e  # Sair se houver erro

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploy para CapRover${NC}"
echo ""

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    exit 1
fi

# Carregar variáveis do .env
export $(grep -v '^#' .env | xargs)

# Verificar variáveis obrigatórias
if [ -z "$CAPROVER_URL" ]; then
    echo -e "${RED}❌ CAPROVER_URL não definida no .env${NC}"
    exit 1
fi

if [ -z "$CAPROVER_APP_NAME" ]; then
    echo -e "${RED}❌ CAPROVER_APP_NAME não definida no .env${NC}"
    exit 1
fi

if [ -z "$CAPROVER_APP_TOKEN" ]; then
    echo -e "${RED}❌ CAPROVER_APP_TOKEN não definida no .env${NC}"
    exit 1
fi

if [ "$CAPROVER_APP_TOKEN" = "seu_token_aqui" ] || [ "$CAPROVER_APP_TOKEN" = "your-caprover-app-token-here" ]; then
    echo -e "${RED}❌ Configure o CAPROVER_APP_TOKEN no arquivo .env${NC}"
    echo -e "${YELLOW}💡 Obtenha o token em: $CAPROVER_URL${NC}"
    exit 1
fi

# Nome base da imagem (sem tag)
DOCKER_IMAGE_BASE="docker-registry.de.vix.br/versiona-ai-complete"
DOCKER_IMAGE_DEFAULT="${DOCKER_IMAGE_BASE}:latest"

echo -e "${BLUE}📦 Configuração:${NC}"
echo -e "  URL: $CAPROVER_URL"
echo -e "  App: $CAPROVER_APP_NAME"
echo -e "  Registry: $DOCKER_IMAGE_BASE"
echo ""

# Variável para armazenar a imagem final a ser deployada
DEPLOY_IMAGE="$DOCKER_IMAGE_DEFAULT"

# Perguntar se deve fazer build antes
read -p "$(echo -e ${YELLOW}🔨 Fazer build da imagem antes? [s/N]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${BLUE}🔨 Buildando imagem...${NC}"
    echo ""

    # Executar build e capturar output em arquivo temporário
    BUILD_LOG=$(mktemp)

    # Executar build mostrando output em tempo real E salvando em arquivo
    ./versiona-ai/build-and-push-complete.sh 2>&1 | tee "$BUILD_LOG"
    BUILD_EXIT_CODE=${PIPESTATUS[0]}

    echo ""

    if [ $BUILD_EXIT_CODE -ne 0 ]; then
        echo -e "${RED}❌ Erro no build! Exit code: $BUILD_EXIT_CODE${NC}"
        echo -e "${RED}❌ Abortando deploy.${NC}"
        rm -f "$BUILD_LOG"
        exit 1
    fi

    # Extrair a versão gerada do output (linha que contém "Tag: ")
    BUILD_VERSION=$(grep "📋 Tag:" "$BUILD_LOG" | awk '{print $3}')

    # Limpar arquivo temporário
    rm -f "$BUILD_LOG"

    if [ -n "$BUILD_VERSION" ]; then
        # Construir o nome completo da imagem com a versão específica
        DEPLOY_IMAGE="${DOCKER_IMAGE_BASE}:${BUILD_VERSION}"
        echo -e "${GREEN}✅ Imagem buildada: $DEPLOY_IMAGE${NC}"
    else
        echo -e "${YELLOW}⚠️  Não foi possível detectar a versão, usando: $DOCKER_IMAGE_DEFAULT${NC}"
        DEPLOY_IMAGE="$DOCKER_IMAGE_DEFAULT"
    fi
    echo ""
fi

# Fazer deploy
echo -e "${BLUE}🚀 Iniciando deploy...${NC}"
echo -e "  Imagem: ${DEPLOY_IMAGE}"
echo ""

caprover deploy \
  --caproverUrl "$CAPROVER_URL" \
  --appToken "$CAPROVER_APP_TOKEN" \
  --imageName "$DEPLOY_IMAGE" \
  --appName "$CAPROVER_APP_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Endpoints:${NC}"
    APP_URL=$(echo "$CAPROVER_URL" | sed 's/captain\.//')
    APP_URL="${APP_URL/https:\/\//https://$CAPROVER_APP_NAME.}"
    echo -e "  Health: ${APP_URL}/health"
    echo -e "  Frontend: ${APP_URL}/"
    echo -e "  API: ${APP_URL}/api/"
else
    echo ""
    echo -e "${RED}❌ Deploy falhou!${NC}"
    exit 1
fi
