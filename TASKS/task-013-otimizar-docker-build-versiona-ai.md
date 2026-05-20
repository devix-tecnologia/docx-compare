# Task 013 — Otimizar Docker Build - Versiona AI

Status: pending
Type: refactor
Assignee: Sidarta Veloso

## Description

A imagem Docker atual tem ~1.29GB devido a inclusão de arquivos de desenvolvimento (~110-215MB) e ferramentas de build no runtime (~300-400MB). Otimizar através de multi-stage build, .dockerignore aprimorado e separação de dependências prod/dev.

**Problema**: Build lento (~240s), imagem grande (~1.29GB), sem aproveitamento de layer cache, arquivos desnecessários no runtime.

**Escopo**: Otimização de Dockerfile, .dockerignore, pyproject.toml e scripts de build. Tornar BuildKit opcional (incompatível com Colima no macOS).

## Tasks

- [ ] Criar `.dockerignore` otimizado excluindo ~40 patterns (tests/, test*\*.py, debug*\*.py, web/node_modules/, web/src/, exemplos/, backups/, htmlcov/)
- [ ] Implementar multi-stage Dockerfile separando builder (deps + build tools) de runtime (apenas produção)
- [ ] Atualizar pyproject.toml com `[dependency-groups]` separando prod vs dev
- [ ] Substituir `COPY versiona-ai/ .` por cópias seletivas (directus_server.py, wsgi.py, core/, matching/, repositorio.py, docx_utils.py, templates/, assets/, web/dist/)
- [ ] Usar `uv sync --frozen --no-dev` para instalar apenas dependências de produção
- [ ] Otimizar ordem de layers para maximizar cache (COPY dependências antes de código)
- [ ] Adicionar variável `USE_BUILDKIT` em scripts de build com default=false (compatibilidade Colima macOS)
- [ ] Atualizar scripts de build (build-and-push-complete.sh) para suportar `DOCKER_BUILDKIT` opcional
- [ ] Validar redução de tamanho (~800-900MB), tempo de rebuild (~10s com cache) e funcionalidade (/health endpoint)

## Notes

- BuildKit incompatível com Colima no macOS: tornar configurável via `USE_BUILDKIT=1` (default off)
- Manter Debian Slim (não Alpine) para evitar builds 2-3x mais lentos
- Preservar web/dist/ pré-buildado (frontend já compilado, não precisa de node_modules no Docker)
- Incluir implementacoes_mock.py (~10KB) e swagger_docs.py para testes de integração e documentação
- Python não precisa minificação (diferente de JavaScript): bytecode é gerado automaticamente pelo runtime

## Validation

- Tamanho da imagem: `docker images versiona-ai:optimized` deve mostrar ~800-900MB (vs ~1.29GB atual)
- Conteúdo: `docker run --rm versiona-ai:optimized ls -la /app/` não deve ter tests/, debug\_\*.py, node_modules/
- Funcionalidade: `docker run -p 8001:8001 --env-file .env versiona-ai:optimized` → curl http://localhost:8001/health
- Layer cache: rebuild após mudança em .py deve usar cache até step de COPY código (~10s vs ~240s)
- Startup: container deve iniciar directus_server.py sem erros de import
- BuildKit opcional: build deve funcionar com e sem `DOCKER_BUILDKIT=1`
