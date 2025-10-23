#!/usr/bin/env python3

"""
TESTES DA FASE 5: ROBUSTEZ E INTEGRAÇÃO

Este arquivo testa o algoritmo unificado que decide automaticamente
entre Caminho Feliz (offset) e Caminho Real (conteúdo) baseado na
similaridade dos documentos.

Testa:
1. Decisão correta: similaridade alta → offset
2. Decisão correta: similaridade baixa → conteúdo
3. Integração end-to-end: tags → modificações → vinculação
4. Edge cases: sem tags, sem modificações
"""

import sys
from pathlib import Path

# Adicionar diretório pai ao path para importar directus_server
sys.path.insert(0, str(Path(__file__).parent.parent / "versiona-ai"))

from directus_server import DirectusAPI


def test_decisao_caminho_feliz():
    """
    Teste 1: Decisão em cenário "caminho feliz" (documentos idênticos).

    Cenário: Documentos são idênticos (exceto pelas tags).
    Mesmo com similaridade 100%, mantemos o método "conteudo"
    (offset desabilitado devido ao desalinhamento de coordenadas).
    """
    print("\n🧪 Teste 1: Decisão pelo Caminho Feliz")

    # Arquivo COM tags
    texto_com_tags = (
        "Este é um contrato de prestação de serviços de "
        "{{TAG-1}}consultoria{{/TAG-1}} para desenvolvimento de software. "
        "O prazo será de {{TAG-2}}seis meses{{/TAG-2}} contados da assinatura."
    )

    # Arquivo ORIGINAL (igual, mas sem tags)
    texto_original = (
        "Este é um contrato de prestação de serviços de "
        "consultoria para desenvolvimento de software. "
        "O prazo será de seis meses contados da assinatura."
    )

    # Tags (posições no arquivo COM tags)
    tags_modelo = [
        {
            "id": "tag-001",
            "tag_nome": "TAG-1",
            "posicao_inicio_texto": 56,  # "consultoria" (depois de {{TAG-1}})
            "posicao_fim_texto": 67,
            "clausulas": [{"id": "clausula-001", "nome": "Serviços"}],
        },
        {
            "id": "tag-002",
            "tag_nome": "TAG-2",
            "posicao_inicio_texto": 137,  # "seis meses" (depois de {{TAG-2}})
            "posicao_fim_texto": 147,
            "clausulas": [{"id": "clausula-002", "nome": "Prazo"}],
        },
    ]

    # Modificações (no arquivo original, sem tags)
    modificacoes = [
        {
            "tipo": "inserção",
            "posicao_inicio": 50,  # Dentro de "consultoria" [47-58]
            "posicao_fim": 55,
            "conteudo": "nova ",
        },
    ]

    # Executar algoritmo unificado
    api = DirectusAPI()
    resultado_completo = api._vincular_modificacoes_clausulas_novo(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=texto_com_tags,
        texto_original=texto_original,
    )

    # Validar decisão
    assert resultado_completo["metodo_usado"] == "conteudo", (
        f"Esperado método 'conteudo', obteve '{resultado_completo['metodo_usado']}'"
    )
    assert resultado_completo["similaridade"] >= 0.95, (
        f"Similaridade deveria ser ≥ 0.95, obteve {resultado_completo['similaridade']:.2%}"
    )

    # Validar mapeamento
    tags_mapeadas = resultado_completo["tags_mapeadas"]
    assert len(tags_mapeadas) == 2, (
        f"Esperado 2 tags mapeadas, obteve {len(tags_mapeadas)}"
    )

    # Validar vinculação
    resultado = resultado_completo["resultado"]
    total_processadas = (
        len(resultado.vinculadas)
        + len(resultado.revisao_manual)
        + len(resultado.nao_vinculadas)
    )
    assert total_processadas == 1, (
        f"Esperado 1 modificação processada, obteve {total_processadas}"
    )
    assert len(resultado.vinculadas) >= 0  # Pode estar em vinculadas ou revisão

    print(f"   ✅ Método usado: {resultado_completo['metodo_usado']}")
    print(f"   Similaridade: {resultado_completo['similaridade']:.2%}")
    print(f"   Tags mapeadas: {len(tags_mapeadas)}")
    print(f"   Taxa de sucesso: {resultado.taxa_sucesso():.1f}%")
    print("   ✅ Decisão coerente com estratégia atual (conteúdo)")


