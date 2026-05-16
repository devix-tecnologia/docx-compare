# PostgreSQL with PostGIS - Imagem Base

## Visão Geral

Imagem base customizada do PostgreSQL 16 com PostGIS 3.5, configurada com localização PT-BR para o projeto Versiona.ai.

**Toda configuração é feita via variáveis de ambiente** — compatível com CapRover e deploy sem volumes de config.

Esta imagem serve como base para:

- **directus_postgres** - Banco de dados do Directus
- **superset_postgres** - Banco de dados do Apache Superset
- **production** - Deploy em CapRover (config via ENV)
- **staging** - Ambiente de homologação

## Arquitetura

```
postgis/postgis:16-3.5
        ↓
Dockerfile.base (locale + entrypoint ENV→config)
        ↓
    postgis:16-ptbr-base
        ↓
    ┌───────┴───────┐───────────────┐
    ↓               ↓               ↓
dev (Dockerfile)  staging         production
```

## Funcionalidades

### 1. PostGIS 3.5

- Extensão geoespacial completa
- Suporte a geometrias 2D/3D
- Funções de análise espacial
- Índices espaciais (GIST)

### 2. Localização PT-BR

```bash
LANG=pt_BR.UTF-8
LC_ALL=pt_BR.UTF-8
LC_COLLATE=pt_BR.UTF-8
LC_CTYPE=pt_BR.UTF-8
```

### 3. Timezone

```bash
TZ=America/Sao_Paulo
```

### 4. Encoding UTF-8

- Database encoding: UTF8
- Collation: pt_BR.UTF-8
- Ctype: pt_BR.UTF-8

### 5. Configuração via ENV (sem volumes de config)

O `postgresql.conf` é gerado automaticamente pelo entrypoint a partir de variáveis `PG_*`:

| ENV                                 | Default | Descrição                              |
| ----------------------------------- | ------- | -------------------------------------- |
| `PG_MAX_CONNECTIONS`                | 100     | Conexões simultâneas                   |
| `PG_SHARED_BUFFERS`                 | 256MB   | Cache de dados em memória              |
| `PG_WORK_MEM`                       | 16MB    | Memória por operação de sort           |
| `PG_MAINTENANCE_WORK_MEM`           | 128MB   | Memória para VACUUM, CREATE INDEX      |
| `PG_EFFECTIVE_CACHE_SIZE`           | 768MB   | Estimativa de cache do SO              |
| `PG_WAL_LEVEL`                      | replica | Nível do WAL (replica para HA)         |
| `PG_MAX_WAL_SIZE`                   | 1GB     | Tamanho máximo do WAL                  |
| `PG_JIT`                            | off     | JIT compilation                        |
| `PG_LOG_MIN_DURATION_STATEMENT`     | 1000    | Logar queries > N ms                   |
| `PG_AUTOVACUUM_VACUUM_SCALE_FACTOR` | 0.1     | % de dead tuples para vacuum           |
| `PG_SSL`                            | off     | SSL (desnecessário em Docker/CapRover) |

**Exemplo CapRover (produção 64GB RAM):**

```bash
PG_SHARED_BUFFERS=12GB
PG_WORK_MEM=64MB
PG_EFFECTIVE_CACHE_SIZE=40GB
PG_MAX_CONNECTIONS=150
PG_JIT=on
PG_AUTOVACUUM_VACUUM_SCALE_FACTOR=0.01
```

### 6. Monitoramento com pg_stat_statements

A extensão `pg_stat_statements` está habilitada para análise de performance, essencial para o `postgres_exporter`:
pg_stat_statements.max=5000
pg_stat_statements.track=all

````

**Benefícios:**

- 🔍 Rastreamento de queries SQL executadas
- ⏱️ Tempo médio de execução
- 💾 Consumo de I/O por query
- 📊 Estatísticas para otimização
- 🎯 Integração com Grafana via postgres_exporter

