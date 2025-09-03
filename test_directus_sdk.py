#!/usr/bin/env python3
"""
Teste simples do SDK do Directus
"""

import os
from directus_sdk_py import DirectusClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DIRECTUS_BASE_URL = os.getenv('DIRECTUS_BASE_URL', 'https://contract.devix.co').replace('/admin/', '').rstrip('/')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN', 'your-directus-token')

print(f"🔗 Testando conexão com: {DIRECTUS_BASE_URL}")
print(f"🔑 Token: {DIRECTUS_TOKEN[:20]}...")

# Cliente Directus
directus_client = DirectusClient(url=DIRECTUS_BASE_URL, token=DIRECTUS_TOKEN)

try:
    # Teste simples de buscar versões sem filtro primeiro
    print("📋 Buscando todas as versões...")
    versoes_all = directus_client.get_items("versao")
    
    print(f"📊 Quantidade total: {len(versoes_all)}")
    
    # Mostrar o status de cada versão
    for versao in versoes_all:
        print(f"  ID: {versao['id'][:8]}... Status: {versao.get('status', 'N/A')}")
    
    # Agora teste com filtro simplificado
    print("\n📋 Testando filtro simples...")
    
    # Tentar sintaxe mais simples
    versoes_filtradas = directus_client.get_items("versao", {
        "filter": {
            "status": "processar"
        }
    })
    
    print(f"� Tipo do retorno (filtrado): {type(versoes_filtradas)}")
    print(f"📊 Conteúdo do retorno (filtrado): {versoes_filtradas}")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
