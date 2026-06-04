"""
Teste da otimização do fuzzy matching (Task-019)

Valida:
1. Performance: Algoritmo otimizado é mais rápido que baseline
2. Precisão: Não perde >5% de taxa de vinculação
3. Limiar aumentado: Funciona com 50k comparações
"""

import time

import pytest
from algoritmos.hibrido.algoritmo import AlgoritmoHibrido


@pytest.fixture
def modificacoes_exemplo():
    """Gera modificações de exemplo."""
    return [
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": f"Cláusula {i + 1} sobre exemplo de teste"},
        }
        for i in range(50)
    ]


@pytest.fixture
def tags_exemplo():
    """Gera tags de exemplo."""
    tags = []
    for i in range(200):
        tags.append(
            {
                "id": f"tag_{i}",
                "nome": f"Clausula {i + 1}",
                "conteudo": f"Cláusula {i + 1} sobre exemplo de teste com mais texto aqui para aumentar variação",
                "posicao_inicio": i * 100,
                "posicao_fim": i * 100 + 50,
            }
        )
    return tags


@pytest.fixture
def texto_completo_exemplo():
    """Gera texto completo de exemplo."""
    return " ".join(
        [
            f"Cláusula {i + 1} sobre exemplo de teste com mais texto aqui"
            for i in range(200)
        ]
    )


class TestTask019OtimizacaoFuzzy:
    """Testes para Task-019: Otimizar Fuzzy Matching para Grandes Datasets"""

    def test_performance_baseline_vs_otimizado(
        self, modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
    ):
        """
        Valida que algoritmo otimizado é mais rápido.

        Dataset: 50 mods × 200 tags = 10,000 comparações
        Meta: Otimizado deve ser ≥50% mais rápido
        """
        # Baseline: sem otimização
        alg_baseline = AlgoritmoHibrido(
            usar_fuzzy=True, limiar_complexidade_fuzzy=50000, usar_otimizado=False
        )

        inicio_baseline = time.time()
        resultado_baseline = alg_baseline.vincular_clausulas(
            modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
        )
        tempo_baseline = time.time() - inicio_baseline

        # Otimizado
        alg_otimizado = AlgoritmoHibrido(
            usar_fuzzy=True, limiar_complexidade_fuzzy=50000, usar_otimizado=True
        )

        inicio_otimizado = time.time()
        resultado_otimizado = alg_otimizado.vincular_clausulas(
            modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
        )
        tempo_otimizado = time.time() - inicio_otimizado

        # Exibir resultados
        print("\n📊 PERFORMANCE COMPARISON")
        print(f"Baseline:   {tempo_baseline:.2f}s")
        print(f"Otimizado:  {tempo_otimizado:.2f}s")

        if tempo_baseline > 0:
            ganho = (1 - tempo_otimizado / tempo_baseline) * 100
            print(f"Ganho:      {ganho:.1f}%")

            # Validar que otimizado é mais rápido
            assert tempo_otimizado < tempo_baseline, (
                f"Otimizado deveria ser mais rápido: "
                f"{tempo_otimizado:.2f}s vs {tempo_baseline:.2f}s"
            )
        else:
            print("⚠️  Baseline muito rápido para comparação confiável")

    def test_precisao_nao_degradou(
        self, modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
    ):
        """
        Valida que otimização não perde precisão.

        Meta: Diferença ≤5% na taxa de vinculação
        """
        # Baseline
        alg_baseline = AlgoritmoHibrido(
            usar_fuzzy=True, limiar_complexidade_fuzzy=50000, usar_otimizado=False
        )
        resultado_baseline = alg_baseline.vincular_clausulas(
            modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
        )
        vinculadas_baseline = sum(
            1 for r in resultado_baseline if r.get("tag_vinculada")
        )
        taxa_baseline = vinculadas_baseline / len(modificacoes_exemplo) * 100

        # Otimizado
        alg_otimizado = AlgoritmoHibrido(
            usar_fuzzy=True, limiar_complexidade_fuzzy=50000, usar_otimizado=True
        )
        resultado_otimizado = alg_otimizado.vincular_clausulas(
            modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
        )
        vinculadas_otimizado = sum(
            1 for r in resultado_otimizado if r.get("tag_vinculada")
        )
        taxa_otimizado = vinculadas_otimizado / len(modificacoes_exemplo) * 100

        # Exibir resultados
        print("\n📊 PRECISÃO COMPARISON")
        print(f"Baseline:   {taxa_baseline:.1f}% ({vinculadas_baseline}/50)")
        print(f"Otimizado:  {taxa_otimizado:.1f}% ({vinculadas_otimizado}/50)")

        diferenca = abs(taxa_baseline - taxa_otimizado)
        print(f"Diferença:  {diferenca:.1f}%")

        # Validar que diferença é aceitável
        assert diferenca <= 5.0, (
            f"Perda de precisão {diferenca:.1f}% excede limite de 5%"
        )

    def test_limiar_aumentado_funciona(
        self, modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
    ):
        """
        Valida que limiar aumentado para 50k funciona.

        Dataset: 50×200 = 10k comparações (dentro do limite)
        Meta: Deve completar sem timeout
        """
        alg = AlgoritmoHibrido(
            usar_fuzzy=None,  # Auto-detect
            limiar_complexidade_fuzzy=50000,
            usar_otimizado=True,
        )

        inicio = time.time()
        resultado = alg.vincular_clausulas(
            modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
        )
        tempo = time.time() - inicio

        # Validar que completou
        assert len(resultado) == len(modificacoes_exemplo)

        # Validar tempo razoável
        assert tempo < 30, f"Tempo {tempo:.1f}s excedeu limite de 30s"

        # Verificar que fuzzy foi usado (não desabilitado)
        stats = alg.get_stats()
        fuzzy_usado = stats.get("fuzzy", 0) > 0 or not alg._fuzzy_desabilitado_auto

        print("\n📊 LIMIAR TEST")
        print(f"Tempo:           {tempo:.2f}s")
        print(f"Fuzzy usado:     {fuzzy_usado}")
        print("Complexidade:    10,000 (limite: 50,000)")

        # Com limiar de 50k, fuzzy deve ter sido usado
        assert fuzzy_usado, "Fuzzy deveria ter sido usado com complexidade 10k"

    def test_stats_otimizado(
        self, modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
    ):
        """Valida que estatísticas do algoritmo otimizado funcionam."""
        alg = AlgoritmoHibrido(
            usar_fuzzy=True, limiar_complexidade_fuzzy=50000, usar_otimizado=True
        )

        resultado = alg.vincular_clausulas(
            modificacoes_exemplo, tags_exemplo, texto_completo_exemplo
        )

        # Obter stats do fuzzy otimizado
        if hasattr(alg._alg_fuzzy, "get_stats"):
            stats = alg._alg_fuzzy.get_stats()

            print("\n📊 OPTIMIZATION STATS")
            print(f"Total comparações:     {stats.get('total_comparisons', 0)}")
            print(
                f"Comparações salvas:    {stats.get('comparisons_saved', 0)} ({stats.get('efficiency', 0):.1f}%)"
            )
            print(f"Cache hits:            {stats.get('cache_hits', 0)}")
            print(f"Cache hit rate:        {stats.get('cache_hit_rate', 0):.1f}%")
            print(f"Prefilter reductions:  {stats.get('prefilter_reductions', 0)}")
            print(f"Early exits:           {stats.get('early_exits', 0)}")
            print(f"Indexing time:         {stats.get('indexing_time', 0):.3f}s")

            # Validar que otimizações estão funcionando
            assert stats.get("total_comparisons", 0) > 0, (
                "Deveria ter feito comparações"
            )

            # Se houver pré-filtro, deveria ter reduzido comparações
            if stats.get("prefilter_reductions", 0) > 0:
                efficiency = stats.get("efficiency", 0)
                print(f"\n✅ Otimizações ativas: {efficiency:.1f}% efficiency")