**Consultar estatísticas:**

```sql
-- Top 10 queries mais lentas
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Queries mais executadas
SELECT query, calls, total_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;
````

## Build

### Via docker-compose

```bash
# Build automático da imagem base
docker-compose up -d directus_postgres superset_postgres

# Rebuild apenas a imagem base
docker-compose build --no-cache pgbase
```

### Build Manual

```bash
docker build -t pgbase \
  -f docker/postgres/Dockerfile.base \
  docker/postgres/
```

## Uso

### docker-compose.yml

```yaml
# Imagem base
pgbase:
  build:
    context: ./docker/postgres
    dockerfile: Dockerfile.base
  image: pgbase
  entrypoint: ["echo", "Imagem base PostgreSQL criada"]

# Banco Directus (usa pgbase)
directus_postgres:
  build:
    context: ./docker/postgres
    dockerfile: Dockerfile
  image: ${PROJECT_NAME}_directus_postgres:15-ptbr
  depends_on:
    pgbase:
      condition: service_completed_successfully
  environment:
    POSTGRES_DB: directus
    POSTGRES_USER: directus
    POSTGRES_PASSWORD_FILE: /run/secrets/senha_usuario_postgres_directus
  volumes:
    - directus_db_data:/var/lib/postgresql/data
    - ./docker/postgres/init:/docker-entrypoint-initdb.d
  secrets:
    - senha_usuario_postgres_directus
```

## Scripts de Inicialização

Os scripts SQL em `docker/postgres/init/` são executados automaticamente na primeira inicialização:

```
docker/postgres/init/
├── 01-create-users.sh          # Cria usuários (postgres_exporter)
├── 02-create-exporter-user-superset.sh  # Exporter no Superset DB
└── 99-*.sql                    # Scripts customizados por projeto
```

### Ordem de Execução

1. Scripts `.sh` e `.sql` são executados em ordem alfabética
2. Apenas na primeira inicialização (quando `/var/lib/postgresql/data` está vazio)
3. Se houver erro, o container para de inicializar

## Configuração PostGIS

### Habilitar Extensão

```sql
-- Conectar ao banco de dados
\c seu_banco

-- Criar extensão PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verificar versão
SELECT PostGIS_Version();
```

### Exemplo de Uso

```sql
-- Criar tabela com geometria
CREATE TABLE localizacoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    geom GEOMETRY(Point, 4326)
);

-- Criar índice espacial
CREATE INDEX idx_localizacoes_geom ON localizacoes USING GIST (geom);

-- Inserir ponto (lat, lon)
INSERT INTO localizacoes (nome, geom)
VALUES ('Sede Versiona.ai', ST_SetSRID(ST_MakePoint(-46.6333, -23.5505), 4326));

-- Buscar pontos próximos (raio de 10km)
SELECT nome, ST_Distance(
    geom::geography,
    ST_SetSRID(ST_MakePoint(-46.6400, -23.5600), 4326)::geography
) / 1000 AS distancia_km
FROM localizacoes
WHERE ST_DWithin(
    geom::geography,
    ST_SetSRID(ST_MakePoint(-46.6400, -23.5600), 4326)::geography,
    10000
)
ORDER BY distancia_km;
```

## Backup e Restore

### Backup

```bash
# Backup de todos os bancos
docker exec directus_postgres pg_dumpall -U postgres > backup.sql

# Backup de um banco específico
docker exec directus_postgres pg_dump -U directus directus > backup_directus.sql

# Backup com compressão
docker exec directus_postgres pg_dump -U directus -Fc directus > backup.dump
```

### Restore

```bash
# Restore de todos os bancos
docker exec -i directus_postgres psql -U postgres < backup.sql

# Restore de um banco específico
docker exec -i directus_postgres psql -U directus directus < backup_directus.sql

