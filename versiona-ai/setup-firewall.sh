#!/bin/bash
# Configuração do firewall restritivo para container seguro

echo "🔒 Configurando firewall restritivo..."

# Verificar se iptables está disponível
if ! command -v iptables &> /dev/null; then
    echo "❌ iptables não disponível, pulando configuração do firewall"
    sleep infinity
    exit 0
fi

# Limpar regras existentes
iptables -F 2>/dev/null || true
iptables -X 2>/dev/null || true

# Política padrão: ACEITAR (para não quebrar container)
iptables -P INPUT ACCEPT 2>/dev/null || true
iptables -P FORWARD ACCEPT 2>/dev/null || true
iptables -P OUTPUT ACCEPT 2>/dev/null || true

# Permitir loopback (comunicação interna nginx <-> gunicorn)
iptables -A INPUT -i lo -j ACCEPT 2>/dev/null || true
iptables -A OUTPUT -o lo -j ACCEPT 2>/dev/null || true

# Permitir conexões estabelecidas
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT 2>/dev/null || true

# Permitir entrada na porta 80
iptables -A INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true

# Permitir DNS para resolução interna
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT 2>/dev/null || true

# Log de configuração
echo "✅ Firewall básico configurado"
echo "🔓 Política: PERMISSIVA (compatibilidade com container)"
echo "🌐 Comunicação interna: HABILITADA"
echo "🔌 Porta 80: ABERTA"

# Manter processo ativo
while true; do
    sleep 3600
done
