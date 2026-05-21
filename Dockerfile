# Dockerfile para Versiona AI - API de Comparação de Documentos
# Otimizado para produção com uv e Python 3.13

FROM python:3.13-slim

# Metadados da imagem
LABEL maintainer="Devix Tecnologia <dev@devix.co>"
LABEL description="Versiona AI - Sistema de comparação de documentos com integração Directus"
LABEL version="1.0.0"

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema e UV
RUN apt-get update && apt-get install -y \
    curl \
    git \
    pandoc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração do projeto
COPY pyproject.toml uv.lock ./

# Instalar dependências Python com UV
RUN uv sync --frozen

# Copiar código da aplicação
COPY --chown=app:app versiona-ai/ ./versiona-ai/

# Criar diretório de logs e definir permissões adequadas
RUN mkdir -p /app/logs && chown -R app:app /app

# Mudar para usuário não-root
USER app

# Definir diretório de trabalho para a aplicação
WORKDIR /app/versiona-ai

# Porta da aplicação (8001 para dev, 8000 para produção via FLASK_PORT)
EXPOSE 8001 8000

# Health check - start-period aumentado para 60s pois imports levam ~30s
# Usa porta 8000 por padrão (produção) ou 8001 se FLASK_PORT não estiver setado
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || curl -f http://localhost:8001/health || exit 1

# Comando padrão para produção com Gunicorn
# Usa o venv já instalado em /app/.venv diretamente para evitar que
# 'uv run' recrie o ambiente ao detectar o pyproject.toml de versiona-ai/
CMD ["/app/.venv/bin/gunicorn", "--config", "/app/versiona-ai/deploy/gunicorn.conf.py", "wsgi:app"]
