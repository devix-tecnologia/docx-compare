"""
Testes Automatizados de Comparação de Algoritmos - Task 019

Valida que todos os algoritmos registrados:
1. Executam sem erros
2. Atendem critérios de performance
3. Mantêm taxa de vinculação aceitável
4. São comparáveis entre si

Uso:
    pytest versiona-ai/tests/test_task_019_comparacao.py -v
"""

import pytest
from algoritmos.fuzzy import algoritmo, algoritmo_otimizado  # noqa: F401
from algoritmos.registry import get_registered_algorithms, list_algorithms
from benchmark_fuzzy_runner import AlgorithmBenchmarkRunner


class TestAlgorithmRegistry:
    """Testa sistema de registro de algoritmos."""

    def test_registry_nao_vazio(self):
        """Valida que pelo menos um algoritmo está registrado."""
        algoritmos = list_algorithms()
        assert len(algoritmos) > 0, "Nenhum algoritmo registrado!"

    def test_baseline_fuzzy_registrado(self):
        """Valida que baseline fuzzy está registrado."""
        algoritmos = list_algorithms()
        assert "fuzzy" in algoritmos, "Algoritmo baseline 'fuzzy' não registrado!"

    def test_todos_algoritmos_tem_nome_unico(self):
        """Valida que não há duplicatas de nomes."""
        algoritmos = list_algorithms()
        assert len(algoritmos) == len(set(algoritmos)), (
            "Nomes de algoritmos duplicados!"
        )


class TestAlgorithmExecution:
    """Testa execução de algoritmos."""

    @pytest.fixture
    def dataset_pequeno(self):
        """Dataset pequeno para testes rápidos."""
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Cláusula primeira do contrato"},
            },
            {
                "tipo": "ALTERACAO",
                "conteudo": {
                    "original": "prazo de 6 meses",
                    "novo": "prazo de 12 meses",
                },
            },
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Cláusula segunda sobre pagamentos"},
            },
        ]

        tags = [
            {
                "nome": "clausula_1",
                "texto": "Cláusula primeira do contrato",
                "posicao_inicio": 0,
                "posicao_fim": 50,
            },
            {
                "nome": "clausula_2",
                "texto": "Prazo de vigência de 6 meses",
                "posicao_inicio": 51,
                "posicao_fim": 100,
            },
            {
                "nome": "clausula_3",
                "texto": "Cláusula segunda sobre pagamentos",
                "posicao_inicio": 101,
                "posicao_fim": 150,
            },
        ]

        texto_completo = " ".join([tag["texto"] for tag in tags])

        return {"modificacoes": modificacoes, "tags": tags, "texto": texto_completo}

    def test_todos_algoritmos_executam_sem_erro(self, dataset_pequeno):
        """Valida que todos os algoritmos executam sem exceções."""
        runner = AlgorithmBenchmarkRunner()
        resultados = runner.compare_all(
            dataset_pequeno["modificacoes"],
            dataset_pequeno["tags"],
            dataset_pequeno["texto"],
        )

        for resultado in resultados:
            assert resultado.erro_execucao is None, (
                f"Algoritmo '{resultado.algoritmo_nome}' falhou: {resultado.erro_execucao}"
            )

    def test_todos_algoritmos_retornam_resultados(self, dataset_pequeno):
        """Valida que todos os algoritmos retornam lista de resultados."""
        algoritmos = get_registered_algorithms()

        for nome, classe in algoritmos.items():
            algo = classe()
            resultado = algo.vincular_clausulas(
                dataset_pequeno["modificacoes"],
                dataset_pequeno["tags"],
                dataset_pequeno["texto"],
            )

            assert isinstance(resultado, list), f"'{nome}' não retornou lista"
            assert len(resultado) == len(dataset_pequeno["modificacoes"]), (
                f"'{nome}' retornou número errado de resultados"
            )


