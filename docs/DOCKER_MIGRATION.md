# 🐳 Atualização Docker para Orquestrador

## 📋 Resumo das Mudanças

Todos os arquivos Docker foram atualizados para executar o **Orquestrador de Processadores** ao invés de processadores individuais. Agora o sistema utiliza uma abordagem centralizada e coordenada.

## ✅ Arquivos Atualizados

### 1. **Dockerfile** (Principal)

- ✅ **Porta**: Mudou de `5005` para `5007` (orquestrador)
- ✅ **CMD**: Agora executa `gunicorn` com `wsgi_orquestrador:app`
- ✅ **Variáveis**: Adicionadas variáveis específicas do orquestrador:
  - `ORQUESTRADOR_MODO=sequencial`
  - `ORQUESTRADOR_INTERVALO=60`
  - `ORQUESTRADOR_PORTA=5007`
  - `ORQUESTRADOR_VERBOSE=false`
- ✅ **Health Check**: Atualizado para `http://localhost:5007/health`

### 2. **Dockerfile.uv** (Desenvolvimento)

- ✅ **Porta**: Mudou para `5007`
- ✅ **CMD**: Executa orquestrador diretamente com Python
- ✅ **Environment**: Configurado para desenvolvimento com verbose
- ✅ **Health Check**: Atualizado para porta do orquestrador

### 3. **docker-compose.yml** (Principal)

- ✅ **Service**: Renomeado de `docx-compare` para `docx-compare-orquestrador`
- ✅ **Container**: `docx-compare-orquestrador`
- ✅ **Porta**: `5007:5007`
- ✅ **Variáveis**: Adicionadas todas as configurações do orquestrador
- ✅ **Health Check**: Atualizado para endpoint do orquestrador

### 4. **docker-compose.production.yml** (Produção)

- ✅ **Serviços Atualizados**:
  - `docx-compare-orquestrador`: Serviço principal de produção
  - `docx-compare-dev`: Desenvolvimento com uv
  - `docx-compare-single`: Execução única para testes/CI
  - `docx-compare-test`: Testes automatizados
- ✅ **Profiles**: Organizados por ambiente (`dev`, `single`, `test`)
- ✅ **Comandos**: Todos usando orquestrador com diferentes configurações

### 5. **config/wsgi_orquestrador.py** (NOVO)

- ✅ **WSGI App**: Aplicação Flask específica para o orquestrador
- ✅ **Configuração**: Lê variáveis de ambiente do Docker
- ✅ **Signal Handling**: Encerramento gracioso com SIGINT/SIGTERM
- ✅ **Modos**: Suporte para single-run e contínuo

### 6. **config/gunicorn_orquestrador.conf.py** (NOVO)

- ✅ **Workers**: Configurado para 1 worker (singleton)
- ✅ **Porta**: Configurável via `ORQUESTRADOR_PORTA`
- ✅ **Logs**: Estruturados com informações do orquestrador
- ✅ **Hooks**: Logs informativos durante inicialização

### 7. **Makefile** (Comandos Docker)

- ✅ **Novos Comandos**:
  - `docker-up`: Iniciar com Docker Compose
  - `docker-up-prod`: Modo produção
  - `docker-up-dev`: Modo desenvolvimento
  - `docker-single`: Execução única
  - `docker-logs`: Ver logs
  - `docker-down`: Parar containers
  - `docker-build`: Build da imagem principal
  - `docker-run`: Container standalone
- ✅ **Help Atualizado**: Seção Docker prominente no help

### 8. **.env.example** (Configurações)

- ✅ **Variáveis do Orquestrador**:
  - `ORQUESTRADOR_MODO=sequencial`
  - `ORQUESTRADOR_INTERVALO=60`
  - `ORQUESTRADOR_PORTA=5007`
  - `ORQUESTRADOR_VERBOSE=false`
  - `ORQUESTRADOR_SINGLE_RUN=false`

## 🎯 Comandos de Uso

### Desenvolvimento Local

```bash
# Execução única (recomendado para testes)
make run-orquestrador-single

# Desenvolvimento com logs
make run-orquestrador-single-verbose
```

### Docker (Recomendado para Produção)

```bash
# Iniciar com Docker Compose (mais simples)
make docker-up

# Ver logs
make docker-logs

# Parar
make docker-down

# Execução única em container
make docker-single
```

### Diferentes Ambientes

```bash
# Produção
make docker-up-prod

# Desenvolvimento
make docker-up-dev

# Testes
docker-compose -f docker-compose.production.yml --profile test up
```

## 🔄 Migração do Sistema Antigo

### Antes (Sistema Antigo)

- ❌ **Processadores individuais** executando separadamente
- ❌ **Múltiplas portas** (5005, 5006) para monitorar
- ❌ **Coordenação manual** entre processadores
- ❌ **Docker** configurado para processador único

### Depois (Sistema Novo)

- ✅ **Orquestrador centralizado** gerencia tudo
- ✅ **Porta única** (5007) para monitoramento
- ✅ **Coordenação automática** sequencial ou paralela
- ✅ **Docker** otimizado para orquestração

## 📊 Portas e Endpoints

| Serviço          | Porta | Endpoint              | Descrição                       |
| ---------------- | ----- | --------------------- | ------------------------------- |
| **Orquestrador** | 5007  | http://localhost:5007 | Dashboard e coordenação         |
| Proc. Versões    | 5005  | http://localhost:5005 | Processador individual (legacy) |
| Proc. Modelos    | 5006  | http://localhost:5006 | Processador individual (legacy) |

## 🚀 Vantagens da Nova Arquitetura

### 🎯 **Coordenação Inteligente**

- Execução sequencial: modelo de contrato → automático
- Execução paralela: ambos simultaneamente
- Controle centralizado de ciclos e intervalos

### 🐳 **Docker Otimizado**

- Container único para todo o sistema
- Configuração simplificada
- Health checks unificados
- Logs centralizados

### 📊 **Monitoramento Unificado**

- Dashboard único em http://localhost:5007
- APIs REST para integração
- Métricas consolidadas
- Status de todos os processadores

### 🔧 **Operação Simplificada**

- Um comando para iniciar tudo: `make docker-up`
- Configuração via variáveis de ambiente
- Profiles para diferentes ambientes
- Encerramento gracioso

## ⚠️ Notas de Migração

### Para Usuários Existentes

1. **Atualizar comandos**: Use `make docker-up` ao invés de comandos individuais
2. **Nova porta**: Monitoramento agora em http://localhost:5007
3. **Variáveis de ambiente**: Adicione as novas variáveis `ORQUESTRADOR_*`

### Para Deployment

1. **Docker Compose**: Use o novo `docker-compose.yml`
2. **Health Checks**: Atualize para porta 5007
3. **Load Balancer**: Aponte para porta 5007
4. **Monitoring**: Configure alertas para a nova porta

## 🧪 Validação

✅ **Build testado**: `make docker-build` funcionando
✅ **Container funcional**: Inicialização sem erros
✅ **Configuração validada**: Variáveis de ambiente corretas
✅ **Health check**: Endpoint /health respondendo

## 📚 Documentação Relacionada

- **[docs/ORQUESTRADOR.md](docs/ORQUESTRADOR.md)**: Guia completo do orquestrador
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**: Endpoints e APIs
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Guia de deployment atualizado
- **[CHANGELOG.md](CHANGELOG.md)**: Histórico completo de mudanças

---

🎉 **Sistema Docker totalmente migrado para o Orquestrador!**
