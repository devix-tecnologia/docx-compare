#!/bin/bash
# Não usar set -e para permitir que extensões opcionais falhem
# set -e

# =============================================================================
# 00-extensions.sh — Cria extensões PostGIS + monitoramento + busca textual
# Executado automaticamente pelo docker-entrypoint-initdb.d na inicialização
# =============================================================================

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"
}

log "Criando extensões no banco $POSTGRES_DB..."

# ON_ERROR_STOP=0 permite que extensões opcionais (como PostGIS) falhem sem parar o script
psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
    CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
    CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS citext;
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
EOSQL

log "Extensões processadas (algumas podem ter falhado se não disponíveis)"
