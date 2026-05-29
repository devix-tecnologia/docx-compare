#!/usr/bin/env python3
"""
Diagnóstico: Por que a taxa de ALTERACAO cai no agrupamento semântico?

Analisa modificações antes e depois do agrupamento para identificar padrões.
"""

import sys

from directus_server import (
    DirectusAPI,
    SemanticGroupingConfig,
    _group_modifications_semantically,
)


def analyze_modifications(mods: list[dict], label: str) -> dict:
    """Analisa composição de tipos e tamanhos das modificações."""
    tipos = {}
    tamanhos = []

    for mod in mods:
        tipo = mod.get("tipo", "UNKNOWN")
        tipos[tipo] = tipos.get(tipo, 0) + 1

        # Calcular tamanho
        conteudo = mod.get("conteudo", {})
        size = 0
        if isinstance(conteudo, dict):
            if "original" in conteudo:
                size += len(str(conteudo.get("original", "")))
            if "novo" in conteudo:
                size += len(str(conteudo.get("novo", "")))
        tamanhos.append(size)

    total = len(mods)

    print(f"\n{'=' * 80}")
    print(f"📊 {label}")
    print(f"{'=' * 80}")
    print(f"Total: {total} modificações")
    print("\nTipos:")
    for tipo, count in sorted(tipos.items()):
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {tipo}: {count} ({pct:.1f}%)")

    if tamanhos:
        avg_size = sum(tamanhos) / len(tamanhos)
        min_size = min(tamanhos)
        max_size = max(tamanhos)
        triviais = sum(1 for s in tamanhos if s < 10)
        print("\nTamanhos:")
        print(f"  Média: {avg_size:.1f} chars")
        print(f"  Min: {min_size} chars")
        print(f"  Max: {max_size} chars")
        print(f"  Triviais (<10): {triviais} ({triviais / total * 100:.1f}%)")

    return {
        "total": total,
        "tipos": tipos,
        "tamanhos": tamanhos,
    }


def analyze_filtered_trivials(before: list[dict], after: list[dict]):
    """Analisa quais tipos foram filtrados como triviais."""
    before_ids = {id(mod) for mod in before}
    after_ids = {id(mod) for mod in after}

    # Criar mapeamento aproximado por posição + tipo
    before_map = {}
    for mod in before:
        pos = mod.get("posicao", {})
        linha = pos.get("linha", 0) if isinstance(pos, dict) else 0
        key = (linha, mod.get("tipo"))
        before_map[key] = mod

    after_map = {}
    for mod in after:
        pos = mod.get("posicao", {})
        linha = pos.get("linha", 0) if isinstance(pos, dict) else 0
        key = (linha, mod.get("tipo"))
        after_map[key] = mod

    # Encontrar removidos (filtrados)
    removed_keys = set(before_map.keys()) - set(after_map.keys())
    removed = [before_map[key] for key in removed_keys]

    if removed:
        print(f"\n{'=' * 80}")
        print("🗑️ MODIFICAÇÕES FILTRADAS (triviais < 10 chars)")
        print(f"{'=' * 80}")

        tipos_removidos = {}
        for mod in removed:
            tipo = mod.get("tipo", "UNKNOWN")
            tipos_removidos[tipo] = tipos_removidos.get(tipo, 0) + 1

        print(f"Total filtradas: {len(removed)}")
        print("\nTipos filtrados:")
        for tipo, count in sorted(tipos_removidos.items()):
            print(f"  {tipo}: {count}")


def analyze_grouping_behavior(before_group: list[dict], after_group: dict):
    """Analisa como um grupo específico foi transformado."""
    tipos_antes = [mod.get("tipo") for mod in before_group]
    tipo_depois = after_group.get("tipo")

    print(f"\nGrupo de {len(before_group)} mods:")
    print(f"  Antes: {tipos_antes}")
    print(f"  Depois: {tipo_depois}")

    # Verificar se priorização funcionou corretamente
    if "ALTERACAO" in tipos_antes and tipo_depois != "ALTERACAO":
        print(f"  ⚠️ PROBLEMA: Tinha ALTERACAO mas virou {tipo_depois}")
    elif (
        "INSERCAO" in tipos_antes
        and "ALTERACAO" not in tipos_antes
        and tipo_depois != "INSERCAO"
    ):
        print(f"  ⚠️ PROBLEMA: Tinha INSERCAO mas virou {tipo_depois}")


