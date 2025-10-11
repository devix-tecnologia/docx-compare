"""
Testes para vinculação de modificações às cláusulas baseado em tags.

Este teste valida a lógica principal:
1. Tags são mapeadas no documento COM tags (arquivo_com_tags)
2. As posições das tags representam onde o conteúdo está no documento ORIGINAL
3. Modificações são buscadas no documento ORIGINAL
4. Se a posição da modificação está entre posicao_inicio e posicao_fim de uma tag, vinculamos!
"""

import json
import re
import sys
from pathlib import Path

import pytest

# Adicionar o diretório pai ao path para importar directus_server
sys.path.insert(0, str(Path(__file__).parent.parent))


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


def test_mapear_posicoes_tags_no_documento_original(sample_data):
    """
    Testa que as tags são mapeadas corretamente e suas posições
    representam onde o conteúdo está no documento ORIGINAL.
    """
    documento_com_tags = sample_data["documento_com_tags"]
    documento_original = sample_data["documento_original"]
    tags_esperadas = sample_data["tags_esperadas"]

    # Simular o mapeamento de tags
    tag_positions = []

    for tag in tags_esperadas:
        # Remover as tags do conteúdo para encontrar o texto limpo
        conteudo = tag["conteudo"]

        # Buscar no documento COM tags primeiro
        # (para simular o que o código faz)
        pos_tagueado = documento_com_tags.find(conteudo)
        assert pos_tagueado >= 0, f"Tag {tag['nome']} não encontrada no doc com tags"

        # Agora buscar no documento ORIGINAL para calcular a posição real
        pos_original = documento_original.find(conteudo)
        assert pos_original >= 0, f"Tag {tag['nome']} não encontrada no doc original"

        # Validar que as posições esperadas estão corretas
        assert pos_original == tag["posicao_no_original"], (
            f"Tag {tag['nome']}: posição original incorreta"
        )
        assert pos_tagueado == tag["posicao_no_tagueado"], (
            f"Tag {tag['nome']}: posição tagueada incorreta"
        )

        tag_positions.append(
            {
                "tag_nome": tag["nome"],
                "posicao_inicio": pos_original,  # Posição no documento ORIGINAL
                "posicao_fim": pos_original + len(conteudo),
                "clausula_id": tag["clausula_id"],
                "conteudo": conteudo,
            }
        )

    # Ordenar por posição
    tag_positions.sort(key=lambda x: x["posicao_inicio"])

    # Verificar que temos 3 tags mapeadas
    assert len(tag_positions) == 3, "Deveria ter 3 tags mapeadas"

    # Verificar que as posições estão em ordem crescente
    for i in range(len(tag_positions) - 1):
        assert (
            tag_positions[i]["posicao_inicio"] < tag_positions[i + 1]["posicao_inicio"]
        ), "Tags devem estar ordenadas por posição"


def test_vincular_modificacoes_as_clausulas(sample_data):
    """
    Testa que as modificações são vinculadas corretamente às cláusulas
    baseado nas posições das tags no documento ORIGINAL.
    """
    documento_original = sample_data["documento_original"]
    tags_esperadas = sample_data["tags_esperadas"]
    modificacoes = sample_data["modificacoes"]
    vinculacao_esperada = sample_data["vinculacao_esperada"]

    # Mapear posições das tags no documento ORIGINAL
    tag_positions = []
    for tag in tags_esperadas:
        conteudo = tag["conteudo"]
        pos_original = documento_original.find(conteudo)

        tag_positions.append(
            {
                "tag_nome": tag["nome"],
                "posicao_inicio": pos_original,
                "posicao_fim": pos_original + len(conteudo),
                "clausula_id": tag["clausula_id"],
            }
        )

    tag_positions.sort(key=lambda x: x["posicao_inicio"])

    # Vincular modificações às cláusulas
    resultados = {}

    for mod in modificacoes:
        mod_id = mod["id"]
        pos_mod = mod["posicao_original"]

        # Encontrar a tag que contém esta posição
        clausula_vinculada = None
        for tag_info in tag_positions:
            if tag_info["posicao_inicio"] <= pos_mod <= tag_info["posicao_fim"]:
                clausula_vinculada = tag_info["clausula_id"]
                break

        resultados[mod_id] = clausula_vinculada

    # Verificar resultados esperados
    assert resultados == vinculacao_esperada, "Vinculação não corresponde ao esperado"

    # Verificar casos específicos:
    # mod-1: posição 35, ANTES da primeira tag (posição 35 é o início do texto antes da tag)
    assert resultados["mod-1"] is None, "mod-1 deveria estar FORA de qualquer tag"

    # mod-2: posição 88, DENTRO da tag 1 (que vai de 35 a ~98)
    assert resultados["mod-2"] == "clausula-1", (
        "mod-2 deveria estar vinculada à clausula-1"
    )

    # mod-3: posição 180, DENTRO da tag 2 (que vai de ~100 a ~162)
    # Nota: precisamos verificar os valores exatos
    assert resultados["mod-3"] == "clausula-2", (
        "mod-3 deveria estar vinculada à clausula-2"
    )


