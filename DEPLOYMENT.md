# Guia de Deployment - docx-compare

Este guia explica como fazer deploy da aplicação `docx-compare` usando GitHub Actions otimizados, Docker com arquitetura de estágios base e ferramentas Python modernas.

## 🚀 Workflows de GitHub Actions

### 1. **deploy.yml** - Workflow Padrão ✅
- **Trigger**: Push para `main`/`master`
- **Dockerfile**: `docker/Dockerfile.optimized`
- **Cache**: GitHub Actions Cache otimizado
- **Segurança**: Scan automático de vulnerabilidades
- **Testes**: Validação funcional da imagem

### 2. **deploy-advanced.yml** - Workflow Avançado 🚀
- **Trigger**: Push ou Manual (workflow_dispatch)
- **Escolha de Dockerfile**: optimized/secure/alpine
- **Cache**: Scoped por variante para máxima eficiência
- **Multi-platform**: Preparado para ARM64/AMD64
- **Segurança**: Trivy scan detalhado
- **Relatórios**: Summary completo no GitHub

### 3. **deploy-traditional.yml** - Compatibilidade
- **Trigger**: Push para `main`/`master`
- **Fallback**: Sem uv, usando pip tradicional

## ⚡ Principais Melhorias dos Workflows

### **Cache Inteligente:**
- **GitHub Actions Cache**: Reutilização de dependências Python
- **Docker BuildKit Cache**: Layers Docker reutilizáveis por variante
- **Base Stage Reuse**: Pandoc instalado apenas 1x por build

### **Segurança Integrada:**
- **Trivy Scanner**: Detecção automática de vulnerabilidades
- **Multi-stage builds**: Superfície de ataque reduzida
- **Non-root execution**: Princípio do menor privilégio

### **Flexibilidade:**
- **Manual triggers**: Escolha de Dockerfile via UI
- **Conditional push**: Push apenas quando necessário
- **Comprehensive reports**: Summaries detalhados no GitHub

## 🔧 Como Usar os Workflows

### Automático (Push)
```bash
git push origin main
# → Executa deploy.yml automaticamente
```

### Manual (Escolha de Dockerfile)
1. Acesse **Actions** no GitHub
2. Selecione **Advanced Build and Deploy**
3. Clique **Run workflow**
4. Escolha:
   - **Dockerfile**: optimized/secure/alpine
   - **Push to registry**: true/false
   - **Security scan**: true/false

## 🐳 Docker

### Imagens Disponíveis

1. **docker/Dockerfile.secure** - ✅ **Recomendado** - Sem vulnerabilidades
2. **docker/Dockerfile.alpine** - 🏔️ **Máxima segurança** - Base Alpine 
3. **Dockerfile.uv** - Otimizada com uv (atualizada com patches)
4. **Dockerfile** - Tradicional (⚠️ contém vulnerabilidades)

### Docker Compose

```bash
# Produção (imagem segura)
docker build -f docker/Dockerfile.secure -t docx-compare:secure .
docker run -p 8000:8000 docx-compare:secure

# Desenvolvimento
docker-compose -f docker-compose.production.yml --profile dev up -d

# Testes
docker-compose -f docker-compose.production.yml --profile test up
```

### Comandos Make

```bash
# Build imagem segura
make docker-build-secure

# Teste de segurança
make docker-scan

# Execução
make docker-run-secure
```

## ⚙️ Configuração do GitHub

### Secrets Necessários (Opcional)

Para push automático para Docker Hub:

```
DOCKER_USERNAME - seu usuário do Docker Hub
DOCKER_PASSWORD - sua senha/token do Docker Hub
```

### Variáveis de Ambiente

No arquivo `.env`:
```bash
FLASK_ENV=production
RESULTS_DIR=/app/results
PYTHONUNBUFFERED=1
```

## 🔧 Troubleshooting

### UV não funciona em produção?
- Use o workflow `deploy-traditional.yml`
- Set `USE_UV=false` no script de deploy

### Problemas de dependências?
```bash
# Limpar cache
uv cache clean
# ou
pip cache purge

# Reinstalar
uv sync --reinstall
# ou
pip install -r requirements.txt --force-reinstall
```

### Problemas de Docker?
```bash
# Limpar imagens
docker system prune -f

# Rebuild sem cache
docker build --no-cache -t docx-compare:latest .
```

## 📦 Estrutura do Projeto

```
docx-compare/
├── .github/workflows/
│   ├── deploy.yml              # Deploy com uv
│   └── deploy-traditional.yml  # Deploy tradicional
├── scripts/
│   └── deploy.sh              # Script de deploy
├── Dockerfile                 # Docker tradicional
├── Dockerfile.uv             # Docker otimizado
├── docker-compose.production.yml
└── pyproject.toml
```

## 🎯 Próximos Passos

1. Configure os secrets no GitHub (se usar Docker Hub)
2. Ajuste as portas e comandos conforme sua aplicação
3. Teste o deployment em ambiente de staging
4. Configure monitoring e logging

## 📚 Links Úteis

- [UV Documentation](https://docs.astral.sh/uv/)
- [GitHub Actions](https://docs.github.com/actions)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
