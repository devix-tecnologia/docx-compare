#!/bin/bash
# Script de build para versão All-in-One Segura
# Frontend + Backend + Nginx Proxy + Firewall

set -e

# Configurações
REGISTRY="docker-registry.de.vix.br"
IMAGE_NAME="versiona-ai-secure"
VERSION=$(date +%Y%m%d-%H%M%S)

echo "🔒 Iniciando build da versão All-in-One Segura..."
echo "📦 Registry: ${REGISTRY}"
echo "🏷️  Imagem: ${IMAGE_NAME}"
echo "🔖 Versão: ${VERSION}"

# Limpar cache
echo "🧹 Limpando cache..."
docker builder prune -f

# Build da imagem segura
echo "🔨 Executando docker build..."
docker build \
    --platform linux/amd64 \
    -f versiona-ai/Dockerfile.secure \
    -t "${REGISTRY}/${IMAGE_NAME}:${VERSION}" \
    -t "${REGISTRY}/${IMAGE_NAME}:latest" \
    .

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso!"
else
    echo "❌ Erro no build da imagem"
    exit 1
fi

# Push para registry
echo "📤 Fazendo push para o registry..."
docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker push "${REGISTRY}/${IMAGE_NAME}:latest"

if [ $? -eq 0 ]; then
    echo "✅ Push concluído com sucesso!"
    echo ""
    echo "🎉 Imagem All-in-One disponível em:"
    echo "   ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    echo "   ${REGISTRY}/${IMAGE_NAME}:latest"
    echo ""
    echo "🚀 Para usar no CapRover:"
    echo "   Imagem: ${REGISTRY}/${IMAGE_NAME}:latest"
    echo "   Porta: 80"
    echo "   Health Check: /health"
    echo ""
    echo "🔒 Recursos de Segurança:"
    echo "   ✅ Nginx proxy reverso"
    echo "   ✅ Rate limiting"
    echo "   ✅ Security headers"
    echo "   ✅ API interna (não exposta)"
    echo "   ✅ Frontend otimizado"
    echo "   ✅ Firewall configurado"
    echo ""
    echo "🌐 Rotas disponíveis:"
    echo "   / → Frontend Vue.js"
    echo "   /api/* → Backend Python (proxy)"
    echo "   /health → Health check"
else
    echo "❌ Erro no push da imagem"
    exit 1
fi

# Mostrar tamanho da imagem
echo "📊 Informações da imagem:"
docker images "${REGISTRY}/${IMAGE_NAME}:latest" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo "🎯 Build All-in-One concluído!"
