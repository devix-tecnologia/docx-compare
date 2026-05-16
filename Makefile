.PHONY: help install lint lint-fix format test test-coverage check run-processor run-api clean dev-server prod-server kill-server health-check taskin
.DEFAULT_GOAL := help

# Configuração
PYTHON := uv run python
UV := uv

help: ## Mostrar esta ajuda
	@echo "📚 Comandos disponíveis para docx-compare:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Exemplos de uso:"
	@echo "  make install                      # Instalar dependências"
	@echo "  make check                        # Verificação completa"
	@echo "  make run-orquestrador-single      # Executar todos os processadores (recomendado)"
	@echo "  make docker-up                    # Executar com Docker Compose"
	@echo ""
	@echo "🎯 Processadores disponíveis:"
	@echo "  🔄 Processador de Versões:"
	@echo "    run-processor                   # Modo contínuo"
	@echo "    run-processor-verbose           # Modo contínuo com logs"
	@echo "    run-processor-dry               # Modo simulação"
	@echo ""
	@echo "  🏷️  Processador de Modelos:"
	@echo "    run-processor-modelo            # Modo contínuo"
	@echo "    run-processor-modelo-verbose    # Modo contínuo com logs"
	@echo ""
	@echo "  🎯 Orquestrador (Execução Coordenada):"
	@echo "    run-orquestrador-single         # Execução única sequencial ⭐"
	@echo "    run-orquestrador-single-verbose # Execução única com logs"
	@echo "    run-orquestrador                # Modo contínuo paralelo"
	@echo "    run-orquestrador-sequencial     # Modo contínuo sequencial"
	@echo ""
	@echo "  🐳 Docker (Recomendado para Produção):"
	@echo "    docker-up                       # Iniciar com Docker Compose ⭐"
	@echo "    docker-single                   # Execução única em container"
	@echo "    docker-up-prod                  # Modo produção"
	@echo "    docker-up-dev                   # Modo desenvolvimento"
	@echo "    docker-logs                     # Ver logs do container"
	@echo "    docker-down                     # Parar containers"
	@echo ""
	@echo "  🌐 Servidor Web (Versiona AI):"
	@echo "    dev-server                      # Modo desenvolvimento com watch ⭐"
	@echo "    prod-server                     # Modo produção"
	@echo "    restart-dev                     # Reiniciar em modo dev"
	@echo "    kill-server                     # Parar servidor"
	@echo "    health-check                    # Verificar status"
	@echo "    test-version                    # Testar versão específica"
	@echo ""
	@echo "  🧪 Testes E2E (End-to-End):"
	@echo "    e2e-test                        # Testes E2E locais (requer servidor rodando)"
	@echo "    e2e-test-docker                 # Testes E2E completos com Docker ⭐"
	@echo "    e2e-up                          # Subir infraestrutura de testes"
	@echo "    e2e-down                        # Derrubar infraestrutura"
	@echo "    e2e-logs                        # Ver logs dos testes"
	@echo "    e2e-test-report                 # Abrir relatório HTML"
	@echo "    e2e-ci                          # Executar para CI/CD"
	@echo ""
	@echo "  🎭 Testes E2E UI (Task 011) - Interface de Usuário:"
	@echo "    e2e-ui-test                     # Testes completos UI (Playwright + SDK) ⭐"
	@echo "    e2e-ui-test-critical            # Apenas testes críticos Task 010 🎯"
	@echo "    e2e-ui-up                       # Subir infraestrutura UI"
	@echo "    e2e-ui-down                     # Derrubar infraestrutura UI"
	@echo "    e2e-ui-logs                     # Ver logs UI"
	@echo "    e2e-ui-shell                    # Shell interativo test-runner"
	@echo "    e2e-ui-test-playwright          # Apenas testes Playwright"
	@echo "    e2e-ui-test-sdk                 # Apenas validações SDK"
	@echo "    e2e-ui-test-report              # Abrir relatório HTML UI"
	@echo "    e2e-ui-rebuild                  # Rebuild containers UI"
	@echo "    e2e-ui-clean                    # Limpeza completa UI"
	@echo ""
	@echo "  📊 Monitoramento:"
	@echo "    Orquestrador:    http://localhost:5007"
	@echo "    Proc. Versões:   http://localhost:5005"
	@echo "    Proc. Modelos:   http://localhost:5006"
	@echo "    Versiona AI:     http://localhost:8001"

