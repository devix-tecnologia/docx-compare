#!/usr/bin/env python3
"""
Script CLI para comparação de algoritmos de vinculação de cláusulas.

Uso:
    # Comparar todos os algoritmos em todas as fixtures
    python comparar_algoritmos.py

    # Comparar algoritmos específicos
    python comparar_algoritmos.py --algoritmos naive_sequencial offset_acumulado

    # Testar apenas fixtures simples
    python comparar_algoritmos.py --nivel simples

    # Testar fixtures específicas
    python comparar_algoritmos.py --fixtures caso_01 caso_04

    # Gerar relatório HTML
    python comparar_algoritmos.py --report html --output relatorio.html

    # Modo verbose
    python comparar_algoritmos.py -v
"""

import argparse
import sys
from pathlib import Path

# Adicionar tests/ ao path se necessário
tests_dir = Path(__file__).parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

# Importar algoritmos e framework
from algoritmos.fuzzy.algoritmo import AlgoritmoFuzzyAvancado
from algoritmos.hibrido.algoritmo import AlgoritmoHibrido
from algoritmos.producao.algoritmo import AlgoritmoProducao
from algoritmos.regex.algoritmo import AlgoritmoRegex
from framework_comparacao import ComparadorAlgoritmos
from test_comparacao_algoritmos import (
    AlgoritmoComOffsetAcumulado,
    AlgoritmoNaiveSequencial,
)

# Registro de algoritmos disponíveis
ALGORITMOS_DISPONIVEIS = {
    "naive_sequencial": AlgoritmoNaiveSequencial,
    "offset_acumulado": AlgoritmoComOffsetAcumulado,
    "producao": AlgoritmoProducao,  # BASELINE
    "fuzzy": AlgoritmoFuzzyAvancado,  # Fuzzy matching avançado
    "regex": AlgoritmoRegex,  # Padrões estruturados
    "hibrido": AlgoritmoHibrido,  # Cascata de estratégias (melhor)
    # Adicione novos algoritmos aqui
}


def main():
    parser = argparse.ArgumentParser(
        description="Compara algoritmos de vinculação de cláusulas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                                    # Comparar tudo
  %(prog)s --nivel simples                   # Apenas casos simples
  %(prog)s --algoritmos naive offset         # Algoritmos específicos
  %(prog)s --report markdown -o report.md    # Salvar relatório
        """,
    )

    parser.add_argument(
        "--algoritmos",
        "-a",
        nargs="+",
        choices=list(ALGORITMOS_DISPONIVEIS.keys()),
        help="Algoritmos a comparar (padrão: todos)",
    )

    parser.add_argument(
        "--fixtures",
        "-f",
        nargs="+",
        help="IDs de fixtures específicas (ex: caso_01 caso_04)",
    )

    parser.add_argument(
        "--nivel",
        "-n",
        choices=["simples", "medio", "complexo"],
        help="Filtrar por nível de complexidade",
    )

    parser.add_argument(
        "--report",
        "-r",
        choices=["console", "markdown", "html"],
        default="console",
        help="Formato do relatório (padrão: console)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Arquivo de saída para relatório (padrão: stdout)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Modo verbose com detalhes",
    )

    args = parser.parse_args()

    # Instanciar algoritmos
    if args.algoritmos:
        algoritmos = [ALGORITMOS_DISPONIVEIS[nome]() for nome in args.algoritmos]
    else:
        algoritmos = [cls() for cls in ALGORITMOS_DISPONIVEIS.values()]

    if not algoritmos:
        print("❌ Nenhum algoritmo selecionado")
        return 1

    # Carregar fixtures
    comparador = ComparadorAlgoritmos()
    fixtures = comparador.carregar_fixtures(nivel=args.nivel, ids=args.fixtures)

    if not fixtures:
        print("❌ Nenhuma fixture encontrada")
        return 1

    # Executar comparação
    print(f"🧪 Comparando {len(algoritmos)} algoritmos:")
    for alg in algoritmos:
        print(f"   - {alg.nome}: {alg.descricao}")
    print(f"\n📋 Em {len(fixtures)} fixtures:")
    for fixture in fixtures:
        print(f"   - {fixture.id} ({fixture.nivel_complexidade}): {fixture.descricao}")
    print()

    resultados = comparador.comparar(algoritmos, fixtures)

    # Gerar relatório
    if args.report == "console":
        comparador.gerar_relatorio(resultados, formato="console")

    elif args.report == "markdown":
        md = comparador.gerar_relatorio(resultados, formato="markdown")
        if args.output:
            args.output.write_text(md)
            print(f"\n💾 Relatório salvo em: {args.output}")
        else:
            print(md)

    elif args.report == "html":
        html = comparador.gerar_relatorio(resultados, formato="html")
        if args.output:
            args.output.write_text(html)
            print(f"\n💾 Relatório HTML salvo em: {args.output}")
        else:
            print(html)

    # Resumo final
    print("\n" + "=" * 80)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 80)

    # Determinar vencedor
    scores_gerais = {}
    for alg_nome, fixtures_metricas in resultados.items():
        scores = [m.score_geral for m in fixtures_metricas.values()]
        scores_gerais[alg_nome] = sum(scores) / len(scores) if scores else 0

    vencedor = max(scores_gerais.items(), key=lambda x: x[1])
    print(f"\n🏆 MELHOR ALGORITMO: {vencedor[0]} (score: {vencedor[1]:.1f})")

    # Sugestões
    if args.verbose:
        print("\n💡 SUGESTÕES:")
        for alg_nome, score in sorted(
            scores_gerais.items(), key=lambda x: x[1], reverse=True
        ):
            if score < 80:
                print(f"   - {alg_nome}: Score {score:.1f} < 80 - considere melhorias")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
