#!/usr/bin/env python3
"""
Testes para o processador de modelo de contrato
"""

import os
import sys

# Adicionar o diretório versiona-ai ao path ANTES de importar
versiona_ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, versiona_ai_dir)

# Importação após ajuste do path (necessário para encontrar o módulo)
# ruff: noqa: E402
from processador_tags_modelo import ProcessadorTagsModelo  # type: ignore


# Helper para extrair tags usando o novo processador
def extract_tags_from_differences(modifications):
    """Extrai tags usando o ProcessadorTagsModelo"""
    processador = ProcessadorTagsModelo("https://test.com", "fake-token")
    return processador._extrair_tags(modifications)


def test_extract_tags_basic():
    """Testa extração básica de tags"""
    print("🧪 Teste: Extração básica de tags")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Este é o {{cabecalho}} do documento",
            "sort": 1,
        },
        {
            "categoria": "modificacao",
            "conteudo": "Texto original",
            "alteracao": "Texto com {{nome_cliente}} modificado",
            "sort": 2,
        },
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
    expected_tags = {"cabecalho", "nome_cliente"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    # Verificar se tem informações de caminho
    for tag_info in tags_info:
        assert "caminho_tag_inicio" in tag_info, "Tag deve ter caminho_tag_inicio"
        assert "caminho_tag_fim" in tag_info, "Tag deve ter caminho_tag_fim"

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
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
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
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
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
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
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
            "sort": 1,
        },
        {
            "categoria": "modificacao",
            "conteudo": "Texto original {{old_tag}}",
            "alteracao": "Texto modificado {{ new_tag }}",
            "sort": 2,
        },
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
    expected_tags = {
        "cabecalho",
        "nome_cliente",
        "linha",
        "inicio",
        "old_tag",
        "new_tag",
    }

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
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
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
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
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
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
    expected_tags = {"cabecalho", "nome_cliente", "data_atual"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_numeric():
    """Testa extração de tags numéricas que envolvem conteúdo de cláusulas"""
    print("🧪 Teste: Tags numéricas")

    modifications = [
        {
            "categoria": "modificacao",
            "conteudo": "Cláusula 6\nlorem lorem lorem e subcláusula 7.4 e 10.1.2",
            "alteracao": "{{6}}Cláusula 6\nlorem lorem lorem{{/6}} e subcláusula {{7.4}}texto da 7.4{{/7.4}} e {{10.1.2}}texto{{/10.1.2}}",
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
    expected_tags = {"6", "7.4", "10.1.2"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_tags_with_prefix():
    """Testa extração de tags com prefixo TAG-"""
    print("🧪 Teste: Tags com prefixo TAG-")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{TAG-cabecalho}} e {{TAG-rodape}} no documento",
            "sort": 1,
        }
    ]

    tags_info = extract_tags_from_differences(modifications)
    tags = {tag["nome"] for tag in tags_info}
    expected_tags = {"cabecalho", "rodape"}

    print(f"   Tags encontradas: {sorted(tags)}")
    print(f"   Tags esperadas: {sorted(expected_tags)}")

    assert tags == expected_tags, f"Esperado {expected_tags}, obtido {tags}"
    print("   ✅ Teste passou!")
    print()


def test_extract_content_between_tags():
    """Testa extração de conteúdo entre tags de abertura/fechamento"""
    print("🧪 Teste: Conteúdo entre tags")

    processador = ProcessadorTagsModelo("https://test.com", "fake-token")

    texto = """
    {{TAG-secao1}}
    Este é o conteúdo da seção 1
    Com múltiplas linhas
    {{/TAG-secao1}}

    {{6}}
    Conteúdo da cláusula 6
    {{/6}}

    {{nome}}
    Conteúdo da tag nome
    {{/nome}}
    """

    conteudo_map = processador._extrair_conteudo_entre_tags(texto)

    print(f"   Tags com conteúdo: {sorted(conteudo_map.keys())}")

    # Verificar se as 3 tags foram encontradas
    expected_tags = {"secao1", "6", "nome"}
    found_tags = set(conteudo_map.keys())

    assert found_tags == expected_tags, f"Esperado {expected_tags}, obtido {found_tags}"

    # Verificar se o conteúdo foi extraído
    for tag_name, conteudo in conteudo_map.items():
        assert conteudo, f"Tag {tag_name} deveria ter conteúdo"
        assert "{{" not in conteudo, "Conteúdo NÃO deve incluir tags de abertura"
        assert "}}" not in conteudo, "Conteúdo NÃO deve incluir tags de fechamento"
        print(f"   ✓ Tag '{tag_name}' tem {len(conteudo)} caracteres de conteúdo")

    print("   ✅ Teste passou!")
    print()


def test_extract_content_real_document():
    """Testa extração de conteúdo com dados reais do documento"""
    print("🧪 Teste: Conteúdo de documento real")

    processador = ProcessadorTagsModelo("https://test.com", "fake-token")

    # Conteúdo real extraído do arquivo com tags do modelo
    texto = """{{1.1}}

1.  O CONTRATO tem por objeto a execução, pela EMPREITEIRA, das obras
    descritas no QUADRO RESUMO, conforme especificações detalhadas no
    Memorial Descritivo, parte integrante deste instrumento.

{{/1.1}}

Texto intermediário sem tag

{{7.4}}
A EMPREITEIRA obriga-se a executar os serviços de acordo com as normas
técnicas aplicáveis e seguindo as melhores práticas de engenharia.
{{/7.4}}

{{10.1.2}}
O prazo para conclusão das obras será de 180 dias contados da data
de emissão da Ordem de Serviço.
{{/10.1.2}}"""

    conteudo_map = processador._extrair_conteudo_entre_tags(texto)

    print(f"   Tags com conteúdo: {sorted(conteudo_map.keys())}")

    # Verificar se as 3 tags foram encontradas
    expected_tags = {"1.1", "7.4", "10.1.2"}
    found_tags = set(conteudo_map.keys())

    assert found_tags == expected_tags, f"Esperado {expected_tags}, obtido {found_tags}"

    # Verificar conteúdo específico de cada tag (removendo espaços/quebras para comparação)
    conteudo_1_1 = conteudo_map["1.1"].replace("\n", " ").replace("  ", " ")
    assert "O CONTRATO tem por objeto" in conteudo_1_1, (
        "Tag 1.1 deve conter texto esperado"
    )
    assert "execução, pela EMPREITEIRA" in conteudo_1_1, (
        "Tag 1.1 deve conter texto esperado"
    )

    conteudo_7_4 = conteudo_map["7.4"].replace("\n", " ").replace("  ", " ")
    assert "normas" in conteudo_7_4 and "técnicas" in conteudo_7_4, (
        "Tag 7.4 deve conter texto esperado"
    )
    assert "melhores práticas" in conteudo_7_4, "Tag 7.4 deve conter texto esperado"

    conteudo_10_1_2 = conteudo_map["10.1.2"].replace("\n", " ").replace("  ", " ")
    assert "180 dias" in conteudo_10_1_2, "Tag 10.1.2 deve conter texto esperado"
    assert "Ordem de Serviço" in conteudo_10_1_2, (
        "Tag 10.1.2 deve conter texto esperado"
    )

    # Verificar que NÃO inclui as tags no conteúdo
    for tag_name, conteudo in conteudo_map.items():
        assert f"{{{{{tag_name}}}}}" not in conteudo, (
            f"Conteúdo NÃO deve incluir tag de abertura {{{{{tag_name}}}}}"
        )
        assert f"{{{{/{tag_name}}}}}" not in conteudo, (
            f"Conteúdo NÃO deve incluir tag de fechamento {{{{/{tag_name}}}}}"
        )
        print(
            f"   ✓ Tag '{tag_name}' tem {len(conteudo)} caracteres de conteúdo válido"
        )

    print("   ✅ Teste passou!")
    print()


def test_extract_content_orphan_tags():
    """Testa que tags órfãs (sem par) são desconsideradas"""
    print("🧪 Testando descarte de tags órfãs...")

    processador = ProcessadorTagsModelo(
        directus_base_url="http://test.com", directus_token="test_token"
    )

    # Documento com tags órfãs
    texto = """
    Documento de teste com tags órfãs

    {{1.1}}
    Conteúdo válido da tag 1.1 com abertura e fechamento
    {{/1.1}}

    {{/7.4}}
    Esta tag só tem fechamento, sem abertura - deve ser descartada

    {{7.10}}
    Esta tag só tem abertura, sem fechamento - deve ser descartada

    {{2.5}}
    Conteúdo válido da tag 2.5 com ambas as tags
    {{/2.5}}

    {{/710}}
    Outra tag órfã apenas com fechamento

    {{3.1}}
    Mais um conteúdo válido
    {{/3.1}}
    """

    conteudo_map = processador._extrair_conteudo_entre_tags(texto)

    # Verificar que apenas tags válidas foram extraídas
    assert len(conteudo_map) == 3, f"Deve extrair 3 tags válidas, extraiu {len(conteudo_map)}"

    # Tags válidas devem estar presentes
    assert "1.1" in conteudo_map, "Tag 1.1 (válida) deve estar presente"
    assert "2.5" in conteudo_map, "Tag 2.5 (válida) deve estar presente"
    assert "3.1" in conteudo_map, "Tag 3.1 (válida) deve estar presente"

    # Tags órfãs NÃO devem estar presentes
    assert "7.4" not in conteudo_map, "Tag 7.4 (órfã - só fechamento) NÃO deve estar presente"
    assert "7.10" not in conteudo_map, "Tag 7.10 (órfã - só abertura) NÃO deve estar presente"
    assert "710" not in conteudo_map, "Tag 710 (órfã - só fechamento) NÃO deve estar presente"

    # Verificar conteúdo das tags válidas
    assert "Conteúdo válido da tag 1.1" in conteudo_map["1.1"]
    assert "Conteúdo válido da tag 2.5" in conteudo_map["2.5"]
    assert "Mais um conteúdo válido" in conteudo_map["3.1"]

    print(f"   ✓ Tags válidas extraídas: {sorted(conteudo_map.keys())}")
    print("   ✓ Tags órfãs corretamente descartadas: 7.4, 7.10, 710")
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
        test_extract_tags_case_insensitive,
        test_extract_tags_numeric,
        test_extract_tags_with_prefix,
        test_extract_content_between_tags,
        test_extract_content_real_document,
        test_extract_content_orphan_tags,
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
