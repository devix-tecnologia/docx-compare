#!/bin/bash

# Script para build e push apenas do Frontend para CapRover
set -e

# Configurações
REGISTRY="docker-registry.de.vix.br"
IMAGE_NAME="versiona-ai-frontend"
TAG="$(date +%Y%m%d-%H%M%S)"

echo "🔨 Iniciando build do Frontend para CapRover..."
echo "📋 Registry: $REGISTRY"
echo "📋 Imagem: $IMAGE_NAME"
echo "📋 Tag: $TAG"

# Limpar imagens antigas locais para economizar espaço
echo "🧹 Limpando imagens antigas..."
docker image prune -f

# Build da imagem do frontend
echo "🔨 Fazendo build do frontend..."
docker build \
  --platform linux/amd64 \
  -f Dockerfile.frontend \
  -t $REGISTRY/$IMAGE_NAME:$TAG \
  -t $REGISTRY/$IMAGE_NAME:latest \
  .

echo "✅ Build do frontend concluído!"

# Push para o registry
echo "📤 Fazendo push para o registry..."
docker push $REGISTRY/$IMAGE_NAME:$TAG
docker push $REGISTRY/$IMAGE_NAME:latest

echo "✅ Push concluído!"

# Mostrar informações da imagem
echo "📊 Informações da imagem:"
docker images $REGISTRY/$IMAGE_NAME

echo ""
echo "🎉 Build e push do frontend concluídos com sucesso!"
echo "📋 Frontend: $REGISTRY/$IMAGE_NAME:$TAG"
echo "📋 Frontend latest: $REGISTRY/$IMAGE_NAME:latest"
echo ""
echo "💡 Para usar no CapRover:"
echo "   - Imagem Docker: $REGISTRY/$IMAGE_NAME:latest"
echo "   - Porta do Container: 80"
echo "   - Configure proxy para /api/* → API externa"
echo ""
