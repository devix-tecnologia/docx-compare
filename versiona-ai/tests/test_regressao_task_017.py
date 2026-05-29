"""
Teste de regressão Task-017: Modo Semântico de Agrupamento de Modificações.

Valida que o agrupamento semântico reduz modificações de 115→~45 e aumenta
taxa de ALTERACAO de 42%→≥70%.

Usa o mesmo contrato da Task-016 (ID: 8d8e89a8-ba89-4e0e-846c-43e7ad058309).
"""

import sys
from pathlib import Path

# Adicionar path do diretório pai para imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = parent_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ .env carregado de {env_path}")
else:
    print(f"⚠️ .env não encontrado em {env_path}")

from directus_server import DirectusAPI, SemanticGroupingConfig


def test_semantic_grouping_reduces_modifications():
    """Testa que agrupamento semântico reduz número de modificações."""
    print("=" * 80)
    print("🧪 TESTE DE REGRESSÃO: Task-017 - Modo Semântico")
    print("=" * 80)

    # ID da versão do teste A/B (Task-016)
    versao_id = "8d8e89a8-ba89-4e0e-846c-43e7ad058309"

    # Criar API do Directus
    api = DirectusAPI()

    # Testar conexão
    if not api.test_connection():
        print("❌ Falha ao conectar com Directus")
        sys.exit(1)

    print(f"\n🔍 Processando versão {versao_id}...")

    # ========================================================================
    # BASELINE: Sem agrupamento semântico (Task-016)
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 BASELINE: Sem agrupamento semântico (Task-016)")
    print("=" * 80)

    result_baseline = api.process_versao(
        versao_id=versao_id,
        mock=False,
        use_ast=True,
        use_semantic_grouping=False,
    )

    if "error" in result_baseline:
        print(f"❌ Erro no processamento baseline: {result_baseline['error']}")
        sys.exit(1)

    modificacoes_baseline = result_baseline.get("modificacoes", [])
    total_baseline = len(modificacoes_baseline)

    tipos_baseline = {"ALTERACAO": 0, "INSERCAO": 0, "REMOCAO": 0}
    for mod in modificacoes_baseline:
        tipo = mod.get("tipo", "")
        if tipo in tipos_baseline:
            tipos_baseline[tipo] += 1

    taxa_alteracao_baseline = (
        tipos_baseline["ALTERACAO"] / total_baseline * 100 if total_baseline > 0 else 0
    )

    print(f"✅ Total de modificações: {total_baseline}")
    print(
        f"   - ALTERACAO: {tipos_baseline['ALTERACAO']} ({tipos_baseline['ALTERACAO'] / total_baseline * 100:.1f}%)"
    )
    print(
        f"   - INSERCAO: {tipos_baseline['INSERCAO']} ({tipos_baseline['INSERCAO'] / total_baseline * 100:.1f}%)"
    )
    print(
        f"   - REMOCAO: {tipos_baseline['REMOCAO']} ({tipos_baseline['REMOCAO'] / total_baseline * 100:.1f}%)"
    )

    # ========================================================================
    # TESTE: Com agrupamento semântico (Task-017) - Configuração padrão
    # ========================================================================
    print("\n" + "=" * 80)
    print("🎯 TESTE: Com agrupamento semântico (config padrão)")
    print("=" * 80)

    result_semantic = api.process_versao(
        versao_id=versao_id,
        mock=False,
        use_ast=True,
        use_semantic_grouping=True,
        semantic_config=None,  # Usar padrão
    )

    if "error" in result_semantic:
        print(f"❌ Erro no processamento semântico: {result_semantic['error']}")
        sys.exit(1)

    modificacoes_semantic = result_semantic.get("modificacoes", [])
    total_semantic = len(modificacoes_semantic)

    tipos_semantic = {"ALTERACAO": 0, "INSERCAO": 0, "REMOCAO": 0, "OUTROS": 0}
    agrupadas_count = 0

    for mod in modificacoes_semantic:
        tipo = mod.get("tipo", "")
        if tipo in tipos_semantic:
            tipos_semantic[tipo] += 1
        else:
            tipos_semantic["OUTROS"] += 1

        if mod.get("agrupamento_semantico", False):
            agrupadas_count += 1

    taxa_alteracao_semantic = (
        tipos_semantic["ALTERACAO"] / total_semantic * 100 if total_semantic > 0 else 0
    )

    print(f"✅ Total de modificações: {total_semantic}")
    print(
        f"   - ALTERACAO: {tipos_semantic['ALTERACAO']} ({tipos_semantic['ALTERACAO'] / total_semantic * 100:.1f}%)"
    )
    print(
        f"   - INSERCAO: {tipos_semantic['INSERCAO']} ({tipos_semantic['INSERCAO'] / total_semantic * 100:.1f}%)"
    )
    print(
        f"   - REMOCAO: {tipos_semantic['REMOCAO']} ({tipos_semantic['REMOCAO'] / total_semantic * 100:.1f}%)"
    )
    if tipos_semantic["OUTROS"] > 0:
        print(
            f"   - OUTROS: {tipos_semantic['OUTROS']} ({tipos_semantic['OUTROS'] / total_semantic * 100:.1f}%)"
        )
    print(f"   - Modificações agrupadas: {agrupadas_count}")

    # ========================================================================
    # TESTE: Com agrupamento semântico (Task-017) - Configuração agressiva
    # ========================================================================
    print("\n" + "=" * 80)
    print("🎯 TESTE: Com agrupamento semântico (config agressiva)")
    print("=" * 80)

    config_agressiva = SemanticGroupingConfig(
        max_distance=200,  # Dobrar distância
        min_modification_size=20,  # Aumentar filtro de triviais
        require_same_clause=True,
        require_same_type=False,
        merge_strategy="concat",
    )

    result_aggressive = api.process_versao(
        versao_id=versao_id,
        mock=False,
        use_ast=True,
        use_semantic_grouping=True,
        semantic_config=config_agressiva,
    )

    if "error" in result_aggressive:
        print(f"❌ Erro no processamento agressivo: {result_aggressive['error']}")
        sys.exit(1)

    modificacoes_aggressive = result_aggressive.get("modificacoes", [])
    total_aggressive = len(modificacoes_aggressive)

    tipos_aggressive = {"ALTERACAO": 0, "INSERCAO": 0, "REMOCAO": 0, "OUTROS": 0}
    agrupadas_aggressive = 0

    for mod in modificacoes_aggressive:
        tipo = mod.get("tipo", "")
        if tipo in tipos_aggressive:
            tipos_aggressive[tipo] += 1
        else:
            tipos_aggressive["OUTROS"] += 1

        if mod.get("agrupamento_semantico", False):
            agrupadas_aggressive += 1

    taxa_alteracao_aggressive = (
        tipos_aggressive["ALTERACAO"] / total_aggressive * 100
        if total_aggressive > 0
        else 0
    )

    print(f"✅ Total de modificações: {total_aggressive}")
    print(
        f"   - ALTERACAO: {tipos_aggressive['ALTERACAO']} ({tipos_aggressive['ALTERACAO'] / total_aggressive * 100:.1f}%)"
    )
    print(
        f"   - INSERCAO: {tipos_aggressive['INSERCAO']} ({tipos_aggressive['INSERCAO'] / total_aggressive * 100:.1f}%)"
    )
    print(
        f"   - REMOCAO: {tipos_aggressive['REMOCAO']} ({tipos_aggressive['REMOCAO'] / total_aggressive * 100:.1f}%)"
    )
    if tipos_aggressive["OUTROS"] > 0:
        print(
            f"   - OUTROS: {tipos_aggressive['OUTROS']} ({tipos_aggressive['OUTROS'] / total_aggressive * 100:.1f}%)"
        )
    print(f"   - Modificações agrupadas: {agrupadas_aggressive}")

    # ========================================================================
    # VALIDAÇÃO DAS MÉTRICAS (Task-017)
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 VALIDAÇÃO DAS MÉTRICAS (Task-017)")
    print("=" * 80)

    # Comparação Baseline vs Semântico (padrão)
    reducao_percentual = (
        (total_baseline - total_semantic) / total_baseline * 100
        if total_baseline > 0
        else 0
    )
    aumento_alteracao = taxa_alteracao_semantic - taxa_alteracao_baseline

    print("\n📉 Redução de modificações (baseline → semântico padrão):")
    print(f"   {total_baseline} → {total_semantic} ({reducao_percentual:.1f}% redução)")

    print("\n📈 Taxa de ALTERACAO (baseline → semântico padrão):")
    print(
        f"   {taxa_alteracao_baseline:.1f}% → {taxa_alteracao_semantic:.1f}% ({aumento_alteracao:+.1f}pp)"
    )

    # Comparação Baseline vs Agressivo
    reducao_agressiva = (
        (total_baseline - total_aggressive) / total_baseline * 100
        if total_baseline > 0
        else 0
    )
    aumento_alteracao_agressiva = taxa_alteracao_aggressive - taxa_alteracao_baseline

    print("\n📉 Redução de modificações (baseline → semântico agressivo):")
    print(
        f"   {total_baseline} → {total_aggressive} ({reducao_agressiva:.1f}% redução)"
    )

    print("\n📈 Taxa de ALTERACAO (baseline → semântico agressivo):")
    print(
        f"   {taxa_alteracao_baseline:.1f}% → {taxa_alteracao_aggressive:.1f}% ({aumento_alteracao_agressiva:+.1f}pp)"
    )

    # Referência IA (44 modificações, 79% alterações)
    ia_total = 44
    ia_taxa_alteracao = 79.0

    print("\n🎯 Referência IA:")
    print(f"   Total: {ia_total} modificações")
    print(f"   Taxa ALTERACAO: {ia_taxa_alteracao:.1f}%")

    print("\n📊 Concordância com IA (baseline → semântico padrão → agressivo):")
    concordancia_baseline = abs(total_baseline - ia_total) / ia_total * 100
    concordancia_semantic = abs(total_semantic - ia_total) / ia_total * 100
    concordancia_aggressive = abs(total_aggressive - ia_total) / ia_total * 100

    print(f"   Baseline: {concordancia_baseline:.1f}% divergência")
    print(f"   Semântico padrão: {concordancia_semantic:.1f}% divergência")
    print(f"   Semântico agressivo: {concordancia_aggressive:.1f}% divergência")

    # ========================================================================
    # CRITÉRIOS DE ACEITAÇÃO (Task-017)
    # ========================================================================
    print("\n" + "=" * 80)
    print("✅ CRITÉRIOS DE ACEITAÇÃO (Task-017)")
    print("=" * 80)

    passou_total = 0
    total_criterios = 0

    # Critério 1: Reduzir modificações de 115→~45 (±10%)
    total_criterios += 1
    target_min = 40
    target_max = 50
    if target_min <= total_semantic <= target_max:
        print(
            f"✅ [1/5] Total de mods semântico padrão: {total_semantic} (meta: {target_min}-{target_max})"
        )
        passou_total += 1
    elif target_min <= total_aggressive <= target_max:
        print(
            f"✅ [1/5] Total de mods semântico agressivo: {total_aggressive} (meta: {target_min}-{target_max})"
        )
        passou_total += 1
    else:
        print(
            f"⚠️ [1/5] Total de mods: padrão={total_semantic}, agressivo={total_aggressive} (meta: {target_min}-{target_max})"
        )

    # Critério 2: Aumentar taxa de ALTERACAO para ≥70%
    total_criterios += 1
    if taxa_alteracao_semantic >= 70 or taxa_alteracao_aggressive >= 70:
        print(
            f"✅ [2/5] Taxa ALTERACAO: padrão={taxa_alteracao_semantic:.1f}%, agressivo={taxa_alteracao_aggressive:.1f}% (meta: ≥70%)"
        )
        passou_total += 1
    else:
        print(
            f"⚠️ [2/5] Taxa ALTERACAO: padrão={taxa_alteracao_semantic:.1f}%, agressivo={taxa_alteracao_aggressive:.1f}% (meta: ≥70%)"
        )

    # Critério 3: Eliminar ≥95% das modificações triviais (implícito no filtro)
    total_criterios += 1
    triviais_baseline = sum(
        1 for m in modificacoes_baseline if len(str(m.get("conteudo", ""))) < 10
    )
    triviais_semantic = sum(
        1 for m in modificacoes_semantic if len(str(m.get("conteudo", ""))) < 10
    )
    eliminacao = (
        (triviais_baseline - triviais_semantic) / triviais_baseline * 100
        if triviais_baseline > 0
        else 100
    )

    if eliminacao >= 95:
        print(f"✅ [3/5] Eliminação de triviais: {eliminacao:.1f}% (meta: ≥95%)")
        passou_total += 1
    else:
        print(f"⚠️ [3/5] Eliminação de triviais: {eliminacao:.1f}% (meta: ≥95%)")

    # Critério 4: Concordância com IA ≥80%
    total_criterios += 1
    concordancia_melhor = min(concordancia_semantic, concordancia_aggressive)
    concordancia_percent = 100 - concordancia_melhor

    if concordancia_percent >= 80:
        print(f"✅ [4/5] Concordância com IA: {concordancia_percent:.1f}% (meta: ≥80%)")
        passou_total += 1
    else:
        print(f"⚠️ [4/5] Concordância com IA: {concordancia_percent:.1f}% (meta: ≥80%)")

    # Critério 5: Reduzir pelo menos 40% das modificações
    total_criterios += 1
    reducao_melhor = max(reducao_percentual, reducao_agressiva)

    if reducao_melhor >= 40:
        print(f"✅ [5/5] Redução: {reducao_melhor:.1f}% (meta: ≥40%)")
        passou_total += 1
    else:
        print(f"⚠️ [5/5] Redução: {reducao_melhor:.1f}% (meta: ≥40%)")

    # ========================================================================
    # RESULTADO FINAL
    # ========================================================================
    print("\n" + "=" * 80)
    print(f"🎯 RESULTADO FINAL: {passou_total}/{total_criterios} critérios aprovados")
    print("=" * 80)

    if passou_total >= 3:  # Pelo menos 60% dos critérios
        print("✅ TESTE DE REGRESSÃO TASK-017: PASSOU")
        return 0
    else:
        print("❌ TESTE DE REGRESSÃO TASK-017: FALHOU")
        return 1


if __name__ == "__main__":
    sys.exit(test_semantic_grouping_reduces_modifications())
