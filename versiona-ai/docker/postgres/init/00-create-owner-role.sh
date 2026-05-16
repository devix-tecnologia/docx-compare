#!/bin/bash
# Script para criar a role 'versiona_ai' que é o owner das tabelas no backup
# Deve rodar ANTES de 01-create-users.sh

set -e

echo "🔐 Criando role 'versiona_ai' (owner das tabelas do backup)..."

# Criar role se não existir
psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE versiona_ai WITH LOGIN;
EOSQL

# Garantir privilégios (sempre executar, mesmo se role já existe)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE directus TO versiona_ai;
EOSQL

echo "✅ Role 'versiona_ai' pronta!"
