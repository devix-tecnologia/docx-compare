"""
Testes unitários para agrupamento semântico de modificações (Task-017).

Valida:
- Filtro de modificações triviais
- Agrupamento por proximidade
- Agrupamento por cláusula
- Agrupamento por tipo
- Estratégias de merge (concat, summary, range)
"""

import sys
from pathlib import Path

# Adicionar path do diretório pai para imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from directus_server import SemanticGroupingConfig, _group_modifications_semantically


def test_filter_trivial_modifications():
    """Testa filtro de modificações triviais (< 10 chars)."""
    modifications = [
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 1, "coluna": 1},
            "conteudo": {"novo": ","},  # 1 char - trivial
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 2, "coluna": 1},
            "conteudo": {
                "original": "palavra",
                "novo": "texto modificado",
            },  # 25 chars - relevante
        },
        {
            "tipo": "REMOCAO",
            "posicao": {"linha": 3, "coluna": 1},
            "conteudo": {"original": "xy"},  # 2 chars - trivial
        },
    ]

    config = SemanticGroupingConfig(min_modification_size=10)
    result = _group_modifications_semantically(modifications, config)

    # Deve retornar apenas 1 modificação (a de 25 chars)
    assert len(result) == 1
    assert result[0]["tipo"] == "ALTERACAO"
    assert "texto modificado" in str(result[0]["conteudo"])


def test_group_close_modifications():
    """Testa agrupamento de modificações próximas (< 100 chars)."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},  # pos ~1000
            "clausula_original": "2.5",
            "conteudo": {"original": "trinta", "novo": "quinze"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 20},  # pos ~1020 (distância = 20)
            "clausula_original": "2.5",
            "conteudo": {"original": "30", "novo": "15"},
        },
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 1, "coluna": 30},  # pos ~1030 (distância = 10)
            "clausula_modificada": "2.5",
            "conteudo": {"novo": "dias úteis"},
        },
    ]

    config = SemanticGroupingConfig(max_distance=100, min_modification_size=2)
    result = _group_modifications_semantically(modifications, config)

    # Deve agrupar todas em 1 modificação
    assert len(result) == 1
    assert result[0]["modificacoes_agrupadas"] == 3
    assert result[0]["agrupamento_semantico"] is True


def test_no_group_distant_modifications():
    """Testa que modificações distantes NÃO são agrupadas (> 100 chars)."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},  # pos ~1000
            "clausula_original": "2.5",
            "conteudo": {"original": "palavra1", "novo": "palavra2"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 10, "coluna": 1},  # pos ~10000 (distância = 9000)
            "clausula_original": "2.5",
            "conteudo": {"original": "texto1", "novo": "texto2"},
        },
    ]

    config = SemanticGroupingConfig(max_distance=100, min_modification_size=5)
    result = _group_modifications_semantically(modifications, config)

    # Deve retornar 2 modificações separadas (distância > 100)
    assert len(result) == 2


def test_group_same_clause_only():
    """Testa agrupamento apenas de modificações da mesma cláusula."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "palavra1", "novo": "palavra2"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 20},  # Próximo, mas cláusula diferente
            "clausula_original": "3.1",
            "conteudo": {"original": "texto1", "novo": "texto2"},
        },
    ]

    config = SemanticGroupingConfig(
        max_distance=100, min_modification_size=5, require_same_clause=True
    )
    result = _group_modifications_semantically(modifications, config)

    # Deve retornar 2 modificações separadas (cláusulas diferentes)
    assert len(result) == 2


def test_group_same_type_only():
    """Testa agrupamento apenas de modificações do mesmo tipo."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "palavra1", "novo": "palavra2"},
        },
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 1, "coluna": 20},  # Próximo, mas tipo diferente
            "clausula_modificada": "2.5",
            "conteudo": {"novo": "texto inserido"},
        },
    ]

    config = SemanticGroupingConfig(
        max_distance=100,
        min_modification_size=5,
        require_same_clause=True,
        require_same_type=True,
    )
    result = _group_modifications_semantically(modifications, config)

    # Deve retornar 2 modificações separadas (tipos diferentes)
    assert len(result) == 2


