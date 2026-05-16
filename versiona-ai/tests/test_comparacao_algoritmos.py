"""
Testes automatizados para comparação de algoritmos de vinculação.

Uso:
    # Rodar todos os testes
    uv run pytest tests/test_comparacao_algoritmos.py -v

    # Ver relatório detalhado
    uv run pytest tests/test_comparacao_algoritmos.py -v -s
"""

import sys
from pathlib import Path

# Adicionar tests/ ao path se necessário
if __name__ == "__main__" or "pytest" in sys.modules:
    tests_dir = Path(__file__).parent
    if str(tests_dir) not in sys.path:
        sys.path.insert(0, str(tests_dir))

import pytest
from framework_comparacao import (
    AlgoritmoVinculacao,
    ComparadorAlgoritmos,
)


class AlgoritmoNaiveSequencial(AlgoritmoVinculacao):
    """
    Algoritmo naive: busca texto sequencialmente, sem ajuste de offset.
    Baseline para comparação.
    """

    @property
    def nome(self) -> str:
        return "naive_sequencial"

    @property
    def descricao(self) -> str:
        return "Busca simples de texto sem ajuste de offset entre modificações"

    def calcular_posicoes(self, modificacoes: list[dict], texto: str) -> list[dict]:
        """Busca cada modificação no texto, sem ajustes"""
        for mod in modificacoes:
            tipo = mod["tipo"]
            conteudo = mod["conteudo"]

            if tipo in ["INSERCAO", "ALTERACAO"]:
                texto_busca = conteudo.get("novo", "")
            else:  # REMOCAO
                texto_busca = conteudo.get("original", "")

            if texto_busca:
                pos = texto.find(texto_busca)
                if pos >= 0:
                    mod["posicao_inicio"] = pos
                    mod["posicao_fim"] = pos + len(texto_busca)
                else:
                    mod["posicao_inicio"] = None
                    mod["posicao_fim"] = None

        return modificacoes

    def vincular_clausulas(
        self, modificacoes: list[dict], tags: list[dict], texto: str
    ) -> list[dict]:
        """Vincula por sobreposição simples"""
        for mod in modificacoes:
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")

            if pos_inicio is None or pos_fim is None:
                mod["tag_vinculada"] = None
                continue

            # Buscar tag com maior sobreposição
            melhor_tag = None
            melhor_overlap = 0

            for tag in tags:
                tag_inicio = tag["posicao_inicio"]
                tag_fim = tag["posicao_fim"]

                # Calcular sobreposição
                inicio_overlap = max(pos_inicio, tag_inicio)
                fim_overlap = min(pos_fim, tag_fim)
                overlap = max(0, fim_overlap - inicio_overlap)

                if overlap > melhor_overlap:
                    melhor_overlap = overlap
                    melhor_tag = tag

            mod["tag_vinculada"] = melhor_tag

        return modificacoes


