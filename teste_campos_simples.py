#!/usr/bin/env python3
"""Teste simples dos novos campos de caminho"""

import os

import requests

# Configuração do Directus
DIRECTUS_URL = os.environ.get("DIRECTUS_URL", "http://localhost:8055")
DIRECTUS_TOKEN = os.environ.get("DIRECTUS_TOKEN", "")

headers = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}

def testar_campos():
    print("=== TESTANDO CAMPOS DE CAMINHO ===")

    # 1. Testar modificação com novos campos
    print("1. Testando modificação com campos caminho_inicio/fim...")
    try:
        response = requests.get(
            f"{DIRECTUS_URL}/items/modificacao",
            headers=headers,
            params={
                "limit": 1,
                "fields": "id,conteudo,caminho_inicio,caminho_fim"
            }
        )

        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                mod = data[0]
                print("✅ Campos de modificação funcionam!")
                print(f"   - id: {mod.get('id')}")
                print(f"   - caminho_inicio: {mod.get('caminho_inicio')}")
                print(f"   - caminho_fim: {mod.get('caminho_fim')}")
            else:
                print("⚠️ Nenhuma modificação encontrada")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")

    # 2. Testar modelo_contrato_tag com campos de caminho
    print("\n2. Testando modelo_contrato_tag com campos caminho_tag_inicio/fim...")
    try:
        response = requests.get(
            f"{DIRECTUS_URL}/items/modelo_contrato_tag",
            headers=headers,
            params={
                "limit": 1,
                "fields": "id,tag_nome,conteudo,caminho_tag_inicio,caminho_tag_fim"
            }
        )

        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                tag = data[0]
                print("✅ Campos de tag do modelo funcionam!")
                print(f"   - id: {tag.get('id')}")
                print(f"   - tag_nome: {tag.get('tag_nome')}")
                print(f"   - caminho_tag_inicio: {tag.get('caminho_tag_inicio')}")
                print(f"   - caminho_tag_fim: {tag.get('caminho_tag_fim')}")
            else:
                print("⚠️ Nenhuma tag encontrada")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            print("Os campos caminho_tag_inicio/fim podem não existir ainda")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_campos()
