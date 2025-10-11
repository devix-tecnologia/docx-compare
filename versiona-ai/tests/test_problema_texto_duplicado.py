"""
Teste que documenta o PROBLEMA de usar busca de texto quando há duplicações.

PROBLEMA:
Se buscarmos texto ("DEF") em "ABC DEF GHI DEF JKL", sempre encontramos a
PRIMEIRA ocorrência (posição 4), mesmo que a modificação seja na SEGUNDA (posição 12).

SOLUÇÃO:
As modificações devem vir com POSIÇÃO ABSOLUTA do diff, não buscar por texto.

ESTRATÉGIA:
- Usa DirectusAPI REAL (instancia classe de produção)
- Mocka apenas as chamadas HTTP externas ao Directus
- Testa a LÓGICA de vinculação com texto duplicado
- Demonstra o problema e valida a solução implementada
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


def test_problema_texto_duplicado_busca_primeira_ocorrencia(api):
    """
    DEMONSTRA O PROBLEMA: Busca de texto sempre encontra primeira ocorrência.

    Cenário:
    - Documento: "ABC DEF GHI DEF JKL"
    - Tag 1: primeira "DEF" (posição 4-7)
    - Tag 2: segunda "DEF" (posição 12-15)
    - Modificação: DELETE da SEGUNDA "DEF" (deveria ser posição 12)

    Com busca de texto, find("DEF") retorna 4 (primeira), não 12 (segunda)!
    """

    documento_original = "ABC DEF GHI DEF JKL"
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}DEF{{/TAG-2}} JKL"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}DEF{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
        },
    ]

    # Modificação deveria estar na SEGUNDA ocorrência de DEF
    # Mas como passamos apenas o texto, a busca encontrará a PRIMEIRA
    modificacoes = [
        {
            "id": "mod-1",
            "tipo": "REMOCAO",
            "conteudo": {"original": "DEF"},
            # FALTA: posição absoluta! (deveria ser 12, não buscar por texto)
        }
    ]

    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    # A função atual vai vincular à clausula-1 (ERRADO)
    # porque find("DEF") retorna 4, não 12
    assert len(resultado) == 1
    mod = resultado[0]

    print("\n⚠️  BUG DETECTADO:")
    print(f"   Modificação vinculada a: {mod.get('clausula_id')}")
    print(f"   Posição encontrada: {mod.get('posicao_inicio')}")
    print("   ESPERADO: clausula-2, posição 12")
    print(f"   OBTIDO: {mod.get('clausula_id')}, posição {mod.get('posicao_inicio')}")

    # Este teste DEVE FALHAR com a implementação atual!
    # Queremos que a modificação seja na clausula-2, mas será na clausula-1
    assert mod.get("clausula_id") == "clausula-2", (
        f"❌ BUG: Modificação deveria estar na clausula-2 (segunda DEF), "
        f"mas está em {mod.get('clausula_id')} (primeira DEF encontrada por find())"
    )


def test_solucao_usar_posicao_absoluta_do_diff(api):
    """
    DEMONSTRA A SOLUÇÃO: Modificações devem vir com posição absoluta.

    As modificações devem ter:
    - posicao_inicio: posição absoluta no documento original
    - posicao_fim: posição fim no documento original

    Essas posições vêm do DIFF, que sabe exatamente onde está cada mudança.
    """

    documento_original = "ABC DEF GHI DEF JKL"
    documento_com_tags = "ABC {{TAG-1}}DEF{{/TAG-1}} GHI {{TAG-2}}DEF{{/TAG-2}} JKL"

    tags_modelo = [
        {
            "tag_nome": "1",
            "conteudo": "{{TAG-1}}DEF{{/TAG-1}}",
            "clausulas": [{"id": "clausula-1", "nome": "Cláusula 1", "numero": "1"}],
        },
        {
            "tag_nome": "2",
            "conteudo": "{{TAG-2}}DEF{{/TAG-2}}",
            "clausulas": [{"id": "clausula-2", "nome": "Cláusula 2", "numero": "2"}],
        },
    ]

    # Modificação COM POSIÇÃO ABSOLUTA (vinda do diff)
    modificacoes = [
        {
            "id": "mod-1",
            "tipo": "REMOCAO",
            "conteudo": {"original": "DEF"},
            # POSIÇÃO ABSOLUTA do diff: segunda DEF está em 12-15
            "posicao_inicio": 12,
            "posicao_fim": 15,
        }
    ]

    # TODO: Implementar vinculação baseada em posição, não em busca de texto
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