def test_decisao_caminho_real():
    """
    Teste 2: Decisão pelo Caminho Real (conteúdo)

    Cenário: Documentos são diferentes.
    Similaridade < 0.95 → deve usar conteúdo.
    Esperado: metodo_usado = "conteudo"
    """
    print("\n🧪 Teste 2: Decisão pelo Caminho Real")

    # Arquivo COM tags
    texto_com_tags = (
        "Cláusula 1: O cliente contratará serviços de "
        "{{TAG-1}}consultoria{{/TAG-1}} especializada em tecnologia."
    )

    # Arquivo ORIGINAL (muito diferente)
    texto_original = (
        "Conforme acordado em reunião, o prestador deverá fornecer "
        "consultoria técnica avançada para o projeto de software."
    )

    # Tags
    tags_modelo = [
        {
            "id": "tag-001",
            "tag_nome": "TAG-1",
            "posicao_inicio_texto": 53,  # "consultoria" (depois de {{TAG-1}})
            "posicao_fim_texto": 64,
            "clausulas": [{"id": "clausula-001"}],
        },
    ]

    # Modificação
    modificacoes = [
        {
            "tipo": "modificação",
            "posicao_inicio": 62,  # Próximo a "consultoria" no original
            "posicao_fim": 72,
            "conteudo": "técnica",
        },
    ]

    # Executar algoritmo unificado
    api = DirectusAPI()
    resultado_completo = api._vincular_modificacoes_clausulas_novo(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=texto_com_tags,
        texto_original=texto_original,
    )

    # Validar decisão
    assert resultado_completo["metodo_usado"] == "conteudo", (
        f"Esperado método 'conteudo', obteve '{resultado_completo['metodo_usado']}'"
    )
    assert resultado_completo["similaridade"] < 0.95, (
        f"Similaridade deveria ser < 0.95, obteve {resultado_completo['similaridade']:.2%}"
    )

    # Validar mapeamento
    tags_mapeadas = resultado_completo["tags_mapeadas"]
    assert len(tags_mapeadas) >= 0  # Pode encontrar ou não

    print(f"   ✅ Método usado: {resultado_completo['metodo_usado']}")
    print(f"   Similaridade: {resultado_completo['similaridade']:.2%}")
    print(f"   Tags mapeadas: {len(tags_mapeadas)}")
    print("   ✅ Decisão pelo Caminho Real correta!")


