"""
Testes para vinculação de modificações às cláusulas.

Este teste valida a lógica de:
1. Mapear tags no documento tagueado
2. Calcular posições das tags no documento original
3. Vincular modificações (feitas no documento original) às cláusulas baseado nas posições
"""

import json
from pathlib import Path

import pytest


def load_sample_data():
    """Carrega os dados de exemplo da pasta sample/"""
    sample_dir = Path(__file__).parent.parent / "sample"

    with open(sample_dir / "documento_original.txt", encoding="utf-8") as f:
        documento_original = f.read()

    with open(sample_dir / "documento_com_tags.txt", encoding="utf-8") as f:
        documento_com_tags = f.read()

    with open(sample_dir / "modificacoes.json", encoding="utf-8") as f:
        modificacoes = json.load(f)

    with open(sample_dir / "tags_esperadas.json", encoding="utf-8") as f:
        tags_esperadas = json.load(f)

    with open(sample_dir / "vinculacao_esperada.json", encoding="utf-8") as f:
        vinculacao_esperada = json.load(f)

    return {
        "documento_original": documento_original,
        "documento_com_tags": documento_com_tags,
        "modificacoes": modificacoes,
        "tags_esperadas": tags_esperadas,
        "vinculacao_esperada": vinculacao_esperada,
    }


def calcular_posicao_no_original(texto_com_tags, conteudo_tag, posicao_tag_no_tagueado):
    """
    Calcula a posição real do conteúdo da tag no documento original.

    A lógica é:
    1. Encontramos a tag no documento tagueado (ex: <<1>>conteudo<</1>>)
    2. Contamos quantas tags existem ANTES dessa posição
    3. A posição no original = posição no tagueado - total de caracteres de tags antes

    Args:
        texto_com_tags: Texto completo do documento com tags
        conteudo_tag: Conteúdo da cláusula (sem as tags)
        posicao_tag_no_tagueado: Posição onde a tag inicia no documento tagueado

    Returns:
        Posição no documento original
    """
    # Pega o texto antes da tag
    texto_antes = texto_com_tags[:posicao_tag_no_tagueado]

    # Conta quantos caracteres de tags existem antes
    # Tags têm formato: <<N>> e <</N>>
    import re

    tags_antes = re.findall(r"<<\d+>>|<</\d+>>", texto_antes)
    total_chars_tags = sum(len(tag) for tag in tags_antes)

    # A posição no original é a posição no tagueado menos os caracteres das tags
    posicao_no_original = posicao_tag_no_tagueado - total_chars_tags

    return posicao_no_original


def mapear_tags_com_posicoes_originais(documento_com_tags, tags_modelo):
    """
    Mapeia as tags no documento tagueado e calcula suas posições no documento original.

    Args:
        documento_com_tags: Texto do documento com tags
        tags_modelo: Lista de tags com estrutura [{"nome": "1", "conteudo": "...", "clausula_id": "..."}]

    Returns:
        Lista de dicionários com formato:
        [
            {
                "nome": "1",
                "posicao_inicio": 35,  # Posição no documento ORIGINAL
                "posicao_fim": 99,     # Posição no documento ORIGINAL
                "comprimento": 64,
                "clausula_id": "clausula-1"
            }
        ]
    """
    tag_positions = []

    for tag in tags_modelo:
        tag_nome = tag["nome"]
        conteudo = tag["conteudo"]
        clausula_id = tag["clausula_id"]

        # Encontra a posição da tag no documento TAGUEADO
        # A tag tem formato: <<N>>conteudo<</N>>
        tag_abertura = f"<<{tag_nome}>>"

        pos_abertura = documento_com_tags.find(tag_abertura)
        if pos_abertura == -1:
            continue

        # Posição do conteúdo no documento tagueado (depois de <<N>>)
        pos_conteudo_tagueado = pos_abertura + len(tag_abertura)

        # Calcula a posição no documento ORIGINAL
        pos_inicio_original = calcular_posicao_no_original(
            documento_com_tags, conteudo, pos_conteudo_tagueado
        )

        pos_fim_original = pos_inicio_original + len(conteudo)

        tag_positions.append(
            {
                "nome": tag_nome,
                "posicao_inicio": pos_inicio_original,
                "posicao_fim": pos_fim_original,
                "comprimento": len(conteudo),
                "clausula_id": clausula_id,
            }
        )

    return tag_positions


