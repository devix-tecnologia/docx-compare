FROM python:3.13-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    pandoc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar arquivos de dependências
COPY requirements.txt pyproject.toml ./

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p results outputs logs

# Definir variáveis de ambiente
ENV PYTHONPATH=/app \
    FLASK_ENV=production \
    RESULTS_DIR=/app/results \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Definir usuário não-root
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 5005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5005/health || exit 1

# Comando de inicialização com Gunicorn para produção
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
