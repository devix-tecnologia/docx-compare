#!/usr/bin/env python3
"""Debug script para verificar se as modificações estão sendo atualizadas"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from docx_compare.utils.directus_sdk import DirectusSDK


def main():
    sdk = DirectusSDK()

    print("=== VERIFICANDO MODIFICAÇÕES NÃO ASSOCIADAS ===")

    # Buscar modificações não associadas a cláusulas
    try:
        response = sdk.get_items("modificacao", {
            "filter[clausula][_null]": "true",
            "fields": "id,conteudo_original,clausula.id"
        })

        modificacoes = response.get("data", [])
        print(f"Encontradas {len(modificacoes)} modificações não associadas:")

        for mod in modificacoes:
            print(f"  - Modificação {mod['id']}: '{mod['conteudo_original'][:50]}...' (clausula: {mod.get('clausula')})")

    except Exception as e:
        print(f"Erro ao buscar modificações: {e}")

    print("\n=== VERIFICANDO MODIFICAÇÕES COM CLÁUSULAS ===")

    # Buscar modificações já associadas
    try:
        response = sdk.get_items("modificacao", {
            "filter[clausula][_nnull]": "true",
            "fields": "id,conteudo_original,clausula.id"
        })

        modificacoes_com_clausula = response.get("data", [])
        print(f"Encontradas {len(modificacoes_com_clausula)} modificações JÁ associadas:")

        for mod in modificacoes_com_clausula:
            print(f"  - Modificação {mod['id']}: '{mod['conteudo_original'][:50]}...' (clausula: {mod.get('clausula')})")

    except Exception as e:
        print(f"Erro ao buscar modificações com cláusulas: {e}")

if __name__ == "__main__":
    main()
