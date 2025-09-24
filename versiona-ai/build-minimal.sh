#!/bin/bash
# Build Minimal All-in-One - Baseado na API existente

set -e

REGISTRY="docker-registry.de.vix.br"
IMAGE_NAME="versiona-ai-minimal"
VERSION=$(date +%Y%m%d-%H%M%S)

echo "⚡ Build MINIMAL All-in-One..."
echo "📦 Registry: ${REGISTRY}"
echo "🏷️  Imagem: ${IMAGE_NAME}"
echo "🔖 Versão: ${VERSION}"

cd /Users/sidarta/repositorios/docx-compare

echo "🔨 Build super rápido usando imagem base existente..."
docker build \
    --platform linux/amd64 \
    -f versiona-ai/Dockerfile.minimal \
    -t "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
    -t "${REGISTRY}/${IMAGE_NAME}:latest" \
    .

if [ $? -eq 0 ]; then
    echo "✅ Build concluído!"

    echo "📤 Push para registry..."
    docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    docker push "${REGISTRY}/${IMAGE_NAME}:latest"

    echo ""
    echo "🎉 ALL-IN-ONE PRONTO:"
    echo "   ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    echo "   ${REGISTRY}/${IMAGE_NAME}:latest"
    echo ""
    echo "🚀 Para CapRover:"
    echo "   Imagem: ${REGISTRY}/${IMAGE_NAME}:latest"
    echo "   Porta: 80"
    echo "   Health Check: /health"
    echo ""
    echo "🌐 Rotas:"
    echo "   / → Frontend Vue.js"
    echo "   /api/* → Backend Python"
    echo "   /health → Health check"

else
    echo "❌ Erro no build"
    exit 1
fi
