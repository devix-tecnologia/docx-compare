#!/usr/bin/env python3
"""
Teste do processamento automatico sem Flask
"""

import os
from datetime import datetime

import requests
from dotenv import load_dotenv

# Carregar configuração
load_dotenv()

# Configuração do Directus
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "g52oLdjEmwURNK4KmqjAXEtY3e4DCUzP")

DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}


def buscar_versoes_para_processar():
    """Busca versões com status 'processar'"""
    try:
        print(
            f"🔍 {datetime.now().strftime('%H:%M:%S')} - Buscando versões para processar..."
        )

        # Query com filtros
        url = f"{DIRECTUS_BASE_URL}/items/versao"
        params = {
            "filter[status][_eq]": "processar",
            "limit": 10,
            "sort": "date_created",
            "fields": "id,date_created,status,versao,observacao,contrato,versiona_ai_request_json",
        }

        print(f"🔍 URL: {url}")
        print(f"🔍 Params: {params}")

        response = requests.get(url, headers=DIRECTUS_HEADERS, params=params)

        print(f"🔍 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            versoes = data.get("data", [])

            print(f"✅ Encontradas {len(versoes)} versões para processar")

            if versoes:
                for i, versao in enumerate(versoes):
                    versao_id = versao.get("id", "N/A")
                    versao_num = versao.get("versao", "N/A")
                    contrato = versao.get("contrato", "N/A")

                    print(
                        f"  {i + 1}. {versao_id[:8]}... - {versao_num} (contrato: {contrato[:8]}...)"
                    )

                    # Analisar dados do request
                    request_data = versao.get("versiona_ai_request_json", {})
                    if request_data:
                        is_first = request_data.get("is_first_version", False)
                        tipo = request_data.get("versao_comparacao_tipo", "N/A")
                        arquivo_preenchido = request_data.get(
                            "arquivoPreenchido", "N/A"
                        )
                        arquivo_template = request_data.get("arquivoTemplate", "N/A")
                        arquivo_branco = request_data.get("arquivoBranco", "N/A")

                        print(f"     - Primeira versão: {is_first}")
                        print(f"     - Tipo comparação: {tipo}")
                        print(f"     - Arquivo preenchido: {arquivo_preenchido}")
                        print(f"     - Arquivo template: {arquivo_template}")
                        print(f"     - Arquivo branco: {arquivo_branco}")
                        print()

            return versoes
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text[:300]}")
            return []

    except Exception as e:
        print(f"❌ Erro: {e}")
        return []


def determine_original_file(versao_data):
    """Determina arquivo original baseado nos dados"""
    try:
        versao_id = versao_data["id"]
        request_data = versao_data.get("versiona_ai_request_json", {})

        print(f"🧠 Determinando arquivo original para {versao_id[:8]}...")

        if not request_data:
            raise Exception("Campo versiona_ai_request_json não encontrado")

        is_first_version = request_data.get("is_first_version", False)
        versao_comparacao_tipo = request_data.get("versao_comparacao_tipo", "")

        if is_first_version or versao_comparacao_tipo == "modelo_template":
            # Primeira versão: comparar com template
            arquivo_original = request_data.get("arquivoTemplate")
            arquivo_modificado = request_data.get("arquivoPreenchido")
            fonte = "modelo_template"
        else:
            # Versão posterior: comparar com versão anterior
            arquivo_original = request_data.get("arquivoBranco")
            arquivo_modificado = request_data.get("arquivoPreenchido")
            fonte = "versao_anterior"

        print(f"  ✅ Original: {arquivo_original}")
        print(f"  ✅ Modificado: {arquivo_modificado}")
        print(f"  ✅ Fonte: {fonte}")

        return arquivo_original, arquivo_modificado, fonte

    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return None, None, None


def main():
    """Função principal de teste"""
    print("🚀 Teste do Processamento Automático")
    print("=" * 50)

    # Buscar versões
    versoes = buscar_versoes_para_processar()

    if not versoes:
        print("😴 Nenhuma versão encontrada para processar")
        return

    print()
    print("🔍 Analisando arquivos para comparação:")
    print("-" * 40)

    for versao in versoes:
        versao_id = versao.get("id", "N/A")
        versao_num = versao.get("versao", "N/A")

        print(f"📄 Versão {versao_num} ({versao_id[:8]}...):")

        original, modificado, fonte = determine_original_file(versao)

        if original and modificado:
            print(f"  📥 Comparação: {fonte}")
            print(f"  📂 Original: {original}")
            print(f"  📝 Modificado: {modificado}")
            print("  ✅ Pronto para processar!")
        else:
            print("  ❌ Não foi possível determinar arquivos")

        print()


if __name__ == "__main__":
    main()
