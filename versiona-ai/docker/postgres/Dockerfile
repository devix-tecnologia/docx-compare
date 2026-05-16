# ./docker/postgres/Dockerfile (desenvolvimento)
# Usa imagem base com config via ENV + entrypoint
FROM postgis:16-ptbr-base

# Copia scripts de inicialização (.sh)
COPY init/*.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/*.sh

# Copia backup do Directus para restauração automática
# Padrão de nomenclatura: backup-<servico>-anonimizado.tar
# Exemplo: backup-directus-anonimizado.tar, backup-superset-anonimizado.tar
COPY backup/backup-directus-anonimizado.tar /docker-entrypoint-initdb.d/backup-directus-anonimizado.tar
