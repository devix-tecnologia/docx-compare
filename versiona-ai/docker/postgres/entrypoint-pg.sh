#!/bin/bash
set -e

# =============================================================================
# entrypoint-pg.sh — Gera postgresql.conf via ENV e delega ao entrypoint oficial
# =============================================================================

TEMPLATE="/etc/postgresql/postgresql.conf.template"
CONFIG="/etc/postgresql/postgresql.conf"
PGDATA="${PGDATA:-/var/lib/postgresql/data}"

# Gerar postgresql.conf a partir do template + env vars
if [ -f "$TEMPLATE" ]; then
    echo "[entrypoint-pg] Gerando postgresql.conf a partir de variáveis de ambiente..."

    # Lista apenas as variáveis PG_* para envsubst (não substituir $data_directory etc.)
    PG_VARS=$(env | grep '^PG_' | cut -d= -f1 | sed 's/^/\$/' | tr '\n' ' ')

    envsubst "$PG_VARS" < "$TEMPLATE" > "$CONFIG"
    chown postgres:postgres "$CONFIG"

    echo "[entrypoint-pg] postgresql.conf gerado com sucesso"
    
    # Se PGDATA já existe (restart), copiar config para lá também
    if [ -d "$PGDATA" ] && [ -f "$PGDATA/PG_VERSION" ]; then
        echo "[entrypoint-pg] Atualizando postgresql.conf em $PGDATA"
        cp "$CONFIG" "$PGDATA/postgresql.conf"
        chown postgres:postgres "$PGDATA/postgresql.conf"
    fi
else
    echo "[entrypoint-pg] AVISO: Template não encontrado em $TEMPLATE, usando config padrão"
fi

# Se o primeiro argumento começa com '-c', prepend 'postgres'
# para manter compatibilidade com o entrypoint oficial
if [ "${1:0:2}" = "-c" ]; then
    set -- postgres "$@"
fi

# Adicionar shared_preload_libraries se o comando for postgres
if [ "$1" = 'postgres' ]; then
    # Verificar se -c shared_preload_libraries já está nos args
    HAS_PRELOAD=false
    for arg in "$@"; do
        if echo "$arg" | grep -q "shared_preload_libraries"; then
            HAS_PRELOAD=true
            break
        fi
    done

    if [ "$HAS_PRELOAD" = false ]; then
        set -- "$@" -c "shared_preload_libraries=pg_stat_statements"
    fi
fi

# Delegar ao entrypoint oficial do PostgreSQL
exec /usr/local/bin/docker-entrypoint.sh "$@"