install: ## Instalar dependências do projeto
	@echo "📦 Instalando dependências..."
	$(UV) sync --group dev

lint: ## Executar linting com Ruff
	@echo "🔍 Executando linting..."
	$(UV) run ruff check .

lint-fix: ## Corrigir problemas de linting automaticamente
	@echo "🔧 Corrigindo problemas de linting..."
	$(UV) run ruff check --fix .

format: ## Formatar código com Ruff
	@echo "✨ Formatando código..."
	$(UV) run ruff format .

test: ## Executar testes
	@echo "🧪 Executando testes..."
	$(UV) run pytest tests/ -v

test-coverage: ## Executar testes com cobertura
	@echo "🧪 Executando testes com cobertura..."
	$(UV) run pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

check: lint format test ## Verificação completa do código
	@echo "✅ Verificação completa concluída!"

run-processor: ## Executar processador automático
	@echo "🤖 Iniciando processador automático..."
	$(PYTHON) src/docx_compare/processors/processador_automatico.py

run-processor-dry: ## Executar processador automático em modo dry-run
	@echo "🏃‍♂️ Iniciando processador automático (DRY-RUN)..."
	$(PYTHON) src/docx_compare/processors/processador_automatico.py --dry-run

run-processor-modelo: ## Executar processador de modelo de contrato
	@echo "🏷️ Iniciando processador de modelo de contrato..."
	$(PYTHON) src/docx_compare/processors/processador_modelo_contrato.py

run-processor-modelo-verbose: ## Executar processador de modelo de contrato com logs detalhados
	@echo "🏷️ Iniciando processador de modelo de contrato (VERBOSE)..."
	$(PYTHON) src/docx_compare/processors/processador_modelo_contrato.py --verbose

run-orquestrador: ## Executar orquestrador (todos os processadores em paralelo)
	@echo "🎯 Iniciando orquestrador de processadores..."
	$(PYTHON) src/docx_compare/processors/orquestrador.py

run-orquestrador-sequencial: ## Executar orquestrador em modo sequencial
	@echo "🎯 Iniciando orquestrador de processadores (sequencial)..."
	$(PYTHON) src/docx_compare/processors/orquestrador.py --modo sequencial

run-orquestrador-single: ## Executar orquestrador uma única vez
	@echo "🎯 Executando orquestrador (ciclo único)..."
	$(PYTHON) src/docx_compare/processors/orquestrador.py --single-run

run-orquestrador-verbose: ## Executar orquestrador com logs detalhados
	@echo "🎯 Iniciando orquestrador de processadores (verbose)..."
	$(PYTHON) src/docx_compare/processors/orquestrador.py --verbose

clean: ## Limpar arquivos temporários e cache
	@echo "🧹 Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -name "temp_*.html" -delete
	find . -name "temp_*.docx" -delete
	@echo "✅ Limpeza concluída!"

# Comandos de conveniência
dev: install ## Configurar ambiente de desenvolvimento
	@echo "🚀 Ambiente de desenvolvimento configurado!"
	@echo "💡 Use 'make help' para ver todos os comandos disponíveis"

# Comando para comparar documentos (exemplo)
compare: ## Exemplo: make compare ORIG=doc1.docx MOD=doc2.docx OUT=result.html
	@if [ -z "$(ORIG)" ] || [ -z "$(MOD)" ]; then \
		echo "❌ Erro: Especifique ORIG e MOD"; \
		echo "   Exemplo: make compare ORIG=doc1.docx MOD=doc2.docx [OUT=result.html]"; \
		exit 1; \
	fi
	@echo "📄 Comparando $(ORIG) com $(MOD)..."
	@if [ -n "$(OUT)" ]; then \
		$(PYTHON) -m src.docx_compare.core.docx_diff_viewer "$(ORIG)" "$(MOD)" "$(OUT)"; \
	else \
		$(PYTHON) -m src.docx_compare.core.docx_diff_viewer "$(ORIG)" "$(MOD)" "results/resultado.html"; \
		echo "✅ Resultado salvo em: results/resultado.html"; \
	fi

