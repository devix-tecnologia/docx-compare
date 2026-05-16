# PostgreSQL Secrets

Este diretório contém os arquivos de secrets (senhas) utilizados pelos serviços PostgreSQL.

## ⚠️ Segurança

**Os arquivos `.txt` NÃO devem ser commitados no Git!** Apenas os arquivos `.example` são versionados.

## 📁 Arquivos de Secrets

### Cluster Directus:

- **`db_password.txt`** - Senha do usuário principal do PostgreSQL (`versiona-ai_user`)
- **`replication_password.txt`** - Senha do usuário de replicação para streaming replication
- **`senha_usuario_directus.txt`** - Senha do usuário `usuario_directus` (usado pelo Directus)
- **`senha_usuario_pgadmin.txt`** - Senha do usuário `usuario_pgadmin` (read-only para administração)
- **`senha_usuario_postgres_exporter.txt`** - Senha do usuário `postgres_exporter` (métricas Prometheus)
- **`senha_usuario_superset_leitura.txt`** - Senha do usuário `usuario_superset_leitura` (read-only para BI)

### Cluster Superset:

- **`superset_db_password.txt`** - Senha do usuário principal do PostgreSQL Superset
- **`superset_replication_password.txt`** - Senha do usuário de replicação do cluster Superset

## 🚀 Setup Inicial

### 1. Copiar os exemplos:

```bash
cd docker/postgres/secrets
for file in *.example; do
  cp "$file" "${file%.example}"
done
```

### 2. Gerar senhas seguras:

**Linux/macOS:**

```bash
# Gerar senha aleatória de 32 caracteres
openssl rand -base64 32
```

**Ou usando pwgen:**

```bash
pwgen -s 32 1
```

### 3. Editar os arquivos:

Substitua o conteúdo de cada arquivo `.txt` por senhas seguras geradas.

```bash
echo "sua_senha_forte_gerada" > db_password.txt
echo "senha_replicacao_forte" > replication_password.txt
# ... e assim por diante
```

## 🔒 Boas Práticas

1. ✅ Use senhas de **no mínimo 16 caracteres**
2. ✅ Combine letras maiúsculas, minúsculas, números e símbolos
3. ✅ Use senhas **diferentes para cada serviço**
4. ✅ Mantenha as senhas em um **gerenciador de senhas**
5. ❌ **NUNCA** commite os arquivos `.txt` no Git
6. ❌ **NUNCA** compartilhe senhas via chat/email/tickets

## 📋 Verificação

Para verificar se todos os secrets foram configurados:

```bash
cd docker/postgres/secrets
ls -1 *.txt 2>/dev/null | wc -l
```

Deve retornar **8 arquivos**.

## 🐳 Docker Secrets

Estes arquivos são montados como Docker secrets nos containers via:

```yaml
secrets:
  db_password:
    file: ./docker/postgres/secrets/db_password.txt
  # ...etc
```

No container, acessíveis via `/run/secrets/<nome_do_secret>`.
