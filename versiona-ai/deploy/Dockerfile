# Dockerfile para Versiona AI Backend - Produção
FROM python:3.13-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    pandoc \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Criar usuário não-root
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -m -d /home/appuser -s /bin/bash appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY deploy/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY core/ ./core/
COPY *.py ./
COPY deploy/gunicorn.conf.py ./
COPY deploy/.env.example ./.env

# Criar diretórios necessários
RUN mkdir -p logs results temp && \
    chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Definir variáveis de ambiente
ENV PYTHONPATH=/app \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    FLASK_PORT=8000

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização com Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "directus_server:app"]
