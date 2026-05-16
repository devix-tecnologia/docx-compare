"""
Testes específicos para o algoritmo de produção (baseline).

Valida que o adapter funciona corretamente e documenta o desempenho atual.
"""

import sys
from pathlib import Path

# Setup path
tests_dir = Path(__file__).parent.parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

import pytest
from algoritmos.producao.algoritmo import AlgoritmoProducao
from framework_comparacao import ComparadorAlgoritmos


@pytest.fixture
def algoritmo():
    """Instância do algoritmo de produção"""
    return AlgoritmoProducao()


@pytest.fixture
def comparador():
    """Instância do comparador"""
    return ComparadorAlgoritmos()


def test_algoritmo_interface(algoritmo):
    """Valida que o algoritmo implementa a interface corretamente"""
    assert algoritmo.nome == "producao"
    assert "baseline" in algoritmo.descricao.lower()
    assert hasattr(algoritmo, "calcular_posicoes")
    assert hasattr(algoritmo, "vincular_clausulas")


def test_calcular_posicoes_insercao(algoritmo):
    """Testa cálculo de posições para INSERCAO"""
    texto = "Início do documento. Texto inserido aqui. Final do documento."
    modificacoes = [
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "Texto inserido aqui"},
        }
    ]

    resultado = algoritmo.calcular_posicoes(modificacoes, texto)

    assert len(resultado) == 1
    assert resultado[0]["posicao_inicio"] == 21  # Posição de "Texto inserido"
    assert resultado[0]["posicao_fim"] == 40  # 21 + len("Texto inserido aqui") = 40


def test_calcular_posicoes_alteracao(algoritmo):
    """Testa cálculo de posições para ALTERACAO"""
    texto = "Valor antigo foi substituído por Valor novo no documento."
    modificacoes = [
        {
            "tipo": "ALTERACAO",
            "conteudo": {"original": "Valor antigo", "novo": "Valor novo"},
        }
    ]

    resultado = algoritmo.calcular_posicoes(modificacoes, texto)

    assert len(resultado) == 1
    # Busca pelo novo valor
    assert resultado[0]["posicao_inicio"] == 33
    assert resultado[0]["posicao_fim"] == 43


def test_vincular_com_fuzzy_matching(algoritmo):
    """Testa vinculação usando fuzzy matching"""
    texto = "CLÁUSULA 1 - OBJETO\nO objeto do contrato é prestação de serviços."
    tags = [
        {
            "id": "tag_1",
            "nome": "Cláusula 1",
            "posicao_inicio": 0,
            "posicao_fim": 65,
            "texto": "CLÁUSULA 1 - OBJETO\nO objeto do contrato é prestação de serviços.",
        }
    ]
    modificacoes = [
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "prestação de serviços"},
            "posicao_inicio": 43,
            "posicao_fim": 64,
        }
    ]

    resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

    assert len(resultado) == 1
    assert resultado[0]["tag_vinculada"] is not None
    assert resultado[0]["tag_vinculada"]["id"] == "tag_1"


def test_vincular_sem_tag_correspondente(algoritmo):
    """Testa que modificações fora de tags retornam None"""
    texto = "Cabeçalho\n\nCLÁUSULA 1\nConteúdo\n\nRodapé com modificação"
    tags = [
        {
            "id": "tag_1",
            "nome": "Cláusula 1",
            "posicao_inicio": 10,
            "posicao_fim": 30,
            "texto": "CLÁUSULA 1\nConteúdo",
        }
    ]
    modificacoes = [
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "modificação"},
            "posicao_inicio": 45,  # No rodapé, fora da tag
            "posicao_fim": 56,
        }
    ]

    resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

    assert len(resultado) == 1
    assert resultado[0]["tag_vinculada"] is None


def test_vincular_template_vs_valores_reais(algoritmo):
    """
    TDD: Testa vinculação de template com placeholders vs. valores reais.
    
    Problema identificado no caso real c2b1dfa0:
    - Template: "LOCADOR: ________ , ________ , portador..."
    - Valor:    "LOCADOR: Joris Veloso, portador..."
    - ratio():       ~54% (baseline atual)
    - token_set_ratio(): ~93% (deveria usar)
    
    Este teste DEVE PASSAR com threshold ajustado ou métrica melhor.
    """
    # Template com placeholders
    tag_texto = (
        "LOCADOR: ________ , ________ , ________ , ________ , "
        "portador da cédula de identidade R.G. nº ________ e CPF nº ________ , "
        "residente e domiciliado à ________ , ________ ."
    )
    
    # Valor real preenchido
    mod_texto = (
        "LOCADOR: Joris Veloso, portador da cédula de identidade "
        "R.G. nº 123654789 e CPF nº 58755666 , residente e domiciliado à "
        "Rua Cyro Lopes, 234."
    )
    
    tags = [
        {
            "id": "tag_locador",
            "titulo": "locador",
            "texto": tag_texto,
            "posicao_inicio": 30,
            "posicao_fim": 244,
        }
    ]
    
    # Modificação sem posição calculada (baseline precisa calcular)
    modificacoes = [
        {
            "id": "mod_1",
            "tipo": "INSERCAO",
            "conteudo": {"novo": mod_texto},
        }
    ]
    
    # Texto completo é o template (como no caso real)
    texto_completo = f"CONTRATO DE LOCAÇÃO\n{tag_texto}\nCláusulas seguem..."
    
    resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto_completo)
    
    # DEVE vincular a tag correta
    assert len(resultado) == 1
    assert resultado[0]["tag_vinculada"] is not None, (
        "Baseline DEVE vincular template com placeholders vs. valores reais! "
        "Precisa usar token_set_ratio ou métrica similar."
    )
    assert resultado[0]["tag_vinculada"]["id"] == "tag_locador"


def test_avaliacao_caso_simples(algoritmo, comparador):
    """
    Testa avaliação em fixture simples.

    Documenta desempenho atual (baseline) para comparação futura.
    """
    fixtures = comparador.carregar_fixtures(ids=["caso_01_insercao_simples"])

    if not fixtures:
        pytest.skip("Fixture caso_01 não encontrada")

    fixture = fixtures[0]
    metricas = comparador.avaliar(algoritmo, fixture)

    # Documentar métricas (não falhar o teste)
    print(f"\n📊 Baseline - {fixture.id}:")
    print(f"   {metricas}")

    # Validações mínimas (algoritmo funciona, não necessariamente bem)
    assert metricas.tempo_execucao_ms >= 0
    assert 0 <= metricas.taxa_vinculacao <= 100
    assert 0 <= metricas.score_geral <= 100


def test_comparacao_todos_casos_simples(algoritmo, comparador):
    """
    Avalia algoritmo em todos os casos simples.

    Estabelece baseline de desempenho.
    """
    fixtures = comparador.carregar_fixtures(nivel="simples")

    if not fixtures:
        pytest.skip("Nenhuma fixture simples encontrada")

    print(f"\n📊 Baseline - Avaliação em {len(fixtures)} fixtures simples:")

    scores = []
    for fixture in fixtures:
        metricas = comparador.avaliar(algoritmo, fixture)
        scores.append(metricas.score_geral)
        print(f"   {fixture.id}: Score {metricas.score_geral:.1f}")

    score_medio = sum(scores) / len(scores) if scores else 0
    print(f"\n   Score Médio: {score_medio:.1f}")

    # Documentar, não falhar
    assert score_medio >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
