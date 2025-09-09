#!/usr/bin/env python3
"""
Testes para o processador de modelo de contrato
"""

import os
import sys

# Adicionar o diretório raiz ao path para importar o processador
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.docx_compare.processors.processador_modelo_contrato import (
    extract_tags_from_differences,
)


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

    tags = extract_tags_from_differences(modifications)

    print(f"   Modificações analisadas: {len(modifications)}")
    print(f"   Tags encontradas: {len(tags)}")

    # Verificações básicas
    assert isinstance(tags, list), "Tags deve ser uma lista"
    assert len(tags) == 2, f"Esperado 2 tags, encontrado {len(tags)}"

    # Verificar estrutura das tags
    for tag in tags:
        assert isinstance(tag, dict), "Cada tag deve ser um dicionário"
        assert "tag" in tag, "Tag deve ter campo 'tag'"
        assert "contexto" in tag, "Tag deve ter campo 'contexto'"

    print("✅ Teste básico passou!")


def test_extract_tags_duplicated():
    """Testa remoção de tags duplicadas"""
    print("🧪 Teste: Remoção de tags duplicadas")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{nome_cliente}} é cliente premium",
            "sort": 1,
        },
        {
            "categoria": "modificacao",
            "conteudo": "Cliente normal",
            "alteracao": "{{nome_cliente}} é VIP",
            "sort": 2,
        },
    ]

    tags = extract_tags_from_differences(modifications)

    print(f"   Modificações analisadas: {len(modifications)}")
    print(f"   Tags encontradas: {len(tags)}")

    # Deve ter apenas uma tag 'nome_cliente' mesmo aparecendo 2 vezes
    assert len(tags) == 1, f"Esperado 1 tag única, encontrado {len(tags)}"
    assert tags[0]["tag"] == "nome_cliente", (
        f"Esperado 'nome_cliente', encontrado '{tags[0]['tag']}'"
    )

    print("✅ Teste de duplicação passou!")


def test_extract_tags_complex():
    """Testa extração de múltiplas tags em contextos complexos"""
    print("🧪 Teste: Extração de múltiplas tags")

    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "Contrato entre {{empresa_contratante}} e {{empresa_contratada}}",
            "sort": 1,
        },
        {
            "categoria": "modificacao",
            "conteudo": "Valor: R$ 1000",
            "alteracao": "Valor: R$ {{valor_contrato}} para {{prazo_contrato}} meses",
            "sort": 2,
        },
    ]

    tags = extract_tags_from_differences(modifications)

    print(f"   Modificações analisadas: {len(modifications)}")
    print(f"   Tags encontradas: {len(tags)}")

    # Deve encontrar 4 tags
    expected_tags = {
        "empresa_contratante",
        "empresa_contratada",
        "valor_contrato",
        "prazo_contrato",
    }
    found_tags = {tag["tag"] for tag in tags}

    assert len(tags) == 4, f"Esperado 4 tags, encontrado {len(tags)}"
    assert found_tags == expected_tags, (
        f"Tags esperadas: {expected_tags}, encontradas: {found_tags}"
    )

    print("✅ Teste complexo passou!")


if __name__ == "__main__":
    test_extract_tags_basic()
    test_extract_tags_duplicated()
    test_extract_tags_complex()
    print("🎉 Todos os testes passaram!")
