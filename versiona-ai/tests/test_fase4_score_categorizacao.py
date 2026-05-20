#!/usr/bin/env python3

"""
TESTES DA FASE 4: SCORE E CATEGORIZAÇÃO

Este arquivo testa o sistema de vinculação por sobreposição com scores
e a categorização em três filas: vinculadas, revisão manual, não vinculadas.

Testa:
1. Alta confiança (score ≥ 0.8) → vinculação automática
2. Média confiança (0.5 ≤ score < 0.8) → revisão manual
3. Baixa confiança (score < 0.5) → não vinculada
4. Múltiplas modificações na mesma tag
"""

from directus_server import DirectusAPI, TagMapeada


def test_vinculacao_alta_confianca():
    """
    Teste 1: Vinculação com alta confiança (score ≥ 0.8)

    Cenário: Modificação totalmente dentro da tag, inferência com score alto.
    Esperado: Vinculação automática, score ≥ 0.8
    """
    print("\n🧪 Teste 1: Vinculação com alta confiança")

    # Tags mapeadas (com scores de inferência altos)
    tags = [
        TagMapeada(
            tag_id="tag-001",
            tag_nome="TAG-1",
            posicao_inicio_original=0,
            posicao_fim_original=100,  # Tag cobre [0-100]
            clausulas=[{"id": "clausula-001"}],
            score_inferencia=0.9,  # Inferência com contexto completo
            metodo="contexto_completo",
        ),
        TagMapeada(
            tag_id="tag-002",
            tag_nome="TAG-2",
            posicao_inicio_original=150,
            posicao_fim_original=200,  # Tag cobre [150-200]
            clausulas=[{"id": "clausula-002"}],
            score_inferencia=0.9,
            metodo="offset",
        ),
    ]

    # Modificações totalmente dentro das tags
    modificacoes = [
        {
            "tipo": "inserção",
            "posicao_inicio": 20,
            "posicao_fim": 30,  # Modificação [20-30] dentro de TAG-1 [0-100]
            "conteudo": "novo texto",
        },
        {
            "tipo": "remoção",
            "posicao_inicio": 160,
            "posicao_fim": 170,  # Modificação [160-170] dentro de TAG-2 [150-200]
            "conteudo": "texto removido",
        },
    ]

    # Executar vinculação
    api = DirectusAPI()
    resultado = api._vincular_por_sobreposicao_com_score(
        tags_mapeadas=tags, modificacoes=modificacoes
    )

    # Validar
    assert len(resultado.vinculadas) == 2, (
        f"Esperado 2 vinculadas, obteve {len(resultado.vinculadas)}"
    )
    assert len(resultado.revisao_manual) == 0
    assert len(resultado.nao_vinculadas) == 0

    # Validar scores
    vinc1 = resultado.vinculadas[0]
    assert vinc1["score"] >= 0.8, f"Score deveria ser ≥ 0.8, obteve {vinc1['score']}"
    assert vinc1["tag"].tag_nome == "TAG-1"

    vinc2 = resultado.vinculadas[1]
    assert vinc2["score"] >= 0.8
    assert vinc2["tag"].tag_nome == "TAG-2"

    # Validar taxas
    assert resultado.taxa_sucesso() == 100.0  # 2/2 = 100%
    assert resultado.taxa_cobertura() == 100.0  # (2+0)/2 = 100%

    print("   ✅ 2 vinculações com alta confiança")
    print(f"   Score 1: {vinc1['score']:.2f}, Score 2: {vinc2['score']:.2f}")
    print(f"   Taxa de sucesso: {resultado.taxa_sucesso():.1f}%")
    print("   ✅ Teste de alta confiança passou!")


def test_vinculacao_media_confianca():
    """
    Teste 2: Vinculação com média confiança (0.5 ≤ score < 0.8)

    Cenário: Sobreposição parcial ou inferência com score médio.
    Esperado: Categorizado em revisão manual
    """
    print("\n🧪 Teste 2: Vinculação com média confiança")

    # Tag mapeada com score médio de inferência
    tags = [
        TagMapeada(
            tag_id="tag-001",
            tag_nome="TAG-1",
            posicao_inicio_original=0,
            posicao_fim_original=100,
            clausulas=[{"id": "clausula-001"}],
            score_inferencia=0.5,  # Inferência apenas por conteúdo
            metodo="conteudo_apenas",
        ),
    ]

    # Modificação com sobreposição parcial
    modificacoes = [
        {
            "tipo": "inserção",
            "posicao_inicio": 80,
            "posicao_fim": 120,  # Modificação [80-120], tag [0-100] → overlap de 20
            "conteudo": "texto parcial",
        },
    ]

    # Executar vinculação
    api = DirectusAPI()
    resultado = api._vincular_por_sobreposicao_com_score(
        tags_mapeadas=tags, modificacoes=modificacoes
    )

    # Validar
    assert len(resultado.vinculadas) == 0
    assert len(resultado.revisao_manual) == 1, (
        f"Esperado 1 em revisão manual, obteve {len(resultado.revisao_manual)}"
    )
    assert len(resultado.nao_vinculadas) == 0

    # Validar score
    rev1 = resultado.revisao_manual[0]
    assert 0.5 <= rev1["score"] < 0.8, (
        f"Score deveria estar em [0.5, 0.8), obteve {rev1['score']}"
    )
    assert rev1["tag"].tag_nome == "TAG-1"
    assert rev1["motivo"] == "score_medio"

    # Validar taxas
    assert resultado.taxa_sucesso() == 0.0  # 0/1 = 0%
    assert resultado.taxa_cobertura() == 100.0  # (0+1)/1 = 100%

    print("   ⚠️  1 modificação em revisão manual")
    print(f"   Score: {rev1['score']:.2f}, Motivo: {rev1['motivo']}")
    print("   ✅ Teste de média confiança passou!")


