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

# Definir permissões adequadas
RUN chown -R app:app /app

# Mudar para usuário não-root
USER app

# Definir diretório de trabalho para a aplicação
WORKDIR /app/versiona-ai

# Porta da aplicação
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Comando padrão para produção com Gunicorn
CMD ["uv", "run", "gunicorn", "--config", "/app/versiona-ai/deploy/gunicorn.conf.py", "versiona-ai.wsgi:app"]