# Comando para análise sem gerar arquivo (dry-run)
analyze: ## Exemplo: make analyze ORIG=doc1.docx MOD=doc2.docx (apenas análise)
	@if [ -z "$(ORIG)" ] || [ -z "$(MOD)" ]; then \
		echo "❌ Erro: Especifique ORIG e MOD"; \
		echo "   Exemplo: make analyze ORIG=doc1.docx MOD=doc2.docx"; \
		exit 1; \
	fi
	@echo "🔍 Analisando $(ORIG) vs $(MOD) (dry-run)..."
	$(PYTHON) docx_diff_viewer.py "$(ORIG)" "$(MOD)" --dry-run --verbose

# Comando para testar com documentos de exemplo
demo: ## Demonstração com documentos de exemplo
	@echo "🎭 Executando demonstração com documentos de exemplo..."
	@if [ -f "documentos/doc-rafael-original.docx" ] && [ -f "documentos/doc-rafael-alterado.docx" ]; then \
		echo "📋 1. Análise rápida (dry-run):"; \
		$(PYTHON) docx_diff_viewer.py documentos/doc-rafael-original.docx documentos/doc-rafael-alterado.docx --dry-run; \
		echo ""; \
		echo "📄 2. Gerando relatório HTML:"; \
		$(PYTHON) docx_diff_viewer.py documentos/doc-rafael-original.docx documentos/doc-rafael-alterado.docx results/demo.html --style modern; \
		echo "✅ Demonstração concluída! Veja results/demo.html"; \
	else \
		echo "⚠️  Documentos de exemplo não encontrados em documentos/"; \
	fi

# Comando para rodar um teste específico
test-file: ## Executar um arquivo de teste específico: make test-file FILE=test_arquivo.py
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Erro: Especifique o arquivo de teste"; \
		echo "   Exemplo: make test-file FILE=tests/test_imports.py"; \
		exit 1; \
	fi
	@echo "🧪 Executando teste: $(FILE)..."
	$(PYTHON) "$(FILE)"

## 🐳 Docker Commands

# Docker Compose Commands (Orquestrador)
docker-up: ## Iniciar orquestrador com Docker Compose
	@echo "🚀 Iniciando orquestrador com Docker Compose..."
	docker-compose up -d

docker-up-prod: ## Iniciar orquestrador em modo produção
	@echo "🏭 Iniciando orquestrador em modo produção..."
	docker-compose -f docker-compose.production.yml up -d

docker-up-dev: ## Iniciar orquestrador em modo desenvolvimento
	@echo "🔧 Iniciando orquestrador em modo desenvolvimento..."
	docker-compose -f docker-compose.production.yml --profile dev up -d

docker-single: ## Executar orquestrador uma única vez
	@echo "🎯 Executando orquestrador em modo single-run..."
	docker-compose -f docker-compose.production.yml --profile single up --rm docx-compare-single

docker-logs: ## Ver logs do orquestrador
	@echo "📋 Visualizando logs do orquestrador..."
	docker-compose logs -f docx-compare-orquestrador

docker-down: ## Parar e remover containers
	@echo "🛑 Parando containers..."
	docker-compose down

docker-build: ## Build da imagem principal (orquestrador)
	@echo "🏗️ Construindo imagem do orquestrador..."
	docker build -f docker/Dockerfile.orquestrador -t docx-compare:latest .

docker-run: ## Executar orquestrador em container standalone
	@echo "🎯 Executando orquestrador em container..."
	docker run -d --name docx-compare-orquestrador \
		-p 5007:5007 \
		-v $(PWD)/results:/app/results \
		-v $(PWD)/logs:/app/logs \
		-e DIRECTUS_BASE_URL=${DIRECTUS_BASE_URL} \
		-e DIRECTUS_TOKEN=${DIRECTUS_TOKEN} \
		-e ORQUESTRADOR_MODO=sequencial \
		docx-compare:latest

