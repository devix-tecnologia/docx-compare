#!/usr/bin/env python3
"""Script de debug para testar o endpoint process_versao diretamente"""

import sys

sys.path.insert(
    0,
    "/app/versiona-ai"
    if "/app" in __file__
    else "/Users/sidarta/repositorios/docx-compare/versiona-ai",
)

from directus_server import directus_api

# Testar process_versao diretamente
versao_id = "2573b998-63d0-4471-ad85-db6f860c3721"

print(f"🧪 Testando process_versao com versao_id={versao_id}")
print(f"🔍 directus_api = {directus_api}")
print(f"🔍 type(directus_api) = {type(directus_api)}")

result = directus_api.process_versao(versao_id, mock=False, use_ast=True)

print("\n📊 RESULTADO:")
print(f"🔍 type(result) = {type(result)}")
print(f"🔍 result = {result}")

if result:
    print(
        f"🔍 result.keys() = {list(result.keys()) if isinstance(result, dict) else 'N/A'}"
    )
    if isinstance(result, dict):
        for key, value in result.items():
            print(
                f"  - {key}: {type(value).__name__} = {value if not isinstance(value, (list, dict)) or len(str(value)) < 100 else f'{type(value).__name__} com {len(value)} items'}"
            )
else:
    print("❌ result é None ou False!")
