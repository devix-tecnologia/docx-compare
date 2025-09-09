#!/usr/bin/env python3
"""
Script direto para processar v02 e testar o sistema de agrupamento por cláusula
"""

import os
import sys
import tempfile
from datetime import datetime

import requests

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from bs4 import BeautifulSoup

from src.docx_compare.core.docx_diff_viewer import generate_diff_html
from src.docx_compare.utils.agrupador_modificacoes import AgrupadorModificacoes
from src.docx_compare.utils.text_analysis_utils import analyze_differences

# Configurações
DIRECTUS_URL = "https://contract.devix.co"
DIRECTUS_TOKEN = "PA1wND73JUkLp4ODOyRFAFPBasgTBOO0"
VERSAO_ID = "06319e34-1024-43ef-a59b-30f9ab761208"

def html_to_text(html_content):
    """Converte HTML para texto"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()

def download_file(file_id, file_path):
    """Baixa um arquivo do Directus"""
    url = f"{DIRECTUS_URL}/assets/{file_id}"
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Arquivo baixado: {file_path}")
        return True
    else:
        print(f"❌ Erro ao baixar arquivo {file_id}: {response.status_code}")
        return False

def update_versao_status(versao_id, status, observacao=None):
    """Atualiza o status da versão"""
    url = f"{DIRECTUS_URL}/items/versao/{versao_id}"
    headers = {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {"status": status}
    if observacao:
        data["observacao"] = observacao

    response = requests.patch(url, headers=headers, json=data)
    if response.status_code in [200, 204]:
        print(f"✅ Status atualizado para: {status}")
        return True
    else:
        print(f"❌ Erro ao atualizar status: {response.status_code}")
        return False

def main():
    print("🚀 Processamento direto da v02 com sistema de agrupamento")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Definir arquivos
    original_file_id = "c1d0d224-837c-455a-9e91-53933d886b63"  # v01
    modified_file_id = "00ee1aca-60a2-46f9-abfd-6cb64025d0dd"   # v02

    # Criar arquivos temporários
    original_path = tempfile.mktemp(suffix=".docx")
    modified_path = tempfile.mktemp(suffix=".docx")
    result_path = os.path.join("results", f"diff_v02_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    try:
        # 1. Baixar arquivos
        print(f"📥 Baixando arquivo original: {original_file_id}")
        if not download_file(original_file_id, original_path):
            return False

        print(f"📥 Baixando arquivo modificado: {modified_file_id}")
        if not download_file(modified_file_id, modified_path):
            return False

        # 2. Atualizar status para processando
        update_versao_status(VERSAO_ID, "processando", "Processamento local com sistema de agrupamento")

        # 3. Gerar comparação
        print("🔄 Gerando comparação visual...")
        os.makedirs("results", exist_ok=True)
        stats = generate_diff_html(original_path, modified_path, result_path)
        print(f"✅ Comparação gerada: {stats}")

        # 4. Ler HTMLs gerados para análise
        with open(result_path, encoding="utf-8") as f:
            full_html = f.read()

        # Extrair partes original e modificada
        soup = BeautifulSoup(full_html, "html.parser")
        original_section = soup.find("div", {"id": "original"})
        modified_section = soup.find("div", {"id": "modified"})

        original_html = str(original_section) if original_section else ""
        modified_html = str(modified_section) if modified_section else ""

        original_text = html_to_text(original_html)
        modified_text = html_to_text(modified_html)

        # 5. Analisar diferenças
        print("🔍 Analisando diferenças...")
        stats_detailed = analyze_differences(original_text, modified_text)
        modifications = stats_detailed["details"]

        print(f"📊 Encontradas {len(modifications)} modificações")
        for i, mod in enumerate(modifications[:3]):  # Mostrar apenas as primeiras 3
            print(f"   {i+1}. {mod.get('tipo', 'N/A')}: {mod.get('conteudo_novo', 'N/A')[:50]}...")

        # 6. TESTE DO AGRUPAMENTO POR CLÁUSULA
        print("\n🎯 TESTANDO AGRUPAMENTO POR CLÁUSULA")
        print("=" * 50)

        # Criar instância do agrupador
        agrupador = AgrupadorModificacoes(DIRECTUS_URL, DIRECTUS_TOKEN)

        # Processar agrupamento da versão
        resultado = agrupador.processar_agrupamento_versao(VERSAO_ID, threshold=0.6, dry_run=True)

        print("� Resultado do agrupamento:")
        print(f"   ✅ Sucesso: {resultado.get('success', False)}")
        print(f"   � Clausulas criadas/atualizadas: {resultado.get('clausulas_criadas', 0)}")
        print(f"   � Modificações vinculadas: {resultado.get('modificacoes_vinculadas', 0)}")

        if resultado.get("clausulas_detalhes"):
            print("\n📄 Detalhes das cláusulas:")
            for i, clausula in enumerate(resultado["clausulas_detalhes"][:3]):  # Mostrar apenas as 3 primeiras
                print(f"   {i+1}. {clausula.get('tag', 'N/A')}: {len(clausula.get('modificacoes', []))} modificações")

        # 7. Atualizar status para concluído
        clausulas_count = resultado.get("clausulas_criadas", 0)
        observacao = f"Processamento local concluído em {datetime.now().strftime('%d/%m/%Y %H:%M')} - {clausulas_count} cláusulas agrupadas"
        update_versao_status(VERSAO_ID, "concluido", observacao)

        print("\n✅ Processamento concluído com sucesso!")
        print(f"📄 Relatório salvo em: {result_path}")
        print(f"📊 Total: {len(modifications)} modificações → {clausulas_count} cláusulas")

        return True

    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        update_versao_status(VERSAO_ID, "erro", f"Erro no processamento local: {str(e)}")
        return False

    finally:
        # Limpar arquivos temporários
        for path in [original_path, modified_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
