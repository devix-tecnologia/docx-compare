#!/usr/bin/env python3
"""
Script para verificar versões no sistema e seus status
"""

import os

import requests
from dotenv import load_dotenv

# Carregar configurações
load_dotenv()
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://admin.devix.ai")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "token_aqui")

def verificar_versoes():
    print("🔍 Verificando versões no sistema...")

    url = f"{DIRECTUS_BASE_URL}/items/versao"
    params = {
        "fields": "id,status,versao,date_created,contrato.id,modificacoes.id",
        "limit": 20,
        "sort": "-date_created"
    }

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            versoes = response.json().get("data", [])
            print(f"✅ Encontradas {len(versoes)} versões:")
            print()

            status_count = {}
            for versao in versoes:
                status = versao.get("status", "N/A")
                versao_nome = versao.get("versao", "N/A")
                versao_id = versao.get("id", "N/A")
                date_created = versao.get("date_created", "N/A")[:10]  # Apenas data
                contrato_id = versao.get("contrato", {}).get("id", "N/A") if isinstance(versao.get("contrato"), dict) else "N/A"

                # Contar modificações
                modificacoes = versao.get("modificacoes", [])
                num_mods = len(modificacoes) if isinstance(modificacoes, list) else 0

                print(f"📋 {versao_nome} ({versao_id[:8]}...)")
                print(f"   Status: {status}")
                print(f"   Data: {date_created}")
                print(f"   Contrato: {contrato_id[:8]}..." if contrato_id != "N/A" else f"   Contrato: {contrato_id}")
                print(f"   Modificações: {num_mods}")
                print()

                # Contar por status
                status_count[status] = status_count.get(status, 0) + 1

            print("📊 Resumo por status:")
            for status, count in status_count.items():
                print(f"   {status}: {count} versões")

        else:
            print(f"❌ Erro ao buscar versões: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_modificacoes_sem_clausula():
    print("\n🔍 Verificando modificações sem cláusula...")

    url = f"{DIRECTUS_BASE_URL}/items/modificacao"
    params = {
        "filter[clausula][_null]": "true",
        "fields": "id,versao.id,versao.status,versao.versao,categoria,conteudo",
        "limit": 10
    }

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            modificacoes = response.json().get("data", [])
            print(f"✅ Encontradas {len(modificacoes)} modificações sem cláusula:")
            print()

            versoes_com_mods = {}
            for mod in modificacoes:
                versao = mod.get("versao", {})
                if isinstance(versao, dict):
                    versao_id = versao.get("id", "N/A")
                    versao_status = versao.get("status", "N/A")
                    versao_nome = versao.get("versao", "N/A")

                    if versao_id not in versoes_com_mods:
                        versoes_com_mods[versao_id] = {
                            "status": versao_status,
                            "nome": versao_nome,
                            "modificacoes": []
                        }

                    versoes_com_mods[versao_id]["modificacoes"].append({
                        "id": mod.get("id", "N/A"),
                        "categoria": mod.get("categoria", "N/A"),
                        "conteudo": mod.get("conteudo", "")[:50] + "..." if len(mod.get("conteudo", "")) > 50 else mod.get("conteudo", "")
                    })

            for versao_id, info in versoes_com_mods.items():
                print(f"📋 Versão {info['nome']} ({versao_id[:8]}...)")
                print(f"   Status: {info['status']}")
                print(f"   Modificações sem cláusula: {len(info['modificacoes'])}")

                for mod in info["modificacoes"][:3]:  # Mostrar apenas as 3 primeiras
                    print(f"     • [{mod['categoria']}] {mod['conteudo']}")

                if len(info["modificacoes"]) > 3:
                    print(f"     ... e mais {len(info['modificacoes']) - 3}")
                print()

        else:
            print(f"❌ Erro ao buscar modificações: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_versoes()
    verificar_modificacoes_sem_clausula()
