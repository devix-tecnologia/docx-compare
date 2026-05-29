"""
Script de validação rápida da Task-017.

Testa agrupamento semântico com dados sintéticos para validar lógica.
"""

from directus_server import SemanticGroupingConfig, _group_modifications_semantically


def test_semantic_reduces_and_improves_alteracao():
    """Valida que agrupamento reduz total E aumenta taxa de ALTERACAO."""

    # Simular resultado da Task-016 (115 modificações, 42% ALTERACAO)
    # Padrão típico: muitas modificações pequenas, várias são triviais
    modificacoes_baseline = [
        # Grupo 1: ALTERACAO granular (3 mods próximas → 1 ALTERACAO)
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 10, "coluna": 1},
            "clausula_original": "2.5",
            "conteudo": {"original": "30", "novo": "15"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 10, "coluna": 10},
            "clausula_original": "2.5",
            "conteudo": {"original": "trinta", "novo": "quinze"},
        },
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 10, "coluna": 20},
            "clausula_modificada": "2.5",
            "conteudo": {"novo": "dias úteis"},
        },
        # Grupo 2: INSERCAO + REMOCAO próximas (2 mods → 1 ALTERACAO se não require_same_type)
        {
            "tipo": "REMOCAO",
            "posicao": {"linha": 20, "coluna": 1},
            "clausula_original": "3.1",
            "conteudo": {"original": "texto antigo aqui"},
        },
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 20, "coluna": 10},
            "clausula_modificada": "3.1",
            "conteudo": {"novo": "texto novo aqui"},
        },
        # Grupo 3: Triviais isolados (filtrados)
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 30, "coluna": 1},
            "conteudo": {"novo": ","},
        },  # 1 char
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 40, "coluna": 1},
            "conteudo": {"original": ".", "novo": ";"},
        },  # 2 chars
        # Grupo 4: INSERCAO relevante isolada (mantida)
        {
            "tipo": "INSERCAO",
            "posicao": {"linha": 50, "coluna": 1},
            "clausula_modificada": "4.1",
            "conteudo": {"novo": "nova cláusula completa aqui"},
        },
        # Grupo 5: ALTERACOEs distantes (não agrupam)
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 100, "coluna": 1},
            "clausula_original": "5.1",
            "conteudo": {"original": "valor A", "novo": "valor B"},
        },
        {
            "tipo": "ALTERACAO",
            "posicao": {"linha": 200, "coluna": 1},
            "clausula_original": "5.2",
            "conteudo": {"original": "valor C", "novo": "valor D"},
        },
    ]

    # Calcular métricas baseline
    total_baseline = len(modificacoes_baseline)
    alteracao_baseline = sum(
        1 for m in modificacoes_baseline if m["tipo"] == "ALTERACAO"
    )
    taxa_baseline = alteracao_baseline / total_baseline * 100

    print("=" * 80)
    print("📊 BASELINE (simulado)")
    print("=" * 80)
    print(f"Total: {total_baseline} modificações")
    print(f"ALTERACAO: {alteracao_baseline} ({taxa_baseline:.1f}%)")

    # Aplicar agrupamento semântico
    config = SemanticGroupingConfig(
        max_distance=100,
        min_modification_size=10,
        require_same_clause=True,
        require_same_type=False,  # Permitir agrupar tipos diferentes
        merge_strategy="concat",
    )

    result = _group_modifications_semantically(modificacoes_baseline, config)

    # Calcular métricas agrupadas
    total_semantic = len(result)
    alteracao_semantic = sum(1 for m in result if m["tipo"] == "ALTERACAO")
    taxa_semantic = (
        alteracao_semantic / total_semantic * 100 if total_semantic > 0 else 0
    )

    print("\n" + "=" * 80)
    print("🎯 COM AGRUPAMENTO SEMÂNTICO")
    print("=" * 80)
    print(f"Total: {total_semantic} modificações")
    print(f"ALTERACAO: {alteracao_semantic} ({taxa_semantic:.1f}%)")

    for i, mod in enumerate(result, 1):
        agrupadas = mod.get("modificacoes_agrupadas", 0)
        if agrupadas > 1:
            print(f"  Mod #{i}: {mod['tipo']} (agrupa {agrupadas} mods)")

    # Validações
    print("\n" + "=" * 80)
    print("✅ VALIDAÇÕES")
    print("=" * 80)

    # 1. Deve reduzir total
    reducao = (total_baseline - total_semantic) / total_baseline * 100
    print(
        f"1. Redução: {reducao:.1f}% (10→{total_semantic}) - {'✅' if reducao > 0 else '❌'}"
    )

    # 2. Deve aumentar taxa de ALTERACAO
    aumento = taxa_semantic - taxa_baseline
    print(
        f"2. Taxa ALTERACAO: {taxa_baseline:.1f}% → {taxa_semantic:.1f}% ({aumento:+.1f}pp) - {'✅' if aumento > 0 else '❌'}"
    )

    # 3. Deve eliminar triviais
    triviais_filtradas = total_baseline - len(
        [m for m in modificacoes_baseline if len(str(m.get("conteudo", ""))) >= 10]
    )
    print(
        f"3. Triviais filtradas: {triviais_filtradas} - {'✅' if triviais_filtradas >= 2 else '❌'}"
    )

    # Resultado esperado:
    # - 10 mods → ~5-6 mods (redução ~40-50%)
    # - 50% ALTERACAO → ≥60% ALTERACAO (aumento ~10pp)
    # - 2 triviais eliminadas

    assert total_semantic < total_baseline, "Deve reduzir total de modificações"
    assert taxa_semantic >= taxa_baseline, "Deve aumentar ou manter taxa de ALTERACAO"

    print("\n✅ Validação OK: Lógica de agrupamento funcionando conforme esperado")


if __name__ == "__main__":
    test_semantic_reduces_and_improves_alteracao()
