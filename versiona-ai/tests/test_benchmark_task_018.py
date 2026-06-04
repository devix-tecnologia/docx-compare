"""
Benchmark específico para validar Task-018

Dataset: Usa fixture REAL da versão 99090886
- 55 modificações
- 100 tags mapeadas
- Taxa esperada: ~41.8%
"""

import json
import sys
from pathlib import Path

# Adicionar tests/ ao path
tests_dir = Path(__file__).parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from algoritmos.fuzzy import algoritmo, algoritmo_otimizado  # noqa: F401
from benchmark_fuzzy_runner import AlgorithmBenchmarkRunner


def carregar_dataset_real():
    """Carrega dataset REAL da fixture versão 99090886."""
    fixture_dir = Path(__file__).parent / "sample" / "versao-99090886"

    # Carregar resultado processamento (tem modificações E tags vinculadas)
    with open(fixture_dir / "resultado_processamento.json", encoding="utf-8") as f:
        resultado = json.load(f)

    modificacoes_data = resultado.get("modificacoes", [])
    texto_completo = resultado.get("texto_tagueado", "") or resultado.get(
        "texto_original", ""
    )

    # Converter modificações para formato esperado pelo benchmark
    modificacoes = []
    tags_set = {}  # Dict para coletar tags únicas

    for item in modificacoes_data[:55]:  # Limitar a 55
        mod = item.get("modificacao", {})

        # Extrair texto da modificação
        texto_busca = ""
        tipo = mod.get("tipo", "")

        if tipo == "INSERCAO" or tipo == "ALTERACAO":
            texto_busca = mod.get("conteudo", {}).get("novo", "")
        elif tipo == "REMOCAO":
            texto_busca = mod.get("conteudo", {}).get("original", "")

        if texto_busca:  # Só adiciona se houver texto
            modificacoes.append(
                {
                    "id": mod.get("id", f"mod_{len(modificacoes)}"),
                    "tipo": tipo,
                    "texto_busca": texto_busca[:500],  # Limitar tamanho
                }
            )

        # Coletar tag vinculada (se houver)
        tag_data = item.get("tag", {})
        if tag_data and "conteudo" in tag_data:
            tag_id = tag_data.get("id", f"tag_{len(tags_set)}")
            if tag_id not in tags_set:
                # Extrair informação da cláusula
                clausulas = tag_data.get("clausulas", [])
                primeira_clausula = clausulas[0] if clausulas else {}

                tags_set[tag_id] = {
                    "id": tag_id,
                    "numero": primeira_clausula.get("numero", ""),
                    "nome": primeira_clausula.get("nome", ""),
                    "conteudo": tag_data.get("conteudo", "")[:500],  # Limitar
                    "posicao_inicio": tag_data.get("posicao_inicio_original", 0),
                    "posicao_fim": tag_data.get("posicao_fim_original", 0),
                }

    # Converter dict de tags para lista
    tags = list(tags_set.values())

    return modificacoes, tags, texto_completo


def main():
    print("=" * 80)
    print("BENCHMARK TASK-018: Dataset REAL (versão 99090886)")
    print("=" * 80)

    # Carrega dataset REAL
    print("\n🔨 Carregando fixture real...")
    modificacoes, tags, texto_completo = carregar_dataset_real()

    print(f"   ✅ {len(modificacoes)} modificações")
    print(f"   ✅ {len(tags)} tags")
    print(f"   ✅ Complexidade: {len(modificacoes) * len(tags):,} comparações\n")

    # Executa benchmark com timeout de 60s
    runner = AlgorithmBenchmarkRunner(timeout_segundos=60)

    print("⚠️  AVISO: fuzzy baseline pode demorar >60s (será marcado como INVIÁVEL)\n")

    resultados = runner.compare_all(modificacoes, tags, texto_completo)

    # Imprime tabela
    runner.print_comparison_table(resultados)

    # Análise específica
    print("\n" + "=" * 80)
    print("📈 ANÁLISE TASK-018")
    print("=" * 80)

    otimizado = next(
        (r for r in resultados if r.algoritmo_nome == "fuzzy_otimizado"), None
    )
    baseline = next((r for r in resultados if r.algoritmo_nome == "fuzzy"), None)

    if otimizado and otimizado.status == "ok":
        print("\n✅ fuzzy_otimizado VIÁVEL:")
        print(f"   Tempo: {otimizado.tempo_execucao_s:.2f}s")
        print(f"   Taxa vinculação: {otimizado.taxa_vinculacao:.1f}%")
        print(f"   Comparações: {otimizado.comparacoes_realizadas:,}")
        print(f"   Economizadas: {otimizado.comparacoes_economizadas:,}")
        print(f"   Early exits: {otimizado.early_exits}")

        # Verifica meta da task-019
        meta_tempo = 10.0  # ≤10s
        meta_taxa = 40.0  # ≥40% taxa vinculação (fixture real tem 41.8%)

        if otimizado.tempo_execucao_s <= meta_tempo:
            print(
                f"\n   🎯 META PERFORMANCE: ✅ ({otimizado.tempo_execucao_s:.2f}s ≤ {meta_tempo}s)"
            )
        else:
            print(
                f"\n   ⚠️  META PERFORMANCE: ❌ ({otimizado.tempo_execucao_s:.2f}s > {meta_tempo}s)"
            )

        if otimizado.taxa_vinculacao >= meta_taxa:
            print(
                f"   🎯 META PRECISÃO: ✅ ({otimizado.taxa_vinculacao:.1f}% ≥ {meta_taxa}%)"
            )
        else:
            print(
                f"   ⚠️  META PRECISÃO: ❌ ({otimizado.taxa_vinculacao:.1f}% < {meta_taxa}%)"
            )

    if baseline:
        if baseline.status == "timeout":
            print("\n⏱️  fuzzy baseline: INVIÁVEL (timeout >60s)")
            print("   Confirma problema original da task-018")
        else:
            print(f"\n✅ fuzzy baseline completou em {baseline.tempo_execucao_s:.2f}s")
            if otimizado and otimizado.status == "ok":
                ganho = (
                    (baseline.tempo_execucao_s - otimizado.tempo_execucao_s)
                    / baseline.tempo_execucao_s
                    * 100
                )
                print(f"   Ganho: {ganho:.1f}% mais rápido com otimização")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
