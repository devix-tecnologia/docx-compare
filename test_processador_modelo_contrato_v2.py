#!/usr/bin/env python3
"""
Testes atualizados para o processador de modelo de contrato (versão v2)
Incluindo suporte para tags numéricas e campos de caminho
"""

import sys
import os

# Adicionar o diretório raiz ao path para importar o processador
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processador_modelo_contrato import extract_tags_from_differences


def test_extract_tags_basic():
    """Testa extração básica de tags textuais"""
    print("🧪 Teste: Extração básica de tags textuais")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Este é o {{preambulo}} do documento",
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
    expected_tags = {"preambulo", "nome_cliente"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    # Verificar se tem informações de caminho
    for tag_info in tags_info:
        assert 'caminho_tag_inicio' in tag_info, "Tag deve ter caminho_tag_inicio"
        assert 'caminho_tag_fim' in tag_info, "Tag deve ter caminho_tag_fim"
        assert 'nome' in tag_info, "Tag deve ter nome"
        assert 'contexto' in tag_info, "Tag deve ter contexto"

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_numeric():
    """Testa extração de tags numéricas"""
    print("🧪 Teste: Extração de tags numéricas")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Cláusula {{1}} - Objeto do contrato",
            "sort": 1
        },
        {
            "categoria": "modificacao",
            "conteudo": "Item 1",
            "alteracao": "Item {{1.1}} - Primeiro subitem",
            "sort": 2
        },
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Subitem {{1.2.3}} detalhado",
            "sort": 3
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag['nome'] for tag in tags_info}
    expected_tags = {"1", "1.1", "1.2.3"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_mixed():
    """Testa extração de tags mistas (textuais + numéricas)"""
    print("🧪 Teste: Extração de tags mistas")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{preambulo}} seguido da cláusula {{1}} e {{condicoes_gerais}}",
            "sort": 1
        },
        {
            "categoria": "modificacao",
            "conteudo": "Texto original",
            "alteracao": "Item {{1.1}} com {{definicoes}} incluídas",
            "sort": 2
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag['nome'] for tag in tags_info}
    expected_tags = {"preambulo", "1", "condicoes_gerais", "1.1", "definicoes"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

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
            "alteracao": "{{ preambulo }} e {{ 1 }} com espaços",
            "sort": 1
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag['nome'] for tag in tags_info}
    expected_tags = {"preambulo", "1"}

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
            "alteracao": "Insira {{1 /}} aqui e {{preambulo /}} também",
            "sort": 1
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag['nome'] for tag in tags_info}
    expected_tags = {"1", "preambulo"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_tag_info_structure():
    """Testa estrutura das informações das tags"""
    print("🧪 Teste: Estrutura das informações das tags")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Teste com {{1}} e {{preambulo}} para verificar estrutura",
            "sort": 1
        }
    ]

    tags_info = extract_tags_from_differences(modifications)

    required_fields = [
        'nome', 'texto_completo', 'posicao_inicio', 'posicao_fim',
        'contexto', 'fonte', 'linha_aproximada', 'modificacao_indice',
        'caminho_tag_inicio', 'caminho_tag_fim'
    ]

    for tag_info in tags_info:
        for field in required_fields:
            assert field in tag_info, f"Tag deve ter campo '{field}'"

        # Verificar tipos esperados
        assert isinstance(tag_info['nome'], str), "nome deve ser string"
        assert isinstance(tag_info['posicao_inicio'], int), "posicao_inicio deve ser int"
        assert isinstance(tag_info['posicao_fim'], int), "posicao_fim deve ser int"
        assert isinstance(tag_info['linha_aproximada'], int), "linha_aproximada deve ser int"

        print(f"   Tag '{tag_info['nome']}':")
        print(f"     Caminho início: {tag_info['caminho_tag_inicio']}")
        print(f"     Caminho fim: {tag_info['caminho_tag_fim']}")
        print(f"     Contexto: {tag_info['contexto'][:50]}...")

    print("   ✅ Teste passou!")
    print()


def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Executando todos os testes do processador v2...")
    print("=" * 50)

    test_functions = [
        test_extract_tags_basic,
        test_extract_tags_numeric,
        test_extract_tags_mixed,
        test_extract_tags_with_spaces,
        test_extract_tags_self_closing,
        test_tag_info_structure,
    ]

    passed = 0
    total = len(test_functions)

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ Teste {test_func.__name__} falhou: {e}")
            print()

    print("=" * 50)
    print(f"📊 Resultado: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 Todos os testes passaram!")
        return True
    else:
        print("❌ Alguns testes falharam!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
