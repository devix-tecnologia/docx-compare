#!/bin/bash
# ./docker/postgres/init/04-setup-replication-replica.sh
# =============================================================================
# Script de inicialização do PostgreSQL REPLICA
# Configura a réplica para conectar ao primary via streaming replication
# Executado via ENTRYPOINT customizado (não docker-entrypoint-initdb.d)
# =============================================================================
set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}  PostgreSQL REPLICA - Configuração de Replicação Streaming${NC}"
echo -e "${BLUE}================================================================${NC}"

# Variáveis de ambiente obrigatórias
REQUIRED_VARS=(
    "POSTGRES_PRIMARY_HOST"
    "POSTGRES_PRIMARY_PORT"
    "POSTGRES_REPLICATION_USER"
    "POSTGRES_DB"
)

# Verificar variáveis obrigatórias
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}[REPLICA] ERRO: Variável $var não definida!${NC}"
        exit 1
    fi
done

# Ler senha de replicação do secret
if [ -n "$POSTGRES_REPLICATION_PASSWORD_FILE" ] && [ -f "$POSTGRES_REPLICATION_PASSWORD_FILE" ]; then
    POSTGRES_REPLICATION_PASSWORD=$(cat "$POSTGRES_REPLICATION_PASSWORD_FILE")
elif [ -f /run/secrets/replication_password ]; then
    POSTGRES_REPLICATION_PASSWORD=$(cat /run/secrets/replication_password)
elif [ -f /run/secrets/superset_replication_password ]; then
    POSTGRES_REPLICATION_PASSWORD=$(cat /run/secrets/superset_replication_password)
else
    echo -e "${RED}[REPLICA] ERRO: Secret replication_password não encontrado!${NC}"
    echo -e "${YELLOW}[REPLICA] Procurado em:${NC}"
    echo -e "${YELLOW}  - \$POSTGRES_REPLICATION_PASSWORD_FILE ($POSTGRES_REPLICATION_PASSWORD_FILE)${NC}"
    echo -e "${YELLOW}  - /run/secrets/replication_password${NC}"
    echo -e "${YELLOW}  - /run/secrets/superset_replication_password${NC}"
    exit 1
fi

# Verificar se PGDATA já está inicializado
if [ -s "$PGDATA/PG_VERSION" ]; then
    echo -e "${YELLOW}[REPLICA] PGDATA já inicializado. Pulando pg_basebackup.${NC}"
    echo -e "${GREEN}[REPLICA] Iniciando PostgreSQL em modo standby...${NC}"
    # Executar como usuário postgres se rodando como root
    if [ "$(id -u)" = '0' ]; then
        exec gosu postgres postgres
    else
        exec postgres
    fi
fi

echo -e "${YELLOW}[REPLICA] PGDATA vazio. Iniciando pg_basebackup do primary...${NC}"

# Aguardar primary estar disponível
echo -e "${YELLOW}[REPLICA] Aguardando primary estar disponível...${NC}"
MAX_ATTEMPTS=30
ATTEMPT=0

while ! pg_isready -h "$POSTGRES_PRIMARY_HOST" -p "$POSTGRES_PRIMARY_PORT" >/dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo -e "${RED}[REPLICA] ERRO: Primary não ficou disponível após ${MAX_ATTEMPTS} tentativas!${NC}"
        echo -e "${RED}[REPLICA] Host: $POSTGRES_PRIMARY_HOST:$POSTGRES_PRIMARY_PORT${NC}"
        exit 1
    fi
    echo -e "${YELLOW}[REPLICA] Tentativa $ATTEMPT/$MAX_ATTEMPTS - Aguardando primary...${NC}"
    sleep 2
done

echo -e "${GREEN}[REPLICA] Primary disponível! Iniciando pg_basebackup...${NC}"

# Criar arquivo .pgpass para autenticação
export PGPASSFILE="/tmp/.pgpass"
echo "$POSTGRES_PRIMARY_HOST:$POSTGRES_PRIMARY_PORT:replication:$POSTGRES_REPLICATION_USER:$POSTGRES_REPLICATION_PASSWORD" > "$PGPASSFILE"
chmod 0600 "$PGPASSFILE"

# Executar pg_basebackup
echo -e "${BLUE}[REPLICA] Copiando dados do primary (pode demorar)...${NC}"
pg_basebackup \
    -h "$POSTGRES_PRIMARY_HOST" \
    -p "$POSTGRES_PRIMARY_PORT" \
    -U "$POSTGRES_REPLICATION_USER" \
    -D "$PGDATA" \
    -Fp \
    -Xs \
    -P \
    -R \
    -v

# NÃO remover .pgpass - é necessário para streaming replication contínua
# O pg_basebackup -R configura primary_conninfo para usar passfile='/tmp/.pgpass'
# rm -f "$PGPASSFILE"  # COMENTADO: arquivo necessário durante a vida da replica

# Verificar se pg_basebackup foi bem-sucedido
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo -e "${RED}[REPLICA] ERRO: pg_basebackup falhou!${NC}"
    exit 1
fi

echo -e "${GREEN}[REPLICA] pg_basebackup concluído com sucesso!${NC}"

# Configurar permissões
chown -R postgres:postgres "$PGDATA"
chmod 0700 "$PGDATA"

# Criar standby.signal (PostgreSQL 12+)
echo -e "${YELLOW}[REPLICA] Criando standby.signal...${NC}"
touch "$PGDATA/standby.signal"

# Configurar postgresql.auto.conf para hot standby
echo -e "${YELLOW}[REPLICA] Configurando parâmetros de hot standby...${NC}"
cat >> "$PGDATA/postgresql.auto.conf" <<-EOF

# ===========================================================================
# Configuração de Hot Standby - Réplica Read-Only
# ===========================================================================
hot_standby = on
hot_standby_feedback = on
max_standby_streaming_delay = 30s
wal_receiver_status_interval = 10s

# Primary connection info (já configurado pelo pg_basebackup -R)
# primary_conninfo = 'host=$POSTGRES_PRIMARY_HOST port=$POSTGRES_PRIMARY_PORT user=$POSTGRES_REPLICATION_USER'
EOF

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Réplica configurada com sucesso!${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "${BLUE}  Primary: $POSTGRES_PRIMARY_HOST:$POSTGRES_PRIMARY_PORT${NC}"
echo -e "${BLUE}  Database: $POSTGRES_DB${NC}"
echo -e "${BLUE}  Modo: Hot Standby (Read-Only)${NC}"
echo -e "${GREEN}================================================================${NC}"

# Iniciar PostgreSQL
echo -e "${GREEN}[REPLICA] Iniciando PostgreSQL em modo standby...${NC}"
# Executar como usuário postgres se rodando como root
if [ "$(id -u)" = '0' ]; then
    exec gosu postgres postgres
else
    exec postgres
fi
