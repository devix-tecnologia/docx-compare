#!/usr/bin/env python3
"""Script para verificar se os campos de caminho existem nas tags do modelo"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from docx_compare.utils.directus_sdk import DirectusSDK


def main():
    sdk = DirectusSDK()

    print("=== VERIFICANDO CAMPOS DA COLEÇÃO modelo_contrato_tag ===")

    try:
        # Tentar buscar com todos os campos de caminho
        response = sdk.get_items("modelo_contrato_tag", {
            "limit": 1,
            "fields": "id,tag_nome,conteudo,caminho_tag_inicio,caminho_tag_fim"
        })

        print("✅ Campos caminho_tag_inicio e caminho_tag_fim EXISTEM!")

        tags = response.get("data", [])
        if tags:
            tag = tags[0]
            print("Exemplo de tag com caminhos:")
            print(f"  - id: {tag.get('id')}")
            print(f"  - tag_nome: {tag.get('tag_nome')}")
            print(f"  - caminho_tag_inicio: {tag.get('caminho_tag_inicio')}")
            print(f"  - caminho_tag_fim: {tag.get('caminho_tag_fim')}")

    except Exception as e:
        print(f"❌ Erro ao buscar com campos de caminho: {e}")
        print("Os campos caminho_tag_inicio/fim podem não existir ainda.")

        # Tentar buscar apenas campos básicos
        try:
            response = sdk.get_items("modelo_contrato_tag", {
                "limit": 1,
                "fields": "id,tag_nome,conteudo"
            })
            print("✅ Campos básicos funcionam normalmente")
        except Exception as e2:
            print(f"❌ Erro com campos básicos também: {e2}")

    print("\n=== VERIFICANDO CAMPOS DA COLEÇÃO modificacao ===")

    try:
        # Verificar se os novos campos de modificacao funcionam
        response = sdk.get_items("modificacao", {
            "limit": 1,
            "fields": "id,conteudo,caminho_inicio,caminho_fim"
        })

        print("✅ Campos caminho_inicio e caminho_fim na modificacao EXISTEM!")

        modificacoes = response.get("data", [])
        if modificacoes:
            mod = modificacoes[0]
            print("Exemplo de modificação com caminhos:")
            print(f"  - id: {mod.get('id')}")
            print(f"  - conteudo: {mod.get('conteudo', '')[:50]}...")
            print(f"  - caminho_inicio: {mod.get('caminho_inicio')}")
            print(f"  - caminho_fim: {mod.get('caminho_fim')}")

    except Exception as e:
        print(f"❌ Erro ao buscar modificações com campos de caminho: {e}")

if __name__ == "__main__":
    main()
