#!/bin/bash
# ./docker/postgres/entrypoint-replica.sh
# =============================================================================
# Entrypoint customizado para PostgreSQL REPLICA
# Inicializa réplica via pg_basebackup na primeira execução
# =============================================================================
set -e

# Executar script de setup da réplica
exec /setup-replica.sh
