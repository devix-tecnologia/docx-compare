#!/bin/bash
# Script para restaurar backup do Directus automaticamente
# Executa ANTES dos outros scripts de seed (ordem alfabética: 00-)

set -e

BACKUP_FILE="/docker-entrypoint-initdb.d/backup-directus-anonimizado.tar"
FLAG_FILE="/var/lib/postgresql/data/.restored-directus-e2e"
DB_NAME="directus"

echo "🔍 Verificando backup do Directus..."

# Verificar se já foi restaurado anteriormente
if [ -f "$FLAG_FILE" ]; then
    echo "ℹ️  Backup já foi restaurado anteriormente (flag encontrada)"
    echo "   Para forçar nova restauração: docker-compose down -v"
    exit 0
fi

# Verificar se arquivo de backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "⚠️  Arquivo de backup não encontrado: $BACKUP_FILE"
    echo "   Os scripts de seed SQL serão executados normalmente"
    exit 0
fi

echo "📦 Backup encontrado: $BACKUP_FILE"
echo "🔄 Iniciando restauração do banco Directus..."

# Restaurar backup
pg_restore \
    --username="$POSTGRES_USER" \
    --dbname="$DB_NAME" \
    --verbose \
    --no-owner \
    --no-acl \
    "$BACKUP_FILE" 2>&1 | grep -E "^(processing|creating|restoring|ERROR|FATAL)" || true

# Verificar se restauração foi bem-sucedida
TABLE_COUNT=$(psql -U "$POSTGRES_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

if [ "$TABLE_COUNT" -gt 5 ]; then
    echo "✅ Backup restaurado com sucesso! ($TABLE_COUNT tabelas criadas)"
    
    # Criar flag para evitar restaurações duplicadas
    touch "$FLAG_FILE"
    echo "✅ Flag de restauração criada: $FLAG_FILE"
    
    # Pular scripts de seed SQL (01-, 02-, 03-) pois o backup já tem tudo
    echo "ℹ️  Scripts de seed SQL (01-, 02-, 03-) serão pulados"
    echo "   O banco já está completo com dados do backup"
else
    echo "⚠️  Restauração pode ter falhado (apenas $TABLE_COUNT tabelas)"
    echo "   Scripts de seed SQL serão executados como fallback"
fi

echo "🎉 Restauração do Directus concluída!"
