#!/bin/bash

# =================================================================
# Script de inicialização rápida para testes E2E UI - Task 011
# =================================================================

set -e

echo "🎭 Testes E2E via Interface de Usuário - Task 011"
echo "=================================================="
echo ""

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    echo "   Por favor, inicie o Docker Desktop e tente novamente."
    exit 1
fi

echo "✅ Docker está rodando"
echo ""

# Verificar se arquivos necessários existem
if [ ! -f "docker-compose.ui-test.yml" ]; then
    echo "❌ Arquivo docker-compose.ui-test.yml não encontrado!"
    exit 1
fi

if [ ! -d "tests/e2e_ui" ]; then
    echo "❌ Diretório tests/e2e_ui não encontrado!"
    exit 1
fi

echo "✅ Arquivos necessários encontrados"
echo ""

# Perguntar ao usuário o que fazer
echo "Escolha uma opção:"
echo ""
echo "  1) 🎭 Executar todos os testes E2E UI (recomendado)"
echo "  2) 🎯 Executar apenas testes críticos Task 010"
echo "  3) 🚀 Subir apenas a infraestrutura (para debug manual)"
echo "  4) 🧹 Limpar ambiente E2E UI"
echo ""
read -p "Opção (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🎭 Executando todos os testes E2E UI..."
        echo "⏱️  Isso pode levar 5-10 minutos na primeira execução (build + testes)"
        echo ""
        make e2e-ui-test
        ;;
    2)
        echo ""
        echo "🎯 Executando testes críticos Task 010..."
        echo ""
        make e2e-ui-test-critical
        ;;
    3)
        echo ""
        echo "🚀 Subindo infraestrutura E2E UI..."
        echo ""
        make e2e-ui-up
        echo ""
        echo "✅ Infraestrutura rodando!"
        echo ""
        echo "Serviços disponíveis:"
        echo "  📊 Directus:  http://localhost:8065"
        echo "     Login:     admin@example.com / TestPassword123!"
        echo "  🔧 API:       http://localhost:8011/health"
        echo "  🐘 Postgres:  localhost:5442 (interno)"
        echo ""
        echo "Para executar testes manualmente:"
        echo "  make e2e-ui-shell"
        echo ""
        echo "Para derrubar:"
        echo "  make e2e-ui-down"
        ;;
    4)
        echo ""
        echo "🧹 Limpando ambiente E2E UI..."
        echo ""
        make e2e-ui-clean
        echo ""
        echo "✅ Limpeza concluída!"
        ;;
    *)
        echo ""
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "✅ Operação concluída!"
echo ""
echo "Comandos úteis:"
echo "  make e2e-ui-test        # Executar todos testes"
echo "  make e2e-ui-logs        # Ver logs"
echo "  make e2e-ui-test-report # Abrir relatório HTML"
echo "  make e2e-ui-down        # Derrubar ambiente"
echo ""
