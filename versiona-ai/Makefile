# Makefile para Versiona AI
# Gerenciamento de testes E2E UI com Playwright + Docker

.PHONY: help e2e-ui-test e2e-ui-up e2e-ui-down e2e-ui-logs e2e-ui-shell e2e-ui-watch
.DEFAULT_GOAL := help

# Detectar UV (gerenciador de pacotes Python)
UV := $(shell command -v uv 2> /dev/null)
ifndef UV
$(error "UV não encontrado. Instale: https://github.com/astral-sh/uv")
endif

help: ## Mostrar esta ajuda
	@echo "🎭 Versiona AI - Testes E2E UI"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""

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
	@echo "   📊 Directus:    http://localhost:8065"
	@echo "   🔧 API:         http://localhost:8011"
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
	@if [ -f "../test-results/report-ui.html" ]; then \
		open ../test-results/report-ui.html || xdg-open ../test-results/report-ui.html; \
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

# ============================================================================
# 📁 Gerenciamento de Uploads do Directus
# ============================================================================

e2e-ui-uploads: ## 📁 Listar arquivos na pasta uploads do Directus E2E
	@echo "📁 Conteúdo de tests/e2e_ui/uploads/:"
	@ls -lhR tests/e2e_ui/uploads/ || echo "❌ Pasta não encontrada"

e2e-ui-uploads-add: ## 📤 Adicionar arquivo aos uploads (uso: make e2e-ui-uploads-add FILE=/caminho/arquivo.docx)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Erro: especifique o arquivo com FILE=/caminho/arquivo.docx"; \
		exit 1; \
	fi
	@echo "📤 Copiando $(FILE) para tests/e2e_ui/uploads/..."; \
	@cp "$(FILE)" tests/e2e_ui/uploads/
	@echo "✅ Arquivo copiado! Reinicie o Directus se necessário: make e2e-ui-down && make e2e-ui-up"

e2e-ui-uploads-clean: ## 🧹 Limpar pasta uploads (exceto README)
	@echo "🧹 Limpando uploads..."
	@cd tests/e2e_ui/uploads && find . -maxdepth 1 -type f ! -name 'README.md' ! -name 'exemplo-*.txt' -delete
	@echo "✅ Uploads limpos!"
