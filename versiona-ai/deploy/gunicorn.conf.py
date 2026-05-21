# Configuração do Gunicorn para Versiona AI
import logging
import os
import sys

# Server socket
bind = f"0.0.0.0:{os.getenv('FLASK_PORT', '8001')}"
backlog = 2048

# Worker processes
workers = 2  # Ajustado para produção
worker_class = "sync"
worker_connections = 1000
timeout = 300  # Aumentado para operações longas
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging - Para containers, logar em stdout/stderr
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
capture_output = True  # Captura prints do Flask para os logs do Gunicorn


# Filtro para remover health checks dos logs
class HealthCheckFilter(logging.Filter):
    """Filtro para suprimir logs de requisições ao /health"""

    def filter(self, record):
        return "/health" not in record.getMessage()


# Configuração de logging customizada
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "health_check_filter": {
            "()": HealthCheckFilter,
        }
    },
    "formatters": {
        "generic": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr",
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "filters": ["health_check_filter"],  # Aplica o filtro aqui
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["error_console"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["access_console"],  # Usa handler com filtro
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

# Process naming
proc_name = "versiona-ai"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190


# Callbacks para debug
def on_starting(server):
    """Chamado logo quando o Gunicorn está iniciando"""
    print("=" * 80, flush=True)
    print("🚀 GUNICORN INICIANDO...", flush=True)
    print(f"   Bind: {bind}", flush=True)
    print(f"   Workers: {workers}", flush=True)
    print(f"   Timeout: {timeout}s", flush=True)
    print(f"   Python: {sys.version}", flush=True)
    print("   🔇 Health checks: silenciados", flush=True)
    print("=" * 80, flush=True)


def when_ready(server):
    """Chamado quando o servidor está pronto para receber requisições"""
    print("=" * 80, flush=True)
    print("✅ GUNICORN PRONTO PARA RECEBER REQUISIÇÕES", flush=True)
    print(f"   Listening on: {bind}", flush=True)
    print("=" * 80, flush=True)


def worker_int(worker):
    """Chamado quando um worker é interrompido"""
    print(f"⚠️  Worker {worker.pid} interrompido", flush=True)


def worker_abort(worker):
    """Chamado quando um worker aborta"""
    print(f"❌ Worker {worker.pid} abortou", flush=True)