# Comandos Docker existentes (imagens especializadas)
docker-build-secure: ## Build da imagem Docker segura
	@echo "🐳 Construindo imagem Docker segura..."
	docker build -f docker/Dockerfile.secure -t docx-compare:secure .

docker-build-alpine: ## Build da imagem Docker Alpine (máxima segurança)
	@echo "🏔️ Construindo imagem Docker Alpine..."
	docker build -f docker/Dockerfile.alpine -t docx-compare:alpine .

docker-build-optimized: ## Build da imagem Docker super otimizada (recomendado)
	@echo "⚡ Construindo imagem Docker otimizada com cache..."
	docker build -f docker/Dockerfile.optimized -t docx-compare:optimized .

docker-run-secure: ## Executar container seguro
	@echo "🚀 Executando container seguro..."
	docker run -p 5007:5007 -v $(PWD)/results:/app/results docx-compare:secure

docker-run-optimized: ## Executar container otimizado
	@echo "⚡ Executando container otimizado..."
	docker run -p 5007:5007 -v $(PWD)/results:/app/results docx-compare:optimized

docker-scan: ## Scan de vulnerabilidades na imagem
	@echo "🔍 Verificando vulnerabilidades..."
	docker scout cves docx-compare:latest || echo "Docker Scout não disponível, use: docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image docx-compare:latest"

docker-test: docker-build ## Build e teste da imagem principal
	@echo "✅ Testando imagem do orquestrador..."
	docker run --rm -e ORQUESTRADOR_SINGLE_RUN=true docx-compare:latest

docker-benchmark: ## Comparar tamanhos das imagens Docker
	@echo "📊 Comparando tamanhos das imagens..."
	@echo "🎯 Dockerfile principal (orquestrador):"
	@docker images docx-compare:latest --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"
	@echo "🛡️ Dockerfile.secure:"
	@docker images docx-compare:secure --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"
	@echo "🏔️ Dockerfile.alpine:"
	@docker images docx-compare:alpine --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"
	@echo "⚡ Dockerfile.optimized:"
	@docker images docx-compare:optimized --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"

# Comandos para servidor de desenvolvimento
dev-server: ## Rodar servidor em modo desenvolvimento com watch & reload
	@echo "🔧 Iniciando servidor em modo DESENVOLVIMENTO"
	@echo "📝 Watch & Reload ativo - alterações serão detectadas automaticamente"
	@DEV_MODE=true FLASK_PORT=8001 $(UV) run python versiona-ai/directus_server.py

prod-server: ## Rodar servidor em modo produção
	@echo "🏭 Iniciando servidor em modo PRODUÇÃO"
	@DEV_MODE=false FLASK_PORT=8001 $(UV) run python versiona-ai/directus_server.py

kill-server: ## Matar processos do servidor na porta 8001
	@echo "🛑 Encerrando processos na porta 8001..."
	@lsof -ti:8001 | xargs kill -9 2>/dev/null || echo "✅ Nenhum processo encontrado"

health-check: ## Verificar status do servidor
	@echo "🔍 Verificando status do servidor..."
	@curl -s http://localhost:8001/health | jq . || echo "❌ Servidor não está respondendo"

test-version: ## Testar versão específica no servidor
	@echo "🧪 Testando versão c2b1dfa0-c664-48b8-a5ff-84b70041b428..."
	@curl -s "http://localhost:8001/versao/c2b1dfa0-c664-48b8-a5ff-84b70041b428" | head -10

restart-dev: kill-server ## Reiniciar servidor em modo dev (mata processo anterior e inicia novo)
	@sleep 1
	@make dev-server

# ============================================================================
# 🧪 E2E Testing (docker-compose.test.yml)
# ============================================================================

e2e-test: ## Executar testes E2E completos (local)
	@echo "🧪 Executando testes E2E locais..."
	@echo "⚠️  Certifique-se de que o servidor está rodando: make dev-server"
	$(UV) run pytest tests/e2e/ -v -s

e2e-test-docker: ## Executar testes E2E com docker-compose
	@echo "🐳 Iniciando testes E2E com Docker..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@echo "🧹 Limpando containers..."
	docker-compose -f docker-compose.test.yml down