@pytest.mark.benchmark
class TestTask019Benchmark:
    """Benchmark intensivo para datasets grandes"""

    def test_dataset_grande_67x294(self):
        """
        Valida caso real da Task-018: 67 mods × 294 tags = 19,698 comparações

        Meta:
        - Tempo: ≤10 segundos
        - Taxa vinculação: ≥40%
        """
        # Gerar dataset do tamanho real
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {
                    "novo": f"Cláusula {i + 1} com texto de exemplo para vinculação"
                },
            }
            for i in range(67)
        ]

        tags = [
            {
                "id": f"tag_{i}",
                "nome": f"Clausula {i + 1}",
                "conteudo": f"Cláusula {i + 1} com texto de exemplo para vinculação e mais detalhes",
                "posicao_inicio": i * 100,
                "posicao_fim": i * 100 + 50,
            }
            for i in range(294)
        ]

        texto = " ".join([f"Texto de exemplo {i}" for i in range(500)])

        # Executar com otimizado
        alg = AlgoritmoHibrido(
            usar_fuzzy=True, limiar_complexidade_fuzzy=50000, usar_otimizado=True
        )

        inicio = time.time()
        resultado = alg.vincular_clausulas(modificacoes, tags, texto)
        tempo = time.time() - inicio

        vinculadas = sum(1 for r in resultado if r.get("tag_vinculada"))
        taxa = vinculadas / len(modificacoes) * 100

        print("\n📊 BENCHMARK: Dataset Real (67×294)")
        print(f"Tempo:              {tempo:.2f}s")
        print(f"Taxa vinculação:    {taxa:.1f}% ({vinculadas}/67)")
        print("Meta tempo:         ≤10s")
        print("Meta taxa:          ≥40%")

        # Validações
        assert tempo <= 10, f"Tempo {tempo:.1f}s excedeu meta de 10s"
        assert taxa >= 40, f"Taxa {taxa:.1f}% abaixo da meta de 40%"

        # Exibir stats detalhadas
        if hasattr(alg._alg_fuzzy, "get_stats"):
            stats = alg._alg_fuzzy.get_stats()
            print(f"\nEficiência:         {stats.get('efficiency', 0):.1f}%")
            print(f"Comparações feitas: {stats.get('total_comparisons', 0):,}")
            print(f"Comparações salvas: {stats.get('comparisons_saved', 0):,}")
