#!/usr/bin/env python3
"""
Teste direto com requests para o webhook.site
"""

import requests
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

DIRECTUS_BASE_URL = os.getenv('DIRECTUS_BASE_URL')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN')

print(f"🔗 URL: {DIRECTUS_BASE_URL}")
print(f"🔑 Token: {DIRECTUS_TOKEN}")

# Headers
headers = {
    'Authorization': f'Bearer {DIRECTUS_TOKEN}',
    'Content-Type': 'application/json'
}

# Teste 1: GET simples
print("\n🧪 Teste 1: GET simples")
url1 = f"{DIRECTUS_BASE_URL}/items/versao?limit=5"
print(f"URL: {url1}")
try:
    response1 = requests.get(url1, headers=headers)
    print(f"Status: {response1.status_code}")
    print(f"Response: {response1.text}")
except Exception as e:
    print(f"Erro: {e}")

# Teste 2: GET com query parameters
print("\n🧪 Teste 2: GET com filtros")
params = {
    'filter[status][_eq]': 'processar',
    'limit': 10,
    'sort': 'date_created'
}
url2 = f"{DIRECTUS_BASE_URL}/items/versao"
print(f"URL: {url2}")
print(f"Params: {params}")
try:
    response2 = requests.get(url2, headers=headers, params=params)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")
except Exception as e:
    print(f"Erro: {e}")

# Teste 3: POST com body JSON
print("\n🧪 Teste 3: POST com JSON body")
url3 = f"{DIRECTUS_BASE_URL}/items/versao"
query_body = {
    "query": {
        "filter": {
            "_and": [
                {"status": {"_eq": "processar"}}
            ]
        },
        "sort": ["date_created"],
        "limit": 10
    },
    "fields": ["id", "status", "date_created"]
}
print(f"URL: {url3}")
print(f"Body: {json.dumps(query_body, indent=2)}")
try:
    response3 = requests.post(url3, headers=headers, json=query_body)
    print(f"Status: {response3.status_code}")
    print(f"Response: {response3.text}")
except Exception as e:
    print(f"Erro: {e}")

print("\n✅ Todos os testes enviados para webhook.site")
