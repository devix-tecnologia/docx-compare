"""
Benchmark Runner - Comparação Automática de Algoritmos de Fuzzy Matching

Descobre e executa todos os algoritmos registrados, comparando:
- Performance (tempo de execução)
- Qualidade (taxa de vinculação)
- Eficiência (comparações realizadas)

Uso:
    python versiona-ai/tests/benchmark_fuzzy_runner.py

    # Ou com dataset customizado
    runner = AlgorithmBenchmarkRunner()
    resultados = runner.compare_all(modificacoes, tags, texto_completo)
    runner.print_comparison_table(resultados)
"""

import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Adicionar tests/ ao path
tests_dir = Path(__file__).parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from algoritmos.registry import get_registered_algorithms  # noqa: E402


@dataclass
class BenchmarkResult:
    """Resultado de benchmark de um algoritmo."""

    algoritmo_nome: str
    algoritmo_descricao: str
    tempo_execucao_s: float
    taxa_vinculacao: float  # % de modificações vinculadas
    total_modificacoes: int
    modificacoes_vinculadas: int
    comparacoes_realizadas: int  # Se disponível via stats
    comparacoes_economizadas: int  # Se disponível via stats
    cache_hit_rate: float  # % se disponível
    early_exits: int  # Se disponível
    erro_execucao: str | None = None


