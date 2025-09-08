#!/usr/bin/env python3
"""
Testes para o processador de modelo de contrato
"""

import sys
import os

# Adicionar o diretório raiz ao path para importar o processador
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processador_modelo_contrato import extract_tags_from_differences


def test_extract_tags_basic():
    """Testa extração básica de tags"""
    print("🧪 Teste: Extração básica de tags")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Este é o {{cabecalho}} do documento",
            "sort": 1
        },
        {
            "categoria": "modificacao",
            "conteudo": "Texto original",
            "alteracao": "Texto com {{nome_cliente}} modificado",
            "sort": 2
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag['nome'] for tag in tags_info}
    expected_tags = {"cabecalho", "nome_cliente"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    # Verificar se tem informações de caminho
    for tag_info in tags_info:
        assert 'caminho_tag_inicio' in tag_info, "Tag deve ter caminho_tag_inicio"
        assert 'caminho_tag_fim' in tag_info, "Tag deve ter caminho_tag_fim"

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_with_spaces():
    """Testa extração de tags com espaços"""
    print("🧪 Teste: Tags com espaços")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{ cabecalho }} e {{ data_atual }}",
            "sort": 1
        }
    ]

    tags = extract_tags_from_differences(modifications)
    expected_tags = {"cabecalho", "data_atual"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_self_closing():
    """Testa extração de tags auto-fechadas"""
    print("🧪 Teste: Tags auto-fechadas")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Insira {{linha /}} aqui e {{quebra_pagina /}} também",
            "sort": 1
        }
    ]

    tags = extract_tags_from_differences(modifications)
    expected_tags = {"linha", "quebra_pagina"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_closing():
    """Testa extração de tags de fechamento"""
    print("🧪 Teste: Tags de fechamento")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{inicio_secao}} conteúdo {{/inicio_secao}}",
            "sort": 1
        }
    ]

    tags = extract_tags_from_differences(modifications)
    expected_tags = {"inicio_secao"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_mixed():
    """Testa extração de tags com múltiplos padrões"""
    print("🧪 Teste: Múltiplos padrões de tags")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{cabecalho}} texto {{ nome_cliente }} mais {{linha /}} e {{inicio}} ... {{/inicio}}",
            "sort": 1
        },
        {
            "categoria": "modificacao",
            "conteudo": "Texto original {{old_tag}}",
            "alteracao": "Texto modificado {{ new_tag }}",
            "sort": 2
        }
    ]

    tags = extract_tags_from_differences(modifications)
    expected_tags = {"cabecalho", "nome_cliente", "linha", "inicio", "old_tag", "new_tag"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_no_tags():
    """Testa quando não há tags"""
    print("🧪 Teste: Sem tags")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Texto normal sem tags",
            "sort": 1
        }
    ]

    tags = extract_tags_from_differences(modifications)
    expected_tags = set()

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_invalid_patterns():
    """Testa padrões inválidos que não devem ser capturados"""
    print("🧪 Teste: Padrões inválidos")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{tag} {{}} {{123tag}} {{tag-with-dash}} texto {{{triplo}}}",
            "sort": 1
        }
    ]

    tags = extract_tags_from_differences(modifications)
    expected_tags = set()  # Nenhuma tag válida nesses padrões

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_case_insensitive():
    """Testa se a extração é case-insensitive"""
    print("🧪 Teste: Case insensitive")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{CABECALHO}} {{Nome_Cliente}} {{data_ATUAL}}",
            "sort": 1
        }
    ]

    tags = extract_tags_from_differences(modifications)
    expected_tags = {"cabecalho", "nome_cliente", "data_atual"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Executando testes do processador de modelo de contrato...\n")

    tests = [
        test_extract_tags_basic,
        test_extract_tags_with_spaces,
        test_extract_tags_self_closing,
        test_extract_tags_closing,
        test_extract_tags_mixed,
        test_extract_tags_no_tags,
        test_extract_tags_invalid_patterns,
        test_extract_tags_case_insensitive
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"   ❌ Teste falhou: {e}")
            failed += 1

    print("📊 Resumo dos testes:")
    print(f"   ✅ Passou: {passed}")
    print(f"   ❌ Falhou: {failed}")
    print(f"   📋 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 Todos os testes passaram!")
        return True
    else:
        print(f"\n⚠️ {failed} teste(s) falharam!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