def main():
    """Executa diagnóstico completo."""
    print("=" * 80)
    print("🔬 DIAGNÓSTICO: Taxa de ALTERACAO no Agrupamento Semântico")
    print("=" * 80)

    # Inicializar API
    api = DirectusAPI()

    # ID do contrato de teste
    versao_id = "8d8e89a8-ba89-4e0e-846c-43e7ad058309"

    print(f"\n📄 Buscando modificações existentes da versão: {versao_id}")

    # Buscar modificações do Directus diretamente
    try:
        mods_baseline = api.repo.get_modificacoes_versao(versao_id)
        if not mods_baseline:
            print("❌ Nenhuma modificação encontrada. Execute process_versao primeiro.")
            return

        print(f"✅ {len(mods_baseline)} modificações encontradas")
    except Exception as e:
        print(f"❌ Erro ao buscar modificações: {e}")
        return

    stats_baseline = analyze_modifications(mods_baseline, "BASELINE (do Directus)")

    # Aplicar agrupamento manualmente
    print("\n" + "=" * 80)
    print("🔵 APLICANDO AGRUPAMENTO SEMÂNTICO")
    print("=" * 80)

    config_default = SemanticGroupingConfig()

    # Etapa 1: Filtrar triviais
    print("\n📌 Etapa 1: Filtrar triviais")
    mods_filtered = [
        mod
        for mod in mods_baseline
        if _get_mod_size(mod) >= config_default.min_modification_size
    ]
    print(f"Antes: {len(mods_baseline)} → Depois: {len(mods_filtered)}")

    stats_filtered = analyze_modifications(mods_filtered, "APÓS FILTRO TRIVIAIS")

    # Analisar o que foi filtrado
    analyze_filtered_trivials(mods_baseline, mods_filtered)

    # Etapa 2: Agrupar semanticamente
    print("\n📌 Etapa 2: Agrupar semanticamente")
    mods_grouped = _group_modifications_semantically(mods_baseline, config_default)

    stats_grouped = analyze_modifications(mods_grouped, "APÓS AGRUPAMENTO")

    # Comparar taxas
    print("\n" + "=" * 80)
    print("📈 COMPARAÇÃO DE TAXAS")
    print("=" * 80)

    taxa_baseline = (
        stats_baseline["tipos"].get("ALTERACAO", 0) / stats_baseline["total"] * 100
        if stats_baseline["total"] > 0
        else 0
    )
    taxa_filtered = (
        stats_filtered["tipos"].get("ALTERACAO", 0) / stats_filtered["total"] * 100
        if stats_filtered["total"] > 0
        else 0
    )
    taxa_grouped = (
        stats_grouped["tipos"].get("ALTERACAO", 0) / stats_grouped["total"] * 100
        if stats_grouped["total"] > 0
        else 0
    )

    print(
        f"\n1. Baseline:             {taxa_baseline:.1f}% ALTERACAO ({stats_baseline['tipos'].get('ALTERACAO', 0)}/{stats_baseline['total']})"
    )
    print(
        f"2. Após filtro triviais: {taxa_filtered:.1f}% ALTERACAO ({stats_filtered['tipos'].get('ALTERACAO', 0)}/{stats_filtered['total']})"
    )
    print(
        f"3. Após agrupamento:     {taxa_grouped:.1f}% ALTERACAO ({stats_grouped['tipos'].get('ALTERACAO', 0)}/{stats_grouped['total']})"
    )

    # Identificar onde está o problema
    print("\n" + "=" * 80)
    print("🎯 DIAGNÓSTICO")
    print("=" * 80)

    delta_filtro = taxa_filtered - taxa_baseline
    delta_grupo = taxa_grouped - taxa_filtered

    print(f"\nImpacto do filtro de triviais: {delta_filtro:+.1f}pp")
    if abs(delta_filtro) > 5:
        if delta_filtro < 0:
            print("  ⚠️ Filtro está removendo muitas ALTERACOEs!")
        else:
            print("  ✅ Filtro está ajudando (remove mais INSERCAOes/REMOCAOes)")
    else:
        print("  ℹ️ Impacto neutro")

    print(f"\nImpacto do agrupamento: {delta_grupo:+.1f}pp")
    if abs(delta_grupo) > 5:
        if delta_grupo < 0:
            print("  ⚠️ Agrupamento está criando mais INSERCAOes/REMOCAOes!")
        else:
            print("  ✅ Agrupamento está ajudando (prioriza ALTERACAO)")
    else:
        print("  ℹ️ Impacto neutro")

    # Sugestões
    print("\n" + "=" * 80)
    print("💡 SUGESTÕES")
    print("=" * 80)

    if delta_filtro < -5:
        print("\n1. ⚠️ Reduzir min_modification_size de 10 para 5:")
        print("   - Mantém mais ALTERACOEs pequenas")
        print("   - Testa com: SemanticGroupingConfig(min_modification_size=5)")

    if delta_grupo < -5:
        print("\n2. ⚠️ Habilitar require_same_type=True:")
        print("   - Evita juntar INSERCAO+REMOCAO que poderia virar ALTERACAO")
        print("   - Mantém grupos mais homogêneos")
        print("   - Testa com: SemanticGroupingConfig(require_same_type=True)")

    if taxa_baseline < 50:
        print("\n3. ⚠️ Problema no baseline:")
        print(f"   - Taxa de ALTERACAO já é baixa ({taxa_baseline:.1f}%)")
        print("   - Revisar Task-016: lógica de classificação de tipos")
        print("   - Muitas modificações podem estar sendo classificadas errado")
        print("   - Considerar revisar thresholds de similaridade")

    if taxa_grouped < taxa_baseline:
        print("\n4. ⚠️ Agrupamento está piorando:")
        print(f"   - Taxa caiu de {taxa_baseline:.1f}% → {taxa_grouped:.1f}%")
        print("   - Considerar desabilitar agrupamento para este caso")
        print("   - Ou ajustar parâmetros (max_distance, require_same_type)")

    print("\n" + "=" * 80)


def _get_mod_size(mod: dict) -> int:
    """Calcula tamanho da modificação."""
    conteudo = mod.get("conteudo", {})
    size = 0
    if isinstance(conteudo, dict):
        if "original" in conteudo:
            size += len(str(conteudo.get("original", "")))
        if "novo" in conteudo:
            size += len(str(conteudo.get("novo", "")))
    return size


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
