#!/usr/bin/env python3
"""
Script para criar os campos posicao_inicio e posicao_fim na tabela modificacao
"""

import os
import sys

import requests
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "")

headers = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}


def criar_campo_posicao(campo_nome, descricao):
    """Cria um campo de posição na tabela modificacao"""

    print(f"🔧 Criando campo '{campo_nome}' na tabela modificacao...")

    campo_data = {
        "collection": "modificacao",
        "field": campo_nome,
        "type": "integer",
        "meta": {
            "interface": "input",
            "display": "raw",
            "readonly": False,
            "hidden": False,
            "width": "half",
            "note": descricao,
            "group": None,
            "sort": None,
            "validation": None,
            "validation_message": None,
            "conditions": None,
            "required": False,
            "translations": None,
        },
    }

    try:
        response = requests.post(
            f"{DIRECTUS_BASE_URL}/fields/modificacao",
            headers=headers,
            json=campo_data,
            timeout=30,
        )

        if response.status_code in [200, 201]:
            print(f"✅ Campo '{campo_nome}' criado com sucesso")
            return True
        else:
            print(f"❌ Erro ao criar campo '{campo_nome}': {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erro ao criar campo '{campo_nome}': {e}")
        return False


def main():
    """Função principal"""
    print("🚀 Criando campos de posição na tabela modificacao")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")

    # Criar campo posicao_inicio
    sucesso1 = criar_campo_posicao(
        "posicao_inicio", "Posição de início da modificação no texto (número inteiro)"
    )

    # Criar campo posicao_fim
    sucesso2 = criar_campo_posicao(
        "posicao_fim", "Posição de fim da modificação no texto (número inteiro)"
    )

    if sucesso1 and sucesso2:
        print("\n✅ Todos os campos foram criados com sucesso!")
        print("📋 Campos criados:")
        print("   - posicao_inicio (integer)")
        print("   - posicao_fim (integer)")
        print("\n🔄 Agora você pode executar um script para popular esses campos")
        print("   com base nos valores de caminho_inicio e caminho_fim existentes")
    else:
        print("\n❌ Alguns campos falharam na criação")
        print("   Verifique as permissões e tente novamente")


if __name__ == "__main__":
    main()
