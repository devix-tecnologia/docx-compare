#!/usr/bin/env python3
"""
Servidor de produção para o Processador Automático de Versões
Usa Gunicorn como servidor WSGI para produção
"""

import multiprocessing
import os

# Configurações do Gunicorn
bind = "0.0.0.0:5005"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 60
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logs
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de processo
user = None  # Será definido pelo Docker
group = None
tmp_upload_dir = None
pidfile = "/tmp/gunicorn.pid"
daemon = False

# Configurações específicas da aplicação
raw_env = ["FLASK_ENV=production", "PYTHONPATH=/app"]
