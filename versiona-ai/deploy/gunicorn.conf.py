# Configuração do Gunicorn para Versiona AI
import os

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

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "versiona-ai"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
