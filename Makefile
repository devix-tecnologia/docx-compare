.PHONY: help install lint lint-fix format test test-coverage check run-processor run-api clean
.DEFAULT_GOAL := help

# Configuração
PYTHON := uv run python
UV := uv

help: ## Mostrar esta ajuda
	@echo "📚 Comandos disponíveis para docx-compare:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Exemplos de uso:"
	@echo "  make install       # Instalar dependências"
	@echo "  make check         # Verificação completa"
	@echo "  make run-processor # Executar processador automático"

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
	$(PYTHON) processador_automatico.py

run-api: ## Executar API simples
	@echo "🌐 Iniciando API simples..."
	$(PYTHON) api_simple.py

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
		$(PYTHON) docx_diff_viewer.py "$(ORIG)" "$(MOD)" "$(OUT)"; \
	else \
		$(PYTHON) docx_diff_viewer.py "$(ORIG)" "$(MOD)"; \
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
