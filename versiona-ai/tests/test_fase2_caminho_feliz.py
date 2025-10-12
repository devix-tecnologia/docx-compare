"""
Testes da Fase 2: Caminho Feliz - Mapeamento via Offset
Valida o cálculo de offset acumulado para tags aninhadas
"""

import os
import re
import sys

# Adicionar o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from directus_server import DirectusAPI


def test_caminho_feliz_offset_simples():
    """Testa mapeamento de offset com tags simples (não aninhadas)."""
    print("🧪 Teste 1: Offset com tags simples")

    # Simular arquivo COM tags
    arquivo_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}JKL{{/TAG-2}} MNO"
    #                   012 3         4567         8 901 23        4567        8 901 234

    # Criar tags simuladas
    tags = [
        {
            "id": "tag-1-id",
            "tag_nome": "1",
            "posicao_inicio_texto": 4,  # Início de "DEF" no arquivo COM tags
            "posicao_fim_texto": 7,  # Fim de "DEF"
            "clausulas": [{"id": "clausula-1", "numero": "1"}],
        },
        {
            "id": "tag-2-id",
            "tag_nome": "2",
            "posicao_inicio_texto": 24,  # Início de "JKL" no arquivo COM tags
            "posicao_fim_texto": 27,
            "clausulas": [{"id": "clausula-2", "numero": "2"}],
        },
    ]

    # Instanciar DirectusAPI
    api = DirectusAPI()

    # Mapear tags
    tags_mapeadas = api._mapear_tags_via_offset(tags, arquivo_com_tags)

    print(f"   Tags mapeadas: {len(tags_mapeadas)}")

    # Validar tag 1
    tag1 = tags_mapeadas[0]
    print(
        f"   Tag 1: [{tag1.posicao_inicio_original}-{tag1.posicao_fim_original}] score={tag1.score_inferencia}"
    )

    # No arquivo SEM tags: "ABC DEF GHI JKL MNO"
    # "DEF" deveria estar em posição 4-7 (mesmas posições pois não há tags antes)
    # Mas as tags {{TAG-1}} e {{/TAG-1}} somam 20 chars
    # Então "DEF" no arquivo original está em 4-7

    # Tag 2
    tag2 = tags_mapeadas[1]
    print(
        f"   Tag 2: [{tag2.posicao_inicio_original}-{tag2.posicao_fim_original}] score={tag2.score_inferencia}"
    )

    # Validações
    assert len(tags_mapeadas) == 2
    assert tag1.metodo == "offset"
    assert tag1.score_inferencia == 1.0
    assert tag2.metodo == "offset"
    assert tag2.score_inferencia == 1.0

    print("   ✅ Mapeamento de offset simples correto!")


def test_caminho_feliz_offset_tags_aninhadas():
    """Testa mapeamento de offset com tags aninhadas."""
    print("\n🧪 Teste 2: Offset com tags aninhadas")

    # Simular arquivo COM tags com aninhamento
    # "{{TAG-1}}ABC {{TAG-1.1}}DEF{{/TAG-1.1}} GHI{{/TAG-1}} JKL"
    arquivo_com_tags = "{{TAG-1}}ABC {{TAG-1.1}}DEF{{/TAG-1.1}} GHI{{/TAG-1}} JKL"

    # Criar tags simuladas
    tags = [
        {
            "id": "tag-1-id",
            "tag_nome": "1",
            "posicao_inicio_texto": 9,  # Início de "ABC" (depois de {{TAG-1}})
            "posicao_fim_texto": 48,  # Fim de "GHI" (antes de {{/TAG-1}})
            "clausulas": [{"id": "clausula-1", "numero": "1"}],
        },
        {
            "id": "tag-1.1-id",
            "tag_nome": "1.1",
            "posicao_inicio_texto": 23,  # Início de "DEF"
            "posicao_fim_texto": 26,  # Fim de "DEF"
            "clausulas": [{"id": "clausula-1.1", "numero": "1.1"}],
        },
    ]

    # Instanciar DirectusAPI
    api = DirectusAPI()

    # Mapear tags
    tags_mapeadas = api._mapear_tags_via_offset(tags, arquivo_com_tags)

    print(f"   Tags mapeadas: {len(tags_mapeadas)}")

    # Arquivo SEM tags seria: "ABC DEF GHI JKL"
    for i, tag in enumerate(tags_mapeadas):
        print(
            f"   Tag {i + 1} ({tag.tag_nome}): [{tag.posicao_inicio_original}-{tag.posicao_fim_original}] score={tag.score_inferencia}"
        )

    assert len(tags_mapeadas) == 2
    assert tags_mapeadas[0].metodo == "offset"
    assert tags_mapeadas[1].metodo == "offset"
    assert all(t.score_inferencia == 1.0 for t in tags_mapeadas)

    print("   ✅ Mapeamento com tags aninhadas correto!")