def test_merge_strategy_concat():
    """Testa estratégia de merge 'concat'."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "30", "novo": "15"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 10},
            "clausula_original": "2.5",
            "conteudo": {"original": "trinta", "novo": "quinze"},
        },
    ]

    config = SemanticGroupingConfig(
        max_distance=100, min_modification_size=2, merge_strategy="concat"
    )
    result = _group_modifications_semantically(modifications, config)

    assert len(result) == 1
    merged = result[0]
    assert "15" in str(merged["conteudo"])
    assert "quinze" in str(merged["conteudo"])
    assert merged["modificacoes_agrupadas"] == 2


def test_merge_strategy_summary():
    """Testa estratégia de merge 'summary'."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "30", "novo": "15"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 10},
            "clausula_original": "2.5",
            "conteudo": {"original": "trinta", "novo": "quinze"},
        },
    ]

    config = SemanticGroupingConfig(
        max_distance=100, min_modification_size=2, merge_strategy="summary"
    )
    result = _group_modifications_semantically(modifications, config)

    assert len(result) == 1
    merged = result[0]
    assert "Bloco modificado" in str(merged["conteudo"])
    assert "contexto" in merged
    assert merged["modificacoes_agrupadas"] == 2


def test_merge_strategy_range():
    """Testa estratégia de merge 'range'."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "30", "novo": "15"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 10},
            "clausula_original": "2.5",
            "conteudo": {"original": "trinta", "novo": "quinze"},
        },
    ]

    config = SemanticGroupingConfig(
        max_distance=100, min_modification_size=2, merge_strategy="range"
    )
    result = _group_modifications_semantically(modifications, config)

    assert len(result) == 1
    merged = result[0]
    assert merged["tipo"] == "ALTERACAO_BLOCO"
    assert "detalhes" in merged
    assert len(merged["detalhes"]) == 2
    assert merged["modificacoes_agrupadas"] == 2


def test_mixed_types_priority():
    """Testa prioridade de tipos em grupos mistos (ALTERACAO > INSERCAO > REMOCAO)."""
    modifications = [
        {
            "tipo": "REMOCAO",
            "posicao": {"linha": 1, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "removido"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 15},
            "clausula_original": "2.5",
            "conteudo": {"original": "antigo", "novo": "novo"},
        },
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 1, "coluna": 30},
            "clausula_modificada": "2.5",
            "conteudo": {"novo": "inserido"},
        },
    ]

    config = SemanticGroupingConfig(
        max_distance=100,
        min_modification_size=4,
        require_same_clause=True,
        require_same_type=False,
    )
    result = _group_modifications_semantically(modifications, config)

    # Deve agrupar todas em 1 modificação com tipo ALTERACAO (prioridade mais alta)
    assert len(result) == 1
    assert result[0]["tipo"] == "ALTERACAO"
    assert result[0]["modificacoes_agrupadas"] == 3


def test_empty_modifications():
    """Testa comportamento com lista vazia."""
    modifications = []
    config = SemanticGroupingConfig()
    result = _group_modifications_semantically(modifications, config)

    assert len(result) == 0


def test_single_modification():
    """Testa que modificação única não é alterada."""
    modifications = [
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 1, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "palavra antiga", "novo": "palavra nova"},
        }
    ]

    config = SemanticGroupingConfig(min_modification_size=10)
    result = _group_modifications_semantically(modifications, config)

    assert len(result) == 1
    # Deve retornar a modificação original sem alterações
    assert result[0]["tipo"] == "ALTERACAO"
    assert "palavra nova" in str(result[0]["conteudo"])


if __name__ == "__main__":
    print("🧪 Executando testes de agrupamento semântico...")

    tests = [
        test_filter_trivial_modifications,
        test_group_close_modifications,
        test_no_group_distant_modifications,
        test_group_same_clause_only,
        test_group_same_type_only,
        test_merge_strategy_concat,
        test_merge_strategy_summary,
        test_merge_strategy_range,
        test_mixed_types_priority,
        test_empty_modifications,
        test_single_modification,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__}: {e}")
            failed += 1

    print(f"\n📊 Resultado: {passed} passou, {failed} falhou")
    sys.exit(0 if failed == 0 else 1)