e2e-up: ## Subir infraestrutura de teste (API server)
	@echo "🚀 Iniciando infraestrutura de testes..."
	docker-compose -f docker-compose.test.yml up -d api-server
	@echo "⏳ Aguardando health check..."
	@sleep 5
	@echo "✅ Infraestrutura pronta!"

e2e-down: ## Derrubar infraestrutura de teste
	@echo "🛑 Parando infraestrutura de testes..."
	docker-compose -f docker-compose.test.yml down -v

e2e-logs: ## Ver logs da infraestrutura de testes
	@echo "📋 Logs da infraestrutura de testes:"
	docker-compose -f docker-compose.test.yml logs -f

e2e-test-runner: ## Executar apenas test runner (assumindo infra já está up)
	@echo "🏃 Executando test runner..."
	docker-compose -f docker-compose.test.yml run --rm test-runner

e2e-test-production: ## Executar testes E2E contra produção (CUIDADO!)
	@echo "⚠️  ATENÇÃO: Executando testes contra PRODUÇÃO!"
	@echo "📝 Confirme definindo E2E_ALLOW_PRODUCTION=true no .env.e2e"
	$(UV) run pytest tests/e2e/ -v -s --e2e-production

e2e-ci: ## Executar testes E2E para CI/CD (sem interação)
	@echo "🤖 Executando testes E2E para CI/CD..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test-runner
	docker-compose -f docker-compose.test.yml down -v

e2e-test-report: ## Abrir relatório HTML dos testes E2E
	@echo "📊 Abrindo relatório de testes..."
	@if [ -f "test-results/report.html" ]; then \
		open test-results/report.html || xdg-open test-results/report.html; \
	else \
		echo "❌ Relatório não encontrado. Execute 'make e2e-test-docker' primeiro."; \
	fi

# ============================================================================
# 🎭 E2E UI Testing (Task 011) - Interface de Usuário
# ============================================================================

e2e-ui-test: ## 🎭 Executar testes E2E UI completos (Playwright + SDK) ⭐
	@echo "🎭 Executando testes E2E via Interface de Usuário..."
	@echo ""
	@echo "📦 Stack: Directus + PostgreSQL + API + Test Runner"
	@echo "🧪 Testes: Playwright (UI) + Directus SDK (dados)"
	@echo "🎯 Validação: Task 010 (vinculação cláusulas-modificações)"
	@echo ""
	docker-compose -f docker-compose.ui-test.yml up --build --abort-on-container-exit --exit-code-from test-runner
	@echo "🧹 Limpando containers..."
	docker-compose -f docker-compose.ui-test.yml down

e2e-ui-up: ## Subir infraestrutura E2E UI (sem executar testes)
	@echo "🚀 Subindo infraestrutura E2E UI..."
	docker-compose -f docker-compose.ui-test.yml up -d postgres directus api-server
	@echo ""
	@echo "✅ Serviços rodando:"
	@echo "   🐘 PostgreSQL:  localhost:5432"
	@echo "   📊 Directus:    http://localhost:8055"
	@echo "   🔧 API:         http://localhost:8001"
	@echo ""
	@echo "Para executar testes:"
	@echo "   make e2e-ui-shell   # Shell interativo no test-runner"
	@echo "   make e2e-ui-down    # Derrubar ambiente"

e2e-ui-down: ## Derrubar infraestrutura E2E UI
	@echo "🛑 Derrubando infraestrutura E2E UI..."
	docker-compose -f docker-compose.ui-test.yml down -v

e2e-ui-logs: ## Ver logs dos serviços E2E UI
	@echo "📋 Logs da infraestrutura E2E UI..."
	docker-compose -f docker-compose.ui-test.yml logs -f

e2e-ui-shell: ## Shell interativo no test-runner E2E UI
	@echo "🐚 Abrindo shell no test-runner..."
	docker-compose -f docker-compose.ui-test.yml run --rm test-runner sh

e2e-ui-test-playwright: ## Executar apenas testes UI (Playwright)
	@echo "🎭 Executando testes Playwright..."
	docker-compose -f docker-compose.ui-test.yml run --rm test-runner \
		pytest tests/e2e_ui/test_ui_*.py -v -s --headed

