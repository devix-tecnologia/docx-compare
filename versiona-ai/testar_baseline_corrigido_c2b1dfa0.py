"""
Processar caso real c2b1dfa0 usando dados salvos (sem precisar Directus rodando).
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "tests"))

from processar_caso_real import extrair_dados_para_algoritmo, processar_com_algoritmo
from algoritmos.producao.algoritmo import AlgoritmoProducao

# Carregar dados do JSON salvo
print("\n📂 Carregando versao_c2b1dfa0_raw.json...")
with open("versao_c2b1dfa0_raw.json", "r", encoding="utf-8") as f:
    versao_data = json.load(f)

print("\n📝 Extraindo dados...")
dados = extrair_dados_para_algoritmo(versao_data)
modificacoes = dados["modificacoes"]
tags = dados["tags"]
texto = dados["texto_completo"]
print(f"   - {len(modificacoes)} modificações")
print(f"   - {len(tags)} tags")
print(f"   - {len(texto)} chars de texto")

print("\n🔬 Processando com BASELINE CORRIGIDO...")
resultado = processar_com_algoritmo(AlgoritmoProducao, dados, verbose=False)

# Extrair estatísticas
modificacoes = dados["modificacoes"]
vinculadas = resultado["vinculadas"]
taxa = resultado["taxa_vinculacao"]

print("\n" + "=" * 80)
print("📊 RESULTADO FINAL")
print("=" * 80)
print(f"Taxa de vinculação: {vinculadas}/{len(modificacoes)} ({taxa:.1f}%)")
print(f"Taxa anterior (debug_baseline_caso_real.py): 50.0%")

if taxa > 50:
    print(f"\n✅ MELHOROU! {taxa:.1f}% > 50%")
elif taxa == 50:
    print(f"\n➡️  IGUAL: {taxa:.1f}% = 50%")
else:
    print(f"\n⚠️  PIOROU: {taxa:.1f}% < 50%")

print("=" * 80)
