#!/usr/bin/env python3
"""
Diagnóstico 2: Processa versão com e sem agrupamento e compara.
"""

import sys
from directus_server import DirectusAPI, SemanticGroupingConfig


def analyze_modifications(mods: list[dict], label: str) -> dict:
    """Analisa composição de tipos."""
    tipos = {}
    
    for mod in mods:
        tipo = mod.get("tipo", "UNKNOWN")
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    total = len(mods)
    
    print(f"\n{'='*80}")
    print(f"📊 {label}")
    print(f"{'='*80}")
    print(f"Total: {total} modificações")
    print(f"\nDistribuição de tipos:")
    for tipo, count in sorted(tipos.items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {tipo:12} {count:3} ({pct:5.1f}%) {bar}")
    
    return {
        "total": total,
        "tipos": tipos,
        "taxa_alteracao": (tipos.get("ALTERACAO", 0) / total * 100) if total > 0 else 0,
    }


def main():
    """Executa comparação com e sem agrupamento."""
    print("="*80)
    print("🔬 COMPARAÇÃO: Com vs Sem Agrupamento Semântico")
    print("="*80)
    
    api = DirectusAPI()
    versao_id = "8d8e89a8-ba89-4e0e-846c-43e7ad058309"
    
    print(f"\n📄 Versão: {versao_id}")
    print(f"⏱️ Processando... (pode levar ~2 minutos)")
    
    # Processar SEM agrupamento
    print("\n" + "🔵" * 40)
    print("Processando SEM agrupamento semântico...")
    print("🔵" * 40)
    
    result_sem = api.process_versao(
        versao_id=versao_id,
        use_semantic_grouping=False,
    )
    
    if "error" in result_sem:
        print(f"❌ Erro: {result_sem['error']}")
        return
    
    mods_sem = result_sem.get("modificacoes", [])
    stats_sem = analyze_modifications(mods_sem, "SEM AGRUPAMENTO (baseline Task-016)")
    
    # Processar COM agrupamento padrão
    print("\n" + "🟢" * 40)
    print("Processando COM agrupamento semântico (config padrão)...")
    print("🟢" * 40)
    
    result_com = api.process_versao(
        versao_id=versao_id,
        use_semantic_grouping=True,
    )
    
    if "error" in result_com:
        print(f"❌ Erro: {result_com['error']}")
        return
    
    mods_com = result_com.get("modificacoes", [])
    stats_com = analyze_modifications(mods_com, "COM AGRUPAMENTO (Task-017)")
    
    # Processar COM agrupamento alternativo (require_same_type=True)
    print("\n" + "🟡" * 40)
    print("Processando COM agrupamento (require_same_type=True)...")
    print("🟡" * 40)
    
    config_alt = SemanticGroupingConfig(require_same_type=True)
    
    result_alt = api.process_versao(
        versao_id=versao_id,
        use_semantic_grouping=True,
        semantic_config=config_alt,
    )
    
    if "error" in result_alt:
        print(f"❌ Erro: {result_alt['error']}")
        return
    
    mods_alt = result_alt.get("modificacoes", [])
    stats_alt = analyze_modifications(mods_alt, "COM AGRUPAMENTO (same_type=True)")
    
    # Comparar resultados
    print("\n" + "="*80)
    print("📈 COMPARAÇÃO FINAL")
    print("="*80)
    
    print(f"\n{'Modo':<30} {'Total':>8} {'ALTERACAO':>12} {'Taxa':>8}  {'Redução':>10}")
    print("-" * 80)
    
    print(f"{'Baseline (Task-016)':<30} {stats_sem['total']:>8} {stats_sem['tipos'].get('ALTERACAO', 0):>12} {stats_sem['taxa_alteracao']:>7.1f}%  {'-':>10}")
    
    reducao_com = ((stats_sem['total'] - stats_com['total']) / stats_sem['total'] * 100) if stats_sem['total'] > 0 else 0
    print(f"{'Semântico padrão':<30} {stats_com['total']:>8} {stats_com['tipos'].get('ALTERACAO', 0):>12} {stats_com['taxa_alteracao']:>7.1f}%  {reducao_com:>9.1f}%")
    
    reducao_alt = ((stats_sem['total'] - stats_alt['total']) / stats_sem['total'] * 100) if stats_sem['total'] > 0 else 0
    print(f"{'Semântico (same_type=True)':<30} {stats_alt['total']:>8} {stats_alt['tipos'].get('ALTERACAO', 0):>12} {stats_alt['taxa_alteracao']:>7.1f}%  {reducao_alt:>9.1f}%")
    
    # Análise
    print("\n" + "="*80)
    print("🎯 ANÁLISE")
    print("="*80)
    
    delta_taxa_com = stats_com['taxa_alteracao'] - stats_sem['taxa_alteracao']
    delta_taxa_alt = stats_alt['taxa_alteracao'] - stats_sem['taxa_alteracao']
    
    print(f"\nImpacto na taxa de ALTERACAO:")
    print(f"  Padrão:        {delta_taxa_com:+.1f}pp ({stats_sem['taxa_alteracao']:.1f}% → {stats_com['taxa_alteracao']:.1f}%)")
    print(f"  Same_type=True: {delta_taxa_alt:+.1f}pp ({stats_sem['taxa_alteracao']:.1f}% → {stats_alt['taxa_alteracao']:.1f}%)")
    
    print(f"\nRedução no total:")
    print(f"  Padrão:         {reducao_com:.1f}% ({stats_sem['total']} → {stats_com['total']})")
    print(f"  Same_type=True: {reducao_alt:.1f}% ({stats_sem['total']} → {stats_alt['total']})")
    
    # Recomendação
    print("\n" + "="*80)
    print("💡 RECOMENDAÇÃO")
    print("="*80)
    
    if delta_taxa_com > 5:
        print("\n✅ Config padrão está funcionando bem!")
        print(f"   - Taxa ALTERACAO aumentou {delta_taxa_com:.1f}pp")
        print(f"   - Redução de {reducao_com:.1f}% no total")
    elif delta_taxa_alt > delta_taxa_com:
        print("\n⚠️ Config alternativa (same_type=True) é melhor:")
        print(f"   - Taxa ALTERACAO: {delta_taxa_alt:.1f}pp vs {delta_taxa_com:.1f}pp")
        print(f"   - Redução: {reducao_alt:.1f}% vs {reducao_com:.1f}%")
        print("\n   Atualizar SemanticGroupingConfig padrão:")
        print("   SemanticGroupingConfig(require_same_type=True)")
    else:
        print("\n⚠️ Nenhuma config atinge meta de 70% ALTERACAO")
        print(f"   - Baseline já tem apenas {stats_sem['taxa_alteracao']:.1f}% ALTERACAO")
        print(f"   - Problema pode estar na Task-016 (classificação de tipos)")
        print("\n   Próximos passos:")
        print("   1. Revisar thresholds de similaridade na Task-016")
        print("   2. Ajustar lógica de classificação INSERCAO/REMOCAO → ALTERACAO")
        print("   3. Considerar usar análise semântica (embeddings) para classificar tipos")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