class AlgorithmBenchmarkRunner:
    """Runner para executar e comparar múltiplos algoritmos."""

    def __init__(self):
        self.resultados: list[BenchmarkResult] = []

    def _extract_stats(self, algoritmo: Any) -> dict:
        """Extrai estatísticas do algoritmo se disponível."""
        stats = {}

        # Tenta obter stats se algoritmo tiver
        if hasattr(algoritmo, "_stats"):
            stats = algoritmo._stats.copy()
        elif hasattr(algoritmo, "stats"):
            stats = algoritmo.stats.copy()
        elif hasattr(algoritmo, "get_stats") and callable(algoritmo.get_stats):
            stats = algoritmo.get_stats()

        return stats

    def run_single_algorithm(
        self,
        algoritmo_nome: str,
        algoritmo_class: type,
        modificacoes: list[dict],
        tags: list[dict],
        texto_completo: str,
    ) -> BenchmarkResult:
        """
        Executa um algoritmo e coleta métricas.

        Args:
            algoritmo_nome: Nome do algoritmo
            algoritmo_class: Classe do algoritmo
            modificacoes: Lista de modificações a vincular
            tags: Lista de tags disponíveis
            texto_completo: Texto completo do documento

        Returns:
            BenchmarkResult com métricas coletadas
        """
        try:
            # Instancia algoritmo
            algoritmo = algoritmo_class()

            # Extrai descrição
            descricao = (
                algoritmo.descricao
                if hasattr(algoritmo, "descricao")
                else "Sem descrição"
            )

            # Executa com medição de tempo
            inicio = time.time()
            resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto_completo)
            tempo_execucao = time.time() - inicio

            # Calcula taxa de vinculação
            total_mods = len(modificacoes)
            vinculadas = sum(1 for r in resultado if r.get("tag_vinculada") is not None)
            taxa_vinculacao = (vinculadas / total_mods * 100) if total_mods > 0 else 0.0

            # Extrai estatísticas adicionais
            stats = self._extract_stats(algoritmo)

            comparacoes_realizadas = stats.get("total_comparisons", 0)
            comparacoes_economizadas = stats.get("comparisons_saved", 0)

            cache_hits = stats.get("cache_hits", 0)
            cache_misses = stats.get("cache_misses", 0)
            cache_hit_rate = (
                (cache_hits / (cache_hits + cache_misses) * 100)
                if (cache_hits + cache_misses) > 0
                else 0.0
            )

            early_exits = stats.get("early_exits", 0)

            return BenchmarkResult(
                algoritmo_nome=algoritmo_nome,
                algoritmo_descricao=descricao,
                tempo_execucao_s=tempo_execucao,
                taxa_vinculacao=taxa_vinculacao,
                total_modificacoes=total_mods,
                modificacoes_vinculadas=vinculadas,
                comparacoes_realizadas=comparacoes_realizadas,
                comparacoes_economizadas=comparacoes_economizadas,
                cache_hit_rate=cache_hit_rate,
                early_exits=early_exits,
                erro_execucao=None,
            )

        except Exception as e:
            return BenchmarkResult(
                algoritmo_nome=algoritmo_nome,
                algoritmo_descricao="ERRO",
                tempo_execucao_s=0.0,
                taxa_vinculacao=0.0,
                total_modificacoes=len(modificacoes),
                modificacoes_vinculadas=0,
                comparacoes_realizadas=0,
                comparacoes_economizadas=0,
                cache_hit_rate=0.0,
                early_exits=0,
                erro_execucao=str(e),
            )

    def compare_all(
        self, modificacoes: list[dict], tags: list[dict], texto_completo: str
    ) -> list[BenchmarkResult]:
        """
        Executa todos os algoritmos registrados e compara resultados.

        Args:
            modificacoes: Lista de modificações a vincular
            tags: Lista de tags disponíveis
            texto_completo: Texto completo do documento

        Returns:
            Lista de BenchmarkResult ordenada por tempo de execução
        """
        algoritmos = get_registered_algorithms()

        if not algoritmos:
            print("⚠️  Nenhum algoritmo registrado! Importe os módulos primeiro.")
            return []

        resultados = []

        print(f"\n🏁 Executando {len(algoritmos)} algoritmos...")
        print(f"   Dataset: {len(modificacoes)} mods × {len(tags)} tags\n")

        for nome, classe in algoritmos.items():
            print(f"⏱️  Testando '{nome}'...", end=" ", flush=True)

            resultado = self.run_single_algorithm(
                nome, classe, modificacoes, tags, texto_completo
            )

            resultados.append(resultado)

            if resultado.erro_execucao:
                print(f"❌ ERRO: {resultado.erro_execucao}")
            else:
                print(
                    f"✅ {resultado.tempo_execucao_s:.2f}s | "
                    f"{resultado.taxa_vinculacao:.1f}% vinculação"
                )

        # Ordena por tempo de execução
        self.resultados = sorted(resultados, key=lambda r: r.tempo_execucao_s)

        return self.resultados

    def print_comparison_table(self, resultados: list[BenchmarkResult] | None = None):
        """
        Imprime tabela comparativa formatada.

        Args:
            resultados: Lista de resultados (usa self.resultados se None)
        """
        if resultados is None:
            resultados = self.resultados

        if not resultados:
            print("Nenhum resultado para exibir.")
            return

        print("\n" + "=" * 120)
        print("📊 COMPARAÇÃO DE ALGORITMOS DE FUZZY MATCHING")
        print("=" * 120)

        # Header
        print(
            f"{'Algoritmo':<20} | {'Tempo (s)':>10} | {'Taxa Vinc.':>11} | "
            f"{'Comparações':>12} | {'Economizadas':>12} | {'Cache Hit':>10} | {'Early Exit':>11}"
        )
        print("-" * 120)

        # Baseline para cálculo de ganho
        baseline = resultados[0] if resultados else None

        for i, r in enumerate(resultados):
            # Calcula ganho vs baseline
            if i == 0:
                ganho_str = "baseline"
            elif baseline and baseline.tempo_execucao_s > 0:
                ganho_pct = (
                    (baseline.tempo_execucao_s - r.tempo_execucao_s)
                    / baseline.tempo_execucao_s
                    * 100
                )
                ganho_str = f"↑{ganho_pct:+.1f}%"
            else:
                ganho_str = "N/A"

            # Formatação condicional
            tempo_str = (
                f"{r.tempo_execucao_s:10.2f}" if not r.erro_execucao else "      ERRO"
            )
            taxa_str = f"{r.taxa_vinculacao:10.1f}%"
            comp_str = (
                f"{r.comparacoes_realizadas:12,}"
                if r.comparacoes_realizadas > 0
                else "           -"
            )
            econ_str = (
                f"{r.comparacoes_economizadas:12,}"
                if r.comparacoes_economizadas > 0
                else "           -"
            )
            cache_str = (
                f"{r.cache_hit_rate:9.1f}%" if r.cache_hit_rate > 0 else "        -"
            )
            exits_str = f"{r.early_exits:11,}" if r.early_exits > 0 else "          -"

            # Emoji de ranking
            if i == 0:
                emoji = "🥇"
            elif i == 1:
                emoji = "🥈"
            elif i == 2:
                emoji = "🥉"
            else:
                emoji = "  "

            print(
                f"{emoji} {r.algoritmo_nome:<17} | {tempo_str} | {taxa_str} | "
                f"{comp_str} | {econ_str} | {cache_str} | {exits_str} | {ganho_str}"
            )

            if r.erro_execucao:
                print(f"   └─> ❌ Erro: {r.erro_execucao}")

        print("=" * 120)

        # Estatísticas finais
        if len(resultados) > 1:
            melhor = resultados[0]
            print(f"\n🏆 Vencedor: {melhor.algoritmo_nome}")
            print(f"   Tempo: {melhor.tempo_execucao_s:.2f}s")
            print(f"   Taxa de vinculação: {melhor.taxa_vinculacao:.1f}%")
            print(
                f"   Vinculadas: {melhor.modificacoes_vinculadas}/{melhor.total_modificacoes}"
            )

    def export_to_json(self, filepath: str):
        """Exporta resultados para JSON."""
        import json

        data = [
            {
                "algoritmo": r.algoritmo_nome,
                "descricao": r.algoritmo_descricao,
                "tempo_s": r.tempo_execucao_s,
                "taxa_vinculacao": r.taxa_vinculacao,
                "comparacoes": r.comparacoes_realizadas,
                "cache_hit_rate": r.cache_hit_rate,
                "erro": r.erro_execucao,
            }
            for r in self.resultados
        ]

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Resultados exportados para: {filepath}")


