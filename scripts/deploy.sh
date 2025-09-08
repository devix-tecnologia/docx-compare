#!/bin/bash
# Script de deployment para docx-compare

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Verificar se estamos na raiz do projeto
if [ ! -f "pyproject.toml" ]; then
    error "Este script deve ser executado na raiz do projeto docx-compare"
fi

# Opções de deployment
USE_UV=${USE_UV:-"true"}
BUILD_TESTS=${BUILD_TESTS:-"true"}
PUSH_TO_REGISTRY=${PUSH_TO_REGISTRY:-"false"}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}

log "Iniciando processo de deployment..."

# Ler informações do projeto
if command -v uv &> /dev/null && [ "$USE_UV" = "true" ]; then
    VERSION=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    PROJECT_NAME=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")
    PYTHON_CMD="uv run python"
    log "Usando uv para gerenciamento de dependências"
else
    VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    PROJECT_NAME=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")
    PYTHON_CMD="python"
    warn "uv não encontrado ou desabilitado, usando pip tradicional"
fi

log "Projeto: $PROJECT_NAME"
log "Versão: $VERSION"

# Instalar dependências
if [ "$USE_UV" = "true" ] && command -v uv &> /dev/null; then
    log "Instalando dependências com uv..."
    uv sync --group dev
else
    log "Instalando dependências com pip..."
    pip install -r requirements.txt
    pip install ruff pytest pytest-cov
fi

# Executar testes
if [ "$BUILD_TESTS" = "true" ]; then
    log "Executando linting..."
    $PYTHON_CMD -m ruff check .

    log "Verificando formatação..."
    $PYTHON_CMD -m ruff format --check .

    log "Executando testes..."
    $PYTHON_CMD -m pytest tests/ --cov=src --cov-report=term-missing
fi

# Construir imagem Docker
log "Construindo imagem Docker..."
if [ "$USE_UV" = "true" ] && [ -f "docker/Dockerfile.uv" ]; then
    DOCKERFILE="docker/Dockerfile.uv"
    log "Usando Dockerfile otimizado com uv"
else
    DOCKERFILE="docker/Dockerfile.orquestrador"
    log "Usando Dockerfile do orquestrador"
fi

docker build -f $DOCKERFILE -t ${PROJECT_NAME}:${VERSION} .
docker tag ${PROJECT_NAME}:${VERSION} ${PROJECT_NAME}:latest

log "Imagem Docker criada: ${PROJECT_NAME}:${VERSION}"

# Push para registry (opcional)
if [ "$PUSH_TO_REGISTRY" = "true" ] && [ -n "$DOCKER_REGISTRY" ]; then
    log "Fazendo push para registry: $DOCKER_REGISTRY"
    docker tag ${PROJECT_NAME}:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}:${VERSION}
    docker tag ${PROJECT_NAME}:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:${VERSION}
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
fi

log "Deployment concluído com sucesso!"
log "Imagem disponível: ${PROJECT_NAME}:${VERSION}"

# Mostrar comandos úteis
echo ""
log "Comandos úteis:"
echo "  docker run -p 8000:8000 ${PROJECT_NAME}:${VERSION}"
echo "  docker-compose -f docker-compose.production.yml up -d"
echo "  docker-compose -f docker-compose.production.yml --profile dev up -d"