def test_vinculacao_baixa_confianca():
    """
    Teste 3: Vinculação com baixa confiança (score < 0.5)

    Cenário: Sobreposição mínima ou sem sobreposição.
    Esperado: Não vinculada
    """
    print("\n🧪 Teste 3: Vinculação com baixa confiança")

    # Tag mapeada
    tags = [
        TagMapeada(
            tag_id="tag-001",
            tag_nome="TAG-1",
            posicao_inicio_original=0,
            posicao_fim_original=50,
            clausulas=[{"id": "clausula-001"}],
            score_inferencia=0.9,
            metodo="offset",
        ),
    ]

    # Modificação fora da tag
    modificacoes = [
        {
            "tipo": "inserção",
            "posicao_inicio": 100,
            "posicao_fim": 120,  # Modificação [100-120], tag [0-50] → sem overlap
            "conteudo": "texto longe",
        },
    ]

    # Executar vinculação
    api = DirectusAPI()
    resultado = api._vincular_por_sobreposicao_com_score(
        tags_mapeadas=tags, modificacoes=modificacoes
    )

    # Validar
    assert len(resultado.vinculadas) == 0
    assert len(resultado.revisao_manual) == 0
    assert len(resultado.nao_vinculadas) == 1, (
        f"Esperado 1 não vinculada, obteve {len(resultado.nao_vinculadas)}"
    )

    # Validar motivo
    nao_vinc1 = resultado.nao_vinculadas[0]
    assert nao_vinc1["motivo"] == "sem_sobreposicao"
    assert nao_vinc1["score"] == 0.0

    # Validar taxas
    assert resultado.taxa_sucesso() == 0.0  # 0/1 = 0%
    assert resultado.taxa_cobertura() == 0.0  # (0+0)/1 = 0%

    print("   ❌ 1 modificação não vinculada")
    print(f"   Motivo: {nao_vinc1['motivo']}")
    print("   ✅ Teste de baixa confiança passou!")


def test_multiplas_modificacoes_mesma_tag():
    """
    Teste 4: Múltiplas modificações na mesma tag

    Cenário: Várias modificações dentro da mesma tag.
    Esperado: Todas vinculadas à mesma tag
    """
    print("\n🧪 Teste 4: Múltiplas modificações na mesma tag")

    # Uma tag grande
    tags = [
        TagMapeada(
            tag_id="tag-001",
            tag_nome="TAG-1",
            posicao_inicio_original=0,
            posicao_fim_original=200,  # Tag grande [0-200]
            clausulas=[{"id": "clausula-001"}],
            score_inferencia=0.9,
            metodo="offset",
        ),
    ]

    # Múltiplas modificações dentro da tag
    modificacoes = [
        {
            "tipo": "inserção",
            "posicao_inicio": 20,
            "posicao_fim": 30,
            "conteudo": "mod 1",
        },
        {
            "tipo": "remoção",
            "posicao_inicio": 50,
            "posicao_fim": 60,
            "conteudo": "mod 2",
        },
        {
            "tipo": "modificação",
            "posicao_inicio": 100,
            "posicao_fim": 120,
            "conteudo": "mod 3",
        },
    ]

    # Executar vinculação
    api = DirectusAPI()
    resultado = api._vincular_por_sobreposicao_com_score(
        tags_mapeadas=tags, modificacoes=modificacoes
    )

    # Validar
    assert len(resultado.vinculadas) == 3, (
        f"Esperado 3 vinculadas, obteve {len(resultado.vinculadas)}"
    )
    assert len(resultado.revisao_manual) == 0
    assert len(resultado.nao_vinculadas) == 0

    # Validar que todas apontam para a mesma tag
    for vinc in resultado.vinculadas:
        assert vinc["tag"].tag_nome == "TAG-1"
        assert vinc["score"] >= 0.8

    # Validar taxas
    assert resultado.taxa_sucesso() == 100.0  # 3/3 = 100%

    print("   ✅ 3 modificações vinculadas à mesma tag")
    print(f"   Scores: {[v['score'] for v in resultado.vinculadas]}")
    print("   ✅ Teste de múltiplas modificações passou!")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FASE 4: TESTES DE SCORE E CATEGORIZAÇÃO")
    print("=" * 70)

    try:
        test_vinculacao_alta_confianca()
        test_vinculacao_media_confianca()
        test_vinculacao_baixa_confianca()
        test_multiplas_modificacoes_mesma_tag()

        print("\n" + "=" * 70)
        print("✅ FASE 4 COMPLETA: Todos os testes de score e categorização passaram!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
