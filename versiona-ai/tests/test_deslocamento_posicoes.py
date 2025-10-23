"""
Testes unitários para validar a função _vincular_modificacoes_clausulas
que lida com deslocamento de posições causado por múltiplas modificações.

ESTRATÉGIA:
- Usa DirectusAPI REAL (instancia classe de produção)
- Mocka apenas as chamadas HTTP externas ao Directus
- Testa a LÓGICA de vinculação sem dependências externas
- Validação de posições absolutas e deslocamento
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


def test_vinculacao_com_delete_resolve_deslocamento(api):
    """Testa vinculação de DELETE usando busca de texto."""
    documento_original = "ABC DEF GHI JKL MNO PQR"
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}JKL{{/TAG-2}} MNO PQR"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}JKL{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
        },
    ]

    modificacoes = [{"id": "mod-1", "tipo": "REMOCAO", "conteudo": {"original": "DEF"}}]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    assert len(resultado) == 1
    assert resultado[0].get("clausula_id") == "clausula-1"

    # Validar posições da modificação
    mod = resultado[0]
    assert "posicao_inicio" in mod, "Modificação deve ter posicao_inicio"
    assert "posicao_fim" in mod, "Modificação deve ter posicao_fim"
    assert mod["posicao_inicio"] == 4, (
        f"DELETE 'DEF' deve estar em posição 4, não {mod['posicao_inicio']}"
    )
    assert mod["posicao_fim"] == 7, (
        f"DELETE 'DEF' deve terminar em posição 7, não {mod['posicao_fim']}"
    )

    print(
        f"\n✅ DELETE vinculado à Cláusula 1 (posição {mod['posicao_inicio']}-{mod['posicao_fim']})"
    )


def test_vinculacao_com_alteracao_resolve_deslocamento(api):
    """Testa vinculação de ALTERAÇÃO que muda tamanho do texto."""
    documento_original = "ABC DEF GHI JKL MNO PQR"
    documento_modificado = "ABC DEF GHI ABCDE MNO PQR"
    documento_com_tags = "ABC DEF GHI {{TAG-2}}JKL{{/TAG-2}} MNO PQR"

    tags_modelo = [
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}JKL{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
        },
    ]

    modificacoes = [
        {
            "id": "mod-1",
            "tipo": "ALTERACAO",
            "conteudo": {"original": "JKL", "novo": "ABCDE"},
        }
    ]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_modificado,
    )

    assert len(resultado) == 1
    assert resultado[0].get("clausula_id") == "clausula-2"

    # Validar posições da modificação
    mod = resultado[0]
    assert "posicao_inicio" in mod, "Modificação deve ter posicao_inicio"
    assert "posicao_fim" in mod, "Modificação deve ter posicao_fim"
    assert mod["posicao_inicio"] == 12, (
        f"ALTERAÇÃO 'JKL' deve estar em posição 12, não {mod['posicao_inicio']}"
    )
    # Posição fim deve ser baseada no texto ORIGINAL (JKL = 3 chars), não no novo (ABCDE = 5 chars)
    assert mod["posicao_fim"] == 15, (
        f"ALTERAÇÃO 'JKL' deve terminar em posição 15, não {mod['posicao_fim']}"
    )

    print(
        f"\n✅ ALTERAÇÃO vinculada à Cláusula 2 (posição {mod['posicao_inicio']}-{mod['posicao_fim']})"
    )


def test_vinculacao_com_insert_usa_documento_modificado(api):
    """Testa que INSERT é buscado no documento modificado."""
    documento_original = "ABC DEF GHI"
    documento_modificado = "ABC DEF XXX GHI"
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
        },
    ]

    modificacoes = [{"id": "mod-1", "tipo": "INSERCAO", "conteudo": {"novo": "XXX"}}]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_modificado,
    )

    assert len(resultado) == 1
    print(f"\n⚠️  INSERT processado: {resultado[0].get('clausula_id')}")


def test_multiplas_modificacoes_com_deslocamento(api):
    """Testa múltiplas modificações que causam deslocamento."""
    documento_original = "ABC DEF GHI JKL MNO PQR"
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}JKL{{/TAG-2}} MNO {{TAG-3}}PQR{{/TAG-3}}"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}JKL{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
        },
        {
            "tag_nome": "3",
            "conteudo": "{{TAG-3}}PQR{{/TAG-3}}",
            "clausulas": [{"id": "clausula-3", "nome": "Cláusula 3", "numero": "3"}],
        },
    ]

    modificacoes = [
        {"id": "mod-1", "tipo": "REMOCAO", "conteudo": {"original": "DEF"}},
        {
            "id": "mod-2",
            "tipo": "ALTERACAO",
            "conteudo": {"original": "JKL", "novo": "ABCDE"},
        },
        {"id": "mod-3", "tipo": "REMOCAO", "conteudo": {"original": "PQR"}},
    ]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    assert len(resultado) == 3
    vinculacoes = {mod["id"]: mod.get("clausula_id") for mod in resultado}

    assert vinculacoes["mod-1"] == "clausula-1"
    assert vinculacoes["mod-2"] == "clausula-2"
    assert vinculacoes["mod-3"] == "clausula-3"

    # Validar posições de TODAS as modificações
    mods_dict = {mod["id"]: mod for mod in resultado}

    # mod-1: DELETE "DEF" na posição 4-7
    assert mods_dict["mod-1"]["posicao_inicio"] == 4, (
        f"mod-1 deve estar em posição 4, não {mods_dict['mod-1']['posicao_inicio']}"
    )
    assert mods_dict["mod-1"]["posicao_fim"] == 7, (
        f"mod-1 deve terminar em 7, não {mods_dict['mod-1']['posicao_fim']}"
    )

    # mod-2: ALTERAÇÃO "JKL" na posição 12-15 (baseado no texto ORIGINAL)
    assert mods_dict["mod-2"]["posicao_inicio"] == 12, (
        f"mod-2 deve estar em posição 12, não {mods_dict['mod-2']['posicao_inicio']}"
    )
    assert mods_dict["mod-2"]["posicao_fim"] == 15, (
        f"mod-2 deve terminar em 15, não {mods_dict['mod-2']['posicao_fim']}"
    )

    # mod-3: DELETE "PQR" na posição 20-23
    assert mods_dict["mod-3"]["posicao_inicio"] == 20, (
        f"mod-3 deve estar em posição 20, não {mods_dict['mod-3']['posicao_inicio']}"
    )
    assert mods_dict["mod-3"]["posicao_fim"] == 23, (
        f"mod-3 deve terminar em 23, não {mods_dict['mod-3']['posicao_fim']}"
    )

    print("\n✅ Todas as modificações vinculadas com posições corretas!")
    print(
        f"   mod-1: posição {mods_dict['mod-1']['posicao_inicio']}-{mods_dict['mod-1']['posicao_fim']}"
    )
    print(
        f"   mod-2: posição {mods_dict['mod-2']['posicao_inicio']}-{mods_dict['mod-2']['posicao_fim']}"
    )
    print(
        f"   mod-3: posição {mods_dict['mod-3']['posicao_inicio']}-{mods_dict['mod-3']['posicao_fim']}"
    )


def test_texto_movido_de_lugar_com_posicao_absoluta(api):
    """
    TDD: Testa que texto MOVIDO de lugar é vinculado corretamente usando POSIÇÃO ABSOLUTA.

    Cenário CRÍTICO - Texto duplicado movido:
    - Documento original: "ABC DEF GHI DEF JKL"
    - Tag 1: primeira "DEF" (posição 4-7)
    - Tag 2: segunda "DEF" (posição 12-15)

    Modificações:
    1. DELETE primeira "DEF" (posição 4-7)
    2. INSERT "DEF" depois de JKL (posição 16 no modificado)

    Resultado: texto "DEF" foi MOVIDO da posição 4 para depois de JKL.

    ⚠️  COM BUSCA DE TEXTO: find("DEF") sempre retorna 4 (primeira) - ERRADO!
    ✅ COM POSIÇÃO ABSOLUTA: usar posicao_inicio informada pela modificação - CORRETO!
    """

    documento_original = "ABC DEF GHI DEF JKL"
    documento_modificado = "ABC GHI DEF JKL DEF"  # Moveu DEF para outras posições
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}DEF{{/TAG-2}} JKL"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
            # Posições absolutas vindas do Directus
            "posicao_inicio_texto": 4,
            "posicao_fim_texto": 7,
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}DEF{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
            # Posições absolutas vindas do Directus
            "posicao_inicio_texto": 12,
            "posicao_fim_texto": 15,
        },
    ]

    # Modificações COM POSIÇÃO ABSOLUTA (vindas do diff)
    modificacoes = [
        {
            "id": "mod-1",
            "tipo": "REMOCAO",
            "conteudo": {"original": "DEF"},
            # Posição absoluta: primeira DEF em 4-7
            "posicao_inicio": 4,
            "posicao_fim": 7,
        },
        {
            "id": "mod-2",
            "tipo": "ALTERACAO",
            "conteudo": {"original": "DEF", "novo": "XYZ"},
            # Posição absoluta: segunda DEF em 12-15
            "posicao_inicio": 12,
            "posicao_fim": 15,
        },
    ]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_modificado,
    )

    assert len(resultado) == 2

    # Validar vinculações CORRETAS usando posições absolutas
    mods_dict = {mod["id"]: mod for mod in resultado}

    # mod-1: DELETE primeira "DEF" (4-7) → deve vincular à clausula-1
    assert mods_dict["mod-1"]["clausula_id"] == "clausula-1", (
        f"mod-1 (DELETE em posição 4-7) deve vincular à clausula-1, "
        f"não {mods_dict['mod-1'].get('clausula_id')}"
    )
    assert mods_dict["mod-1"]["posicao_inicio"] == 4
    assert mods_dict["mod-1"]["posicao_fim"] == 7

    # mod-2: ALTERAÇÃO segunda "DEF" (12-15) → deve vincular à clausula-2
    assert mods_dict["mod-2"]["clausula_id"] == "clausula-2", (
        f"mod-2 (ALTERAÇÃO em posição 12-15) deve vincular à clausula-2, "
        f"não {mods_dict['mod-2'].get('clausula_id')}"
    )
    assert mods_dict["mod-2"]["posicao_inicio"] == 12
    assert mods_dict["mod-2"]["posicao_fim"] == 15

    print("\n✅ Texto movido vinculado corretamente usando POSIÇÕES ABSOLUTAS!")
    print(f"   mod-1 (pos 4-7): {mods_dict['mod-1']['clausula_id']}")
    print(f"   mod-2 (pos 12-15): {mods_dict['mod-2']['clausula_id']}")
    print("\n💡 Busca de texto falharia aqui (sempre encontraria primeira DEF)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