def test_calcular_posicao_tag_removendo_marcadores(sample_data):
    """
    Testa que conseguimos calcular corretamente a posição de uma tag
    no documento original removendo os marcadores <<tag>> e <</tag>>.
    """
    documento_com_tags = sample_data["documento_com_tags"]
    documento_original = sample_data["documento_original"]

    # Exemplo: buscar a primeira tag
    # No doc com tags: "<<1>>Cláusula 1: ..."
    # No doc original: "Cláusula 1: ..."

    # Encontrar posição da tag 1 no documento com tags
    match = re.search(r"<<1>>(.*?)<<\/1>>", documento_com_tags, re.DOTALL)
    assert match is not None, "Tag 1 não encontrada no documento com tags"

    conteudo_tag = match.group(1)
    posicao_com_tags = match.start(1)  # Posição do conteúdo (após <<1>>)

    # Encontrar no documento original
    posicao_original = documento_original.find(conteudo_tag)
    assert posicao_original >= 0, "Conteúdo da tag não encontrado no original"

    # A diferença entre as posições é causada pelos marcadores de tag
    # que existem no documento com tags mas não no original
    diferenca = posicao_com_tags - posicao_original
    assert diferenca > 0, "Documento com tags deveria ter mais caracteres (as tags)"

    # Verificar que a diferença é aproximadamente o tamanho dos marcadores antes
    # Até a tag 1: "<<1>>" = 5 caracteres a mais
    assert diferenca == 5, f"Diferença deveria ser 5 caracteres, mas foi {diferenca}"


def test_integracao_completa_vinculacao(sample_data):
    """
    Teste de integração completo simulando o fluxo real:
    1. Mapear tags no documento COM tags
    2. Calcular posições no documento ORIGINAL
    3. Buscar modificações no documento ORIGINAL
    4. Vincular baseado nas posições
    """
    documento_original = sample_data["documento_original"]
    documento_com_tags = sample_data["documento_com_tags"]
    tags_esperadas = sample_data["tags_esperadas"]
    modificacoes = sample_data["modificacoes"]
    vinculacao_esperada = sample_data["vinculacao_esperada"]

    # Simular o método _vincular_modificacoes_clausulas
    tag_positions = []

    for tag in tags_esperadas:
        conteudo = tag["conteudo"]

        # Buscar no documento COM tags (onde as tags estão marcadas)
        pos_com_tags = documento_com_tags.find(conteudo)
        assert pos_com_tags >= 0, "Conteúdo não encontrado no doc com tags"

        # Buscar no documento ORIGINAL (para saber a posição real)
        pos_original = documento_original.find(conteudo)
        assert pos_original >= 0, "Conteúdo não encontrado no doc original"

        # A posição que interessa é a do documento ORIGINAL
        tag_positions.append(
            {
                "tag_nome": tag["nome"],
                "posicao_inicio": pos_original,
                "posicao_fim": pos_original + len(conteudo),
                "clausula_id": tag["clausula_id"],
            }
        )

    tag_positions.sort(key=lambda x: x["posicao_inicio"])

    # Vincular modificações
    vinculacoes = {}
    for mod in modificacoes:
        pos_mod = mod["posicao_original"]

        clausula_id = None
        for tag_info in tag_positions:
            if tag_info["posicao_inicio"] <= pos_mod <= tag_info["posicao_fim"]:
                clausula_id = tag_info["clausula_id"]
                break

        vinculacoes[mod["id"]] = clausula_id

    # Verificar resultado
    assert vinculacoes == vinculacao_esperada, (
        f"Vinculação incorreta.\nEsperado: {vinculacao_esperada}\nObtido: {vinculacoes}"
    )

    # Estatísticas
    total_mods = len(modificacoes)
    mods_vinculadas = sum(1 for v in vinculacoes.values() if v is not None)

    print(f"\n📊 Resumo: {mods_vinculadas}/{total_mods} modificações vinculadas")
    assert mods_vinculadas == 2, "Deveria ter 2 modificações vinculadas"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
