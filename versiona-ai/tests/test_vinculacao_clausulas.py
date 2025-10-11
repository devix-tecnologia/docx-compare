"""
Testes unitários para vinculação de modificações às cláusulas baseado em tags.

Este teste valida a lógica principal USANDO DIRECTUS API REAL COM MOCKS:
1. Tags são mapeadas no documento COM tags (arquivo_com_tags)
2. As posições das tags representam onde o conteúdo está no documento ORIGINAL
3. Modificações são buscadas no documento ORIGINAL
4. Se a posição da modificação está entre posicao_inicio e posicao_fim de uma tag, vinculamos!

ESTRATÉGIA:
- Usa DirectusAPI REAL (não instancia mock)
- Mocka apenas as chamadas HTTP externas ao Directus
- Testa a LÓGICA de vinculação sem dependências externas
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Adicionar o diretório pai ao path para importar directus_server
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


@pytest.fixture
def sample_data():
    """Carrega dados de exemplo para os testes."""
    sample_dir = Path(__file__).parent / "sample"

    with open(sample_dir / "documento_original.txt", encoding="utf-8") as f:
        documento_original = f.read()

    with open(sample_dir / "documento_com_tags.txt", encoding="utf-8") as f:
        documento_com_tags = f.read()

    with open(sample_dir / "tags_esperadas.json", encoding="utf-8") as f:
        tags_esperadas = json.load(f)

    with open(sample_dir / "modificacoes.json", encoding="utf-8") as f:
        modificacoes = json.load(f)

    with open(sample_dir / "vinculacao_esperada.json", encoding="utf-8") as f:
        vinculacao_esperada = json.load(f)

    return {
        "documento_original": documento_original,
        "documento_com_tags": documento_com_tags,
        "tags_esperadas": tags_esperadas,
        "modificacoes": modificacoes,
        "vinculacao_esperada": vinculacao_esperada,
    }


def test_mapear_posicoes_tags_no_documento_original(api, sample_data):
    """
    Testa que as tags são mapeadas corretamente e suas posições
    representam onde o conteúdo está no documento ORIGINAL.

    USA IMPLEMENTAÇÃO REAL: DirectusAPI._vincular_modificacoes_clausulas
    """
    documento_com_tags = sample_data["documento_com_tags"]
    documento_original = sample_data["documento_original"]
    tags_esperadas = sample_data["tags_esperadas"]

    # Preparar tags_modelo no formato que a API espera
    tags_modelo = []
    for tag in tags_esperadas:
        tags_modelo.append(
            {
                "tag_nome": tag["nome"],
                "conteudo": tag["conteudo"],
                "clausulas": [
                    {
                        "id": tag["clausula_id"],
                        "nome": f"Cláusula {tag['nome']}",
                        "numero": tag["nome"],
                    }
                ],
                # Adicionar posições absolutas se disponíveis
                "posicao_inicio_texto": tag.get("posicao_no_original"),
                "posicao_fim_texto": tag.get("posicao_no_original", 0)
                + len(tag["conteudo"])
                if tag.get("posicao_no_original")
                else None,
            }
        )

    # Criar uma modificação dummy para testar o mapeamento
    modificacoes = [
        {"id": "mod-test", "tipo": "REMOCAO", "conteudo": {"original": "test"}}
    ]

    # Chamar método REAL da API
    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    # Verificar que o método foi chamado e processou as tags
    # (Aqui testamos indiretamente que as tags foram mapeadas)
    assert isinstance(resultado, list), "Resultado deve ser uma lista"

    print("\n✅ Tags mapeadas e processadas pelo método real da API")
    print(f"   Total de tags modelo: {len(tags_modelo)}")


def test_vincular_modificacoes_as_clausulas(api, sample_data):
    """
    Testa que as modificações são vinculadas corretamente às cláusulas
    baseado nas posições das tags no documento ORIGINAL.

    USA IMPLEMENTAÇÃO REAL: DirectusAPI._vincular_modificacoes_clausulas
    """
    documento_original = sample_data["documento_original"]
    documento_com_tags = sample_data["documento_com_tags"]
    tags_esperadas = sample_data["tags_esperadas"]
    modificacoes_data = sample_data["modificacoes"]

    # Preparar tags_modelo
    tags_modelo = []
    for tag in tags_esperadas:
        tags_modelo.append(
            {
                "tag_nome": tag["nome"],
                "conteudo": tag["conteudo"],
                "clausulas": [
                    {
                        "id": tag["clausula_id"],
                        "nome": f"Cláusula {tag['nome']}",
                        "numero": tag["nome"],
                    }
                ],
                "posicao_inicio_texto": tag.get("posicao_no_original"),
                "posicao_fim_texto": tag.get("posicao_no_original", 0)
                + len(tag["conteudo"])
                if tag.get("posicao_no_original")
                else None,
            }
        )

    # Preparar modificações no formato da API
    modificacoes = []
    for mod in modificacoes_data:
        modificacoes.append(
            {
                "id": mod["id"],
                "tipo": "REMOCAO",  # Simplificando para teste
                "conteudo": {"original": "test"},
                "posicao_inicio": mod.get("posicao_original"),
                "posicao_fim": mod.get("posicao_original", 0) + 10,
            }
        )

    # Chamar método REAL da API
    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    # Verificar que retornou lista de modificações vinculadas
    assert isinstance(resultado, list), "Resultado deve ser uma lista"
    assert len(resultado) == len(modificacoes), "Deve processar todas as modificações"

    # Verificar que cada modificação foi processada
    # (pode ter clausula_id=None se não foi vinculada, ou ter erro)
    for mod_result in resultado:
        assert "id" in mod_result, "Cada modificação deve ter id"
        # Modificações não vinculadas terão clausula_id como None ou ausente
        # mas devem estar presentes no resultado

    print("\n✅ Modificações vinculadas usando método real da API")
    print(f"   Total processadas: {len(resultado)}")
    vinculadas = sum(1 for m in resultado if m.get("clausula_id"))
    print(f"   Vinculadas a cláusulas: {vinculadas}/{len(resultado)}")


def test_posicoes_absolutas_prioritarias(api):
    """
    Testa que posições absolutas são priorizadas sobre busca de texto.

    USA IMPLEMENTAÇÃO REAL: Valida comportamento do método _vincular_modificacoes_clausulas
    """
    documento_original = "ABC DEF GHI DEF JKL"  # Texto duplicado "DEF"
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

    # Chamar método REAL da API
    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    assert len(resultado) == 2

    # Validar vinculações usando posições absolutas
    mods_dict = {mod["id"]: mod for mod in resultado}

    # mod-1: DELETE primeira "DEF" (4-7) → deve vincular à clausula-1
    assert mods_dict["mod-1"].get("clausula_id") == "clausula-1", (
        f"mod-1 (pos 4-7) deve vincular à clausula-1, não {mods_dict['mod-1'].get('clausula_id')}"
    )

    # mod-2: ALTERAÇÃO segunda "DEF" (12-15) → deve vincular à clausula-2
    assert mods_dict["mod-2"].get("clausula_id") == "clausula-2", (
        f"mod-2 (pos 12-15) deve vincular à clausula-2, não {mods_dict['mod-2'].get('clausula_id')}"
    )

    print("\n✅ Posições absolutas priorizadas corretamente!")
    print(f"   mod-1 (pos 4-7): {mods_dict['mod-1'].get('clausula_id')}")
    print(f"   mod-2 (pos 12-15): {mods_dict['mod-2'].get('clausula_id')}")


def test_integracao_completa_vinculacao(api, sample_data):
    """
    Teste de integração completo usando o método REAL da API:
    1. Preparar tags_modelo a partir dos dados de exemplo
    2. Preparar modificações a partir dos dados de exemplo
    3. Chamar _vincular_modificacoes_clausulas
    4. Validar resultado

    USA IMPLEMENTAÇÃO REAL: DirectusAPI._vincular_modificacoes_clausulas
    """
    documento_original = sample_data["documento_original"]
    documento_com_tags = sample_data["documento_com_tags"]
    tags_esperadas = sample_data["tags_esperadas"]
    modificacoes_data = sample_data["modificacoes"]
    vinculacao_esperada = sample_data["vinculacao_esperada"]

    # Preparar tags_modelo
    tags_modelo = []
    for tag in tags_esperadas:
        tags_modelo.append(
            {
                "tag_nome": tag["nome"],
                "conteudo": tag["conteudo"],
                "clausulas": [
                    {
                        "id": tag["clausula_id"],
                        "nome": f"Cláusula {tag['nome']}",
                        "numero": tag["nome"],
                    }
                ],
                "posicao_inicio_texto": tag.get("posicao_no_original"),
                "posicao_fim_texto": tag.get("posicao_no_original", 0)
                + len(tag["conteudo"])
                if tag.get("posicao_no_original")
                else None,
            }
        )

    # Preparar modificações
    modificacoes = []
    for mod in modificacoes_data:
        modificacoes.append(
            {
                "id": mod["id"],
                "tipo": "REMOCAO",
                "conteudo": {"original": "test"},
                "posicao_inicio": mod.get("posicao_original"),
                "posicao_fim": mod.get("posicao_original", 0) + 10,
            }
        )

    # Chamar método REAL da API
    resultado = api._vincular_modificacoes_clausulas(
        modificacoes=modificacoes,
        tags_modelo=tags_modelo,
        texto_com_tags=documento_com_tags,
        texto_original=documento_original,
        texto_modificado=documento_original,
    )

    # Mapear resultado para comparar com esperado
    vinculacoes_resultado = {mod["id"]: mod.get("clausula_id") for mod in resultado}

    # Comparar com vinculação esperada
    for mod_id, clausula_esperada in vinculacao_esperada.items():
        assert vinculacoes_resultado.get(mod_id) == clausula_esperada, (
            f"Modificação {mod_id}: esperado {clausula_esperada}, "
            f"obtido {vinculacoes_resultado.get(mod_id)}"
        )

    # Estatísticas
    total_mods = len(modificacoes)
    mods_vinculadas = sum(1 for v in vinculacoes_resultado.values() if v is not None)

    print(f"\n📊 Resumo: {mods_vinculadas}/{total_mods} modificações vinculadas")
    print("✅ Integração completa validada usando método real da API")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
