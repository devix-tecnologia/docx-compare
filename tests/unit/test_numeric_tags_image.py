#!/usr/bin/env python3
"""
Teste baseado na imagem fornecida para validar extração de conteúdo de tags numéricas
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.docx_compare.processors.processador_modelo_contrato import (
    extract_content_between_tags,
)


def test_numeric_tags_from_image():
    """Teste baseado no exemplo da imagem fornecida"""
    print("🧪 Testando extração de tags numéricas baseado na imagem...")

    # Simular o conteúdo do documento baseado na imagem
    documento_exemplo = """
    Início do documento...

    {{1}}
    CLÁUSULA 1ª. OBJETIVO

    1.1. A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no
    campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste
    CONTRATO.
    {{/1}}

    {{1.1}}
    A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no
    campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste
    CONTRATO.
    {{/1.1}}

    {{1.2}}
    Este CONTRATO não implica em nenhum dever de exclusividade da CONTRATANTE, que poderá
    firmar contratos com outras empresas para os mesmos fins, de acordo com os seus interesses.
    {{/1.2}}

    {{1.3}}
    Os ANEXOS "Documentos Contratuais Gerais" ficam dispensados de rubrica ou validação digital
    quando A CONTRATADA declara que os recebe por ANEXOS; prevalecem em vigor desde
    outra forma de acesso, que tem ciência do seu conteúdo e que concorda com os termos neles contidos,
    comprometendo-se a cumprir-los na sua integralidade.
    {{/1.3}}
    """

    # Testar extração
    result = extract_content_between_tags(documento_exemplo)

    print("📊 Resultado da extração:")
    print(f"   Encontradas {len(result)} tags com conteúdo")

    # Verificar tag específica mencionada
    if "1" in result:
        conteudo_tag1 = result["1"]
        print(f"✅ Conteúdo da tag {{1}}: {conteudo_tag1[:50]}...")
        print(f"   Conteúdo completo: {repr(conteudo_tag1)}")

        # Verificar se contém "CLÁUSULA 1ª. OBJETIVO" como esperado
        if "CLÁUSULA 1ª. OBJETIVO" in conteudo_tag1:
            print("✅ Conteúdo da tag {{1}} contém 'CLÁUSULA 1ª. OBJETIVO' como esperado")
        else:
            print("❌ Conteúdo da tag {{1}} NÃO contém 'CLÁUSULA 1ª. OBJETIVO'")
    else:
        print("❌ Tag {{1}} não foi encontrada")

    # Verificar outras tags
    expected_tags = ["1", "1.1", "1.2", "1.3"]
    for tag in expected_tags:
        if tag in result:
            content_preview = result[tag][:80].replace("\n", " ").strip()
            print(f"🏷️  Tag {{{{ {tag} }}}}: {content_preview}...")
        else:
            print(f"❌ Tag {{{{ {tag} }}}} não encontrada")

    return result

def test_edge_cases_numeric():
    """Teste para casos especiais com tags numéricas"""
    print("\n🧪 Testando casos especiais com tags numéricas...")

    # Teste com espaços
    texto_com_espacos = """
    {{ 2 }}
    Conteúdo da seção 2 com espaços
    {{ /2 }}

    {{3.1 }}
    Subseção 3.1 com espaço após
    {{/3.1}}
    """

    result = extract_content_between_tags(texto_com_espacos)
    print(f"📊 Tags com espaços: {len(result)} encontradas")
    for tag_name, content in result.items():
        print(f"   🏷️  '{tag_name}': {content[:30].replace(chr(10), ' ')}...")

if __name__ == "__main__":
    # Ativar modo verbose
    import src.docx_compare.processors.processador_modelo_contrato as processador_module
    processador_module.verbose_mode = True

    result = test_numeric_tags_from_image()
    test_edge_cases_numeric()
    print(f"\n✅ Testes concluídos! Total de tags extraídas: {len(result)}")
