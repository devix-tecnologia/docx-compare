#!/usr/bin/env python3
"""
Carrega seed de dados extraídos da produção no Directus E2E.

Le arquivo JSON gerado por extrair_dados_producao.py e popula o Directus E2E
com modelo, tags, cláusulas, versão e modificações.

Uso:
    python seed_directus_e2e.py --input seed/contrato_producao.json
    python seed_directus_e2e.py --input arquivo.json --directus-url http://localhost:8065
"""

import argparse
import json
import sys
from pathlib import Path

import requests

# Configuração do Directus E2E (padrão)
DIRECTUS_BASE_URL = "http://localhost:8065"
DIRECTUS_TOKEN = "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"


def criar_headers() -> dict:
    """Cria headers para autenticação no Directus"""
    return {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}",
        "Content-Type": "application/json",
    }


def verificar_conexao() -> bool:
    """Verifica se o Directus está acessível"""
    try:
        response = requests.get(f"{DIRECTUS_BASE_URL}/server/info", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False


def limpar_collection(collection: str) -> None:
    """Remove todos os itens de uma collection"""
    print(f"🗑️  Limpando collection {collection}...")

    # Buscar todos os IDs
    url = f"{DIRECTUS_BASE_URL}/items/{collection}"
    response = requests.get(
        url,
        headers=criar_headers(),
        params={"fields": "id", "limit": -1},
    )

    if response.status_code != 200:
        print(f"   ⚠️  Não foi possível buscar itens: {response.status_code}")
        return

    data = response.json()
    items = data.get("data", [])

    if not items:
        print("   ✓ Collection já está vazia")
        return

    # Deletar cada item
    for item in items:
        item_id = item["id"]
        delete_url = f"{DIRECTUS_BASE_URL}/items/{collection}/{item_id}"
        requests.delete(delete_url, headers=criar_headers())

    print(f"   ✓ {len(items)} itens removidos")


def criar_item(collection: str, data: dict, descricao: str = "") -> dict:
    """Cria um item em uma collection"""
    url = f"{DIRECTUS_BASE_URL}/items/{collection}"

    response = requests.post(
        url,
        headers=criar_headers(),
        json=data,
    )

    if response.status_code not in [200, 201]:
        print(f"   ❌ Erro ao criar {descricao}: {response.status_code}")
        print(f"   Payload: {json.dumps(data, indent=2)}")
        print(f"   Resposta: {response.text}")
        return {}

    result = response.json()
    return result.get("data", {})


def carregar_modelo(modelo_data: dict) -> dict:
    """Carrega modelo de contrato"""
    print("📋 Carregando modelo...")

    # Remover relacionamentos para criar apenas o modelo base
    modelo_limpo = {
        "id": modelo_data.get("id"),
        "nome": modelo_data.get("nome", "Modelo de Teste"),
        "versao": modelo_data.get("versao", "1.0"),
        "ativo": modelo_data.get("ativo", True),
        "descricao": modelo_data.get("descricao"),
        "arquivo_original": modelo_data.get("arquivo_original"),
        "arquivo_processado": modelo_data.get("arquivo_processado"),
    }

    modelo = criar_item("modelo_contrato", modelo_limpo, "modelo")

    if modelo:
        print(f"   ✓ Modelo criado: {modelo.get('id', '')[:8]}")

    return modelo


def carregar_clausulas(clausulas_data: list[dict]) -> dict[str, str]:
    """Carrega cláusulas e retorna mapeamento id_antigo -> id_novo"""
    print(f"📄 Carregando {len(clausulas_data)} cláusulas...")

    mapeamento = {}

    for idx, clausula in enumerate(clausulas_data, 1):
        clausula_limpa = {
            "id": clausula.get("id"),
            "numero": clausula.get("numero"),
            "nome": clausula.get("nome"),
            "objetivo": clausula.get("objetivo"),
            "referencias": clausula.get("referencias"),
            "conteudo": clausula.get("conteudo"),
        }

        nova_clausula = criar_item(
            "clausula",
            clausula_limpa,
            f"cláusula {idx}/{len(clausulas_data)}",
        )

        if nova_clausula:
            mapeamento[clausula["id"]] = nova_clausula["id"]

    print(f"   ✓ {len(mapeamento)} cláusulas criadas")
    return mapeamento


def carregar_tags(
    tags_data: list[dict],
    modelo_id: str,
    mapeamento_clausulas: dict[str, str],
) -> dict[str, str]:
    """Carrega tags vinculadas ao modelo e retorna mapeamento"""
    print(f"🏷️  Carregando {len(tags_data)} tags...")

    mapeamento = {}

    for idx, tag in enumerate(tags_data, 1):
        # Preparar dados da tag
        tag_limpa = {
            "id": tag.get("id"),
            "modelo_id": modelo_id,
            "tag_nome": tag.get("tag_nome"),
            "posicao_inicio_texto": tag.get("posicao_inicio_texto"),
            "posicao_fim_texto": tag.get("posicao_fim_texto"),
            "texto_tag": tag.get("texto_tag"),
        }

        # Mapear clausula_id se existir
        clausula_id_antigo = tag.get("clausula_id")
        if clausula_id_antigo:
            if isinstance(clausula_id_antigo, dict):
                clausula_id_antigo = clausula_id_antigo.get("id")

            if clausula_id_antigo in mapeamento_clausulas:
                tag_limpa["clausula_id"] = mapeamento_clausulas[clausula_id_antigo]

        nova_tag = criar_item("tag", tag_limpa, f"tag {idx}/{len(tags_data)}")

        if nova_tag:
            mapeamento[tag["id"]] = nova_tag["id"]

    print(f"   ✓ {len(mapeamento)} tags criadas")
    return mapeamento


def carregar_documento(documento_data: dict) -> dict:
    """Carrega documento"""
    print("📄 Carregando documento...")

    documento_limpo = {
        "id": documento_data.get("id"),
        "nome": documento_data.get("nome", "Documento de Teste"),
        "arquivo_original": documento_data.get("arquivo_original"),
        "arquivo_processado": documento_data.get("arquivo_processado"),
    }

    documento = criar_item("documento", documento_limpo, "documento")

    if documento:
        print(f"   ✓ Documento criado: {documento.get('id', '')[:8]}")

    return documento


def carregar_contrato(
    contrato_data: dict,
    modelo_id: str,
    documento_id: str,
) -> dict:
    """Carrega contrato"""
    print("📝 Carregando contrato...")

    contrato_limpo = {
        "id": contrato_data.get("id") if isinstance(contrato_data, dict) else None,
        "modelo_id": modelo_id,
        "nome": "Contrato de Teste E2E",
        "descricao": "Contrato extraído da produção para testes E2E",
    }

    contrato = criar_item("contrato", contrato_limpo, "contrato")

    if contrato:
        print(f"   ✓ Contrato criado: {contrato.get('id', '')[:8]}")

    return contrato


def carregar_versao(
    versao_data: dict,
    contrato_id: str,
    documento_id: str,
) -> dict:
    """Carrega versão"""
    print("📦 Carregando versão...")

    versao_limpa = {
        "id": versao_data.get("id"),
        "contrato_id": contrato_id,
        "documento_id": documento_id,
        "numero_versao": versao_data.get("numero_versao", "1.0"),
        "status": versao_data.get("status", "processada"),
        "tipo_processamento": versao_data.get("tipo_processamento", "ast"),
    }

    versao = criar_item("versao", versao_limpa, "versão")

    if versao:
        print(f"   ✓ Versão criada: {versao.get('id', '')[:8]}")

    return versao


def carregar_modificacoes(
    modificacoes_data: list[dict],
    versao_id: str,
    mapeamento_clausulas: dict[str, str],
) -> list[dict]:
    """Carrega modificações"""
    print(f"✏️  Carregando {len(modificacoes_data)} modificações...")

    modificacoes_criadas = []

    for idx, mod in enumerate(modificacoes_data, 1):
        mod_limpa = {
            "id": mod.get("id"),
            "versao_id": versao_id,
            "categoria": mod.get("categoria", "ALTERACAO"),
            "posicao_inicio": mod.get("posicao_inicio"),
            "posicao_fim": mod.get("posicao_fim"),
            "conteudo_json": mod.get("conteudo_json"),
        }

        # Mapear clausula_id se existir
        clausula_id_antigo = mod.get("clausula_id")
        if clausula_id_antigo:
            if isinstance(clausula_id_antigo, dict):
                clausula_id_antigo = clausula_id_antigo.get("id")

            if clausula_id_antigo in mapeamento_clausulas:
                mod_limpa["clausula_id"] = mapeamento_clausulas[clausula_id_antigo]

        nova_mod = criar_item(
            "modificacao",
            mod_limpa,
            f"modificação {idx}/{len(modificacoes_data)}",
        )

        if nova_mod:
            modificacoes_criadas.append(nova_mod)

    print(f"   ✓ {len(modificacoes_criadas)} modificações criadas")
    return modificacoes_criadas


def carregar_seed(arquivo_json: str) -> None:
    """Carrega seed completo no Directus E2E"""
    print("\n" + "=" * 60)
    print("📦 CARREGANDO SEED NO DIRECTUS E2E")
    print("=" * 60)
    print(f"Arquivo: {arquivo_json}")
    print(f"Directus: {DIRECTUS_BASE_URL}")
    print("=" * 60)
    print()

    # Verificar conexão
    print("🔌 Verificando conexão com Directus...")
    if not verificar_conexao():
        print("❌ Directus não está acessível")
        print("   Certifique-se de que o docker-compose está rodando:")
        print("   docker-compose -f docker-compose.ui-test.yml up -d")
        sys.exit(1)
    print("   ✓ Conexão estabelecida")
    print()

    # Carregar arquivo JSON
    print(f"📁 Carregando arquivo {arquivo_json}...")
    with open(arquivo_json, encoding="utf-8") as f:
        dados = json.load(f)

    print("   ✓ Arquivo carregado")
    print(f"   - Tags: {len(dados.get('tags', []))}")
    print(f"   - Cláusulas: {len(dados.get('clausulas', []))}")
    print(f"   - Modificações: {len(dados.get('modificacoes', []))}")
    print()

    # Limpar collections (ordem inversa de dependências)
    print("🗑️  Limpando dados existentes...")
    limpar_collection("modificacao")
    limpar_collection("versao")
    limpar_collection("contrato")
    limpar_collection("tag")
    limpar_collection("clausula")
    limpar_collection("modelo_contrato")
    limpar_collection("documento")
    print()

    # Carregar dados (ordem de dependências)
    modelo = carregar_modelo(dados.get("modelo", {}))
    if not modelo:
        print("❌ Falha ao criar modelo. Abortando.")
        sys.exit(1)

    clausulas_map = carregar_clausulas(dados.get("clausulas", []))
    tags_map = carregar_tags(
        dados.get("tags", []),
        modelo["id"],
        clausulas_map,
    )

    documento = carregar_documento(dados.get("documento", {}))
    if not documento:
        print("❌ Falha ao criar documento. Abortando.")
        sys.exit(1)

    contrato = carregar_contrato(
        dados.get("versao", {}).get("contrato_id", {}),
        modelo["id"],
        documento["id"],
    )
    if not contrato:
        print("❌ Falha ao criar contrato. Abortando.")
        sys.exit(1)

    versao = carregar_versao(
        dados.get("versao", {}),
        contrato["id"],
        documento["id"],
    )
    if not versao:
        print("❌ Falha ao criar versão. Abortando.")
        sys.exit(1)

    modificacoes = carregar_modificacoes(
        dados.get("modificacoes", []),
        versao["id"],
        clausulas_map,
    )

    # Sumário final
    print("\n" + "=" * 60)
    print("✅ SEED CARREGADO COM SUCESSO")
    print("=" * 60)
    print("📊 Estatísticas:")
    print(f"   - Modelo: {modelo.get('id', '')[:8]}")
    print(f"   - Cláusulas: {len(clausulas_map)}")
    print(f"   - Tags: {len(tags_map)}")
    print(f"   - Documento: {documento.get('id', '')[:8]}")
    print(f"   - Contrato: {contrato.get('id', '')[:8]}")
    print(f"   - Versão: {versao.get('id', '')[:8]}")
    print(f"   - Modificações: {len(modificacoes)}")
    print()
    print(f"🌐 Acesse o Directus: {DIRECTUS_BASE_URL}")
    print(f"🧪 Teste a versão: {versao.get('id', '')}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Carrega seed de dados da produção no Directus E2E"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Arquivo JSON com dados extraídos",
    )
    parser.add_argument(
        "--directus-url",
        default=DIRECTUS_BASE_URL,
        help=f"URL do Directus E2E (padrão: {DIRECTUS_BASE_URL})",
    )
    parser.add_argument(
        "--token",
        default=DIRECTUS_TOKEN,
        help="Token de autenticação do Directus E2E",
    )

    args = parser.parse_args()

    # Atualizar configurações globais
    global DIRECTUS_BASE_URL, DIRECTUS_TOKEN
    DIRECTUS_BASE_URL = args.directus_url
    DIRECTUS_TOKEN = args.token

    # Verificar se arquivo existe
    if not Path(args.input).exists():
        print(f"❌ Arquivo não encontrado: {args.input}")
        sys.exit(1)

    # Carregar seed
    carregar_seed(args.input)


if __name__ == "__main__":
    main()
