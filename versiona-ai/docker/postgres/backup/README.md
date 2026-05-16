# Backups PostgreSQL - Restauração Automática

Esta pasta contém backups de bancos de dados PostgreSQL que são automaticamente restaurados durante a inicialização do container de desenvolvimento.

## 📋 Nomenclatura de Arquivos

**Padrão**: `backup-<servico>-anonimizado.tar`

### Exemplos:

- ✅ `backup-directus-anonimizado.tar` - Backup do banco Directus CMS (versiona-ai)
- ✅ `backup-superset-anonimizado.tar` - Backup do banco Superset (futuro)
- ❌ `backup-anonimizado.tar` - ❌ Nome genérico (evitar)
- ❌ `dump.tar` - ❌ Sem identificação do serviço

## 🔄 Funcionamento

1. **Durante o build da imagem Docker**:
   - O `Dockerfile` copia os arquivos `.tar` desta pasta para `/docker-entrypoint-initdb.d/` no container
   - Exemplo: `COPY backup/backup-directus-anonimizado.tar /docker-entrypoint-initdb.d/`

2. **Durante a primeira inicialização do container**:
   - O script `99-restore-db.sh` verifica se o arquivo de backup existe
   - Se existir e não houver flag de restauração anterior, executa `pg_restore`
   - Cria flag `.restored-<servico>-anonimizado` no pgdata para evitar restaurações duplicadas

3. **CLI Inteligente** (`pnpm versiona-ai docker:start`):
   - Detecta se volumes não existem ou têm ≤5 tabelas (banco vazio)
   - Pergunta de forma proativa se deseja restaurar o backup
   - Padrão: **Não** (seguro, evita perda de dados acidental)

## 📦 Como Adicionar Novo Backup

### 1. Gerar backup anonimizado:

```bash
# Exemplo para Directus
pg_dump -U postgres -d versiona-ai -F tar -f backup-directus-anonimizado.tar

# Exemplo para Superset (futuro)
pg_dump -U postgres -d superset -F tar -f backup-superset-anonimizado.tar
```

### 2. Colocar na pasta correta:

```bash
mv backup-directus-anonimizado.tar docker/postgres/backup/
```

### 3. Atualizar `Dockerfile`:

```dockerfile
# Adicionar linha para novo serviço
COPY backup/backup-superset-anonimizado.tar /docker-entrypoint-initdb.d/backup-superset-anonimizado.tar
```

### 4. Criar script de restore (opcional):

```bash
# Copiar e adaptar 99-restore-db.sh
cp docker/postgres/init/99-restore-db.sh docker/postgres/init/99-restore-superset.sh
# Editar: BACKUP_FILE, FLAG_FILE, DB_NAME
```

## 🔒 Segurança

⚠️ **Importante**: Backups contêm dados sensíveis!

- ✅ **Arquivos `.tar` são ignorados pelo Git** (`.gitignore`)
- ✅ **Dados devem ser anonimizados** antes de commit (se necessário)
- ❌ **Nunca fazer commit de backups com dados reais**

## 🧹 Limpeza

Remover backups antigos localmente:

```bash
# Remover backup específico
rm docker/postgres/backup/backup-directus-anonimizado.tar

# Rebuild da imagem sem cache para remover da imagem Docker
docker-compose build --no-cache directus_postgres_primary
```

## 📊 Tamanho dos Arquivos

| Backup                          | Tamanho | Tabelas | Observação                  |
| ------------------------------- | ------- | ------- | --------------------------- |
| backup-directus-anonimizado.tar | ~3.1GB  | 60      | Banco completo Directus v11 |
| backup-superset-anonimizado.tar | -       | -       | Futuro                      |

---

**Última atualização**: 2026-05-15
