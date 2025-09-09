#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.getcwd())

from src.docx_compare.core.directus_sdk import DirectusSDK


def main():
    sdk = DirectusSDK()

    # Buscar algumas modificações para ver se têm caminho
    modificacoes = sdk.get_items("modificacao", {
        "limit": 5,
        "fields": ["id", "conteudo_original", "conteudo_modificado", "caminho_inicio", "caminho_fim"]
    })

    print(f"Encontradas {len(modificacoes)} modificações:")

    for i, mod in enumerate(modificacoes):
        print(f"\n--- Modificação {i+1} ---")
        print(f'ID: {mod["id"]}')
        print(f'Original: {mod.get("conteudo_original", "")}')
        print(f'Modificado: {mod.get("conteudo_modificado", "")}')
        print(f'Caminho início: "{mod.get("caminho_inicio", "")}"')
        print(f'Caminho fim: "{mod.get("caminho_fim", "")}"')

if __name__ == "__main__":
    main()