class TestPerformanceCriteria:
    """Testa critérios de performance - Task 019."""

    @pytest.fixture
    def dataset_medio(self):
        """Dataset médio - 50 mods × 200 tags = 10k comparações."""
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": f"Texto modificação {i}"},
            }
            for i in range(50)
        ]

        tags = [
            {
                "nome": f"tag_{i}",
                "texto": f"Texto da tag número {i}",
                "posicao_inicio": i * 50,
                "posicao_fim": (i + 1) * 50,
            }
            for i in range(200)
        ]

        texto_completo = " ".join([tag["texto"] for tag in tags])

        return {"modificacoes": modificacoes, "tags": tags, "texto": texto_completo}

    def test_performance_dataset_medio(self, dataset_medio):
        """Valida performance em dataset médio (10k comparações)."""
        runner = AlgorithmBenchmarkRunner()
        resultados = runner.compare_all(
            dataset_medio["modificacoes"],
            dataset_medio["tags"],
            dataset_medio["texto"],
        )

        # Pelo menos um algoritmo deve completar em tempo razoável
        tempos = [r.tempo_execucao_s for r in resultados if not r.erro_execucao]
        assert min(tempos) < 30.0, "Nenhum algoritmo completou em <30s"

    def test_taxa_vinculacao_aceitavel(self, dataset_medio):
        """Valida que pelo menos um algoritmo atinge taxa aceitável."""
        runner = AlgorithmBenchmarkRunner()
        resultados = runner.compare_all(
            dataset_medio["modificacoes"],
            dataset_medio["tags"],
            dataset_medio["texto"],
        )

        taxas = [r.taxa_vinculacao for r in resultados if not r.erro_execucao]

        # Pelo menos um algoritmo deve ter taxa > 0%
        assert max(taxas) > 0, "Nenhum algoritmo vinculou modificações"


class TestAlgorithmComparison:
    """Testa comparação A/B entre algoritmos."""

    @pytest.fixture
    def dataset_comparacao(self):
        """Dataset para comparação A/B."""
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {"novo": "Cláusula sobre prazo de vigência"},
            },
            {
                "tipo": "ALTERACAO",
                "conteudo": {"original": "12 meses", "novo": "24 meses"},
            },
        ]

        tags = [
            {
                "nome": "prazo",
                "texto": "Prazo de vigência de 12 meses",
                "posicao_inicio": 0,
                "posicao_fim": 50,
            },
            {
                "nome": "valor",
                "texto": "Valor mensal de R$ 1.000,00",
                "posicao_inicio": 51,
                "posicao_fim": 100,
            },
        ]

        texto_completo = " ".join([tag["texto"] for tag in tags])

        return {"modificacoes": modificacoes, "tags": tags, "texto": texto_completo}

    def test_resultados_consistentes_entre_algoritmos(self, dataset_comparacao):
        """
        Valida que algoritmos diferentes produzem resultados similares
        (podem divergir levemente mas não drasticamente).
        """
        runner = AlgorithmBenchmarkRunner()
        resultados = runner.compare_all(
            dataset_comparacao["modificacoes"],
            dataset_comparacao["tags"],
            dataset_comparacao["texto"],
        )

        # Coleta taxas de vinculação
        taxas = [r.taxa_vinculacao for r in resultados if not r.erro_execucao]

        if len(taxas) > 1:
            # Diferença máxima entre algoritmos não deve ser > 30%
            diferenca = max(taxas) - min(taxas)
            assert diferenca <= 30.0, (
                f"Algoritmos divergem muito: {diferenca:.1f}% diferença"
            )

    def test_benchmark_gera_ranking(self, dataset_comparacao):
        """Valida que benchmark gera ranking ordenado por tempo."""
        runner = AlgorithmBenchmarkRunner()
        resultados = runner.compare_all(
            dataset_comparacao["modificacoes"],
            dataset_comparacao["tags"],
            dataset_comparacao["texto"],
        )

        # Verifica ordenação por tempo
        tempos = [r.tempo_execucao_s for r in resultados if not r.erro_execucao]
        assert tempos == sorted(tempos), "Resultados não estão ordenados por tempo"


def test_exemplo_uso_benchmark():
    """Teste de exemplo mostrando uso do benchmark."""
    runner = AlgorithmBenchmarkRunner()

    # Dataset pequeno
    modificacoes = [
        {"tipo": "INSERCAO", "conteudo": {"novo": "Teste"}},
    ]

    tags = [{"nome": "tag1", "texto": "Teste", "posicao_inicio": 0, "posicao_fim": 10}]

    texto = "Teste"

    # Executa
    resultados = runner.compare_all(modificacoes, tags, texto)

    # Valida que retornou resultados
    assert len(resultados) > 0

    # Imprime (para visualização no pytest -s)
    runner.print_comparison_table()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
