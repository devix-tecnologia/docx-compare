#!/usr/bin/env python3
"""
Script simples para baixar versão do Directus e salvar em JSON.
"""

import json
import sys

import requests

VERSAO_ID = "2573b998-63d0-4471-ad85-db6f860c3721"
API_URL = "http://localhost:8011"
TOKEN = "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"

print(f"📡 Baixando versão {VERSAO_ID[:8]}...")
print(f"   URL: {API_URL}/api/versoes/{VERSAO_ID}")

headers = {"Authorization": f"Bearer {TOKEN}"}

try:
    response = requests.get(
        f"{API_URL}/api/versoes/{VERSAO_ID}",
        headers=headers,
        timeout=120,  # 2 minutos
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # Salvar
        output_file = f"versao_{VERSAO_ID[:8]}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Dados salvos em: {output_file}")

        # Mostrar resumo
        versao_data = data.get("data", {})
        mods = versao_data.get("modificacoes", [])
        tags = versao_data.get("documento", {}).get("tags", [])
        texto = versao_data.get("documento", {}).get("texto_completo", "")

        print("\n📊 Resumo:")
        print(f"   - Modificações: {len(mods)}")
        print(f"   - Tags (cláusulas): {len(tags)}")
        print(f"   - Texto: {len(texto)} chars")

    else:
        print(f"❌ Erro: {response.text[:200]}")
        sys.exit(1)

except requests.exceptions.Timeout:
    print("❌ Timeout após 120s - API muito lenta")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)
