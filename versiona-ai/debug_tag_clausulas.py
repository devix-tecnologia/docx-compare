#!/usr/bin/env python3
"""Script para debugar estrutura exata de tag.clausulas do Directus"""

import json
import os
import sys

import requests

# Ler token do .env.production
env_path = os.path.join(os.path.dirname(__file__), ".env.production")
token = None

with open(env_path) as f:
    for line in f:
        if line.startswith("DIRECTUS_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not token or token == "your_production_token_here":
    print("❌ Token não configurado no .env.production")
    sys.exit(1)

DIRECTUS_URL = "https://contract.devix.co"

# Buscar uma TAG específica com suas cláusulas
# UUID da tag que está dando erro: 59a034cc-e29d-4ed2-8989-4a945582d215
tag_id = "59a034cc-e29d-4ed2-8989-4a945582d215"

print(f"🔍 Buscando TAG {tag_id} com cláusulas...")
print()

response = requests.get(
    f"{DIRECTUS_URL}/items/modelo_contrato_tag/{tag_id}",
    headers={"Authorization": f"Bearer {token}"},
    params={
        "fields": "*,clausulas.*",  # Todos os campos da tag + cláusulas expandidas
    },
    timeout=15,
)

print(f"Status: {response.status_code}")
print()

if response.status_code == 200:
    data = response.json()["data"]

    print("✅ TAG encontrada!")
    print(f"   tag_nome: {data.get('tag_nome')}")
    print(f"   tag_id: {data.get('id')}")
    print()

    clausulas = data.get("clausulas", [])
    print(f"📝 Cláusulas ({len(clausulas)} total):")
    print()

    if clausulas:
        print("Estrutura da primeira cláusula:")
        print("-" * 80)
        print(json.dumps(clausulas[0], indent=2, ensure_ascii=False))
        print("-" * 80)
        print()

        # Analizar campos relevantes
        primeira = clausulas[0]
        print("Campos chave:")
        print(f"  - 'id': {primeira.get('id')}")
        print(f"  - 'tag': {primeira.get('tag')}")
        print(f"  - 'numero': {primeira.get('numero')}")
        print(f"  - 'nome': {primeira.get('nome')}")
        print()

        # Verificar se é o ID da tag ou da cláusula
        if primeira.get("id") == tag_id:
            print("❌ PROBLEMA: clausulas[0]['id'] é o ID DA TAG, não da cláusula!")
        else:
            print("✅ clausulas[0]['id'] é diferente do ID da tag (correto)")

        if primeira.get("tag") == tag_id:
            print("✅ clausulas[0]['tag'] é o FK para a tag (correto)")

    else:
        print("⚠️ Nenhuma cláusula vinculada a esta tag")
else:
    print(f"❌ Erro: {response.text[:500]}")
    sys.exit(1)
