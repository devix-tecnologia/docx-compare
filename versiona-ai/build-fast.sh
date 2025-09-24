#!/bin/bash
# Build All-in-One Rápido - Usa frontend pré-buildado

set -e

REGISTRY="docker-registry.de.vix.br"
IMAGE_NAME="versiona-ai-allinone"
VERSION=$(date +%Y%m%d-%H%M%S)

echo "🚀 Build All-in-One RÁPIDO..."
echo "📦 Registry: ${REGISTRY}"
echo "🏷️  Imagem: ${IMAGE_NAME}"
echo "🔖 Versão: ${VERSION}"

# Build do diretório raiz
cd /Users/sidarta/repositorios/docx-compare

echo "🔨 Executando docker build rápido..."
docker build \
    --platform linux/amd64 \
    -f versiona-ai/Dockerfile.simple-allinone \
    -t "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
    -t "${REGISTRY}/${IMAGE_NAME}:latest" \
    .

if [ $? -eq 0 ]; then
    echo "✅ Build concluído!"

    # Push
    echo "📤 Push para registry..."
    docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    docker push "${REGISTRY}/${IMAGE_NAME}:latest"

    echo "🎉 All-in-One disponível:"
    echo "   ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    echo "   ${REGISTRY}/${IMAGE_NAME}:latest"
    echo ""
    echo "🚀 Para CapRover:"
    echo "   Imagem: ${REGISTRY}/${IMAGE_NAME}:latest"
    echo "   Porta: 80"
    echo "   Health Check: /health"

else
    echo "❌ Erro no build"
    exit 1
fi
