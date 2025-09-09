#!/usr/bin/env python3
"""Script para verificar os campos disponíveis nas tags do modelo"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from docx_compare.utils.directus_sdk import DirectusSDK


def main():
    sdk = DirectusSDK()

    print("=== VERIFICANDO CAMPOS DAS TAGS DO MODELO ===")

    try:
        # Buscar uma tag de exemplo para ver todos os campos
        response = sdk.get_items("modelo_contrato_tag", {
            "limit": 1,
            "fields": "*"  # Buscar todos os campos
        })

        tags = response.get("data", [])
        if tags:
            tag = tags[0]
            print("Campos disponíveis na tag:")
            for campo, valor in tag.items():
                print(f"  - {campo}: {valor}")
        else:
            print("Nenhuma tag encontrada")

    except Exception as e:
        print(f"Erro: {e}")

    print("\n=== VERIFICANDO CAMPOS DAS MODIFICAÇÕES ===")

    try:
        # Buscar uma modificação de exemplo
        response = sdk.get_items("modificacao", {
            "limit": 1,
            "fields": "*"  # Buscar todos os campos
        })

        modificacoes = response.get("data", [])
        if modificacoes:
            mod = modificacoes[0]
            print("Campos disponíveis na modificação:")
            for campo, valor in mod.items():
                print(f"  - {campo}: {valor}")
        else:
            print("Nenhuma modificação encontrada")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
