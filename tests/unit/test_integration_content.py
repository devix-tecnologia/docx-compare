#!/usr/bin/env python3
"""
Teste de integração para verificar se o processador de modelo de contrato
está preenchendo corretamente o campo conteudo
"""

import os
import sys
from unittest.mock import patch

# Adicionar o diretório raiz ao path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Importar função que vamos testar
from src.docx_compare.processors.processador_modelo_contrato import (
    extract_content_between_tags,
    extract_tags_from_differences,
    salvar_tags_modelo_contrato,
)


def test_integration_content_extraction():
    """Teste de integração da extração de conteúdo"""
    print("🧪 Teste de integração - Extração de conteúdo com tags")

    # Simular documento "tagged" com tags e conteúdo
    tagged_text = """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS

    {{TAG-responsavel}}
    Nome: Maria Silva
    CPF: 123.456.789-00
    E-mail: maria.silva@empresa.com
    {{/TAG-responsavel}}

    Seção 1 - Objeto do Contrato

    {{TAG-objeto}}
    O presente contrato tem por objeto a prestação de serviços de desenvolvimento
    de software, conforme especificações técnicas constantes do Anexo I.
    {{/TAG-objeto}}

    Seção 2 - Valor

    {{TAG-valor}}
    Valor total: R$ 75.000,00 (setenta e cinco mil reais)
    Forma de pagamento: 3x de R$ 25.000,00
    {{/TAG-valor}}
    """

    # 1. Testar extração de conteúdo
    print("\n1️⃣ Testando extração de conteúdo...")
    content_map = extract_content_between_tags(tagged_text)

    print(f"   📊 Extraídas {len(content_map)} tags com conteúdo:")
    for tag_name, content in content_map.items():
        preview = content.replace("\n", " ").strip()[:60]
        print(f"   🏷️  '{tag_name}': {preview}{'...' if len(content) > 60 else ''}")

    # 2. Simular modificações (diferenças encontradas)
    print("\n2️⃣ Simulando modificações encontradas...")
    modifications = [
        {
            "categoria": "adicao",
            "conteudo": "",
            "alteracao": "{{TAG-responsavel}} conteúdo {{/TAG-responsavel}}",
            "sort": 1,
        },
        {
            "categoria": "modificacao",
            "conteudo": "Valor antigo",
            "alteracao": "{{TAG-valor}} novo valor {{/TAG-valor}}",
            "sort": 2,
        },
    ]

    # 3. Extrair tags das modificações
    print("\n3️⃣ Extraindo tags das modificações...")
    tags_encontradas = extract_tags_from_differences(modifications)

    # 4. Enriquecer com conteúdo
    print("\n4️⃣ Enriquecendo tags com conteúdo...")
    for tag_info in tags_encontradas:
        tag_nome = tag_info["nome"]
        if tag_nome in content_map:
            tag_info["conteudo"] = content_map[tag_nome]
            print(f"   ✅ Tag '{tag_nome}' enriquecida com conteúdo")
        else:
            tag_info["conteudo"] = ""
            print(f"   ⚠️  Tag '{tag_nome}' sem conteúdo")

    # 5. Simular salvamento (dry-run)
    print("\n5️⃣ Simulando salvamento (dry-run)...")
    modelo_id = "test-modelo-123"

    # Mock das requests para simular dry-run
    with patch(
        "src.docx_compare.processors.processador_modelo_contrato.requests"
    ) as mock_requests:
        tags_criadas = salvar_tags_modelo_contrato(
            modelo_id, tags_encontradas, dry_run=True
        )
        print(f"   📊 Simulação de salvamento: {len(tags_criadas)} tags processadas")

    # 6. Verificar se o campo conteudo está sendo incluído
    print("\n6️⃣ Verificando estrutura dos dados...")
    for tag_info in tags_encontradas:
        tag_name = tag_info["nome"]
        has_content = "conteudo" in tag_info and tag_info["conteudo"]
        print(
            f"   🏷️  '{tag_name}': {'✅ COM CONTEÚDO' if has_content else '❌ SEM CONTEÚDO'}"
        )

        if has_content:
            content_preview = tag_info["conteudo"][:50]
            print(
                f"      📄 {content_preview}{'...' if len(tag_info['conteudo']) > 50 else ''}"
            )

    return tags_encontradas


if __name__ == "__main__":
    # Configurar verbose_mode para ver logs detalhados
    import src.docx_compare.processors.processador_modelo_contrato as processador_module

    processador_module.verbose_mode = True

    result = test_integration_content_extraction()
    print("\n✅ Teste de integração concluído!")
    print(f"📊 Resultado final: {len(result)} tags processadas com conteúdo")
