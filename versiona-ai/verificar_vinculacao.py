#!/usr/bin/env python3
"""
Script para verificar se as modificações da versão estão vinculadas às cláusulas
"""

import requests

DIRECTUS_URL = "https://contract.devix.co"
DIRECTUS_TOKEN = "S1okNXYabq9TL1gVj0TxiNEdu0md_F3d"
VERSAO_ID = "99090886-7f43-45c9-bfe4-ec6eddd6cde0"


def verificar_vinculacao():
    """Verifica quantas modificações têm cláusula vinculada"""

    url = f"{DIRECTUS_URL}/items/modificacao"
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
    params = {
        "filter[versao][_eq]": VERSAO_ID,
        "fields": "id,tipo,clausula,posicao_inicio,posicao_fim",
        "limit": 50,
    }

    print(f"🔍 Consultando modificações da versão {VERSAO_ID}...")
    print("=" * 80)

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        modificacoes = data.get("data", [])
        total = len(modificacoes)

        print(f"\n📊 TOTAL: {total} modificações encontradas\n")

        com_clausula = 0
        sem_clausula = 0

        for mod in modificacoes:
            mod_id = mod.get("id")
            tipo = mod.get("tipo", "?")
            clausula = mod.get("clausula")
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")

            if clausula:
                com_clausula += 1
                print(
                    f"✅ Mod {mod_id:3} | Tipo: {tipo:10} | Pos: {pos_inicio:6}-{pos_fim:6} | Cláusula ID: {clausula}"
                )
            else:
                sem_clausula += 1
                print(
                    f"❌ Mod {mod_id:3} | Tipo: {tipo:10} | Pos: {pos_inicio:6}-{pos_fim:6} | SEM CLÁUSULA"
                )

        print("\n" + "=" * 80)
        print("\n📈 RESULTADO DA VINCULAÇÃO:")
        print(
            f"   ✅ Com cláusula: {com_clausula}/{total} ({com_clausula * 100 // max(total, 1)}%)"
        )
        print(
            f"   ❌ Sem cláusula: {sem_clausula}/{total} ({sem_clausula * 100 // max(total, 1)}%)"
        )

        if com_clausula > 0:
            print("\n🎉 SUCESSO! A vinculação está funcionando!")
        else:
            print("\n⚠️  PROBLEMA: Nenhuma modificação foi vinculada às cláusulas")

        return com_clausula, total

    except Exception as e:
        print(f"❌ Erro ao consultar: {e}")
        import traceback

        traceback.print_exc()
        return 0, 0


if __name__ == "__main__":
    verificar_vinculacao()
