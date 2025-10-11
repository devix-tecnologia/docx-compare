"""
Teste de integração para validar que o método _vincular_modificacoes_clausulas
está usando corretamente as posições do documento original.
"""

import json
import sys
from pathlib import Path

import pytest

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from directus_server import DirectusAPI


@pytest.fixture
def server():
    """Cria uma instância do DirectusAPI para testes."""
    return DirectusAPI()


@pytest.fixture
def sample_data():
    """Carrega dados de exemplo."""
    sample_dir = Path(__file__).parent / "sample"

    with open(sample_dir / "documento_original.txt", encoding="utf-8") as f:
        documento_original = f.read()

    with open(sample_dir / "documento_com_tags.txt", encoding="utf-8") as f:
        documento_com_tags = f.read()

    with open(sample_dir / "tags_esperadas.json", encoding="utf-8") as f:
        tags_esperadas = json.load(f)

    with open(sample_dir / "modificacoes.json", encoding="utf-8") as f:
        modificacoes_data = json.load(f)

    with open(sample_dir / "vinculacao_esperada.json", encoding="utf-8") as f:
        vinculacao_esperada = json.load(f)

    # Converter tags para o formato que o Directus retorna
    tags_modelo = []
    for tag in tags_esperadas:
        tags_modelo.append(
            {
                "tag_nome": tag["nome"],
                "conteudo": tag["conteudo"],
                "clausulas": [
                    {"id": tag["clausula_id"], "nome": f"Cláusula {tag['nome']}"}
                ],
            }
        )

    # Converter modificações para o formato esperado
    modificacoes = []
    for mod in modificacoes_data:
        modificacoes.append(
            {
                "id": mod["id"],
                "tipo": mod["tipo"],
                "conteudo": {"novo": mod["texto"]}
                if mod["tipo"] == "insert"
                else {"original": mod["texto"]},
            }
        )

    return {
        "documento_original": documento_original,
        "documento_com_tags": documento_com_tags,
        "tags_modelo": tags_modelo,
        "modificacoes": modificacoes,
        "vinculacao_esperada": vinculacao_esperada,
    }


def test_vincular_modificacoes_usa_posicoes_corretas(server, sample_data):
    """
    Testa que _vincular_modificacoes_clausulas calcula corretamente
    as posições das tags no documento original.
    """
    resultado = server._vincular_modificacoes_clausulas(
        modificacoes=sample_data["modificacoes"],
        tags_modelo=sample_data["tags_modelo"],
        texto_com_tags=sample_data["documento_com_tags"],
        texto_original=sample_data["documento_original"],
    )

    # Verificar vinculações
    vinculacoes = {}
    for mod in resultado:
        vinculacoes[mod["id"]] = mod.get("clausula_id")

    print(f"\n📊 Vinculações obtidas: {vinculacoes}")
    print(f"📊 Vinculações esperadas: {sample_data['vinculacao_esperada']}")

    assert vinculacoes == sample_data["vinculacao_esperada"], (
        f"Vinculação incorreta.\nEsperado: {sample_data['vinculacao_esperada']}\nObtido: {vinculacoes}"
    )


def test_tags_sao_mapeadas_no_documento_original(server, sample_data, capfd):
    """
    Testa que as tags são mapeadas com posições do documento ORIGINAL,
    não do documento com tags.
    """
    server._vincular_modificacoes_clausulas(
        modificacoes=sample_data["modificacoes"],
        tags_modelo=sample_data["tags_modelo"],
        texto_com_tags=sample_data["documento_com_tags"],
        texto_original=sample_data["documento_original"],
    )

    # Capturar output
    captured = capfd.readouterr()

    # Verificar que os prints mostram posições corretas
    # Tag 1 deve estar na posição 32 do original (não 37 do doc com tags)
    assert "posição 32 do original" in captured.out, "Tag 1 deveria estar na posição 32"

    # Tag 2 deve estar na posição 99 do original (não 115 do doc com tags)
    assert "posição 99 do original" in captured.out, "Tag 2 deveria estar na posição 99"

    # Tag 3 deve estar na posição 159 do original (não 186 do doc com tags)
    assert "posição 159 do original" in captured.out, (
        "Tag 3 deveria estar na posição 159"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
