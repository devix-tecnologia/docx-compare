# Makefile para deploy do Versiona AI

.PHONY: help build up down logs clean restart

# Variáveis
COMPOSE_FILE = docker-compose.simple.yml
COMPOSE_FILE_FULL = docker-compose.yml

help: ## Mostrar ajuda
	@echo "🚀 Deploy do Versiona AI"
	@echo ""
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Configurar ambiente inicial
	@echo "📋 Configurando ambiente..."
	@cp -n .env.example .env || true
	@echo "✅ Arquivo .env criado (edite com suas configurações)"
	@mkdir -p data/{logs,results,temp}
	@echo "✅ Diretórios de dados criados"

build: ## Construir imagem Docker
	@echo "🔨 Construindo imagem..."
	@docker-compose -f $(COMPOSE_FILE) build

up: ## Iniciar serviços (simples)
	@echo "🚀 Iniciando Versiona AI..."
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "✅ Serviços iniciados!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔌 API: http://localhost:8000"

up-full: ## Iniciar serviços completos (com Nginx)
	@echo "🚀 Iniciando Versiona AI completo..."
	@docker-compose -f $(COMPOSE_FILE_FULL) up -d
	@echo "✅ Serviços iniciados!"
	@echo "🌐 Acesse: http://localhost:80"

down: ## Parar serviços
	@echo "⏹️  Parando serviços..."
	@docker-compose -f $(COMPOSE_FILE) down
	@docker-compose -f $(COMPOSE_FILE_FULL) down 2>/dev/null || true

logs: ## Ver logs
	@docker-compose -f $(COMPOSE_FILE) logs -f

status: ## Ver status dos containers
	@echo "📊 Status dos containers:"
	@docker-compose -f $(COMPOSE_FILE) ps

health: ## Verificar saúde da aplicação
	@echo "🩺 Verificando saúde..."
	@curl -f http://localhost:8000/health || echo "❌ API não está respondendo"
	@curl -f http://localhost:3000/ >/dev/null 2>&1 || echo "❌ Frontend não está respondendo"

restart: ## Reiniciar serviços
	@echo "🔄 Reiniciando..."
	@make down
	@make up

clean: ## Limpar containers e imagens
	@echo "🧹 Limpando..."
	@docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	@docker-compose -f $(COMPOSE_FILE_FULL) down -v --remove-orphans 2>/dev/null || true
	@docker system prune -f

rebuild: ## Rebuild completo
	@echo "🔄 Rebuild completo..."
	@make down
	@make build
	@make up

dev: ## Modo desenvolvimento (logs em tempo real)
	@echo "🛠️  Modo desenvolvimento..."
	@docker-compose -f $(COMPOSE_FILE) up --build

prod: ## Deploy de produção
	@echo "🏭 Deploy de produção..."
	@make setup
	@make build
	@make up-full

# Comandos de debug
shell-api: ## Entrar no container da API
	@docker exec -it versiona-ai-api bash

shell-web: ## Entrar no container do frontend
	@docker exec -it versiona-ai-web sh

shell: shell-api ## Alias para shell-api

debug-logs: ## Ver logs detalhados
	@echo "📋 Logs do Gunicorn Access:"
	@docker exec versiona-ai-api tail -f /app/logs/gunicorn_access.log &
	@echo "📋 Logs do Gunicorn Error:"
	@docker exec versiona-ai-api tail -f /app/logs/gunicorn_error.log

test-api: ## Testar API
	@echo "🧪 Testando API..."
	@curl -s http://localhost:8000/health | jq . || echo "❌ Falha no teste"
	@curl -s http://localhost:8000/api/status | jq . || echo "❌ Falha no status"
