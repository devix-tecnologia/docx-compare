"""Testar por que fuzzy conseguiu 33.3% de vinculação."""

import json

from rapidfuzz import fuzz

# Carregar dados
with open("versao_c2b1dfa0_raw.json") as f:
    data = json.load(f)

tags = data["contrato"]["modelo_contrato"]["tags"]
modificacoes = data["modificacoes"]

print("=" * 80)
print("TESTE: FUZZY MATCHING COM token_set_ratio")
print("=" * 80)

for i, mod in enumerate(modificacoes, 1):
    mod_texto = mod["alteracao"]
    print(f"\n{i}. Modificação ({mod['categoria']})")
    print(f"   Texto: {mod_texto[:80]}...")

    for tag in tags:
        tag_texto = tag["conteudo"]
        tag_nome = tag["tag_nome"]

        # Calcular todas as métricas
        ratio = fuzz.ratio(mod_texto, tag_texto)
        partial = fuzz.partial_ratio(mod_texto, tag_texto)
        token_sort = fuzz.token_sort_ratio(mod_texto, tag_texto)
        token_set = fuzz.token_set_ratio(mod_texto, tag_texto)

        max_score = max(ratio, partial, token_sort, token_set)

        print(f"\n   vs. Tag '{tag_nome}':")
        print(f"      ratio:      {ratio:.1f}%")
        print(f"      partial:    {partial:.1f}%")
        print(f"      token_sort: {token_sort:.1f}%")
        print(f"      token_set:  {token_set:.1f}% ⭐")
        print(f"      MAX:        {max_score:.1f}%")

        # Threshold dinâmico baseado no tamanho
        if len(mod_texto) < 20:
            threshold = 90.0
        elif len(mod_texto) < 100:
            threshold = 85.0
        else:
            threshold = 80.0

        if max_score >= threshold:
            print(f"      ✅ VINCULARIA! (threshold={threshold:.0f}%)")
        else:
            print(f"      ❌ Abaixo do threshold ({threshold:.0f}%)")

print("\n" + "=" * 80)
print("CONCLUSÃO")
print("=" * 80)
print("O algoritmo fuzzy usa:")
print("1. Múltiplas métricas: ratio, partial_ratio, token_sort_ratio, token_set_ratio")
print("2. Threshold dinâmico: 80-90% dependendo do tamanho do texto")
print("3. Retorna o MÁXIMO score entre todas as métricas")
print("\nO baseline usa:")
print("1. Apenas SequenceMatcher().ratio() (equivalente ao ratio)")
print("2. Threshold fixo de 85%")
