#!/usr/bin/env python3
"""
Script para mostrar os dados brutos da comparação de arquivos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processador_modelo_contrato import analyze_differences_detailed, html_to_text
import tempfile

def mostrar_dados_brutos_comparacao():
    """Mostra como são os dados brutos da comparação de arquivos"""

    print("🔍 Analisando dados brutos da comparação de arquivos...")
    print("=" * 80)

    # Criar conteúdo de texto simulando o processamento real
    original_text = """CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: Empresa ABC
CONTRATADA: Empresa XYZ

PREÂMBULO
Este contrato estabelece as condições gerais...

DEFINIÇÕES
Para fins deste contrato, consideram-se:

CLÁUSULA 1ª - OBJETO
O objeto deste contrato é...

CLÁUSULA 1.1 - ESPECIFICAÇÕES
As especificações técnicas...

CLÁUSULA 1.2 - PRAZO
O prazo de execução..."""

    tagged_text = """CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: {{contratante}}
CONTRATADA: {{contratada}}

{{preambulo}}
Este contrato estabelece as {{condicoes_gerais}}...

{{definicoes}}
Para fins deste contrato, consideram-se:

CLÁUSULA {{1}} - OBJETO
O objeto deste contrato é...

CLÁUSULA {{1.1}} - ESPECIFICAÇÕES
As especificações técnicas...

CLÁUSULA {{1.2}} - PRAZO
O prazo de execução..."""

    print("📄 TEXTO ORIGINAL:")
    print(original_text)

    print("\n" + "=" * 80)
    print("🏷️ TEXTO COM TAGS:")
    print(tagged_text)

    print("\n" + "=" * 80)
    print("🔍 EXECUTANDO COMPARAÇÃO...")

    # Analisar diferenças (esta é a função que realmente usamos)
    modificacoes = analyze_differences_detailed(original_text, tagged_text)

        print(f"\n📊 TOTAL DE MODIFICAÇÕES ENCONTRADAS: {len(modificacoes)}")
        print("=" * 80)

        for i, mod in enumerate(modificacoes):
            print(f"\n🔸 MODIFICAÇÃO {i}:")
            print(f"  • Categoria: {mod['categoria']}")
            print(f"  • Sort: {mod['sort']}")
            print(f"  • Conteúdo original: '{mod['conteudo']}'")
            print(f"  • Alteração: '{mod['alteracao']}'")
            print(f"  • Dados completos: {mod}")

        # Agora mostrar como extraímos as tags
        print("\n" + "=" * 80)
        print("🏷️ EXTRAÇÃO DE TAGS:")

        from processador_modelo_contrato import extract_tags_from_differences
        tags = extract_tags_from_differences(modificacoes)

        for tag in tags:
            print(f"\n🏷️ TAG: '{tag['nome']}'")
            print(f"  • Texto completo encontrado: '{tag['texto_completo']}'")
            print(f"  • Posição início: {tag['posicao_inicio']}")
            print(f"  • Posição fim: {tag['posicao_fim']}")
            print(f"  • Linha aproximada: {tag['linha_aproximada']}")
            print(f"  • Fonte: {tag['fonte']}")
            print(f"  • Índice modificação: {tag['modificacao_indice']}")
            print(f"  • Caminho início: {tag['caminho_tag_inicio']}")
            print(f"  • Caminho fim: {tag['caminho_tag_fim']}")
            print(f"  • Contexto: '{tag['contexto']}'")

    finally:
        # Limpar arquivos temporários
        os.unlink(arquivo_original)
        os.unlink(arquivo_com_tags)

if __name__ == "__main__":
    mostrar_dados_brutos_comparacao()
