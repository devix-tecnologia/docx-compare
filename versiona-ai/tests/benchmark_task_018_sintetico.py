"""
Benchmark Task-018 com dataset SINTÉTICO

Simula cenário real:
- 67 modificações
- 294 tags
- 19,698 comparações total
"""

import sys
import time
from pathlib import Path

# Adicionar tests/ ao path
tests_dir = Path(__file__).parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from algoritmos.hibrido.algoritmo import AlgoritmoHibrido


def gerar_dataset_sintetico():
    """Gera dataset sintético simulando caso real."""
    print("\n🔨 Gerando dataset sintético...")

    # 67 modificações com textos variados
    modificacoes = []
    textos_mod = [
        "o prazo de vigência do contrato é de 12 meses",
        "a empresa contratada deverá fornecer os serviços",
        "o pagamento será efetuado em até 30 dias",
        "fica estabelecido o valor de R$ 50.000,00",
        "o contrato poderá ser rescindido",
        "as partes elegem o foro de São Paulo",
        "a contratada se obriga a manter sigilo",
        "os serviços serão prestados conforme cronograma",
        "fica vedada a subcontratação",
        "o contrato entra em vigor na data de assinatura",
    ]

    for i in range(67):
        texto = textos_mod[i % len(textos_mod)]
        modificacoes.append(
            {
                "id": f"mod_{i}",
                "tipo": "ALTERACAO",
                "conteudo": {
                    "antigo": texto,
                    "novo": texto.replace("12", "24")
                    if "12" in texto
                    else texto + " alterado",
                },
            }
        )

    # 294 tags com conteúdos variados
    tags = []
    textos_tag = [
        "Prazo de vigência do contrato de 12 meses",
        "Fornecimento de serviços pela contratada",
        "Pagamento efetuado em 30 dias",
        "Valor contratual de R$ 50.000,00",
        "Rescisão contratual",
        "Foro eleito São Paulo",
        "Sigilo de informações",
        "Prestação de serviços conforme cronograma",
        "Vedação à subcontratação",
        "Vigência a partir da assinatura",
    ]

    for i in range(294):
        texto = textos_tag[i % len(textos_tag)]
        tags.append(
            {
                "id": f"tag_{i}",
                "numero": f"{(i // 10) + 1}.{(i % 10) + 1}",
                "nome": f"Cláusula {i + 1}",
                "conteudo": texto,
                "posicao_inicio": i * 100,
                "posicao_fim": i * 100 + len(texto),
            }
        )

    texto_completo = "\n\n".join([t["conteudo"] for t in tags])

    print(f"   ✅ {len(modificacoes)} modificações")
    print(f"   ✅ {len(tags)} tags")
    print(f"   ✅ Complexidade: {len(modificacoes) * len(tags):,} comparações")

    return modificacoes, tags, texto_completo


