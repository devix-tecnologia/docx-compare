#!/usr/bin/env python3
"""
Conversor de versões reais do Directus para fixtures de teste.

Baixa dados da API e gera fixture JSON com ground truth (vinculações esperadas).

Uso:
    python criar_fixture_real.py --versao 2573b998-63d0-4471-ad85-db6f860c3721
    python criar_fixture_real.py --versao VERSION_ID --output fixtures/caso_08.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

API_BASE_URL = "http://localhost:8011"
API_TOKEN = "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"


def baixar_versao(versao_id: str) -> dict[str, Any]:
    """Baixa dados da versão via API"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    print(f"📥 Baixando versão {versao_id[:8]}...")

    response = requests.get(
        f"{API_BASE_URL}/api/versoes/{versao_id}",
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception(f"Erro ao baixar versão: {response.status_code}")

    return response.json()


def baixar_arquivo_texto(arquivo_id: str) -> str:
    """Baixa conteúdo de texto de um arquivo"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    response = requests.get(
        f"{API_BASE_URL}/api/files/{arquivo_id}/text",
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception(f"Erro ao baixar arquivo {arquivo_id}: {response.status_code}")

    return response.text


def extrair_tags_modelo(versao_data: dict) -> list[dict]:
    """Extrai tags do modelo de contrato"""
    contrato = versao_data.get("contrato", {})
    modelo = contrato.get("modelo_contrato", {})
    tags = modelo.get("tags", [])

    tags_formatadas = []
    for tag in tags:
        tags_formatadas.append(
            {
                "id": tag["id"],
                "nome": tag.get("tag_nome", tag.get("id")),
                "posicao_inicio": tag.get("posicao_inicio_texto"),
                "posicao_fim": tag.get("posicao_fim_texto"),
                "texto": tag.get("texto_tag", ""),
            }
        )

    return tags_formatadas


def extrair_modificacoes(versao_data: dict) -> tuple[list[dict], list[dict]]:
    """
    Extrai modificações e cria vinculações esperadas baseado no que foi
    persistido no banco (ground truth do sistema atual).

    Returns:
        (modificacoes, vinculacoes_esperadas)
    """
    modificacoes_raw = versao_data.get("modificacoes", [])

    modificacoes = []
    vinculacoes = []

    for idx, mod in enumerate(modificacoes_raw):
        # Extrair tipo e conteúdo
        tipo = mod.get("categoria", "ALTERACAO")
        conteudo_json = mod.get("conteudo_json", {})

        conteudo = {}
        if tipo == "INSERCAO":
            conteudo["novo"] = conteudo_json.get("novo", "")
        elif tipo == "REMOCAO":
            conteudo["original"] = conteudo_json.get("original", "")
        elif tipo == "ALTERACAO":
            conteudo["original"] = conteudo_json.get("original", "")
            conteudo["novo"] = conteudo_json.get("novo", "")

        modificacoes.append(
            {
                "tipo": tipo,
                "conteudo": conteudo,
                "posicao_inicio": None,  # Será calculado pelo algoritmo
                "posicao_fim": None,
            }
        )

        # Se tem vinculação no banco, usar como ground truth
        clausula_id = mod.get("clausula")
        if clausula_id:
            vinculacoes.append(
                {
                    "modificacao_index": idx,
                    "tag_id": clausula_id,
                    "posicao_inicio_esperada": mod.get("posicao_inicio"),
                    "posicao_fim_esperada": mod.get("posicao_fim"),
                    "confianca_minima": 0.5,  # Ground truth do sistema
                    "justificativa": "Vinculação existente no banco de dados",
                }
            )

    return modificacoes, vinculacoes


def criar_fixture(
    versao_id: str,
    fixture_id: str = None,
    nivel_complexidade: str = "complexo",
) -> dict:
    """Cria fixture a partir de versão real"""

    # Baixar dados
    versao_data = baixar_versao(versao_id)

    # Baixar texto do arquivo modificado
    arquivo_novo_id = versao_data.get("arquivo")
    print(f"📄 Baixando texto do arquivo {arquivo_novo_id[:8]}...")
    texto_completo = baixar_arquivo_texto(arquivo_novo_id)

    # Extrair tags
    print("🏷️  Extraindo tags do modelo...")
    tags = extrair_tags_modelo(versao_data)

    # Extrair modificações e vinculações
    print("📝 Extraindo modificações...")
    modificacoes, vinculacoes = extrair_modificacoes(versao_data)

    # Gerar ID da fixture
    if not fixture_id:
        fixture_id = f"caso_real_{versao_id[:8]}"

    # Criar fixture
    fixture = {
        "id": fixture_id,
        "descricao": f"Caso real da versão {versao_id[:8]} - "
        f"{len(modificacoes)} modificações em {len(tags)} tags",
        "nivel_complexidade": nivel_complexidade,
        "metadados_versao": {
            "versao_id": versao_id,
            "contrato_id": versao_data.get("contrato", {}).get("id"),
            "modelo_id": versao_data.get("contrato", {})
            .get("modelo_contrato", {})
            .get("id"),
            "data_criacao": versao_data.get("date_created"),
        },
        "documento": {
            "texto_completo": texto_completo,
            "tags": tags,
        },
        "modificacoes": modificacoes,
        "vinculacoes_esperadas": vinculacoes,
        "metricas_objetivo": {
            "taxa_vinculacao_minima": 50.0 if vinculacoes else 0.0,
            "precisao_minima": 80.0,
            "recall_minimo": 80.0,
            "erro_posicao_max_chars": 50,
        },
        "notas_implementacao": [
            "Ground truth baseado em vinculações existentes no banco",
            f"Sistema original vinculou {len(vinculacoes)}/{len(modificacoes)} modificações",
            "Posições podem ter sido calculadas por método diferente",
        ],
        "metadados": {
            "criado_em": "2026-05-16",
            "autor": "Script de conversão automática",
            "validado": False,
            "requer_validacao_manual": True,
        },
    }

    return fixture


def main():
    parser = argparse.ArgumentParser(
        description="Converte versão real do Directus para fixture de teste"
    )

    parser.add_argument(
        "--versao",
        required=True,
        help="ID da versão a converter",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Arquivo de saída (padrão: fixtures/caso_real_VERSAO.json)",
    )

    parser.add_argument(
        "--id",
        help="ID da fixture (padrão: caso_real_VERSAO)",
    )

    parser.add_argument(
        "--nivel",
        choices=["simples", "medio", "complexo"],
        default="complexo",
        help="Nível de complexidade (padrão: complexo)",
    )

    args = parser.parse_args()

    try:
        # Criar fixture
        fixture = criar_fixture(
            versao_id=args.versao,
            fixture_id=args.id,
            nivel_complexidade=args.nivel,
        )

        # Determinar arquivo de saída
        if args.output:
            output_path = args.output
        else:
            output_path = Path(__file__).parent / "fixtures" / f"{fixture['id']}.json"

        # Salvar
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(fixture, f, indent=2, ensure_ascii=False)

        print("\n✅ Fixture criada com sucesso!")
        print(f"📄 Arquivo: {output_path}")
        print("\n📊 Resumo:")
        print(f"   - ID: {fixture['id']}")
        print(f"   - Nível: {fixture['nivel_complexidade']}")
        print(f"   - Tags: {len(fixture['documento']['tags'])}")
        print(f"   - Modificações: {len(fixture['modificacoes'])}")
        print(f"   - Vinculações esperadas: {len(fixture['vinculacoes_esperadas'])}")
        print("\n⚠️  IMPORTANTE: Validar manualmente ground truth antes de usar!")

        return 0

    except Exception as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
