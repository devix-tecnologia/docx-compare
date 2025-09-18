#!/bin/bash
# Script para executar o servidor API matando processos anteriores

echo "🧹 Limpando processos anteriores..."

# Matar processos específicos do servidor
pkill -f "simple_api_server.py" 2>/dev/null || true

# Matar processos nas portas
lsof -ti:5005,5006,5007 | xargs kill -9 2>/dev/null || true

# Aguardar um pouco para garantir que os processos foram mortos
sleep 2

echo "🚀 Iniciando servidor API em background..."

# Executar o servidor em background
cd /Users/sidarta/repositorios/docx-compare
nohup uv run python versiona-ai/simple_api_server.py > api_server.log 2>&1 &

# Pegar o PID do processo
API_PID=$!
echo "📝 Servidor iniciado com PID: $API_PID"
echo "📊 Health check disponível em: http://localhost:5007/health"
echo "📋 Log do servidor: api_server.log"

# Aguardar um pouco para o servidor iniciar
sleep 3

# Testar se o servidor está rodando
if curl -s http://localhost:5007/health > /dev/null; then
    echo "✅ Servidor API está rodando!"
else
    echo "❌ Erro ao iniciar o servidor. Verifique api_server.log"
fi
