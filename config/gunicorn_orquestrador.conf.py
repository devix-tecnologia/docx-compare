#!/usr/bin/env python3
"""
Configuração do Gunicorn para o Orquestrador de Processadores
"""

import os

# Configuração do servidor
bind = f"0.0.0.0:{os.getenv('ORQUESTRADOR_PORTA', '5007')}"
workers = 1  # Apenas 1 worker para o orquestrador (singleton)
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Configuração de processo
preload_app = True
max_requests = 1000
max_requests_jitter = 50
user = os.getenv("GUNICORN_USER", None)
group = os.getenv("GUNICORN_GROUP", None)

# Configuração de logs
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")  # stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuração de processo
pidfile = os.getenv("GUNICORN_PID_FILE", "/tmp/gunicorn_orquestrador.pid")
tmp_upload_dir = None

# Configuração SSL (se necessário)
keyfile = os.getenv("GUNICORN_KEYFILE", None)
certfile = os.getenv("GUNICORN_CERTFILE", None)


# Hooks do Gunicorn
def when_ready(server):
    """Executado quando o servidor está pronto"""
    server.log.info("🎯 Orquestrador de Processadores está pronto")
    server.log.info(f"📊 Modo: {os.getenv('ORQUESTRADOR_MODO', 'sequencial')}")
    server.log.info(f"⏱️ Intervalo: {os.getenv('ORQUESTRADOR_INTERVALO', '60')}s")
    server.log.info(f"🔊 Verbose: {os.getenv('ORQUESTRADOR_VERBOSE', 'false')}")


def on_starting(server):
    """Executado quando o servidor está iniciando"""
    server.log.info("🚀 Iniciando Orquestrador de Processadores...")


def on_reload(server):
    """Executado quando o servidor é recarregado"""
    server.log.info("🔄 Recarregando Orquestrador de Processadores...")


def worker_int(worker):
    """Executado quando um worker recebe SIGINT"""
    worker.log.info("🛑 Worker recebeu SIGINT, encerrando...")


def pre_fork(server, worker):
    """Executado antes de fazer fork de um worker"""
    pass


def post_fork(server, worker):
    """Executado após fazer fork de um worker"""
    server.log.info(f"👷 Worker {worker.pid} iniciado para o orquestrador")