class AlgoritmoComOffsetAcumulado(AlgoritmoVinculacao):
    """
    Algoritmo melhorado: aplica modificações sequencialmente,
    ajustando offset para próximas buscas.
    """

    @property
    def nome(self) -> str:
        return "offset_acumulado"

    @property
    def descricao(self) -> str:
        return "Busca com ajuste de offset acumulado entre modificações"

    def calcular_posicoes(self, modificacoes: list[dict], texto: str) -> list[dict]:
        """Aplica modificações sequencialmente, ajustando offset"""
        # Ordenar por ordem de aplicação (se disponível)
        modificacoes_ordenadas = sorted(
            modificacoes, key=lambda m: m.get("ordem_aplicacao", 0)
        )

        offset_acumulado = 0
        texto_modificado = texto

        for mod in modificacoes_ordenadas:
            tipo = mod["tipo"]
            conteudo = mod["conteudo"]

            if tipo == "INSERCAO":
                texto_busca = conteudo.get("novo", "")
                if texto_busca:
                    # Buscar no texto já modificado
                    pos = texto_modificado.find(texto_busca)
                    if pos >= 0:
                        mod["posicao_inicio"] = pos
                        mod["posicao_fim"] = pos + len(texto_busca)
                        # Aplicar inserção ao texto
                        texto_modificado = (
                            texto_modificado[:pos]
                            + texto_busca
                            + texto_modificado[pos:]
                        )
                        offset_acumulado += len(texto_busca)
                    else:
                        mod["posicao_inicio"] = None
                        mod["posicao_fim"] = None

            elif tipo == "ALTERACAO":
                texto_original = conteudo.get("original", "")
                texto_novo = conteudo.get("novo", "")

                if texto_original:
                    pos = texto_modificado.find(texto_original)
                    if pos >= 0:
                        mod["posicao_inicio"] = pos
                        mod["posicao_fim"] = pos + len(texto_novo)
                        # Aplicar alteração ao texto
                        texto_modificado = (
                            texto_modificado[:pos]
                            + texto_novo
                            + texto_modificado[pos + len(texto_original) :]
                        )
                        offset_acumulado += len(texto_novo) - len(texto_original)
                    else:
                        mod["posicao_inicio"] = None
                        mod["posicao_fim"] = None

            elif tipo == "REMOCAO":
                texto_removido = conteudo.get("original", "")
                if texto_removido:
                    pos = texto_modificado.find(texto_removido)
                    if pos >= 0:
                        mod["posicao_inicio"] = pos
                        mod["posicao_fim"] = pos
                        # Aplicar remoção ao texto
                        texto_modificado = (
                            texto_modificado[:pos]
                            + texto_modificado[pos + len(texto_removido) :]
                        )
                        offset_acumulado -= len(texto_removido)
                    else:
                        mod["posicao_inicio"] = None
                        mod["posicao_fim"] = None

        return modificacoes_ordenadas

    def vincular_clausulas(
        self, modificacoes: list[dict], tags: list[dict], texto: str
    ) -> list[dict]:
        """Vincula por sobreposição com threshold"""
        for mod in modificacoes:
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")

            if pos_inicio is None or pos_fim is None:
                mod["tag_vinculada"] = None
                continue

            # Buscar tag com maior sobreposição
            melhor_tag = None
            melhor_score = 0

            for tag in tags:
                tag_inicio = tag["posicao_inicio"]
                tag_fim = tag["posicao_fim"]

                # Calcular sobreposição
                inicio_overlap = max(pos_inicio, tag_inicio)
                fim_overlap = min(pos_fim, tag_fim)
                overlap = max(0, fim_overlap - inicio_overlap)

                if overlap > 0:
                    # Score: percentual da modificação coberta pela tag
                    tamanho_mod = pos_fim - pos_inicio
                    score = overlap / tamanho_mod if tamanho_mod > 0 else 0

                    if score > melhor_score:
                        melhor_score = score
                        melhor_tag = tag

            # Threshold: vincular apenas se >50% de sobreposição
            if melhor_score >= 0.5:
                mod["tag_vinculada"] = melhor_tag
            else:
                mod["tag_vinculada"] = None

        return modificacoes


@pytest.fixture
def comparador():
    """Fixture pytest para ComparadorAlgoritmos"""
    return ComparadorAlgoritmos()


@pytest.fixture
def algoritmos():
    """Fixture pytest com lista de algoritmos para testar"""
    return [
        AlgoritmoNaiveSequencial(),
        AlgoritmoComOffsetAcumulado(),
    ]


def test_caso_simples_insercao(comparador, algoritmos):
    """Testa caso simples de inserção única"""
    fixtures = comparador.carregar_fixtures(ids=["caso_01_insercao_simples"])
    assert len(fixtures) == 1

    resultados = comparador.comparar(algoritmos, fixtures)

    # Ambos algoritmos devem conseguir >80% em caso simples
    for alg_nome, metricas_por_fixture in resultados.items():
        metricas = metricas_por_fixture["caso_01_insercao_simples"]
        assert metricas.taxa_vinculacao >= 80.0, (
            f"{alg_nome} falhou em caso simples: {metricas}"
        )
        assert metricas.f1_score >= 80.0, (
            f"{alg_nome} F1 baixo em caso simples: {metricas}"
        )


