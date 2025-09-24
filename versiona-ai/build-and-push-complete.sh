#!/bin/bash

# Script para build e push da imagem completa (Frontend + API) para CapRover
set -e

# Configurações
REGISTRY="docker-registry.de.vix.br"
IMAGE_NAME="versiona-ai-complete"
TAG="$(date +%Y%m%d-%H%M%S)"

echo "🔨 Iniciando build da imagem completa para CapRover..."
echo "📋 Registry: $REGISTRY"
echo "📋 Imagem: $IMAGE_NAME"
echo "📋 Tag: $TAG"

# Limpar imagens antigas locais para economizar espaço
echo "🧹 Limpando imagens antigas..."
docker image prune -f

# Build da imagem multi-stage
echo "🔨 Fazendo build da imagem..."
docker build \
  --platform linux/amd64 \
  -f Dockerfile.caprover \
  -t $REGISTRY/$IMAGE_NAME:$TAG \
  -t $REGISTRY/$IMAGE_NAME:latest \
  .

echo "✅ Build concluído!"

# Push para o registry
echo "📤 Fazendo push para o registry..."
docker push $REGISTRY/$IMAGE_NAME:$TAG
docker push $REGISTRY/$IMAGE_NAME:latest

echo "✅ Push concluído!"

# Mostrar informações da imagem
echo "📊 Informações da imagem:"
docker images $REGISTRY/$IMAGE_NAME

echo ""
echo "🎉 Build e push concluídos com sucesso!"
echo "📋 Imagem disponível em: $REGISTRY/$IMAGE_NAME:$TAG"
echo "📋 Imagem latest: $REGISTRY/$IMAGE_NAME:latest"
echo ""
echo "💡 Para usar no CapRover:"
echo "   - Imagem Docker: $REGISTRY/$IMAGE_NAME:latest"
echo "   - Porta do Container: 80"
echo "   - Health Check Path: /health"
echo ""
