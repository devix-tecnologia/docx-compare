#!/usr/bin/env python3
"""
Script para debugar a query exata do processador de agrupamento
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://admin.devix.ai")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "token_aqui")

def testar_query_agrupamento():
    print("🔍 Testando query exata do processador de agrupamento...")

    # Query exata do processador
    url = f"{DIRECTUS_BASE_URL}/items/modificacao"
    params = {
        "filter[clausula][_null]": "true",
        "fields": "versao.id,versao.status",
        "limit": 1000,
        "groupBy": "versao"
    }

    print(f"🔗 URL: {url}")
    print(f"📋 Params: {params}")

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
            params=params,
            timeout=30
        )

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json().get("data", [])
            print(f"✅ Resposta: {len(data)} registros")

            print("\n📋 Dados detalhados:")
            for i, mod in enumerate(data[:10]):  # Mostrar apenas os 10 primeiros
                print(f"{i+1}. {mod}")

            if len(data) > 10:
                print(f"... e mais {len(data) - 10} registros")

            # Processar como o código faz
            versoes_ids = []
            for mod in data:
                versao = mod.get("versao")
                if versao and isinstance(versao, dict):
                    versao_id = versao.get("id")
                    status = versao.get("status", "")

                    print(f"🔍 Versão {versao_id}: status = '{status}'")

                    if versao_id and status in ["concluido", "erro"] and versao_id not in versoes_ids:
                        versoes_ids.append(versao_id)
                        print("   ✅ Adicionada à lista!")
                    else:
                        print("   ❌ Não atende critérios")

            print(f"\n📊 Resultado final: {len(versoes_ids)} versões para processar")
            print(f"IDs: {versoes_ids}")
        else:
            print(f"❌ Erro: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_query_sem_groupby():
    print("\n🔍 Testando query sem groupBy...")

    url = f"{DIRECTUS_BASE_URL}/items/modificacao"
    params = {
        "filter[clausula][_null]": "true",
        "fields": "id,versao.id,versao.status,versao.versao,categoria",
        "limit": 20
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
            print(f"✅ {len(data)} modificações sem cláusula encontradas")

            versoes_unicas = {}
            for mod in data:
                versao = mod.get("versao", {})
                if isinstance(versao, dict):
                    versao_id = versao.get("id")
                    versao_status = versao.get("status")
                    versao_nome = versao.get("versao")

                    if versao_id not in versoes_unicas:
                        versoes_unicas[versao_id] = {
                            "status": versao_status,
                            "nome": versao_nome,
                            "count": 0
                        }
                    versoes_unicas[versao_id]["count"] += 1

            print("\n📋 Versões com modificações sem cláusula:")
            for versao_id, info in versoes_unicas.items():
                status_ok = info["status"] in ["concluido", "erro"]
                print(f"  {info['nome']} ({versao_id[:8]}...): status='{info['status']}', mods={info['count']} {'✅' if status_ok else '❌'}")

        else:
            print(f"❌ Erro: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_query_agrupamento()
    testar_query_sem_groupby()
