#!/usr/bin/env python3


import requests

from config import Config


def debug_modificacao():
    # Configurações do Directus
    directus_url = Config.DIRECTUS_URL
    directus_token = Config.DIRECTUS_TOKEN

    headers = {
        "Authorization": f"Bearer {directus_token}",
        "Content-Type": "application/json"
    }

    # ID da modificação que vimos sendo processada
    modificacao_id = "b9396f63-69ac-4da7-b9c3-5a0408dd5f8e"

    print(f"🔍 Verificando status da modificação: {modificacao_id}")

    # Buscar a modificação específica
    url = f"{directus_url}/items/modificacao/{modificacao_id}"
    params = {
        "fields": "id,categoria,conteudo,clausula.id,clausula.nome,versao.id"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        modificacao = response.json().get("data", {})
        print("✅ Modificação encontrada:")
        print(f"   ID: {modificacao.get('id')}")
        print(f"   Categoria: {modificacao.get('categoria')}")
        print(f"   Conteúdo: {modificacao.get('conteudo')}")
        print(f"   Cláusula: {modificacao.get('clausula')}")
        print(f"   Versão: {modificacao.get('versao')}")
    else:
        print(f"❌ Erro ao buscar modificação: HTTP {response.status_code}")

if __name__ == "__main__":
    debug_modificacao()