def main():
    """Exemplo de uso do benchmark runner."""

    # Import algoritmos para registrá-los
    print("📦 Importando algoritmos...")
    try:
        # Importa todos os algoritmos da pasta fuzzy (trigger registro)
        from algoritmos.fuzzy import algoritmo, algoritmo_otimizado  # noqa: F401

        print("   ✅ Algoritmos importados com sucesso")
    except ImportError as e:
        print(f"   ❌ Erro ao importar algoritmos: {e}")
        return

    # Cria dataset de teste
    print("\n🔨 Criando dataset de teste...")

    modificacoes = [
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": f"Cláusula {i} do presente contrato"},
        }
        for i in range(50)
    ]

    tags = [
        {
            "nome": f"clausula_{i}",
            "texto": f"Cláusula {i} do presente contrato",
            "posicao_inicio": i * 100,
            "posicao_fim": (i + 1) * 100,
        }
        for i in range(200)
    ]

    texto_completo = " ".join([tag["texto"] for tag in tags])

    print(f"   {len(modificacoes)} modificações")
    print(f"   {len(tags)} tags")
    print(f"   Complexidade: {len(modificacoes) * len(tags):,} comparações")

    # Executa benchmark
    runner = AlgorithmBenchmarkRunner()
    resultados = runner.compare_all(modificacoes, tags, texto_completo)

    # Exibe resultados
    runner.print_comparison_table(resultados)

    # Exporta JSON
    output_path = Path(__file__).parent / "results" / "benchmark_results.json"
    output_path.parent.mkdir(exist_ok=True)
    runner.export_to_json(str(output_path))


if __name__ == "__main__":
    main()
