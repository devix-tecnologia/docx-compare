#!/bin/bash
# Script de build e push para Docker Registry Devix
# Versiona AI - Sistema de Comparação de Documentos

set -e

# Configurações
REGISTRY="docker-registry.de.vix.br"
IMAGE_NAME="versiona-ai"
VERSION=$(date +%Y%m%d-%H%M%S)
LATEST_TAG="latest"

echo "🚀 Iniciando build da imagem Docker..."
echo "📦 Registry: ${REGISTRY}"
echo "🏷️  Imagem: ${IMAGE_NAME}"
echo "🔖 Versão: ${VERSION}"

# Build da imagem
echo "🔨 Executando docker build..."
docker build \
    --tag "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
    --tag "${REGISTRY}/${IMAGE_NAME}:${LATEST_TAG}" \
    --platform linux/amd64 \
    -f ../Dockerfile \
    ..

# Verificar se o build foi bem-sucedido
if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso!"
else
    echo "❌ Erro no build da imagem"
    exit 1
fi

# Push para o registry
echo "📤 Fazendo push para o registry..."
docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker push "${REGISTRY}/${IMAGE_NAME}:${LATEST_TAG}"

if [ $? -eq 0 ]; then
    echo "✅ Push concluído com sucesso!"
    echo ""
    echo "🎉 Imagem disponível em:"
    echo "   ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    echo "   ${REGISTRY}/${IMAGE_NAME}:${LATEST_TAG}"
    echo ""
    echo "📋 Para usar no CapRover:"
    echo "   Imagem Específica: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    echo "   Imagem Latest: ${REGISTRY}/${IMAGE_NAME}:latest"
    echo "   Porta: 8001"
    echo "   Health Check: /health"
else
    echo "❌ Erro no push da imagem"
    exit 1
fi

# Limpar imagens locais antigas (opcional)
echo "🧹 Limpando imagens locais antigas..."
docker images "${REGISTRY}/${IMAGE_NAME}" --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | tail -n +2 | head -n -2 | awk '{print $1}' | xargs -r docker rmi || true

echo "🎯 Deploy script concluído!"
