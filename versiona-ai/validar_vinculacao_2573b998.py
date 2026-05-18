#!/usr/bin/env python3
"""
Validação completa da vinculação da versão 2573b998
Demonstra correção do algoritmo após fixes de overlap
"""

import sys
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "tests"))

from processar_caso_real import (
    baixar_versao_directus,
    extrair_dados_para_algoritmo,
    processar_com_algoritmo,
)

from tests.algoritmos.producao.algoritmo import AlgoritmoProducao


def main():
    versao_id = "2573b998-63d0-4471-ad85-db6f860c3721"

    print("=" * 80)
    print("🎯 VALIDAÇÃO COMPLETA - Versão 2573b998")
    print("=" * 80)

    # Baixar dados do Directus
    print(f"\n📡 Buscando versão {versao_id[:8]}... no Directus...")
    versao_data = baixar_versao_directus(versao_id)

    if not versao_data:
        print("❌ Erro ao baixar dados do Directus")
        return

    print("✅ Dados carregados!")

    # Extrair dados para o algoritmo
    dados = extrair_dados_para_algoritmo(versao_data)

    modificacoes_raw = dados["modificacoes"]
    tags_raw = dados["tags"]
    texto = dados["texto_completo"]

    print("\n📊 Dados extraídos:")
    print(f"   - Modificações: {len(modificacoes_raw)}")
    print(f"   - Tags: {len(tags_raw)}")
    print(f"   - Texto completo: {len(texto):,} caracteres")

    # Mostrar modificações
    print("\n" + "=" * 80)
    print("📋 MODIFICAÇÕES DETECTADAS")
    print("=" * 80)

    for i, mod in enumerate(modificacoes_raw, 1):
        print(f"\n{'─' * 80}")
        print(f"Modificação #{i}")
        print(f"{'─' * 80}")
        print(f"Tipo: {mod['tipo']}")
        print(f"ID: {mod['id'][:8]}...")

        # Extrair texto baseado na categoria
        conteudo = mod["conteudo"]
        if mod["tipo"] == "INSERCAO":
            texto_mod = conteudo.get("novo", "")
        elif mod["tipo"] == "REMOCAO":
            texto_mod = conteudo.get("original", "")
        else:  # ALTERACAO
            texto_mod = conteudo.get("novo", "")

        print(f"Tamanho: {len(texto_mod)} caracteres")
        if len(texto_mod) > 120:
            print(f"Conteúdo: {texto_mod[:120]}...")
        else:
            print(f"Conteúdo: {texto_mod}")

    # Encontrar tag 2.5.2
    print("\n" + "=" * 80)
    print("🏷️  TAG ALVO: 2.5.2")
    print("=" * 80)

    tag_252 = next((t for t in tags_raw if t["titulo"] == "2.5.2"), None)
    if tag_252:
        print(f"ID: {tag_252['id'][:8]}...")
        pos_inicio = tag_252.get("posicao_inicio")
        pos_fim = tag_252.get("posicao_fim")

        if pos_inicio and pos_fim:
            print(
                f"Posição: {pos_inicio:,} → {pos_fim:,} ({pos_fim - pos_inicio:,} chars)"
            )

            conteudo_tag = texto[pos_inicio:pos_fim]
            if len(conteudo_tag) > 200:
                print(f"\nConteúdo: {conteudo_tag[:200]}...")
            else:
                print(f"\nConteúdo: {conteudo_tag}")
        else:
            print("⚠️  Sem posições definidas")

    # Processar com algoritmo
    print("\n" + "=" * 80)
    print("🔬 PROCESSAMENTO COM ALGORITMO DE PRODUÇÃO")
    print("=" * 80)

    resultado = processar_com_algoritmo(AlgoritmoProducao, dados, verbose=True)

    print("\n" + "=" * 80)
    print("✅ RESULTADO DA VINCULAÇÃO")
    print("=" * 80)

    print("\n📊 Métricas finais:")
    print(f"   - Taxa de vinculação: {resultado['taxa_vinculacao']:.1f}%")
    print(
        f"   - Vinculadas: {resultado['vinculadas']}/{resultado['total_modificacoes']}"
    )
    print(f"   - Não vinculadas: {resultado['nao_vinculadas']}")

    # Analisar cada vinculação
    print("\n📋 Análise detalhada:")
    for i, mod_resultado in enumerate(resultado["resultado"], 1):
        tag_vinculada = mod_resultado.get("tag_vinculada")

        if tag_vinculada:
            if isinstance(tag_vinculada, dict):
                tag_id = tag_vinculada.get("id")
            else:
                tag_id = tag_vinculada

            tag = next((t for t in tags_raw if t["id"] == tag_id), None)
            tag_nome = tag["titulo"] if tag else "Desconhecida"

            print(f"\n   ✅ Vinculação #{i}:")
            print(f"      Tipo: {mod_resultado['tipo']}")
            print(f"      → Tag: {tag_nome}")

            # Calcular overlap se tiver posições
            if (
                mod_resultado.get("posicao_inicio")
                and tag
                and tag.get("posicao_inicio")
            ):
                mod_inicio = mod_resultado["posicao_inicio"]
                mod_fim = mod_resultado["posicao_fim"]
                tag_inicio = tag["posicao_inicio"]
                tag_fim = tag["posicao_fim"]

                # Calcular overlap
                inicio_intersecao = max(mod_inicio, tag_inicio)
                fim_intersecao = min(mod_fim, tag_fim)
                tamanho_intersecao = max(0, fim_intersecao - inicio_intersecao)
                tamanho_mod = mod_fim - mod_inicio

                if tamanho_mod > 0:
                    overlap = (tamanho_intersecao / tamanho_mod) * 100
                    print(f"      Overlap: {overlap:.1f}%")
                    print(f"      Mod pos: {mod_inicio:,} → {mod_fim:,}")
                    print(f"      Tag pos: {tag_inicio:,} → {tag_fim:,}")
        else:
            print(f"\n   ❌ Vinculação #{i}:")
            print(f"      Tipo: {mod_resultado['tipo']}")
            print("      Não vinculada")

    print("\n" + "=" * 80)
    print("🎉 VALIDAÇÃO CONCLUÍDA")
    print("=" * 80)

    if resultado["vinculadas"] == resultado["total_modificacoes"]:
        print("✅ 100% das modificações foram vinculadas com sucesso!")
        print("✅ Algoritmo funcionando perfeitamente após correção do overlap")
    else:
        print(
            f"⚠️  {resultado['vinculadas']}/{resultado['total_modificacoes']} modificações vinculadas"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()

    # Processar com algoritmo de produção
    print("\n🔬 Processando com algoritmo de produção...")
    algoritmo = AlgoritmoProducao()
    resultado = algoritmo.processar(modificacoes, tags, texto)

    print("\n" + "=" * 80)
    print("📋 MODIFICAÇÕES PROCESSADAS")
    print("=" * 80)

    for i, mod in enumerate(modificacoes, 1):
        print(f"\n{'─' * 80}")
        print(f"Modificação #{i}")
        print(f"{'─' * 80}")
        print(f"Categoria: {mod.categoria.value}")
        print(
            f"Posição: {mod.posicao_inicio:,} → {mod.posicao_fim:,} ({mod.posicao_fim - mod.posicao_inicio} chars)"
        )

        conteudo = mod.conteudo or mod.alteracao
        if len(conteudo) > 120:
            print(f"Conteúdo: {conteudo[:120]}...")
        else:
            print(f"Conteúdo: {conteudo}")

    print("\n" + "=" * 80)
    print("🏷️  TAG ALVO: 2.5.2")
    print("=" * 80)

    tag_252 = next((t for t in tags if t.tag_nome == "2.5.2"), None)
    if tag_252:
        print(f"ID Cláusula: {tag_252.clausula_id}")
        print(
            f"Posição: {tag_252.posicao_inicio:,} → {tag_252.posicao_fim:,} ({tag_252.posicao_fim - tag_252.posicao_inicio:,} chars)"
        )

        conteudo_tag = texto[tag_252.posicao_inicio : tag_252.posicao_fim]
        if len(conteudo_tag) > 200:
            print(f"\nConteúdo: {conteudo_tag[:200]}...")
        else:
            print(f"\nConteúdo: {conteudo_tag}")

    print("\n" + "=" * 80)
    print("✅ RESULTADO DA VINCULAÇÃO")
    print("=" * 80)

    print("\n📊 Métricas:")
    print(f"   - Taxa de sucesso: {resultado.taxa_sucesso():.1f}%")
    print(f"   - Taxa de cobertura: {resultado.taxa_cobertura():.1f}%")
    print(f"   - Vinculadas: {len(resultado.vinculadas)}")
    print(f"   - Revisão manual: {len(resultado.revisao_manual)}")
    print(f"   - Não vinculadas: {len(resultado.nao_vinculadas)}")

    print("\n📋 Detalhamento das vinculações:")
    for i, vinc in enumerate(resultado.vinculadas, 1):
        print(f"\n   ✅ Vinculação #{i}:")
        print(f"      Modificação: {vinc.modificacao.categoria.value}")
        conteudo = vinc.modificacao.conteudo or vinc.modificacao.alteracao
        if len(conteudo) > 80:
            print(f"      Conteúdo: {conteudo[:80]}...")
        else:
            print(f"      Conteúdo: {conteudo}")
        print(f"      → Tag: {vinc.clausula.tag_nome}")
        print(f"      Score fuzzy: {vinc.score_fuzzy:.1f}%")
        print(f"      Score overlap: {vinc.score_overlap:.1f}%")
        print(f"      Método: {vinc.metodo}")

    if resultado.revisao_manual:
        print("\n⚠️  Revisão manual necessária:")
        for vinc in resultado.revisao_manual:
            print(
                f"      - {vinc.modificacao.categoria.value}: {vinc.score_fuzzy:.1f}% fuzzy → {vinc.clausula.tag_nome}"
            )

    if resultado.nao_vinculadas:
        print("\n❌ Não vinculadas:")
        for mod in resultado.nao_vinculadas:
            print(f"      - {mod.categoria.value}: sem match")

    print("\n" + "=" * 80)
    print("🎉 VALIDAÇÃO CONCLUÍDA")
    print("=" * 80)

    if len(resultado.vinculadas) == len(modificacoes):
        print("✅ 100% das modificações foram vinculadas com sucesso!")
        print("✅ Algoritmo funcionando perfeitamente após correção do overlap")
    else:
        print(
            f"⚠️  {len(resultado.vinculadas)}/{len(modificacoes)} modificações vinculadas"
        )

    print("=" * 80)

if __name__ == "__main__":
    main()
