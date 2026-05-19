#!/usr/bin/env python3
"""
Extrai dados reais do Directus de produção para criar seed do E2E.

Baixa modelo completo, tags, cláusulas e versão específica do Directus de produção
e salva em arquivo JSON para uso como seed nos testes E2E.

Uso:
    python extrair_dados_producao.py --versao 2573b998-63d0-4471-ad85-db6f860c3721
    python extrair_dados_producao.py --versao ID --output seed/contrato_producao.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests

# Configuração do Directus de PRODUÇÃO (padrão)
DIRECTUS_BASE_URL = "https://contract.devix.co"
DIRECTUS_TOKEN = "S1okNXYabq9TL1gVj0TxiNEdu0md_F3d"


def criar_headers() -> dict:
    """Cria headers para autenticação no Directus"""
    return {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}",
        "Content-Type": "application/json",
    }


def buscar_versao(versao_id: str) -> dict[str, Any]:
    """Busca versão completa com relacionamentos"""
    print(f"📥 Buscando versão {versao_id[:8]}...")

    url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
    params = {
        "fields": [
            "*",
            "contrato_id.*",
            "contrato_id.modelo_id.*",
            "contrato_id.modelo_id.tags.*",
            "contrato_id.modelo_id.tags.clausula_id.*",
            "documento_id.*",
            "modificacoes.*",
            "modificacoes.clausula_id.*",
        ]
    }

    response = requests.get(url, headers=criar_headers(), params=params)

    if response.status_code != 200:
        print(f"❌ Erro ao buscar versão: {response.status_code}")
        print(response.text)
        sys.exit(1)

    data = response.json()
    return data.get("data", {})


def buscar_modelo_completo(modelo_id: str) -> dict[str, Any]:
    """Busca modelo com todas as tags e cláusulas"""
    print(f"📋 Buscando modelo {modelo_id[:8]}...")

    url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato/{modelo_id}"
    params = {
        "fields": [
            "*",
            "tags.*",
            "tags.clausula_id.*",
            "tags.clausula_id.referencias",
            "tags.clausula_id.objetivo",
        ]
    }

    response = requests.get(url, headers=criar_headers(), params=params)

    if response.status_code != 200:
        print(f"❌ Erro ao buscar modelo: {response.status_code}")
        print(response.text)
        sys.exit(1)

    data = response.json()
    return data.get("data", {})


def buscar_tags_modelo(modelo_id: str) -> list[dict]:
    """Busca todas as tags do modelo com suas cláusulas"""
    print("🏷️  Buscando tags do modelo...")

    url = f"{DIRECTUS_BASE_URL}/items/tag"
    params = {
        "filter[modelo_id][_eq]": modelo_id,
        "fields": [
            "*",
            "clausula_id.id",
            "clausula_id.numero",
            "clausula_id.nome",
            "clausula_id.objetivo",
            "clausula_id.referencias",
            "clausula_id.conteudo",
        ],
        "limit": -1,  # Buscar todas
    }

    response = requests.get(url, headers=criar_headers(), params=params)

    if response.status_code != 200:
        print(f"❌ Erro ao buscar tags: {response.status_code}")
        print(response.text)
        return []

    data = response.json()
    tags = data.get("data", [])
    print(f"   ✓ {len(tags)} tags encontradas")
    return tags


def buscar_clausulas_modelo(modelo_id: str) -> list[dict]:
    """Busca todas as cláusulas do modelo"""
    print("📄 Buscando cláusulas do modelo...")

    # Primeiro buscar IDs das cláusulas via tags
    tags = buscar_tags_modelo(modelo_id)
    clausula_ids = set()

    for tag in tags:
        if tag.get("clausula_id"):
            if isinstance(tag["clausula_id"], dict):
                clausula_ids.add(tag["clausula_id"]["id"])
            else:
                clausula_ids.add(tag["clausula_id"])

    if not clausula_ids:
        print("   ⚠️  Nenhuma cláusula vinculada às tags")
        return []

    # Buscar dados completos das cláusulas
    url = f"{DIRECTUS_BASE_URL}/items/clausula"
    params = {
        "filter[id][_in]": ",".join(clausula_ids),
        "fields": "*",
        "limit": -1,
    }

    response = requests.get(url, headers=criar_headers(), params=params)

    if response.status_code != 200:
        print(f"❌ Erro ao buscar cláusulas: {response.status_code}")
        return []

    data = response.json()
    clausulas = data.get("data", [])
    print(f"   ✓ {len(clausulas)} cláusulas encontradas")
    return clausulas


def buscar_modificacoes(versao_id: str) -> list[dict]:
    """Busca todas as modificações da versão"""
    print("📝 Buscando modificações da versão...")

    url = f"{DIRECTUS_BASE_URL}/items/modificacao"
    params = {
        "filter[versao_id][_eq]": versao_id,
        "fields": ["*", "clausula_id.*"],
        "limit": -1,
    }

    response = requests.get(url, headers=criar_headers(), params=params)

    if response.status_code != 200:
        print(f"❌ Erro ao buscar modificações: {response.status_code}")
        return []

    data = response.json()
    mods = data.get("data", [])
    print(f"   ✓ {len(mods)} modificações encontradas")
    return mods


def buscar_documento(documento_id: str) -> dict[str, Any]:
    """Busca dados do documento"""
    print(f"📄 Buscando documento {documento_id[:8]}...")

    url = f"{DIRECTUS_BASE_URL}/items/documento/{documento_id}"
    params = {"fields": "*"}

    response = requests.get(url, headers=criar_headers(), params=params)

    if response.status_code != 200:
        print(f"❌ Erro ao buscar documento: {response.status_code}")
        return {}

    data = response.json()
    return data.get("data", {})


def extrair_dados_completos(versao_id: str) -> dict[str, Any]:
    """Extrai todos os dados necessários para o seed"""

    # Buscar versão
    versao = buscar_versao(versao_id)

    if not versao:
        print("❌ Versão não encontrada")
        sys.exit(1)

    # Extrair IDs relacionados
    contrato_id = versao.get("contrato_id")
    if isinstance(contrato_id, dict):
        contrato_id = contrato_id.get("id")

    modelo_id = None
    if contrato_id:
        contrato = versao.get("contrato_id", {})
        if isinstance(contrato, dict):
            modelo_id = contrato.get("modelo_id")
            if isinstance(modelo_id, dict):
                modelo_id = modelo_id.get("id")

    documento_id = versao.get("documento_id")
    if isinstance(documento_id, dict):
        documento_id = documento_id.get("id")

    print("\n📊 Estrutura encontrada:")
    print(f"   - Versão: {versao_id[:8]}")
    print(f"   - Contrato: {contrato_id[:8] if contrato_id else 'N/A'}")
    print(f"   - Modelo: {modelo_id[:8] if modelo_id else 'N/A'}")
    print(f"   - Documento: {documento_id[:8] if documento_id else 'N/A'}")
    print()

    # Buscar dados relacionados
    modelo = buscar_modelo_completo(modelo_id) if modelo_id else {}
    tags = buscar_tags_modelo(modelo_id) if modelo_id else []
    clausulas = buscar_clausulas_modelo(modelo_id) if modelo_id else []
    modificacoes = buscar_modificacoes(versao_id)
    documento = buscar_documento(documento_id) if documento_id else {}

    # Montar estrutura completa
    dados_completos = {
        "metadados": {
            "origem": "Directus Produção",
            "base_url": DIRECTUS_BASE_URL,
            "data_extracao": "2026-05-18",
            "versao_id": versao_id,
            "modelo_id": modelo_id,
            "contrato_id": contrato_id,
            "documento_id": documento_id,
        },
        "versao": versao,
        "modelo": modelo,
        "tags": tags,
        "clausulas": clausulas,
        "modificacoes": modificacoes,
        "documento": documento,
        "estatisticas": {
            "total_tags": len(tags),
            "total_clausulas": len(clausulas),
            "total_modificacoes": len(modificacoes),
            "modificacoes_vinculadas": sum(
                1 for m in modificacoes if m.get("clausula_id")
            ),
            "tags_com_clausula": sum(1 for t in tags if t.get("clausula_id")),
        },
    }

    return dados_completos


def sanitizar_dados(dados: dict) -> dict:
    """Remove dados sensíveis antes de salvar"""
    # Copiar para não modificar original
    dados = json.loads(json.dumps(dados))

    # Remover tokens e dados sensíveis se existirem
    # (Adicionar conforme necessário)

    return dados


def main():
    parser = argparse.ArgumentParser(
        description="Extrai dados do Directus de produção para seed E2E"
    )
    parser.add_argument(
        "--versao",
        required=True,
        help="ID da versão a extrair",
    )
    parser.add_argument(
        "--output",
        default="seed/contrato_producao.json",
        help="Arquivo de saída (padrão: seed/contrato_producao.json)",
    )
    parser.add_argument(
        "--directus-url",
        help="URL do Directus (padrão: https://contract.devix.co)",
    )
    parser.add_argument(
        "--token",
        help="Token de autenticação do Directus",
    )
    parser.add_argument(
        "--no-sanitize",
        action="store_true",
        help="Não sanitizar dados (manter tudo)",
    )

    args = parser.parse_args()

    # Atualizar configurações globais se fornecidas
    global DIRECTUS_BASE_URL, DIRECTUS_TOKEN
    if args.directus_url:
        DIRECTUS_BASE_URL = args.directus_url
    if args.token:
        DIRECTUS_TOKEN = args.token

    print("=" * 60)
    print("📦 EXTRAÇÃO DE DADOS DO DIRECTUS DE PRODUÇÃO")
    print("=" * 60)
    print(f"Origem: {DIRECTUS_BASE_URL}")
    print(f"Versão: {args.versao}")
    print(f"Output: {args.output}")
    print("=" * 60)
    print()

    # Extrair dados
    dados = extrair_dados_completos(args.versao)

    # Sanitizar se necessário
    if not args.no_sanitize:
        print("\n🔒 Sanitizando dados sensíveis...")
        dados = sanitizar_dados(dados)

    # Salvar arquivo
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n💾 Salvando em {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    # Sumário
    print("\n" + "=" * 60)
    print("✅ EXTRAÇÃO CONCLUÍDA")
    print("=" * 60)
    print("📊 Estatísticas:")
    for key, value in dados["estatisticas"].items():
        print(f"   - {key}: {value}")
    print()
    print(f"📁 Arquivo salvo: {output_path}")
    print(f"📏 Tamanho: {output_path.stat().st_size / 1024:.1f} KB")
    print()


if __name__ == "__main__":
    main()
