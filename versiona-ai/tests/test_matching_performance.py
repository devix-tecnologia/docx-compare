"""
Benchmark de performance para estratégias de matching.

Compara velocidade e qualidade de diferentes implementações.
"""

import time

from matching import DifflibMatcher, MatchingStrategy
from matching.rapidfuzz_matcher import (
    RAPIDFUZZ_AVAILABLE,
    RapidFuzzMatcher,
)


def benchmark_matcher(
    matcher: MatchingStrategy,
    needle: str,
    haystack: str,
    iterations: int = 10,
) -> tuple[float, float]:
    """
    Executa benchmark de uma estratégia de matching.

    Returns:
        tuple: (tempo_medio_segundos, similaridade_media)
    """
    times = []
    similarities = []

    for _ in range(iterations):
        start = time.perf_counter()
        result = matcher.find_best_match(needle, haystack, threshold=0.85)
        end = time.perf_counter()

        times.append(end - start)
        similarities.append(result.similarity)

    avg_time = sum(times) / len(times)
    avg_similarity = sum(similarities) / len(similarities)

    return avg_time, avg_similarity


class TestPerformanceBenchmark:
    """Benchmarks de performance comparando diferentes estratégias."""

    def test_benchmark_small_document(self):
        """Benchmark com documento pequeno (~1KB)."""
        needle = "cláusula 5.1 do presente contrato"
        haystack = (
            """
        CONTRATO DE PRESTAÇÃO DE SERVIÇOS

        Entre as partes, doravante denominadas CONTRATANTE e CONTRATADA,
        firmam o presente instrumento de contrato.

        CLÁUSULA PRIMEIRA - DO OBJETO
        O presente contrato tem como objeto a prestação de serviços.

        CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES
        Conforme estipulado na cláusula 5.1 do presente contrato,
        a CONTRATADA deverá prestar os serviços com qualidade.

        CLÁUSULA TERCEIRA - DO PRAZO
        O prazo de vigência será de 12 meses.
        """
            * 10
        )  # Repete 10x para ~1KB

        results = {}

        # Benchmark Difflib
        difflib_matcher = DifflibMatcher()
        time_difflib, sim_difflib = benchmark_matcher(
            difflib_matcher, needle, haystack, iterations=5
        )
        results["difflib"] = {"time": time_difflib, "similarity": sim_difflib}

        # Benchmark RapidFuzz (se disponível)
        if RAPIDFUZZ_AVAILABLE:
            rapidfuzz_matcher = RapidFuzzMatcher()
            time_rapidfuzz, sim_rapidfuzz = benchmark_matcher(
                rapidfuzz_matcher, needle, haystack, iterations=5
            )
            results["rapidfuzz"] = {
                "time": time_rapidfuzz,
                "similarity": sim_rapidfuzz,
            }

        # Imprime resultados
        print("\n" + "=" * 60)
        print("BENCHMARK: Documento Pequeno (~1KB)")
        print("=" * 60)

        for name, data in results.items():
            print(
                f"{name:12} | Tempo: {data['time'] * 1000:7.2f}ms | "
                f"Similaridade: {data['similarity'] * 100:5.1f}%"
            )

        # Calcula speedup se ambos disponíveis
        if "rapidfuzz" in results and "difflib" in results:
            speedup = results["difflib"]["time"] / results["rapidfuzz"]["time"]
            print(f"\n⚡ Speedup RapidFuzz: {speedup:.1f}x mais rápido")

        print("=" * 60)

        # Valida que ambos encontraram o texto
        assert all(data["similarity"] >= 0.85 for data in results.values())

    def test_benchmark_medium_document(self):
        """Benchmark com documento médio (~50KB)."""
        needle = "cláusula específica sobre responsabilidades"

        # Cria documento médio (~50KB)
        base_text = """
        CONTRATO DE PRESTAÇÃO DE SERVIÇOS COMPLEXOS

        Entre as partes qualificadas, conforme previsto na legislação vigente,
        firmam o presente instrumento particular de contrato de prestação de
        serviços profissionais, mediante as cláusulas e condições seguintes:

        CLÁUSULA PRIMEIRA - DO OBJETO
        O presente contrato tem como objeto a prestação de serviços técnicos
        especializados, incluindo consultoria, desenvolvimento e manutenção.

        CLÁUSULA SEGUNDA - DAS RESPONSABILIDADES
        Conforme cláusula específica sobre responsabilidades, compete à
        CONTRATADA executar todos os serviços com qualidade e eficiência.

        CLÁUSULA TERCEIRA - DO PRAZO E VIGÊNCIA
        O prazo inicial será de 24 meses, renovável automaticamente.

        CLÁUSULA QUARTA - DOS VALORES E PAGAMENTOS
        Os valores serão pagos mensalmente mediante apresentação de nota fiscal.

        """
        haystack = base_text * 100  # ~50KB

        results = {}

        # Benchmark Difflib
        difflib_matcher = DifflibMatcher()
        time_difflib, sim_difflib = benchmark_matcher(
            difflib_matcher, needle, haystack, iterations=3
        )
        results["difflib"] = {"time": time_difflib, "similarity": sim_difflib}

        # Benchmark RapidFuzz (se disponível)
        if RAPIDFUZZ_AVAILABLE:
            rapidfuzz_matcher = RapidFuzzMatcher()
            time_rapidfuzz, sim_rapidfuzz = benchmark_matcher(
                rapidfuzz_matcher, needle, haystack, iterations=3
            )
            results["rapidfuzz"] = {
                "time": time_rapidfuzz,
                "similarity": sim_rapidfuzz,
            }

        # Imprime resultados
        print("\n" + "=" * 60)
        print("BENCHMARK: Documento Médio (~50KB)")
        print("=" * 60)

        for name, data in results.items():
            print(
                f"{name:12} | Tempo: {data['time'] * 1000:7.2f}ms | "
                f"Similaridade: {data['similarity'] * 100:5.1f}%"
            )

        if "rapidfuzz" in results and "difflib" in results:
            speedup = results["difflib"]["time"] / results["rapidfuzz"]["time"]
            print(f"\n⚡ Speedup RapidFuzz: {speedup:.1f}x mais rápido")

        print("=" * 60)

        # Valida resultados
        assert all(data["similarity"] >= 0.85 for data in results.values())

    def test_benchmark_large_document(self):
        """Benchmark com documento grande (~500KB) - similar à produção."""
        needle = "item específico da cláusula vigésima segunda"

        # Cria documento grande (~500KB) similar ao que temos em produção
        base_text = """
        CONTRATO CORPORATIVO DE PRESTAÇÃO DE SERVIÇOS PROFISSIONAIS

        Pelo presente instrumento particular de contrato de prestação de serviços,
        de um lado a empresa CONTRATANTE, e de outro lado a empresa CONTRATADA,
        firmam o presente contrato mediante as seguintes cláusulas e condições:

        CLÁUSULA PRIMEIRA - DO OBJETO E ESCOPO
        O presente contrato tem como objeto a prestação de serviços técnicos
        especializados em tecnologia da informação, incluindo mas não se
        limitando a desenvolvimento de software, consultoria técnica,
        manutenção de sistemas, suporte técnico e treinamento de usuários.

        1.1 - Os serviços serão prestados em conformidade com as melhores
        práticas do mercado e legislação aplicável.

        1.2 - O escopo poderá ser ajustado mediante termo aditivo.

        CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA
        Compete à CONTRATADA a execução dos serviços com qualidade, observando
        os prazos acordados e mantendo sigilo profissional.

        2.1 - Alocar profissionais qualificados para execução dos serviços.
        2.2 - Fornecer relatórios periódicos de acompanhamento.
        2.3 - Manter backup de todas as informações críticas.

        CLÁUSULA VIGÉSIMA SEGUNDA - DAS DISPOSIÇÕES GERAIS
        As partes acordam que o item específico da cláusula vigésima segunda
        estabelece condições especiais para casos não previstos inicialmente.

        22.1 - Qualquer alteração deve ser formalizada por escrito.
        22.2 - O contrato prevalece sobre entendimentos verbais.

        """
        haystack = base_text * 200  # ~500KB

        results = {}

        # Benchmark Difflib (com menos iterações devido ao tamanho)
        difflib_matcher = DifflibMatcher()
        time_difflib, sim_difflib = benchmark_matcher(
            difflib_matcher, needle, haystack, iterations=1
        )
        results["difflib"] = {"time": time_difflib, "similarity": sim_difflib}

        # Benchmark RapidFuzz (se disponível)
        if RAPIDFUZZ_AVAILABLE:
            rapidfuzz_matcher = RapidFuzzMatcher()
            time_rapidfuzz, sim_rapidfuzz = benchmark_matcher(
                rapidfuzz_matcher, needle, haystack, iterations=1
            )
            results["rapidfuzz"] = {
                "time": time_rapidfuzz,
                "similarity": sim_rapidfuzz,
            }

        # Imprime resultados
        print("\n" + "=" * 60)
        print("BENCHMARK: Documento Grande (~500KB) - PRODUÇÃO")
        print("=" * 60)

        for name, data in results.items():
            tempo_s = data["time"]
            print(
                f"{name:12} | Tempo: {tempo_s:7.2f}s | "
                f"Similaridade: {data['similarity'] * 100:5.1f}%"
            )

        if "rapidfuzz" in results and "difflib" in results:
            speedup = results["difflib"]["time"] / results["rapidfuzz"]["time"]
            print(f"\n⚡ Speedup RapidFuzz: {speedup:.1f}x mais rápido")

            # Calcula tempo estimado para 440 tags
            time_440_difflib = results["difflib"]["time"] * 440
            time_440_rapidfuzz = results["rapidfuzz"]["time"] * 440

            print("\n📊 Estimativa para 440 tags (produção):")
            print(
                f"   Difflib:    {time_440_difflib / 60:6.1f} minutos "
                f"({time_440_difflib / 3600:4.1f} horas)"
            )
            print(
                f"   RapidFuzz:  {time_440_rapidfuzz / 60:6.1f} minutos "
                f"({time_440_rapidfuzz / 3600:4.1f} horas)"
            )
            print(
                f"   Economia:   {(time_440_difflib - time_440_rapidfuzz) / 60:6.1f} "
                f"minutos"
            )

        print("=" * 60)

        # Valida resultados
        assert all(data["similarity"] >= 0.85 for data in results.values())


if __name__ == "__main__":
    # Executa benchmarks diretamente
    print("\n🔥 EXECUTANDO BENCHMARKS DE PERFORMANCE 🔥\n")

    test = TestPerformanceBenchmark()

    print("\n1️⃣ Documento Pequeno...")
    test.test_benchmark_small_document()

    print("\n2️⃣ Documento Médio...")
    test.test_benchmark_medium_document()

    print("\n3️⃣ Documento Grande (Produção)...")
    test.test_benchmark_large_document()

    print("\n✅ Benchmarks concluídos!\n")
