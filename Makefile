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
	$(PYTHON) -m src.docx_compare.processors.processador_automatico

run-processor-dry: ## Executar processador automático em modo dry-run
	@echo "🏃‍♂️ Iniciando processador automático (DRY-RUN)..."
	$(PYTHON) -m src.docx_compare.processors.processador_automatico --dry-run

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
	docker run -p 8000:8000 -v $(PWD)/results:/app/results docx-compare:secure

docker-run-optimized: ## Executar container otimizado
	@echo "⚡ Executando container otimizado..."
	docker run -p 8000:8000 -v $(PWD)/results:/app/results docx-compare:optimized

docker-scan: ## Scan de vulnerabilidades na imagem
	@echo "🔍 Verificando vulnerabilidades..."
	docker scout cves docx-compare:secure || echo "Docker Scout não disponível, use: docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image docx-compare:secure"

docker-test-secure: docker-build-secure ## Build e teste da imagem segura
	@echo "✅ Testando imagem segura..."
	docker run --rm docx-compare:secure python -c "import src.main; print('✅ Imagem funcionando!')"

docker-benchmark: ## Comparar tamanhos das imagens Docker
	@echo "📊 Comparando tamanhos das imagens..."
	@echo "🐳 Dockerfile original:"
	@docker images docx-compare:latest --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"
	@echo "🛡️ Dockerfile.secure:"
	@docker images docx-compare:secure --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"
	@echo "🏔️ Dockerfile.alpine:"
	@docker images docx-compare:alpine --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"
	@echo "⚡ Dockerfile.optimized:"
	@docker images docx-compare:optimized --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null || echo "  Não encontrada"
