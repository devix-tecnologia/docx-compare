"""
Script para testar baseline corrigido no caso real c2b1dfa0.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "tests"))

from algoritmos.producao.algoritmo import AlgoritmoProducao
from processar_caso_real import (
    baixar_versao_directus,
    extrair_dados_para_algoritmo,
    processar_com_algoritmo,
)

versao_id = "c2b1dfa0-e7a5-4c2a-b7d2-6ca3e93e42ed"
print("\n📥 Baixando versão c2b1dfa0...")
versao_data = baixar_versao_directus(versao_id)

print("\n📝 Extraindo dados...")
modificacoes, tags, texto = extrair_dados_para_algoritmo(versao_data)
print(f"   - {len(modificacoes)} modificações")
print(f"   - {len(tags)} tags")

print("\n🔬 Processando com baseline CORRIGIDO...")
alg = AlgoritmoProducao()
vinculadas = processar_com_algoritmo(alg, modificacoes, tags, texto)

taxa = (vinculadas / len(modificacoes) * 100) if modificacoes else 0
print(f"\n📊 Taxa de vinculação: {vinculadas}/{len(modificacoes)} ({taxa:.1f}%)")

if taxa > 50:
    print("\n✅ MELHOROU! Taxa anterior era 50%")
else:
    print("\n⚠️  Igual ou pior que antes (50%)")