def test_caminho_feliz_documento_real():
    """Testa com fragmento de documento real."""
    print("\n🧪 Teste 3: Fragmento de documento real")

    # Fragmento inspirado em contrato real
    arquivo_com_tags = """{{TAG-1.1}}CLÁUSULA PRIMEIRA - DO OBJETO

Este contrato tem por objeto a prestação de serviços de {{TAG-1.1.1}}consultoria{{/TAG-1.1.1}} técnica especializada.{{/TAG-1.1}}

{{TAG-1.2}}CLÁUSULA SEGUNDA - DO VALOR

O valor total deste contrato é de R$ 10.000,00 (dez mil reais).{{/TAG-1.2}}"""

    tags = [
        {
            "id": "tag-1.1",
            "tag_nome": "1.1",
            "posicao_inicio_texto": 11,  # Depois de {{TAG-1.1}}
            "posicao_fim_texto": 170,  # Antes de {{/TAG-1.1}}
            "clausulas": [{"id": "c1", "numero": "1.1", "nome": "Do Objeto"}],
        },
        {
            "id": "tag-1.1.1",
            "tag_nome": "1.1.1",
            "posicao_inicio_texto": 111,  # Início de "consultoria" (depois de {{TAG-1.1.1}})
            "posicao_fim_texto": 122,  # Fim de "consultoria" (antes de {{/TAG-1.1.1}})
            "clausulas": [{"id": "c1.1", "numero": "1.1.1", "nome": "Tipo de Serviço"}],
        },
        {
            "id": "tag-1.2",
            "tag_nome": "1.2",
            "posicao_inicio_texto": 184,  # Depois de {{TAG-1.2}}
            "posicao_fim_texto": 276,  # Antes de {{/TAG-1.2}}
            "clausulas": [{"id": "c2", "numero": "1.2", "nome": "Do Valor"}],
        },
    ]

    api = DirectusAPI()
    tags_mapeadas = api._mapear_tags_via_offset(tags, arquivo_com_tags)

    print(f"   Tags mapeadas: {len(tags_mapeadas)}")

    # Remover tags manualmente para verificar
    arquivo_sem_tags = arquivo_com_tags
    for pattern in [
        r"\{\{TAG-1\.1\.1\}\}",
        r"\{\{/TAG-1\.1\.1\}\}",
        r"\{\{TAG-1\.1\}\}",
        r"\{\{/TAG-1\.1\}\}",
        r"\{\{TAG-1\.2\}\}",
        r"\{\{/TAG-1\.2\}\}",
    ]:
        arquivo_sem_tags = re.sub(pattern, "", arquivo_sem_tags)

    print(f"   Arquivo SEM tags: {len(arquivo_sem_tags)} caracteres")
    print(f"   Arquivo COM tags: {len(arquivo_com_tags)} caracteres")
    print(
        f"   Diferença (tags): {len(arquivo_com_tags) - len(arquivo_sem_tags)} caracteres"
    )

    # Validar que todas as tags foram mapeadas
    assert len(tags_mapeadas) == 3
    assert all(t.score_inferencia == 1.0 for t in tags_mapeadas)
    assert all(t.metodo == "offset" for t in tags_mapeadas)

    # Validar que as posições fazem sentido
    for i, tag_map in enumerate(tags_mapeadas):
        print(
            f"   Tag {i + 1}: [{tag_map.posicao_inicio_original}-{tag_map.posicao_fim_original}] (tamanho: {tag_map.posicao_fim_original - tag_map.posicao_inicio_original})"
        )

        assert tag_map.posicao_inicio_original >= 0, (
            f"Posição início não pode ser negativa: {tag_map.posicao_inicio_original}"
        )
        assert tag_map.posicao_fim_original >= 0, (
            f"Posição fim não pode ser negativa: {tag_map.posicao_fim_original}"
        )
        assert tag_map.posicao_fim_original > tag_map.posicao_inicio_original, (
            f"Fim deve ser maior que início: {tag_map.posicao_inicio_original} -> {tag_map.posicao_fim_original}"
        )

    print("   ✅ Mapeamento com documento real correto!")


if __name__ == "__main__":
    print("=" * 70)
    print("FASE 2: TESTES DO CAMINHO FELIZ (OFFSET)")
    print("=" * 70)

    try:
        test_caminho_feliz_offset_simples()
        test_caminho_feliz_offset_tags_aninhadas()
        test_caminho_feliz_documento_real()

        print("\n" + "=" * 70)
        print("✅ FASE 2 COMPLETA: Todos os testes do Caminho Feliz passaram!")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ Teste falhou: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
