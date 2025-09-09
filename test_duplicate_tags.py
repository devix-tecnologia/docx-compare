#!/usr/bin/env python3
"""
Teste para validar extração de conteúdo com tags duplicadas.
Segunda ocorrência da mesma tag é considerada como fechamento.
"""

import sys
import os
sys.path.append('/home/joris/repositorio/devix/docx-compare/src')

from docx_compare.processors.processador_modelo_contrato import extract_content_between_tags

def test_duplicate_tags_extraction():
    """Teste com tags duplicadas como fechamento"""

    # Simular conteúdo HTML com tags duplicadas
    html_content = """
    <p>Início do documento</p>

    <p>{{preambulo}}</p>
    <p>Este é o conteúdo do preâmbulo com informações importantes sobre o contrato.</p>
    <p>{{preambulo}}</p>

    <p>Outras informações</p>

    <p>{{1}}</p>
    <p>CLÁUSULA 1ª. OBJETIVO</p>
    <p>Este contrato tem por objeto...</p>
    <p>{{1}}</p>

    <p>{{1.1}}</p>
    <p>1.1. O presente CONTRATO tem por objeto a prestação de serviços de inserir 'Serviços' a serem prestados em inserir.</p>
    <p>{{1.1}}</p>

    <p>{{2}}</p>
    <p>CLÁUSULA 2ª. PRAZO</p>
    <p>O prazo de vigência será de...</p>
    <p>{{2}}</p>

    <p>Final do documento</p>
    """

    print("🔍 Testando extração de conteúdo com tags duplicadas...")
    print("=" * 60)

    # Chamar função de extração
    resultado = extract_content_between_tags(html_content)

    print(f"\n✅ Resultado da extração ({len(resultado)} tags encontradas):")
    print("=" * 60)

    for tag, conteudo in resultado.items():
        print(f"🏷️  Tag: '{tag}'")
        print(f"   📄 Conteúdo: {conteudo}")
        print(f"   📏 Tamanho: {len(conteudo)} caracteres")
        print()

    # Validar resultados esperados
    tags_esperadas = ['preambulo', '1', '1.1', '2']

    print("🧪 Validação dos resultados:")
    print("=" * 60)

    for tag in tags_esperadas:
        if tag in resultado:
            print(f"✅ Tag '{tag}' encontrada com conteúdo")
        else:
            print(f"❌ Tag '{tag}' NÃO encontrada")

    # Verificar conteúdos específicos
    validacoes = {
        'preambulo': 'Este é o conteúdo do preâmbulo',
        '1': 'CLÁUSULA 1ª. OBJETIVO',
        '1.1': '1.1. O presente CONTRATO tem por objeto',
        '2': 'CLÁUSULA 2ª. PRAZO'
    }

    print("\n🔍 Validação de conteúdos específicos:")
    print("=" * 60)

    for tag, texto_esperado in validacoes.items():
        if tag in resultado:
            if texto_esperado in resultado[tag]:
                print(f"✅ Tag '{tag}' contém texto esperado: '{texto_esperado}'")
            else:
                print(f"⚠️  Tag '{tag}' não contém texto esperado: '{texto_esperado}'")
                print(f"   Conteúdo atual: {resultado[tag][:100]}...")
        else:
            print(f"❌ Tag '{tag}' não foi extraída")

    return resultado

if __name__ == "__main__":
    resultado = test_duplicate_tags_extraction()

    if len(resultado) > 0:
        print(f"\n🎉 Sucesso! {len(resultado)} tags extraídas com sucesso!")
    else:
        print("\n❌ Falha! Nenhuma tag foi extraída.")
