#!/usr/bin/env python3
"""
Teste de vinculação de modificações às cláusulas - Cenário Realista

Este teste simula o cenário REAL do sistema:
- Modelo de contrato COM TAGS (arquivo processado)
- Versão do contrato SEM TAGS (arquivo derivado do modelo)
- Diff entre versão original e modificada
- Vinculação das modificações às cláusulas do modelo
"""

import os
import re
import sys

# Adicionar o diretório versiona-ai ao path
versiona_ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, versiona_ai_dir)

# Importação após ajuste do path
# ruff: noqa: E402
from directus_server import DirectusAPI


def test_cenario_realista():
    """
    Teste do cenário REAL do sistema:
    - Modelo COM tags
    - Versão SEM tags (texto limpo)
    - Modificações baseadas na versão SEM tags
    """
    print("\n" + "=" * 80)
    print("🧪 TESTE: Cenário Realista de Vinculação")
    print("=" * 80)

    # =============================================================================
    # FIXTURE 1: Modelo de contrato COM TAGS (como está salvo no Directus)
    # =============================================================================
    modelo_com_tags = """{{1}}
CLÁUSULA PRIMEIRA - DO OBJETO

O presente contrato tem por objeto a prestação de serviços de consultoria
em tecnologia da informação.
{{/1}}

{{2}}
CLÁUSULA SEGUNDA - DO VALOR

O valor total do contrato é de R$ 10.000,00 (dez mil reais), a ser pago
em duas parcelas iguais.
{{/2}}

{{3}}
CLÁUSULA TERCEIRA - DO PRAZO

O prazo de execução será de 30 (trinta) dias corridos, contados a partir
da assinatura do contrato.
{{/3}}"""

    print("\n📄 MODELO COM TAGS:")
    print(f"   Tamanho: {len(modelo_com_tags)} caracteres")
    pattern = r"{{\d+}}"
    print(f"   Número de tags: {len(re.findall(pattern, modelo_com_tags))}")

    # =============================================================================
    # FIXTURE 2: Versão do contrato (DERIVADA do modelo mas SEM TAGS)
    # =============================================================================
    versao_original = """CLÁUSULA PRIMEIRA - DO OBJETO

O presente contrato tem por objeto a prestação de serviços de consultoria
em tecnologia da informação.

CLÁUSULA SEGUNDA - DO VALOR

O valor total do contrato é de R$ 10.000,00 (dez mil reais), a ser pago
em duas parcelas iguais.

CLÁUSULA TERCEIRA - DO PRAZO

O prazo de execução será de 30 (trinta) dias corridos, contados a partir
da assinatura do contrato."""

    versao_modificada = """CLÁUSULA PRIMEIRA - DO OBJETO

O presente contrato tem por objeto a prestação de serviços de consultoria
em tecnologia da informação e análise de dados.

CLÁUSULA SEGUNDA - DO VALOR

O valor total do contrato é de R$ 15.000,00 (quinze mil reais), a ser pago
em três parcelas iguais.

CLÁUSULA TERCEIRA - DO PRAZO

O prazo de execução será de 60 (sessenta) dias corridos, contados a partir
da assinatura do contrato."""

    print("\n📄 VERSÃO DO CONTRATO:")
    print(f"   Original: {len(versao_original)} caracteres")
    print(f"   Modificada: {len(versao_modificada)} caracteres")
    print(f"   Diferença: {len(versao_modificada) - len(versao_original)} caracteres")

    # =============================================================================
    # FIXTURE 3: Tags do modelo (como viriam do Directus após processamento)
    # =============================================================================
    tags_modelo = [
        {
            "tag_nome": "1",
            "posicao_inicio_texto": 0,
            "posicao_fim_texto": modelo_com_tags.find("{{/1}}") + 6,
            "conteudo": "CLÁUSULA PRIMEIRA - DO OBJETO\n\nO presente contrato tem por objeto a prestação de serviços de consultoria\nem tecnologia da informação.",
            "clausulas": [
                {"id": "clausula-1-uuid", "numero": "1", "nome": "DO OBJETO"}
            ],
        },
        {
            "tag_nome": "2",
            "posicao_inicio_texto": modelo_com_tags.find("{{2}}"),
            "posicao_fim_texto": modelo_com_tags.find("{{/2}}") + 6,
            "conteudo": "CLÁUSULA SEGUNDA - DO VALOR\n\nO valor total do contrato é de R$ 10.000,00 (dez mil reais), a ser pago\nem duas parcelas iguais.",
            "clausulas": [{"id": "clausula-2-uuid", "numero": "2", "nome": "DO VALOR"}],
        },
        {
            "tag_nome": "3",
            "posicao_inicio_texto": modelo_com_tags.find("{{3}}"),
            "posicao_fim_texto": modelo_com_tags.find("{{/3}}") + 6,
            "conteudo": "CLÁUSULA TERCEIRA - DO PRAZO\n\nO prazo de execução será de 30 (trinta) dias corridos, contados a partir\nda assinatura do contrato.",
            "clausulas": [{"id": "clausula-3-uuid", "numero": "3", "nome": "DO PRAZO"}],
        },
    ]

    print("\n🏷️  TAGS DO MODELO:")
    for tag in tags_modelo:
        print(
            f"   Tag '{tag['tag_nome']}': pos {tag['posicao_inicio_texto']}-{tag['posicao_fim_texto']}"
        )
        print(
            f"      → Cláusula: {tag['clausulas'][0]['numero']} - {tag['clausulas'][0]['nome']}"
        )

    # =============================================================================
    # FIXTURE 4: Modificações extraídas do diff (baseadas na VERSÃO sem tags)
    # =============================================================================
    modificacoes = [
        {
            "id": 1,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "em tecnologia da informação.",
                "novo": "em tecnologia da informação e análise de dados.",
            },
        },
        {
            "id": 2,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "O valor total do contrato é de R$ 10.000,00 (dez mil reais), a ser pago\nem duas parcelas iguais.",
                "novo": "O valor total do contrato é de R$ 15.000,00 (quinze mil reais), a ser pago\nem três parcelas iguais.",
            },
        },
        {
            "id": 3,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "O prazo de execução será de 30 (trinta) dias corridos",
                "novo": "O prazo de execução será de 60 (sessenta) dias corridos",
            },
        },
    ]

    print("\n📝 MODIFICAÇÕES EXTRAÍDAS DO DIFF:")
    for mod in modificacoes:
        print(f"   Mod #{mod['id']}: {mod['tipo']}")
        if "original" in mod["conteudo"]:
            print(f"      Original: '{mod['conteudo']['original'][:50]}...'")
        print(f"      Novo: '{mod['conteudo']['novo'][:50]}...'")

    # =============================================================================
    # TESTE: Executar vinculação
    # =============================================================================
    print("\n🔗 EXECUTANDO VINCULAÇÃO...")
    print("   ⚠️  PROBLEMA ESPERADO:")
    print("   - Tags têm posições no MODELO COM TAGS")
    print("   - Modificações têm texto da VERSÃO SEM TAGS")
    print("   - Textos diferentes = posições incompatíveis!")

    processor = DirectusAPI()

    # Testar com modelo_com_tags (abordagem atual)
    modificacoes_vinculadas = processor._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=modelo_com_tags,
    )

    # =============================================================================
    # RESULTADOS
    # =============================================================================
    print("\n📊 RESULTADOS DA VINCULAÇÃO:")
    vinculadas = 0
    nao_vinculadas = 0

    for mod in modificacoes_vinculadas:
        if mod.get("clausula_id"):
            vinculadas += 1
            print(f"   ✅ Mod #{mod['id']} → Cláusula {mod.get('clausula_numero')}")
        else:
            nao_vinculadas += 1
            print(f"   ❌ Mod #{mod['id']} NÃO vinculada")

    print(f"\n📈 RESUMO: {vinculadas}/{len(modificacoes)} vinculadas")

    # =============================================================================
    # DIAGNÓSTICO DO PROBLEMA
    # =============================================================================
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO DO PROBLEMA")
    print("=" * 80)

    # Verificar se os textos das modificações existem no modelo COM tags
    print("\n1️⃣  VERIFICANDO SE TEXTOS DAS MODIFICAÇÕES EXISTEM NO MODELO COM TAGS:")
    for mod in modificacoes:
        texto = mod["conteudo"].get("original") or mod["conteudo"].get("novo")
        if modelo_com_tags.find(texto) >= 0:
            print(f"   ✅ Mod #{mod['id']}: texto ENCONTRADO no modelo com tags")
        else:
            print(f"   ❌ Mod #{mod['id']}: texto NÃO ENCONTRADO no modelo com tags")

    # Remover tags do modelo e tentar novamente
    print("\n2️⃣  REMOVENDO TAGS DO MODELO:")
    modelo_sem_tags = re.sub(r"\{\{/?[\w.-]+\}\}", "", modelo_com_tags).strip()

    # Normalizar espaços
    modelo_sem_tags = re.sub(r"\n\n+", "\n\n", modelo_sem_tags)

    print(f"   Modelo original: {len(modelo_com_tags)} caracteres")
    print(f"   Modelo sem tags: {len(modelo_sem_tags)} caracteres")
    print(
        f"   Tags removidas: {len(modelo_com_tags) - len(modelo_sem_tags)} caracteres"
    )

    print("\n3️⃣  VERIFICANDO SE TEXTOS EXISTEM NO MODELO SEM TAGS:")
    for mod in modificacoes:
        texto = mod["conteudo"].get("original") or mod["conteudo"].get("novo")
        if modelo_sem_tags.find(texto) >= 0:
            pos = modelo_sem_tags.find(texto)
            print(f"   ✅ Mod #{mod['id']}: ENCONTRADO na posição {pos}")
        else:
            print(f"   ❌ Mod #{mod['id']}: ainda não encontrado")
            # Tentar busca parcial
            texto_parcial = texto[:50]
            if modelo_sem_tags.find(texto_parcial) >= 0:
                pos = modelo_sem_tags.find(texto_parcial)
                print(f"      (parcial encontrado na posição {pos})")

    print("\n4️⃣  COMPARANDO MODELO SEM TAGS vs VERSÃO ORIGINAL:")
    if modelo_sem_tags == versao_original:
        print("   ✅ IGUAIS! Modelo sem tags = Versão original")
    else:
        print("   ⚠️  DIFERENTES!")
        print(f"      Modelo sem tags: {len(modelo_sem_tags)} chars")
        print(f"      Versão original: {len(versao_original)} chars")
        print(
            f"      Diferença: {abs(len(modelo_sem_tags) - len(versao_original))} chars"
        )

        # Mostrar primeiros caracteres diferentes
        for i, (c1, c2) in enumerate(
            zip(modelo_sem_tags, versao_original, strict=False)
        ):
            if c1 != c2:
                print(f"      Primeira diferença no char {i}:")
                print(f"         Modelo: '{modelo_sem_tags[max(0, i - 20) : i + 20]}'")
                print(f"         Versão: '{versao_original[max(0, i - 20) : i + 20]}'")
                break

    # =============================================================================
    # CONCLUSÕES E PRÓXIMOS PASSOS
    # =============================================================================
    print("\n" + "=" * 80)
    print("💡 CONCLUSÕES")
    print("=" * 80)

    print("\n📌 PROBLEMA IDENTIFICADO:")
    print("   1. Tags do modelo têm posições no texto COM TAGS")
    print("   2. Modificações têm texto da versão SEM TAGS")
    print("   3. Remover tags do modelo altera as posições de tudo")
    print("   4. Não há como mapear posições entre os dois textos diretamente")

    print("\n🎯 POSSÍVEIS SOLUÇÕES:")
    print("   A) Usar algoritmo de diff/alinhamento de texto (complexo)")
    print("   B) Buscar texto das modificações no modelo sem tags")
    print("      e mapear de volta para as tags (aproximação)")
    print("   C) Processar versão COM TAGS também (ideal mas requer mudança)")

    print("\n🔧 PRÓXIMOS PASSOS:")
    print("   1. Implementar solução B (busca + mapeamento)")
    print("   2. Testar com dados reais")
    print("   3. Avaliar precisão da vinculação")

    print("\n" + "=" * 80)

    return vinculadas, nao_vinculadas


if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTE DE CENÁRIO REALISTA\n")

    try:
        vinculadas, nao_vinculadas = test_cenario_realista()

        print(
            f"\n📊 RESULTADO FINAL: {vinculadas} vinculadas, {nao_vinculadas} não vinculadas"
        )

        if vinculadas > 0:
            print("\n✅ Teste concluído com SUCESSO PARCIAL")
            print("   (Algumas modificações foram vinculadas)")
        else:
            print("\n⚠️  Teste concluído mas NENHUMA vinculação foi feita")
            print("   (Era esperado - demonstra o problema)")

        sys.exit(0)

    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
