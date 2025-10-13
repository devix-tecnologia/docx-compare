"""
Benchmark realista simulando o caso de produção.

Força fuzzy matching usando tags ligeiramente modificadas.
"""

import sys
import time
from pathlib import Path

# Adiciona versiona-ai ao path
versiona_ai_path = Path(__file__).parent.parent / "versiona-ai"
sys.path.insert(0, str(versiona_ai_path))

from matching import DifflibMatcher, RapidFuzzMatcher


def create_realistic_document(size_kb: int = 500) -> str:
    """Cria documento similar ao de produção."""
    base_clause = """
    CLÁUSULA {num} - {title}

    {content}

    {num}.1 - {subcontent1}
    {num}.2 - {subcontent2}
    {num}.3 - {subcontent3}

    """

    clauses = []
    for i in range(1, 31):  # 30 cláusulas
        clause = base_clause.format(
            num=i,
            title=f"DAS DISPOSIÇÕES DA CLÁUSULA NÚMERO {i}",
            content=f"O presente contrato estabelece na cláusula {i} "
            f"as condições específicas para este item do contrato. "
            f"As partes concordam com os termos aqui estabelecidos "
            f"conforme previsto na legislação vigente e aplicável.",
            subcontent1=f"Primeiro item da cláusula {i} estabelecendo condições iniciais",
            subcontent2=f"Segundo item da cláusula {i} com disposições intermediárias",
            subcontent3=f"Terceiro item da cláusula {i} finalizando as disposições",
        )
        clauses.append(clause)

    # Repete para atingir o tamanho desejado
    document = "\n".join(clauses)
    repeats_needed = (size_kb * 1024) // len(document) + 1
    return (document * repeats_needed)[: size_kb * 1024]


def benchmark_fuzzy_matching(
    matcher, needle: str, haystack: str
) -> tuple[float, float]:
    """Benchmark focado em fuzzy matching (não há match exato)."""
    start = time.perf_counter()
    result = matcher.find_best_match(needle, haystack, threshold=0.85)
    elapsed = time.perf_counter() - start

    return elapsed, result.similarity


def main():
    print("\n" + "=" * 70)
    print("🔬 BENCHMARK REALISTA - FUZZY MATCHING (Caso de Produção)")
    print("=" * 70)

    # Cria documento de produção (~500KB)
    print("\n📄 Criando documento de 500KB...")
    haystack = create_realistic_document(500)
    print(
        f"   Documento criado: {len(haystack):,} caracteres ({len(haystack) / 1024:.1f} KB)"
    )

    # Tag ligeiramente modificada (força fuzzy matching)
    # Original: "Primeiro item da cláusula 15 estabelecendo condições iniciais"
    needle_fuzzy = "Primeiro item da clausula 15 estabelecendo condicoes iniciais"
    print(f"\n🎯 Tag a procurar (modificada): '{needle_fuzzy[:50]}...'")
    print(f"   Tamanho da tag: {len(needle_fuzzy)} caracteres")

    results = {}

    # Benchmark Difflib
    print("\n⏱️  Testando Difflib...")
    difflib_matcher = DifflibMatcher()
    time_difflib, sim_difflib = benchmark_fuzzy_matching(
        difflib_matcher, needle_fuzzy, haystack
    )
    results["difflib"] = {"time": time_difflib, "similarity": sim_difflib}
    print(f"   ✓ Tempo: {time_difflib:.3f}s | Similaridade: {sim_difflib * 100:.1f}%")

    # Benchmark RapidFuzz
    print("\n⚡ Testando RapidFuzz...")
    rapidfuzz_matcher = RapidFuzzMatcher()
    time_rapidfuzz, sim_rapidfuzz = benchmark_fuzzy_matching(
        rapidfuzz_matcher, needle_fuzzy, haystack
    )
    results["rapidfuzz"] = {"time": time_rapidfuzz, "similarity": sim_rapidfuzz}
    print(
        f"   ✓ Tempo: {time_rapidfuzz:.3f}s | Similaridade: {sim_rapidfuzz * 100:.1f}%"
    )

    # Análise comparativa
    print("\n" + "=" * 70)
    print("📊 RESULTADOS COMPARATIVOS")
    print("=" * 70)

    speedup = time_difflib / time_rapidfuzz
    print(f"\n⚡ Speedup RapidFuzz: {speedup:.1f}x mais rápido")
    print(f"   Difflib:    {time_difflib:.3f}s")
    print(f"   RapidFuzz:  {time_rapidfuzz:.3f}s")
    print(f"   Diferença:  {time_difflib - time_rapidfuzz:.3f}s economizados por tag")

    # Extrapolação para 440 tags
    print("\n📈 EXTRAPOLAÇÃO PARA 440 TAGS (Produção)")
    print("-" * 70)

    time_440_difflib = time_difflib * 440
    time_440_rapidfuzz = time_rapidfuzz * 440
    savings_minutes = (time_440_difflib - time_440_rapidfuzz) / 60

    print(
        f"   Difflib:    {time_440_difflib / 60:7.1f} minutos ({time_440_difflib / 3600:5.2f} horas)"
    )
    print(
        f"   RapidFuzz:  {time_440_rapidfuzz / 60:7.1f} minutos ({time_440_rapidfuzz / 3600:5.2f} horas)"
    )
    print(
        f"   💰 Economia: {savings_minutes:7.1f} minutos ({savings_minutes / 60:5.2f} horas)"
    )

    # Com paralelização (8 workers)
    print("\n🚀 COM PARALELIZAÇÃO (8 workers ProcessPool)")
    print("-" * 70)

    time_440_difflib_parallel = time_440_difflib / 8
    time_440_rapidfuzz_parallel = time_440_rapidfuzz / 8

    print(
        f"   Difflib:    {time_440_difflib_parallel / 60:7.1f} minutos ({time_440_difflib_parallel / 3600:5.2f} horas)"
    )
    print(
        f"   RapidFuzz:  {time_440_rapidfuzz_parallel / 60:7.1f} minutos ({time_440_rapidfuzz_parallel / 3600:5.2f} horas)"
    )

    # Recomendação
    print("\n" + "=" * 70)
    if speedup > 2:
        print("✅ RECOMENDAÇÃO: Migrar para RapidFuzz")
        print(f"   Ganho significativo de {speedup:.1f}x na performance")
        print(f"   Redução de {savings_minutes:.0f} minutos no processamento total")
    elif speedup > 1.2:
        print("⚠️  RECOMENDAÇÃO: Considerar RapidFuzz")
        print(f"   Ganho moderado de {speedup:.1f}x na performance")
    else:
        print("ℹ️  RECOMENDAÇÃO: Manter Difflib")
        print("   Ganho de performance não justifica mudança")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