e2e-ui-test-sdk: ## Executar apenas validações de dados (SDK)
	@echo "📊 Executando validações via SDK..."
	docker-compose -f docker-compose.ui-test.yml run --rm test-runner \
		pytest tests/e2e_ui/test_sdk_*.py -v -s

e2e-ui-test-critical: ## 🎯 Executar apenas testes críticos (Task 010) ⭐
	@echo "🎯 Executando testes críticos Task 010..."
	docker-compose -f docker-compose.ui-test.yml run --rm test-runner \
		pytest tests/e2e_ui/test_ui_visualizar_modificacoes.py -v -s -m critical

e2e-ui-watch: ## 👁️  Executar testes E2E UI em MODO VISUAL (Playwright com janela) ⭐
	@echo "👁️  Modo UI Visual - Playwright com janela do navegador"
	@echo ""
	@echo "📦 Verificando serviços..."
	@if ! docker ps | grep -q e2e-ui-directus; then \
		echo "🚀 Subindo serviços (Directus, PostgreSQL, API)..."; \
		docker-compose -f docker-compose.ui-test.yml up -d postgres directus api-server; \
		echo "⏳ Aguardando 30s para serviços iniciarem..."; \
		sleep 30; \
	else \
		echo "✅ Serviços já estão rodando"; \
	fi
	@echo ""
	@echo "🎭 Executando testes com Playwright UI..."
	@echo "   📊 Directus:  http://localhost:8065"
	@echo "   🔧 API:       http://localhost:8011"
	@echo ""
	@cd tests/e2e_ui && \
		export $$(cat .env.e2e.ui.local | grep -v '^#' | xargs) && \
		$(UV) run pytest -v -s --headed --override-ini="addopts=" -o "python_files=test_*.py"
	@echo ""
	@echo "💡 Dica: Para derrubar serviços, execute: make e2e-ui-down"

e2e-ui-test-report: ## Abrir relatório HTML dos testes E2E UI
	@echo "📊 Abrindo relatório de testes E2E UI..."
	@if [ -f "test-results/report-ui.html" ]; then \
		open test-results/report-ui.html || xdg-open test-results/report-ui.html; \
	else \
		echo "❌ Relatório não encontrado. Execute 'make e2e-ui-test' primeiro."; \
	fi

e2e-ui-rebuild: ## Rebuild dos containers E2E UI (sem cache)
	@echo "🔨 Reconstruindo containers E2E UI..."
	docker-compose -f docker-compose.ui-test.yml build --no-cache

e2e-ui-clean: e2e-ui-down ## Limpar ambiente E2E UI completamente
	@echo "🧹 Limpando volumes e imagens E2E UI..."
	docker volume prune -f
	@echo "✅ Limpeza E2E UI concluída!"

e2e-ui-uploads: ## 📁 Listar arquivos na pasta uploads do Directus E2E
	@echo "📁 Conteúdo de tests/e2e_ui/uploads/:"
	@ls -lhR tests/e2e_ui/uploads/ || echo "❌ Pasta não encontrada"

e2e-ui-uploads-add: ## 📤 Adicionar arquivo aos uploads (uso: make e2e-ui-uploads-add FILE=/caminho/arquivo.docx)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Erro: especifique o arquivo com FILE=/caminho/arquivo.docx"; \
		exit 1; \
	fi
	@echo "📤 Copiando $(FILE) para tests/e2e_ui/uploads/..."
	@cp "$(FILE)" tests/e2e_ui/uploads/
	@echo "✅ Arquivo copiado! Reinicie o Directus se necessário: make e2e-ui-down && make e2e-ui-up"

e2e-ui-uploads-clean: ## 🧹 Limpar pasta uploads (exceto README e .gitignore)
	@echo "🧹 Limpando uploads..."
	@cd tests/e2e_ui/uploads && find . -maxdepth 1 -type f ! -name 'README.md' ! -name '.gitignore' -delete
	@echo "✅ Uploads limpos!"

# ============================================================================
# 📋 Task Management (pnpx taskin wrapper)
# ============================================================================

taskin: ## Executar pnpx taskin através do uv (ex: make taskin ARGS="start 5")
	$(UV) run taskin $(ARGS)
