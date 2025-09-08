#!/usr/bin/env bash
# Scripts de desenvolvimento para o projeto docx-compare

# Função para executar comandos com UV
run_with_uv() {
    echo "🔧 Executando: uv run $*"
    uv run "$@"
}

# Função para executar linting
lint() {
    echo "🔍 Executando linting com Ruff..."
    uv run ruff check .
}

# Função para corrigir problemas de linting automaticamente
lint_fix() {
    echo "🔧 Corrigindo problemas de linting automaticamente..."
    uv run ruff check --fix .
}

# Função para formatar código
format() {
    echo "✨ Formatando código com Ruff..."
    uv run ruff format .
}

# Função para executar testes
test() {
    echo "🧪 Executando testes com pytest..."
    uv run pytest tests/ -v
}

# Função para executar testes com cobertura
test_coverage() {
    echo "🧪 Executando testes com cobertura..."
    uv run pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html
}

# Função para verificar qualidade completa do código
check() {
    echo "🚀 Verificação completa do código..."
    echo ""
    lint
    echo ""
    format
    echo ""
    test
}

# Função para instalar dependências
install() {
    echo "📦 Instalando dependências..."
    uv sync --group dev
}

# Função para executar o processador automático
run_processor() {
    echo "🤖 Iniciando processador automático..."
    run_with_uv processador_automatico.py
}

# Função para executar CLI de comparação
compare() {
    if [ $# -lt 2 ]; then
        echo "Uso: compare <arquivo_original> <arquivo_modificado> [arquivo_saida]"
        return 1
    fi

    echo "📄 Comparando documentos..."
    run_with_uv docx_diff_viewer.py "$@"
}

# Ajuda
help() {
    echo "📚 Scripts disponíveis para docx-compare:"
    echo ""
    echo "  lint              - Executar linting com Ruff"
    echo "  lint_fix          - Corrigir problemas de linting automaticamente"
    echo "  format            - Formatar código com Ruff"
    echo "  test              - Executar testes"
    echo "  test_coverage     - Executar testes com cobertura"
    echo "  check             - Verificação completa (lint + format + test)"
    echo "  install           - Instalar dependências"
    echo "  run_processor     - Executar processador automático"
    echo "  compare           - Executar CLI de comparação"
    echo "  help              - Mostrar esta ajuda"
    echo ""
    echo "Exemplo de uso:"
    echo "  source scripts.sh && lint"
    echo "  source scripts.sh && compare doc1.docx doc2.docx"
}

# Se o script for executado diretamente, mostrar ajuda
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    help
fi
