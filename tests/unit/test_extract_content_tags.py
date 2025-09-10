#!/usr/bin/env python3
"""
Teste para verificar a extração de conteúdo entre tags
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.docx_compare.processors.processador_modelo_contrato import (
    extract_content_between_tags,
)


def test_extract_content_basic():
    """Teste básico de extração de conteúdo entre tags"""
    print("🧪 Testando extração de conteúdo entre tags...")

    # Texto de exemplo com tags no formato da documentação
    texto_exemplo = """
    Este é o início do documento.

    {{TAG-responsavel}}
    Nome: João Silva
    E-mail: joao.silva@empresa.com
    Cargo: Gerente de Projeto
    {{/TAG-responsavel}}

    Continuação do documento...

    {{TAG-cabecalho}}
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    Número: 2025-001
    {{/TAG-cabecalho}}

    Mais conteúdo do documento.

    {{TAG-valor}}
    R$ 50.000,00 (cinquenta mil reais)
    {{/TAG-valor}}

    Também testando formato alternativo:

    {{endereco}}
    Rua das Flores, 123
    Bairro Centro - São Paulo/SP
    CEP: 01234-567
    {{/endereco}}
    """

    # Testar extração
    result = extract_content_between_tags(texto_exemplo)

    print("📊 Resultado da extração:")
    print(f"   Encontradas {len(result)} tags com conteúdo")

    for tag_name, content in result.items():
        print(f"   🏷️  '{tag_name}': {content[:50]}{'...' if len(content) > 50 else ''}")

    # Verificações esperadas
    expected_tags = {"responsavel", "cabecalho", "valor", "endereco"}
    found_tags = set(result.keys())

    print("\n🔍 Verificação:")
    print(f"   Tags esperadas: {sorted(expected_tags)}")
    print(f"   Tags encontradas: {sorted(found_tags)}")

    missing = expected_tags - found_tags
    extra = found_tags - expected_tags

    if missing:
        print(f"   ❌ Tags faltando: {sorted(missing)}")
    if extra:
        print(f"   ⚠️  Tags extras: {sorted(extra)}")

    if not missing and not extra:
        print("   ✅ Todas as tags esperadas foram encontradas!")

    # Verificar conteúdo específico
    if "responsavel" in result:
        responsavel_content = result["responsavel"]
        if (
            "João Silva" in responsavel_content
            and "joao.silva@empresa.com" in responsavel_content
        ):
            print("   ✅ Conteúdo da tag 'responsavel' está correto")
        else:
            print("   ❌ Conteúdo da tag 'responsavel' não está correto")

    # Verificações com assert para pytest
    assert len(result) > 0, "Nenhuma tag foi extraída"
    assert "responsavel" in result, "Tag 'responsavel' não foi encontrada"


def test_extract_content_edge_cases():
    """Teste para casos especiais"""
    print("\n🧪 Testando casos especiais...")

    # Teste com tags não fechadas
    texto_incompleto = """
    {{inicio}}
    Conteúdo sem fechamento

    {{TAG-completa}}
    Conteúdo completo
    {{/TAG-completa}}
    """

    result = extract_content_between_tags(texto_incompleto)
    print(f"📊 Tags incompletas: {len(result)} encontradas")
    for tag_name, content in result.items():
        print(f"   🏷️  '{tag_name}': {content[:30]}...")

    # Teste com tags aninhadas
    texto_aninhado = """
    {{externo}}
    Conteúdo externo
    {{interno}}
    Conteúdo interno
    {{/interno}}
    Mais conteúdo externo
    {{/externo}}
    """

    result_nested = extract_content_between_tags(texto_aninhado)
    print(f"📊 Tags aninhadas: {len(result_nested)} encontradas")
    for tag_name, content in result_nested.items():
        print(f"   🏷️  '{tag_name}': {content[:50]}...")


if __name__ == "__main__":
    test_extract_content_basic()
    test_extract_content_edge_cases()
    print("\n✅ Testes concluídos!")