def vincular_modificacoes_clausulas(modificacoes, tag_positions, documento_original):
    """
    Vincula modificações às cláusulas baseado nas posições.

    Args:
        modificacoes: Lista de modificações com posicao_original
        tag_positions: Lista de tags com posicoes no documento original
        documento_original: Texto do documento original (para validação)

    Returns:
        Dicionário: {modificacao_id: clausula_id ou None}
    """
    vinculacao = {}

    for mod in modificacoes:
        mod_id = mod["id"]
        pos_mod = mod["posicao_original"]

        # Busca a tag que contém essa posição
        clausula_encontrada = None

        for tag in tag_positions:
            if tag["posicao_inicio"] <= pos_mod <= tag["posicao_fim"]:
                clausula_encontrada = tag["clausula_id"]
                break

        vinculacao[mod_id] = clausula_encontrada

    return vinculacao


def test_mapear_tags_documento_tagueado():
    """Testa se conseguimos mapear tags no documento tagueado"""
    data = load_sample_data()

    # Mapeia as tags
    tag_positions = mapear_tags_com_posicoes_originais(
        data["documento_com_tags"], data["tags_esperadas"]
    )

    assert len(tag_positions) == 3, (
        f"Deveria ter 3 tags, mas encontrou {len(tag_positions)}"
    )

    # Valida que todas as tags foram encontradas
    nomes_encontrados = {tag["nome"] for tag in tag_positions}
    assert nomes_encontrados == {"1", "2", "3"}


def test_calcular_posicoes_no_original():
    """Testa se as posições calculadas estão corretas no documento original"""
    data = load_sample_data()

    tag_positions = mapear_tags_com_posicoes_originais(
        data["documento_com_tags"], data["tags_esperadas"]
    )

    # Valida cada tag verificando se o conteúdo está realmente nessa posição no original
    documento_original = data["documento_original"]

    for tag in tag_positions:
        tag_info = next(t for t in data["tags_esperadas"] if t["nome"] == tag["nome"])
        conteudo_esperado = tag_info["conteudo"]

        # Extrai o texto nessa posição do documento original
        texto_na_posicao = documento_original[
            tag["posicao_inicio"] : tag["posicao_fim"]
        ]

        assert texto_na_posicao == conteudo_esperado, (
            f"Tag {tag['nome']}: "
            f"Esperava '{conteudo_esperado}' na posição {tag['posicao_inicio']}, "
            f"mas encontrou '{texto_na_posicao}'"
        )


def test_vincular_modificacoes():
    """Testa a vinculação de modificações às cláusulas"""
    data = load_sample_data()

    # 1. Mapeia as tags e calcula posições no original
    tag_positions = mapear_tags_com_posicoes_originais(
        data["documento_com_tags"], data["tags_esperadas"]
    )

    # 2. Vincula modificações
    vinculacao = vincular_modificacoes_clausulas(
        data["modificacoes"], tag_positions, data["documento_original"]
    )

    # 3. Valida resultado esperado
    vinculacao_esperada = data["vinculacao_esperada"]

    assert vinculacao == vinculacao_esperada, (
        f"Vinculação incorreta!\nEsperado: {vinculacao_esperada}\nObtido: {vinculacao}"
    )


def test_modificacao_proxima_de_clausula():
    """Testa que modificações próximas a uma cláusula são vinculadas a ela"""
    data = load_sample_data()

    tag_positions = mapear_tags_com_posicoes_originais(
        data["documento_com_tags"], data["tags_esperadas"]
    )

    vinculacao = vincular_modificacoes_clausulas(
        data["modificacoes"], tag_positions, data["documento_original"]
    )

    # mod-1 está na posição 35, logo no início da cláusula 1
    assert vinculacao["mod-1"] == "clausula-1", (
        "Modificação próxima da cláusula 1 deveria ser vinculada a ela"
    )


def test_modificacao_dentro_de_clausula():
    """Testa que modificações dentro de cláusulas são vinculadas corretamente"""
    data = load_sample_data()

    tag_positions = mapear_tags_com_posicoes_originais(
        data["documento_com_tags"], data["tags_esperadas"]
    )

    vinculacao = vincular_modificacoes_clausulas(
        data["modificacoes"], tag_positions, data["documento_original"]
    )

    # mod-2 está na posição 88, que está dentro da cláusula 1
    assert vinculacao["mod-2"] == "clausula-1", (
        "Modificação na cláusula 1 não foi vinculada"
    )

    # mod-3 está na posição 180, que agora fica mais próxima da cláusula 3
    assert vinculacao["mod-3"] == "clausula-3", (
        "Modificação na cláusula 3 não foi vinculada"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