# Restore de backup comprimido
docker exec -i directus_postgres pg_restore -U directus -d directus < backup.dump
```

## Monitoramento

### postgres_exporter

Esta imagem base é usada por bancos monitorados via `postgres_exporter`:

```yaml
postgres_exporter_directus:
  image: ${PROJECT_NAME}_postgres_exporter:0.19.1
  environment:
    DATA_SOURCE_NAME: "postgresql://postgres_exporter:senha@directus_postgres:5432/directus?sslmode=disable"
  ports:
    - "9187:9187"
```

Métricas expostas em: http://localhost:9187/metrics

### Queries Úteis

```sql
-- Ver bancos de dados
\l

-- Ver tamanho dos bancos
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;

-- Ver conexões ativas
SELECT datname, count(*) as connections
FROM pg_stat_activity
GROUP BY datname;

-- Ver queries lentas (> 1s)
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 second'
ORDER BY duration DESC;
```

## Troubleshooting

### Container não inicia

```bash
# Verificar logs
docker logs directus_postgres

# Erro comum: permissões do volume
sudo chown -R 999:999 volumes/directus_db_data/
```

### Locale não encontrado

```bash
# Verificar locales disponíveis
docker exec directus_postgres locale -a

# Recriar locale manualmente
docker exec directus_postgres locale-gen pt_BR.UTF-8
docker exec directus_postgres update-locale LANG=pt_BR.UTF-8
```

### PostGIS não disponível

```bash
# Verificar se extensão está instalada
docker exec directus_postgres psql -U postgres -d seu_banco -c "SELECT PostGIS_Version();"

# Criar extensão manualmente
docker exec directus_postgres psql -U postgres -d seu_banco -c "CREATE EXTENSION postgis;"
```

### Banco de dados corrompido

```bash
# Verificar integridade
docker exec directus_postgres pg_checksums --check -D /var/lib/postgresql/data

# Reindexar banco
docker exec directus_postgres psql -U postgres -d seu_banco -c "REINDEX DATABASE seu_banco;"
```

## Atualização de Versão

### PostgreSQL 15 → 16

```bash
# 1. Backup completo
docker exec directus_postgres pg_dumpall -U postgres > backup_pre_upgrade.sql

# 2. Atualizar Dockerfile.base
sed -i 's/postgis:15-3.5/postgis:16-3.5/g' docker/postgres/Dockerfile.base

# 3. Rebuild
docker-compose build --no-cache pgbase
docker-compose build directus_postgres superset_postgres

# 4. Parar containers
docker-compose stop directus_postgres superset_postgres

# 5. Renomear volumes antigos (backup)
docker volume create directus_db_data_backup
docker run --rm -v directus_db_data:/from -v directus_db_data_backup:/to alpine cp -av /from/. /to/

# 6. Remover volumes antigos
docker volume rm directus_db_data superset_db_data

# 7. Recriar e restaurar
docker-compose up -d directus_postgres superset_postgres
docker exec -i directus_postgres psql -U postgres < backup_pre_upgrade.sql
```

## Segurança

### Boas Práticas Implementadas

✅ **Secrets para senhas**: Usa Docker Secrets, não variáveis de ambiente
✅ **Usuário dedicado**: postgres_exporter com permissões mínimas (pg_monitor)
✅ **Init scripts**: Automatizam criação de usuários e extensões
✅ **Volumes nomeados**: Persistência de dados isolada
✅ **Network isolation**: Apenas serviços necessários têm acesso

### Melhorias Futuras

- [ ] Habilitar SSL/TLS para conexões
- [ ] Implementar pg_hba.conf customizado
- [ ] Configurar replicação (hot standby)
- [ ] Implementar backup automatizado (pg_basebackup)

## Referências

- **PostgreSQL**: https://www.postgresql.org/docs/15/
- **PostGIS**: https://postgis.net/documentation/
- **Docker Hub**: https://hub.docker.com/r/postgis/postgis
- **Prometheus Postgres Exporter**: https://github.com/prometheus-community/postgres_exporter
