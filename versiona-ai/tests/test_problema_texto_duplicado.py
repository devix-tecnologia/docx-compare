"""
Testes para validar vinculação correta com texto duplicado.

PROBLEMA ORIGINAL:
Se buscarmos texto ("DEF") em "ABC DEF GHI DEF JKL", find() sempre encontra a
PRIMEIRA ocorrência (posição 4), mesmo que a modificação seja na SEGUNDA (posição 12).

SOLUÇÃO IMPLEMENTADA:
As modificações vêm com POSIÇÃO ABSOLUTA do diff, não buscamos por texto.
Estes testes VALIDAM que a solução funciona corretamente.

ESTRATÉGIA:
- Usa DirectusAPI REAL (instancia classe de produção)
- Mocka apenas as chamadas HTTP externas ao Directus
- Valida que posições absolutas resolvem o problema de texto duplicado
- SE ESTES TESTES FALHAREM, há uma regressão que precisa ser corrigida
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from directus_server import DirectusAPI


@pytest.fixture
def api():
    """Cria uma instância do DirectusAPI com mocks para requisições externas."""
    with patch("directus_server.requests") as mock_requests:
        # Configurar mock para não fazer chamadas HTTP reais
        mock_requests.get.return_value = MagicMock(status_code=200, json=lambda: {})
        mock_requests.post.return_value = MagicMock(status_code=200, json=lambda: {})

        api_instance = DirectusAPI()
        yield api_instance


def test_texto_duplicado_primeira_ocorrencia_vinculada_corretamente(api):
    """
    Valida que modificação na PRIMEIRA ocorrência de texto duplicado é vinculada corretamente.

    Cenário:
    - Documento: "ABC DEF GHI DEF JKL"
    - Tag 1: primeira "DEF" (posição 4-7)
    - Tag 2: segunda "DEF" (posição 12-15)
    - Modificação: DELETE da PRIMEIRA "DEF" com posição absoluta 4

    RESULTADO ESPERADO: Modificação vinculada à clausula-1 ✅
    """

    documento_original = "ABC DEF GHI DEF JKL"
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}DEF{{/TAG-2}} JKL"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
            # Posição absoluta da primeira DEF
            "posicao_inicio_texto": 4,
            "posicao_fim_texto": 7,
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}DEF{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
            # Posição absoluta da segunda DEF
            "posicao_inicio_texto": 12,
            "posicao_fim_texto": 15,
        },
    ]

    # Modificação COM POSIÇÃO ABSOLUTA: primeira DEF (4-7)
    modificacoes = [
        {
            "id": "mod-1",
            "tipo": "REMOCAO",
            "conteudo": {"original": "DEF"},
            "posicao_inicio": 4,
            "posicao_fim": 7,
        }
    ]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    assert len(resultado) == 1
    mod = resultado[0]

    # VALIDAÇÃO: Deve vincular à clausula-1 (primeira ocorrência)
    assert mod.get("clausula_id") == "clausula-1", (
        f"❌ REGRESSÃO: Modificação na primeira DEF (pos 4) deveria vincular à clausula-1, "
        f"mas está em {mod.get('clausula_id')}"
    )
    assert mod.get("posicao_inicio") == 4, "Posição de início deve ser 4"
    assert mod.get("posicao_fim") == 7, "Posição de fim deve ser 7"

    print("\n✅ Primeira ocorrência vinculada corretamente à clausula-1")


def test_texto_duplicado_segunda_ocorrencia_vinculada_corretamente(api):
    """
    Valida que modificação na SEGUNDA ocorrência de texto duplicado é vinculada corretamente.

    Cenário:
    - Documento: "ABC DEF GHI DEF JKL"
    - Tag 1: primeira "DEF" (posição 4-7)
    - Tag 2: segunda "DEF" (posição 12-15)
    - Modificação: DELETE da SEGUNDA "DEF" com posição absoluta 12

    RESULTADO ESPERADO: Modificação vinculada à clausula-2 ✅

    ESTE É O CASO CRÍTICO que falharia com busca de texto!
    """

    documento_original = "ABC DEF GHI DEF JKL"
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}DEF{{/TAG-2}} JKL"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
            # Posição absoluta da primeira DEF
            "posicao_inicio_texto": 4,
            "posicao_fim_texto": 7,
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}DEF{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
            # Posição absoluta da segunda DEF
            "posicao_inicio_texto": 12,
            "posicao_fim_texto": 15,
        },
    ]

    # Modificação COM POSIÇÃO ABSOLUTA: segunda DEF (12-15)
    modificacoes = [
        {
            "id": "mod-1",
            "tipo": "REMOCAO",
            "conteudo": {"original": "DEF"},
            "posicao_inicio": 12,  # Segunda ocorrência!
            "posicao_fim": 15,
        }
    ]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    assert len(resultado) == 1
    mod = resultado[0]

    # VALIDAÇÃO CRÍTICA: Deve vincular à clausula-2 (segunda ocorrência)
    # Se falhar aqui, a busca de texto voltou e há uma REGRESSÃO!
    assert mod.get("clausula_id") == "clausula-2", (
        f"❌ REGRESSÃO CRÍTICA: Modificação na segunda DEF (pos 12) deveria vincular à clausula-2, "
        f"mas está em {mod.get('clausula_id')}. "
        f"Posição encontrada: {mod.get('posicao_inicio')}. "
        f"Isso indica que voltamos a usar busca de texto ao invés de posições absolutas!"
    )
    assert mod.get("posicao_inicio") == 12, "Posição de início deve ser 12"
    assert mod.get("posicao_fim") == 15, "Posição de fim deve ser 15"

    print("\n✅ Segunda ocorrência vinculada corretamente à clausula-2")
    print("   💡 Este teste valida que NÃO estamos usando busca de texto!")


def test_multiplas_duplicacoes_todas_vinculadas_corretamente(api):
    """
    Valida que MÚLTIPLAS modificações em texto duplicado são vinculadas corretamente.

    Cenário complexo:
    - Documento: "ABC DEF GHI DEF JKL DEF MNO"
    - 3 ocorrências de "DEF" em posições 4, 12, 20
    - 3 tags cobrindo cada ocorrência
    - 3 modificações, uma em cada posição

    RESULTADO ESPERADO: Cada modificação vinculada à tag correta ✅
    """

    documento_original = "ABC DEF GHI DEF JKL DEF MNO"
    documento_com_tags = (
        "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}DEF{{/TAG-2}} JKL {{TAG-3}}DEF{{/TAG-3}} MNO"
    )

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
            "posicao_inicio_texto": 4,
            "posicao_fim_texto": 7,
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}DEF{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
            "posicao_inicio_texto": 12,
            "posicao_fim_texto": 15,
        },
        {
            "tag_nome": "3",
            "conteudo": "{{TAG-3}}DEF{{/TAG-3}}",
            "clausulas": [{"id": "clausula-3", "nome": "Cláusula 3", "numero": "3"}],
            "posicao_inicio_texto": 20,
            "posicao_fim_texto": 23,
        },
    ]

    # 3 modificações COM POSIÇÕES ABSOLUTAS
    modificacoes = [
        {
            "id": "mod-1",
            "tipo": "REMOCAO",
            "conteudo": {"original": "DEF"},
            "posicao_inicio": 4,
            "posicao_fim": 7,
        },
        {
            "id": "mod-2",
            "tipo": "ALTERACAO",
            "conteudo": {"original": "DEF", "novo": "XYZ"},
            "posicao_inicio": 12,
            "posicao_fim": 15,
        },
        {
            "id": "mod-3",
            "tipo": "REMOCAO",
            "conteudo": {"original": "DEF"},
            "posicao_inicio": 20,
            "posicao_fim": 23,
        },
    ]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    assert len(resultado) == 3

    # Mapear resultados por ID
    mods_dict = {mod["id"]: mod for mod in resultado}

    # VALIDAÇÃO: Cada modificação deve vincular à tag correta
    assert mods_dict["mod-1"].get("clausula_id") == "clausula-1", (
        f"❌ REGRESSÃO: mod-1 (pos 4) deveria vincular à clausula-1, "
        f"mas está em {mods_dict['mod-1'].get('clausula_id')}"
    )

    assert mods_dict["mod-2"].get("clausula_id") == "clausula-2", (
        f"❌ REGRESSÃO: mod-2 (pos 12) deveria vincular à clausula-2, "
        f"mas está em {mods_dict['mod-2'].get('clausula_id')}"
    )

    assert mods_dict["mod-3"].get("clausula_id") == "clausula-3", (
        f"❌ REGRESSÃO: mod-3 (pos 20) deveria vincular à clausula-3, "
        f"mas está em {mods_dict['mod-3'].get('clausula_id')}"
    )

    print("\n✅ Todas as 3 modificações em texto duplicado vinculadas corretamente!")
    print(f"   mod-1 (pos 4):  {mods_dict['mod-1'].get('clausula_id')}")
    print(f"   mod-2 (pos 12): {mods_dict['mod-2'].get('clausula_id')}")
    print(f"   mod-3 (pos 20): {mods_dict['mod-3'].get('clausula_id')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
    # resultado = api._vincular_modificacoes_por_posicao(...)

    print("\n💡 SOLUÇÃO:")
    print("   1. Diff calcula posições absolutas das modificações")
    print("   2. Tags têm posições absolutas no documento original")
    print(
        "   3. Vinculação: comparar ranges (posicao_inicio <= pos_mod <= posicao_fim)"
    )
    print("   4. Não usar find() - usar posições diretas!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
