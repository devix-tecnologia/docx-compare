"""
Script para processar versão usando implementação AST e gravar no Directus.

Uso:
    python test_ast_with_directus.py <modelo_id> <versao_id>

Exemplo:
    python test_ast_with_directus.py d2699a57-b0ff-472b-a130-626f5fc2852b 322e56c0-4b38-4e62-b563-8f29a131889c
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from directus_server import DirectusAPI

# Configuração do Directus
DIRECTUS_URL = os.getenv("DIRECTUS_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "")

DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}


def baixar_arquivo_directus(file_id: str) -> str:
    """Baixa arquivo do Directus e retorna caminho temporário."""
    url = f"{DIRECTUS_URL}/assets/{file_id}"
    print(f"📥 Baixando arquivo {file_id}...")

    response = requests.get(url, headers=DIRECTUS_HEADERS)
    if response.status_code != 200:
        raise RuntimeError(f"Erro ao baixar arquivo: HTTP {response.status_code}")

    # Salvar em arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
        f.write(response.content)
        temp_path = f.name

    print(f"✅ Arquivo salvo em: {temp_path}")
    return temp_path


def buscar_modelo_directus(modelo_id: str) -> dict:
    """Busca dados do modelo no Directus."""
    url = f"{DIRECTUS_URL}/items/modelo_contrato/{modelo_id}"
    params = {"fields": "id,nome,arquivo_original,arquivo_com_tags,texto_original"}

    print(f"🔍 Buscando modelo {modelo_id}...")
    response = requests.get(url, headers=DIRECTUS_HEADERS, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Erro ao buscar modelo: HTTP {response.status_code}")

    return response.json()["data"]


def buscar_versao_directus(versao_id: str) -> dict:
    """Busca dados da versão no Directus."""
    url = f"{DIRECTUS_URL}/items/versao/{versao_id}"
    params = {"fields": "id,versao,contrato,arquivo,modifica_arquivo,status"}

    print(f"🔍 Buscando versão {versao_id}...")
    response = requests.get(url, headers=DIRECTUS_HEADERS, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Erro ao buscar versão: HTTP {response.status_code}")

    return response.json()["data"]


def gravar_modificacoes_directus(
    versao_id: str, modificacoes: list, metricas: dict
) -> dict:
    """
    Grava modificações no Directus.

    Estrutura:
    - Atualiza versão com métricas
    - Cria registros de modificações vinculadas
    """
    print(f"\n📝 Gravando {len(modificacoes)} modificações no Directus...")

    # Atualizar versão com métricas
    versao_update = {
        "total_modificacoes": metricas["total_modificacoes"],
        "alteracoes": metricas["alteracoes"],
        "remocoes": metricas["remocoes"],
        "insercoes": metricas["insercoes"],
        "metodo_deteccao": "AST_PANDOC",
        "status": "processada",
    }

    url_versao = f"{DIRECTUS_URL}/items/versao/{versao_id}"
    response = requests.patch(url_versao, headers=DIRECTUS_HEADERS, json=versao_update)

    if response.status_code not in [200, 204]:
        print(f"⚠️ Erro ao atualizar versão: HTTP {response.status_code}")
        print(f"Resposta: {response.text}")
    else:
        print("✅ Versão atualizada com métricas")

    # Criar registros de modificações
    modificacoes_criadas = []
    for mod in modificacoes:
        mod_data = {
            "versao": versao_id,
            "tipo": mod["tipo"],
            "confianca": mod.get("confianca", 0.9),
            "clausula_original": mod.get("clausula_original"),
            "clausula_modificada": mod.get("clausula_modificada"),
            "conteudo_original": mod.get("conteudo", {}).get("original"),
            "conteudo_novo": mod.get("conteudo", {}).get("novo"),
            "posicao_linha": mod.get("posicao", {}).get("linha"),
            "posicao_coluna": mod.get("posicao", {}).get("coluna"),
        }

        # Limpar campos None
        mod_data = {k: v for k, v in mod_data.items() if v is not None}

        url_mod = f"{DIRECTUS_URL}/items/modificacao"
        response = requests.post(url_mod, headers=DIRECTUS_HEADERS, json=mod_data)

        if response.status_code in [200, 201]:
            modificacoes_criadas.append(response.json()["data"])
            print(f"  ✅ Modificação #{mod['id']} ({mod['tipo']}) criada")
        else:
            print(
                f"  ⚠️ Erro ao criar modificação #{mod['id']}: HTTP {response.status_code}"
            )

    return {
        "versao_atualizada": True,
        "modificacoes_criadas": len(modificacoes_criadas),
        "modificacoes": modificacoes_criadas,
    }


def processar_versao_com_ast(modelo_id: str, versao_id: str):
    """Processa versão usando AST e grava resultados no Directus."""

    print("=" * 100)
    print("🚀 PROCESSAMENTO COM AST + GRAVAÇÃO NO DIRECTUS")
    print("=" * 100)
    print(f"Modelo ID: {modelo_id}")
    print(f"Versão ID: {versao_id}")
    print()

    try:
        # 1. Buscar dados do Directus
        modelo = buscar_modelo_directus(modelo_id)
        versao = buscar_versao_directus(versao_id)

        print(f"\n📋 Modelo: {modelo.get('nome', 'N/A')}")
        print(f"📋 Versão: {versao.get('versao', 'N/A')}")

        # 2. Baixar arquivos
        arquivo_original_id = modelo.get("arquivo_com_tags") or modelo.get(
            "arquivo_original"
        )
        arquivo_modificado_id = versao.get("modifica_arquivo") or versao.get("arquivo")

        if not arquivo_original_id or not arquivo_modificado_id:
            raise RuntimeError("Arquivos não encontrados no Directus")

        original_docx = baixar_arquivo_directus(arquivo_original_id)
        modified_docx = baixar_arquivo_directus(arquivo_modificado_id)

        # 3. Processar com AST via API
        print("\n" + "=" * 100)
        print("🔬 PROCESSANDO COM IMPLEMENTAÇÃO AST")
        print("=" * 100)

        api = DirectusAPI()
        resultado = api.process_versao(versao_id, mock=False, use_ast=True)

        # 4. Mostrar resultados
        print("\n" + "=" * 100)
        print("📊 RESULTADOS DA ANÁLISE AST")
        print("=" * 100)

        if not resultado or "modificacoes" not in resultado:
            print("❌ Erro: Resultado vazio ou inválido")
            return None

        modificacoes = resultado.get("modificacoes", [])
        print(f"Total de modificações detectadas: {len(modificacoes)}")

        # Contar tipos
        tipos = {"ALTERACAO": 0, "REMOCAO": 0, "INSERCAO": 0}
        for mod in modificacoes:
            tipo = mod.get("tipo", "")
            if tipo in tipos:
                tipos[tipo] += 1

        print(f"  - ALTERACAO: {tipos['ALTERACAO']}")
        print(f"  - REMOCAO: {tipos['REMOCAO']}")
        print(f"  - INSERCAO: {tipos['INSERCAO']}")

        print("\n📋 Detalhes das modificações:")
        for i, mod in enumerate(modificacoes[:10], 1):  # Mostrar primeiras 10
            print(f"\n  Modificação {i} - {mod.get('tipo', 'N/A')}")
            if mod.get("clausula_original"):
                print(f"    Cláusula Original: {mod['clausula_original']}")
            if mod.get("clausula_modificada"):
                print(f"    Cláusula Modificada: {mod['clausula_modificada']}")
            conteudo = mod.get("conteudo", {})
            if conteudo.get("original"):
                print(f"    Original: {conteudo['original'][:80]}...")
            if conteudo.get("novo"):
                print(f"    Novo: {conteudo['novo'][:80]}...")

        # 5. Resultado já foi gravado no Directus pela API
        print("\n" + "=" * 100)
        print("✅ PROCESSAMENTO CONCLUÍDO!")
        print("=" * 100)
        print("Os resultados já foram gravados automaticamente no Directus.")

        print(f"Total de modificações salvas: {len(modificacoes)}")
        print(f"Versão ID: {versao_id}")

        # Limpar arquivos temporários
        Path(original_docx).unlink(missing_ok=True)
        Path(modified_docx).unlink(missing_ok=True)
        print("\n🧹 Arquivos temporários removidos")

        return resultado

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python test_ast_with_directus.py <modelo_id> <versao_id>")
        print("\nExemplo:")
        print(
            "  python test_ast_with_directus.py d2699a57-b0ff-472b-a130-626f5fc2852b 322e56c0-4b38-4e62-b563-8f29a131889c"
        )
        sys.exit(1)

    modelo_id = sys.argv[1]
    versao_id = sys.argv[2]

    # Verificar token
    if not DIRECTUS_TOKEN:
        print("❌ ERRO: DIRECTUS_TOKEN não configurado")
        print("Configure a variável de ambiente DIRECTUS_TOKEN")
        sys.exit(1)

    processar_versao_com_ast(modelo_id, versao_id)