def main():
    print("=" * 80)
    print("BENCHMARK TASK-018: Dataset SINTÉTICO (67 mods × 294 tags)")
    print("=" * 80)

    modificacoes, tags, texto_completo = gerar_dataset_sintetico()

    # Teste com fuzzy DESABILITADO (baseline task-018)
    print("\n" + "-" * 80)
    print("🔴 Teste 1: Fuzzy DESABILITADO (baseline task-018)")
    print("-" * 80)

    algoritmo_sem_fuzzy = AlgoritmoHibrido(usar_fuzzy=False)

    inicio = time.time()
    resultado_sem_fuzzy = algoritmo_sem_fuzzy.vincular_clausulas(
        modificacoes, tags, texto_completo
    )
    tempo_sem_fuzzy = time.time() - inicio

    vinculadas_sem_fuzzy = sum(1 for r in resultado_sem_fuzzy if r.get("tag_vinculada"))
    taxa_sem_fuzzy = vinculadas_sem_fuzzy / len(modificacoes) * 100

    print(f"   Tempo: {tempo_sem_fuzzy:.2f}s")
    print(f"   Vinculadas: {vinculadas_sem_fuzzy}/{len(modificacoes)}")
    print(f"   Taxa: {taxa_sem_fuzzy:.1f}%")

    # Teste com fuzzy BASELINE (deve dar timeout ou demorar muito)
    print("\n" + "-" * 80)
    print("⚠️  Teste 2: Fuzzy BASELINE (deve ser lento)")
    print("-" * 80)

    algoritmo_baseline = AlgoritmoHibrido(usar_fuzzy=True, usar_otimizado=False)

    print("   ⏳ Rodando (pode demorar >60s)...")
    inicio = time.time()
    try:
        resultado_baseline = algoritmo_baseline.vincular_clausulas(
            modificacoes, tags, texto_completo
        )
        tempo_baseline = time.time() - inicio

        vinculadas_baseline = sum(
            1 for r in resultado_baseline if r.get("tag_vinculada")
        )
        taxa_baseline = vinculadas_baseline / len(modificacoes) * 100

        print(f"   Tempo: {tempo_baseline:.2f}s")
        print(f"   Vinculadas: {vinculadas_baseline}/{len(modificacoes)}")
        print(f"   Taxa: {taxa_baseline:.1f}%")

        if tempo_baseline > 60:
            print("   ⚠️  TIMEOUT: Excedeu 60s (INVIÁVEL)")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

    # Teste com fuzzy OTIMIZADO (deve ser rápido)
    print("\n" + "-" * 80)
    print("✅ Teste 3: Fuzzy OTIMIZADO (cache + TF-IDF + early exit)")
    print("-" * 80)

    algoritmo_otimizado = AlgoritmoHibrido(
        usar_fuzzy=True,
        usar_otimizado=True,
        prefilter_top_k=50,
        early_exit_threshold=85.0,
    )

    inicio = time.time()
    resultado_otimizado = algoritmo_otimizado.vincular_clausulas(
        modificacoes, tags, texto_completo
    )
    tempo_otimizado = time.time() - inicio

    vinculadas_otimizado = sum(1 for r in resultado_otimizado if r.get("tag_vinculada"))
    taxa_otimizado = vinculadas_otimizado / len(modificacoes) * 100

    print(f"   Tempo: {tempo_otimizado:.2f}s")
    print(f"   Vinculadas: {vinculadas_otimizado}/{len(modificacoes)}")
    print(f"   Taxa: {taxa_otimizado:.1f}%")

    # Estatísticas do fuzzy otimizado
    stats = algoritmo_otimizado._alg_fuzzy.get_stats()
    print("\n   📊 Estatísticas:")
    print(f"      Cache hit rate: {stats.get('cache_hit_rate', 0):.1f}%")
    print(f"      Comparações economizadas: {stats.get('comparisons_saved', 0):,}")
    print(f"      Early exits: {stats.get('early_exits', 0)}")
    print(f"      TF-IDF reductions: {stats.get('prefilter_reductions', 0):,}")

    # Análise final
    print("\n" + "=" * 80)
    print("📊 ANÁLISE TASK-018")
    print("=" * 80)

    print("\n✅ Sem fuzzy (baseline task-018):")
    print(f"   Taxa: {taxa_sem_fuzzy:.1f}% (abaixo da meta de 40%)")

    print("\n✅ Com fuzzy otimizado:")
    print(f"   Taxa: {taxa_otimizado:.1f}%")

    # Verificar metas da task-019
    meta_tempo = 10.0  # ≤10s
    meta_taxa = 40.0  # ≥40%
    limiar = 50000  # Suporta até 50k comparações

    print("\n🎯 METAS TASK-019:")

    if tempo_otimizado <= meta_tempo:
        print(f"   ✅ Performance: {tempo_otimizado:.2f}s ≤ {meta_tempo}s")
    else:
        print(f"   ❌ Performance: {tempo_otimizado:.2f}s > {meta_tempo}s")

    if taxa_otimizado >= meta_taxa:
        print(f"   ✅ Precisão: {taxa_otimizado:.1f}% ≥ {meta_taxa}%")
    else:
        print(
            f"   ⚠️  Precisão: {taxa_otimizado:.1f}% < {meta_taxa}% (dados sintéticos)"
        )

    comparacoes = len(modificacoes) * len(tags)
    if comparacoes <= limiar:
        print(f"   ✅ Complexidade: {comparacoes:,} ≤ {limiar:,}")
    else:
        print(f"   ❌ Complexidade: {comparacoes:,} > {limiar:,}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