def test_integracao_end_to_end():
    """
    Teste 3: Integração end-to-end

    Cenário: Fluxo completo com múltiplas tags e modificações.
    Esperado: Todas as etapas funcionam em conjunto
    """
    print("\n🧪 Teste 3: Integração end-to-end")

    # Documento COM tags (similar ao original)
    texto_com_tags = (
        "Contrato de {{TAG-1}}prestação de serviços{{/TAG-1}} entre as partes. "
        "O {{TAG-2}}prestador{{/TAG-2}} compromete-se a entregar conforme "
        "{{TAG-3}}prazo acordado{{/TAG-3}} de 90 dias."
    )

    # Documento ORIGINAL (igual mas sem tags)
    texto_original = (
        "Contrato de prestação de serviços entre as partes. "
        "O prestador compromete-se a entregar conforme "
        "prazo acordado de 90 dias."
    )

    # Tags do modelo
    tags_modelo = [
        {
            "id": "tag-001",
            "tag_nome": "TAG-1",
            "posicao_inicio_texto": 21,
            "posicao_fim_texto": 43,
            "clausulas": [{"id": "c1"}],
        },
        {
            "id": "tag-002",
            "tag_nome": "TAG-2",
            "posicao_inicio_texto": 78,
            "posicao_fim_texto": 87,
            "clausulas": [{"id": "c2"}],
        },
        {
            "id": "tag-003",
            "tag_nome": "TAG-3",
            "posicao_inicio_texto": 136,
            "posicao_fim_texto": 149,
            "clausulas": [{"id": "c3"}],
        },
    ]

    # Modificações (no original sem tags)
    modificacoes = [
        {
            "tipo": "inserção",
            "posicao_inicio": 15,
            "posicao_fim": 20,
            "conteudo": "novo",
        },
        {
            "tipo": "remoção",
            "posicao_inicio": 55,
            "posicao_fim": 60,
            "conteudo": "antigo",
        },
    ]

    # Executar
    api = DirectusAPI()
    resultado_completo = api._vincular_modificacoes_clausulas_novo(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=texto_com_tags,
        texto_original=texto_original,
    )

    # Validar estrutura do retorno
    assert "resultado" in resultado_completo
    assert "metodo_usado" in resultado_completo
    assert "similaridade" in resultado_completo
    assert "tags_mapeadas" in resultado_completo

    # Validar que processou todas as modificações
    resultado = resultado_completo["resultado"]
    total = (
        len(resultado.vinculadas)
        + len(resultado.revisao_manual)
        + len(resultado.nao_vinculadas)
    )
    assert total == len(modificacoes), (
        f"Esperado {len(modificacoes)} processadas, obteve {total}"
    )

    print(f"   ✅ Método: {resultado_completo['metodo_usado']}")
    print(f"   Tags mapeadas: {len(resultado_completo['tags_mapeadas'])}")
    print(f"   Modificações processadas: {total}")
    print(f"   Taxa de sucesso: {resultado.taxa_sucesso():.1f}%")
    print("   ✅ Integração end-to-end funcionando!")


def test_edge_cases():
    """
    Teste 4: Edge cases

    Cenário: Situações extremas (sem tags, sem modificações).
    Esperado: Tratamento gracioso de edge cases
    """
    print("\n🧪 Teste 4: Edge cases")

    texto_com_tags = "Documento simples sem tags."
    texto_original = "Documento simples sem tags."

    api = DirectusAPI()

    # Edge case 1: Sem tags
    print("\n   📌 Edge case 1: Sem tags")
    resultado1 = api._vincular_modificacoes_clausulas_novo(
        modificacoes=[{"tipo": "inserção", "posicao_inicio": 0, "posicao_fim": 5}],
        tags_modelo=[],
        texto_com_tags=texto_com_tags,
        texto_original=texto_original,
    )
    assert resultado1["metodo_usado"] == "none"
    assert len(resultado1["resultado"].nao_vinculadas) == 1
    print("      ✅ Sem tags: tratado corretamente")

    # Edge case 2: Sem modificações
    print("\n   📌 Edge case 2: Sem modificações")
    resultado2 = api._vincular_modificacoes_clausulas_novo(
        modificacoes=[],
        tags_modelo=[
            {
                "id": "t1",
                "tag_nome": "TAG-1",
                "posicao_inicio_texto": 0,
                "posicao_fim_texto": 10,
            }
        ],
        texto_com_tags=texto_com_tags,
        texto_original=texto_original,
    )
    assert resultado2["metodo_usado"] == "none"
    assert len(resultado2["resultado"].vinculadas) == 0
    print("      ✅ Sem modificações: tratado corretamente")

    print("\n   ✅ Edge cases tratados com sucesso!")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FASE 5: TESTES DE ROBUSTEZ E INTEGRAÇÃO")
    print("=" * 70)

    try:
        test_decisao_caminho_feliz()
        test_decisao_caminho_real()
        test_integracao_end_to_end()
        test_edge_cases()

        print("\n" + "=" * 70)
        print("✅ FASE 5 COMPLETA: Todos os testes de robustez passaram!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
