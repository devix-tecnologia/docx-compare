#!/bin/bash
# Script para testar webhooks do Directus localmente

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
API_URL="${API_URL:-https://ignai-contract-ia.paas.node10.de.vix.br}"
DIRECTUS_URL="${DIRECTUS_URL:-https://contract.devix.co}"

# Verificar se DIRECTUS_TOKEN está configurado
if [ -z "$DIRECTUS_TOKEN" ]; then
    echo -e "${RED}❌ DIRECTUS_TOKEN não está configurado!${NC}"
    echo "Execute: export DIRECTUS_TOKEN='seu-token-aqui'"
    exit 1
fi

echo -e "${BLUE}🧪 Script de Teste de Webhooks${NC}"
echo "=================================="
echo ""

# Função para testar webhook de modelo
test_modelo_webhook() {
    local modelo_id=$1

    echo -e "${YELLOW}📋 Testando webhook de Modelo...${NC}"
    echo "Modelo ID: $modelo_id"
    echo ""

    response=$(curl -s -X POST "$API_URL/api/process-modelo" \
        -H "Content-Type: application/json" \
        -d "{
            \"modelo_id\": \"$modelo_id\",
            \"use_ast\": true,
            \"process_tags\": false,
            \"process_versions\": true,
            \"dry_run\": false
        }")

    status=$(echo "$response" | jq -r '.status')

    if [ "$status" = "sucesso" ]; then
        echo -e "${GREEN}✅ Webhook de Modelo processado com sucesso!${NC}"
        echo "$response" | jq '.'

        # Mostrar estatísticas
        versoes_proc=$(echo "$response" | jq -r '.versoes_processadas')
        total_mods=$(echo "$response" | jq -r '.total_modificacoes')
        echo ""
        echo -e "${GREEN}📊 Estatísticas:${NC}"
        echo "   - Versões processadas: $versoes_proc"
        echo "   - Total de modificações: $total_mods"
    else
        echo -e "${RED}❌ Erro ao processar modelo${NC}"
        echo "$response" | jq '.'
        return 1
    fi

    echo ""
}

# Função para testar webhook de versão
test_versao_webhook() {
    local versao_id=$1

    echo -e "${YELLOW}📄 Testando webhook de Versão...${NC}"
    echo "Versão ID: $versao_id"
    echo ""

    response=$(curl -s -X POST "$API_URL/api/process" \
        -H "Content-Type: application/json" \
        -d "{
            \"versao_id\": \"$versao_id\",
            \"use_ast\": true,
            \"mock\": false
        }")

    success=$(echo "$response" | jq -r '.success')

    if [ "$success" = "true" ]; then
        echo -e "${GREEN}✅ Webhook de Versão processado com sucesso!${NC}"
        echo "$response" | jq '.'

        # Mostrar estatísticas
        diff_id=$(echo "$response" | jq -r '.diff_id')
        total_mods=$(echo "$response" | jq -r '.metricas.total_modificacoes')
        alteracoes=$(echo "$response" | jq -r '.metricas.alteracoes')
        remocoes=$(echo "$response" | jq -r '.metricas.remocoes')
        insercoes=$(echo "$response" | jq -r '.metricas.insercoes')

        echo ""
        echo -e "${GREEN}📊 Estatísticas:${NC}"
        echo "   - Diff ID: $diff_id"
        echo "   - Total de modificações: $total_mods"
        echo "   - Alterações: $alteracoes"
        echo "   - Remoções: $remocoes"
        echo "   - Inserções: $insercoes"
        echo "   - URL: $API_URL/view/$diff_id"
    else
        echo -e "${RED}❌ Erro ao processar versão${NC}"
        echo "$response" | jq '.'
        return 1
    fi

    echo ""
}

# Função para obter um modelo de teste do Directus
get_sample_modelo() {
    echo -e "${BLUE}🔍 Buscando modelo de teste no Directus...${NC}"

    modelo_id=$(curl -s -H "Authorization: Bearer $DIRECTUS_TOKEN" \
        "$DIRECTUS_URL/items/modelo_contrato?limit=1" | jq -r '.data[0].id')

    if [ "$modelo_id" != "null" ] && [ -n "$modelo_id" ]; then
        echo -e "${GREEN}✅ Modelo encontrado: $modelo_id${NC}"
        echo "$modelo_id"
    else
        echo -e "${RED}❌ Nenhum modelo encontrado${NC}"
        exit 1
    fi
}

# Função para obter uma versão de teste do Directus
get_sample_versao() {
    echo -e "${BLUE}🔍 Buscando versão de teste no Directus...${NC}"

    versao_id=$(curl -s -H "Authorization: Bearer $DIRECTUS_TOKEN" \
        "$DIRECTUS_URL/items/versao?limit=1" | jq -r '.data[0].id')

    if [ "$versao_id" != "null" ] && [ -n "$versao_id" ]; then
        echo -e "${GREEN}✅ Versão encontrada: $versao_id${NC}"
        echo "$versao_id"
    else
        echo -e "${RED}❌ Nenhuma versão encontrada${NC}"
        exit 1
    fi
}

# Função para verificar health da API
check_health() {
    echo -e "${BLUE}🏥 Verificando saúde da API...${NC}"

    response=$(curl -s "$API_URL/health")
    status=$(echo "$response" | jq -r '.status')

    if [ "$status" = "healthy" ]; then
        echo -e "${GREEN}✅ API está saudável${NC}"
        echo "$response" | jq '.'
    else
        echo -e "${RED}❌ API com problemas${NC}"
        echo "$response"
        exit 1
    fi

    echo ""
}

# Menu principal
show_menu() {
    echo ""
    echo "Escolha uma opção:"
    echo "1) Testar webhook de Modelo (com ID específico)"
    echo "2) Testar webhook de Versão (com ID específico)"
    echo "3) Testar webhook de Modelo (ID automático do Directus)"
    echo "4) Testar webhook de Versão (ID automático do Directus)"
    echo "5) Verificar health da API"
    echo "6) Testar tudo"
    echo "0) Sair"
    echo ""
    read -p "Opção: " option

    case $option in
        1)
            read -p "Digite o modelo_id: " modelo_id
            test_modelo_webhook "$modelo_id"
            ;;
        2)
            read -p "Digite o versao_id: " versao_id
            test_versao_webhook "$versao_id"
            ;;
        3)
            modelo_id=$(get_sample_modelo)
            echo ""
            test_modelo_webhook "$modelo_id"
            ;;
        4)
            versao_id=$(get_sample_versao)
            echo ""
            test_versao_webhook "$versao_id"
            ;;
        5)
            check_health
            ;;
        6)
            check_health

            modelo_id=$(get_sample_modelo)
            echo ""
            test_modelo_webhook "$modelo_id"

            versao_id=$(get_sample_versao)
            echo ""
            test_versao_webhook "$versao_id"
            ;;
        0)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo -e "${RED}Opção inválida!${NC}"
            ;;
    esac

    show_menu
}

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq não está instalado!${NC}"
    echo "Instale com: brew install jq (macOS) ou apt-get install jq (Linux)"
    exit 1
fi

# Mostrar configuração
echo -e "${BLUE}⚙️  Configuração:${NC}"
echo "API URL: $API_URL"
echo "Directus URL: $DIRECTUS_URL"
echo "Token: ${DIRECTUS_TOKEN:0:20}..."
echo ""

# Iniciar menu
show_menu
