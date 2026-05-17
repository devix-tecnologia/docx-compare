#!/usr/bin/env python3
"""
Debug de modificações não vinculadas
Analisa por que modificações com 100% overlap não foram vinculadas
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "tests"))

from rapidfuzz import fuzz

# Caso 1: "4. CORREÇÃO MONETÁRIA" (pos 66655-66679, 24 chars)
# Tag 1.5: pos 66226-66928, overlap 100%

texto_modificacao = """4.  CORREÇÃO MONETÁRIA
    1.  Se aplicável, a partir do 12º mês contado da data-base, a   
        CO"""

texto_tag_1_5 = """A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa   
    ou defesa, o desconhecimento, incompreensão, dúvida, no todo ou em 
    parte,"""

# Simular o que o algoritmo faz
print("=" * 80)
print("🔍 ANÁLISE DE CASO FALHADO")
print("=" * 80)

print(f"\n📝 Modificação:")
print(f"   Posição: 66655 → 66679 (24 chars)")
print(f"   Conteúdo: {texto_modificacao[:100]}...")

print(f"\n🏷️  Tag 1.5:")
print(f"   Posição: 66226 → 66928 (702 chars)")
print(f"   Conteúdo: {texto_tag_1_5[:100]}...")

print(f"\n📊 Cálculos:")

# Overlap
mod_inicio = 66655
mod_fim = 66679
tag_inicio = 66226
tag_fim = 66928

inicio_intersecao = max(mod_inicio, tag_inicio)
fim_intersecao = min(mod_fim, tag_fim)
tamanho_intersecao = max(0, fim_intersecao - inicio_intersecao)
tamanho_mod = mod_fim - mod_inicio

if tamanho_mod > 0:
    overlap = (tamanho_intersecao / tamanho_mod) * 100
else:
    overlap = 0

print(f"   Overlap: {overlap:.1f}% ({tamanho_intersecao}/{tamanho_mod} chars)")

# Fuzzy
print(f"\n🔢 Fuzzy Matching:")
scores = {
    "ratio": fuzz.ratio(texto_modificacao, texto_tag_1_5),
    "partial_ratio": fuzz.partial_ratio(texto_modificacao, texto_tag_1_5),
    "token_sort_ratio": fuzz.token_sort_ratio(texto_modificacao, texto_tag_1_5),
    "token_set_ratio": fuzz.token_set_ratio(texto_modificacao, texto_tag_1_5),
}

for metric, score in scores.items():
    print(f"   {metric:20s}: {score:5.1f}%")

score_composto = sum(scores.values()) / len(scores)
print(f"   {'score_composto':20s}: {score_composto:5.1f}%")

# Análise dos thresholds
print(f"\n✅ Análise dos Thresholds:")

if overlap >= 90:
    threshold_fuzzy = 40
    tier = "Tier 1 (overlap ≥90% + fuzzy ≥40%)"
    passou = score_composto >= threshold_fuzzy
elif overlap >= 70:
    threshold_fuzzy = 60
    tier = "Tier 2 (overlap ≥70% + fuzzy ≥60%)"
    passou = score_composto >= threshold_fuzzy
elif overlap > 50:
    threshold_fuzzy = 80  # Assumindo threshold default
    tier = "Tier 3 (overlap >50% + fuzzy ≥80%)"
    passou = score_composto >= threshold_fuzzy
else:
    tier = "Nenhum tier aplicável"
    passou = False
    threshold_fuzzy = 0

print(f"   {tier}")
print(f"   Overlap: {overlap:.1f}% {'✅' if overlap >= 50 else '❌'}")
print(f"   Fuzzy: {score_composto:.1f}% (threshold: ≥{threshold_fuzzy}%) {'✅' if passou else '❌'}")

if passou:
    print(f"\n✅ DEVERIA TER SIDO VINCULADA!")
else:
    print(f"\n❌ NÃO PASSOU NOS THRESHOLDS")
    print(f"   Motivo: Fuzzy score ({score_composto:.1f}%) < threshold ({threshold_fuzzy}%)")

print("\n" + "=" * 80)
print("🔍 CONCLUSÃO")
print("=" * 80)

if overlap == 100 and not passou:
    print("⚠️  BUG DETECTADO:")
    print("   Modificação está 100% contida na tag (overlap perfeito)")
    print("   mas o fuzzy score está muito baixo devido a textos diferentes")
    print()
    print("   A modificação é o TÍTULO da cláusula 4 ('CORREÇÃO MONETÁRIA')")
    print("   mas a tag 1.5 contém OUTRO conteúdo completamente diferente")
    print()
    print("   PROBLEMA: As posições das tags no arquivo_com_tags.docx")
    print("   NÃO correspondem às posições no arquivo modificado!")
    print()
    print("   SOLUÇÃO: Usar arquivo_original.docx como base para calcular")
    print("   posições, não arquivo_com_tags.docx")
