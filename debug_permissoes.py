#!/usr/bin/env python3
"""
Script para testar permissões de acesso às diferentes coleções
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://admin.devix.ai")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "token_aqui")

def testar_acesso_colecoes():
    print("🔍 Testando acesso às coleções do Directus...")

    colecoes_teste = [
        ("versao", "id,status,versao"),
        ("modificacao", "id,categoria,clausula"),
        ("modelo_contrato", "id,nome,status"),
        ("modelo_contrato_tag", "id,tag_nome,conteudo"),
        ("clausula", "id,nome,numero")
    ]

    for colecao, fields in colecoes_teste:
        print(f"\n📋 Testando coleção: {colecao}")

        url = f"{DIRECTUS_BASE_URL}/items/{colecao}"
        params = {
            "fields": fields,
            "limit": 3
        }

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json().get("data", [])
                print(f"   ✅ Status: {response.status_code} - {len(data)} registros")
            elif response.status_code == 403:
                print(f"   ❌ Status: {response.status_code} - ACESSO NEGADO")
            else:
                print(f"   ⚠️ Status: {response.status_code} - {response.text[:100]}")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

def testar_acesso_modelo_especifico():
    print("\n🎯 Testando acesso ao modelo específico encontrado...")

    modelo_id = "afb74c25-4f97-43d1-976c-e97d257ab48c"

    # Testar acesso direto ao modelo
    url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato/{modelo_id}"
    params = {"fields": "id,nome,status,tags"}

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
            params=params,
            timeout=30
        )

        print(f"📋 Modelo direto: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json().get("data", {})
            print(f"   Nome: {data.get('nome', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            tags = data.get("tags", [])
            print(f"   Tags: {len(tags) if isinstance(tags, list) else 'N/A'}")
        elif response.status_code != 200:
            print(f"   Erro: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Testar acesso às tags do modelo
    url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato_tag"
    params = {
        "filter[modelo_contrato][_eq]": modelo_id,
        "fields": "id,tag_nome,conteudo",
        "limit": 5
    }

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
            params=params,
            timeout=30
        )

        print(f"📋 Tags do modelo: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json().get("data", [])
            print(f"   Tags encontradas: {len(data)}")
            for tag in data[:3]:
                print(f"   - {tag.get('tag_nome', 'N/A')}")
        elif response.status_code != 200:
            print(f"   Erro: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    testar_acesso_colecoes()
    testar_acesso_modelo_especifico()