def test_caso_medio_multiplas_modificacoes(comparador, algoritmos):
    """Testa caso com múltiplas modificações interdependentes"""
    fixtures = comparador.carregar_fixtures(
        ids=["caso_04_multiplas_modificacoes_interdependentes"]
    )
    assert len(fixtures) == 1

    resultados = comparador.comparar(algoritmos, fixtures)

    # Algoritmo com offset deve ter score significativamente melhor
    score_naive = resultados["naive_sequencial"][
        "caso_04_multiplas_modificacoes_interdependentes"
    ].score_geral
    score_offset = resultados["offset_acumulado"][
        "caso_04_multiplas_modificacoes_interdependentes"
    ].score_geral

    print(f"\n📊 Score naive: {score_naive:.1f}")
    print(f"📊 Score offset: {score_offset:.1f}")

    # Offset deve ser pelo menos 20% melhor
    assert score_offset > score_naive * 1.2, (
        f"Algoritmo com offset ({score_offset:.1f}) não foi significativamente "
        f"melhor que naive ({score_naive:.1f})"
    )


def test_comparacao_todos_casos(comparador, algoritmos):
    """Testa todos os casos disponíveis e gera relatório"""
    fixtures = comparador.carregar_fixtures()

    if not fixtures:
        pytest.skip("Nenhuma fixture encontrada")

    print(f"\n🧪 Testando {len(algoritmos)} algoritmos em {len(fixtures)} fixtures\n")

    resultados = comparador.comparar(algoritmos, fixtures)

    # Gerar relatório
    print("\n" + "=" * 80)
    comparador.gerar_relatorio(resultados, formato="console")

    # Salvar relatório markdown
    md = comparador.gerar_relatorio(resultados, formato="markdown")
    relatorio_path = Path(__file__).parent / "relatorio_comparacao.md"
    relatorio_path.write_text(md)
    print(f"\n💾 Relatório salvo em: {relatorio_path}")

    # Validação: pelo menos um algoritmo deve ter score >70 na média
    scores_medios = []
    for alg_nome, fixtures_metricas in resultados.items():
        scores = [m.score_geral for m in fixtures_metricas.values()]
        score_medio = sum(scores) / len(scores) if scores else 0
        scores_medios.append(score_medio)

    assert max(scores_medios) >= 70.0, (
        f"Nenhum algoritmo atingiu score médio ≥70. Melhor: {max(scores_medios):.1f}"
    )


def test_validacao_fixtures():
    """Valida que todas as fixtures têm estrutura correta"""
    comparador = ComparadorAlgoritmos()
    fixtures = comparador.carregar_fixtures()

    for fixture in fixtures:
        # Validar campos obrigatórios
        assert fixture.id, f"Fixture {fixture.path} sem ID"
        assert fixture.descricao, f"Fixture {fixture.id} sem descrição"
        assert fixture.nivel_complexidade in [
            "simples",
            "medio",
            "complexo",
        ], f"Fixture {fixture.id} com nível inválido"

        # Validar documento
        assert fixture.texto_completo, f"Fixture {fixture.id} sem texto_completo"
        assert fixture.tags, f"Fixture {fixture.id} sem tags"

        # Validar tags
        for tag in fixture.tags:
            assert "id" in tag, f"Fixture {fixture.id}: tag sem ID"
            assert "posicao_inicio" in tag, (
                f"Fixture {fixture.id}: tag {tag.get('id')} sem posicao_inicio"
            )
            assert "posicao_fim" in tag, (
                f"Fixture {fixture.id}: tag {tag.get('id')} sem posicao_fim"
            )

        # Validar modificações
        assert fixture.modificacoes, f"Fixture {fixture.id} sem modificações"
        for mod in fixture.modificacoes:
            assert "tipo" in mod, f"Fixture {fixture.id}: modificação sem tipo"
            assert "conteudo" in mod, f"Fixture {fixture.id}: modificação sem conteúdo"

        # Vinculações esperadas (pode ser vazia para casos negativos)
        # Casos negativos devem ter taxa_vinculacao_minima == 0
        if not fixture.vinculacoes_esperadas:
            assert fixture.metricas_objetivo["taxa_vinculacao_minima"] == 0, (
                f"Fixture {fixture.id} sem vinculacoes mas taxa_minima != 0"
            )


if __name__ == "__main__":
    # Permite rodar diretamente: python test_comparacao_algoritmos.py
    pytest.main([__file__, "-v", "-s"])
