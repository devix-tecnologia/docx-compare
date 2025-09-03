#!/usr/bin/env python3
"""
Teste completo de processamento - download e comparação
"""
import os
import sys
import requests
import tempfile
import subprocess
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Carregar configuração
load_dotenv()

# Configuração do Directus
DIRECTUS_BASE_URL = os.getenv('DIRECTUS_BASE_URL', 'https://contract.devix.co')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN', 'g52oLdjEmwURNK4KmqjAXEtY3e4DCUzP')

DIRECTUS_HEADERS = {
    'Authorization': f'Bearer {DIRECTUS_TOKEN}',
    'Content-Type': 'application/json'
}

# Diretórios
RESULTS_DIR = "results"

def download_file_from_directus(file_path):
    """Baixa um arquivo do Directus usando o caminho do arquivo"""
    try:
        print(f"📥 Baixando arquivo {file_path}...")
        
        # Construir URL completa para download
        if file_path.startswith('/directus/uploads/'):
            file_id = file_path.replace('/directus/uploads/', '')
        else:
            file_id = file_path
            
        download_url = f"{DIRECTUS_BASE_URL}/assets/{file_id}"
        
        print(f"  🔗 URL: {download_url}")
        
        # Fazer o download do arquivo
        response = requests.get(download_url, headers=DIRECTUS_HEADERS)
        
        if response.status_code == 200:
            # Criar arquivo temporário com extensão correta
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_file.write(response.content)
            temp_file.close()
            
            print(f"  ✅ Arquivo baixado: {temp_file.name} (tamanho: {len(response.content)} bytes)")
            return temp_file.name
        else:
            raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
        
    except Exception as e:
        raise Exception(f"Erro ao baixar arquivo {file_path}: {e}")

def processar_uma_versao(versao_data):
    """Processa uma versão específica"""
    try:
        versao_id = versao_data['id']
        versao_num = versao_data.get('versao', 'N/A')
        
        print(f"🚀 Processando versão {versao_num} ({versao_id[:8]}...)")
        
        # 1. Determinar arquivos
        request_data = versao_data.get('versiona_ai_request_json', {})
        
        if not request_data:
            raise Exception("Campo versiona_ai_request_json não encontrado")
        
        is_first_version = request_data.get('is_first_version', False)
        
        if is_first_version or request_data.get('versao_comparacao_tipo') == 'modelo_template':
            arquivo_original = request_data.get('arquivoTemplate')
            fonte = "modelo_template"
        else:
            arquivo_original = request_data.get('arquivoBranco')
            fonte = "versao_anterior"
        
        arquivo_modificado = request_data.get('arquivoPreenchido')
        
        if not arquivo_original or not arquivo_modificado:
            raise Exception("Arquivos original ou modificado não encontrados")
        
        print(f"  📂 Original ({fonte}): {arquivo_original}")
        print(f"  📝 Modificado: {arquivo_modificado}")
        
        # 2. Baixar arquivos
        print("  📥 Baixando arquivos...")
        original_path = download_file_from_directus(arquivo_original)
        modified_path = download_file_from_directus(arquivo_modificado)
        
        # 3. Verificar se arquivos foram baixados corretamente
        print(f"  🔍 Verificando arquivos baixados...")
        
        if not os.path.exists(original_path):
            raise Exception(f"Arquivo original não foi baixado: {original_path}")
            
        if not os.path.exists(modified_path):
            raise Exception(f"Arquivo modificado não foi baixado: {modified_path}")
        
        original_size = os.path.getsize(original_path)
        modified_size = os.path.getsize(modified_path)
        
        print(f"    ✅ Original: {original_size} bytes")
        print(f"    ✅ Modificado: {modified_size} bytes")
        
        # 4. Gerar comparação
        print("  🔄 Gerando comparação HTML...")
        
        result_id = str(uuid.uuid4())
        result_filename = f"comparison_{result_id}.html"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        
        # Verificar se o CLI existe
        cli_path = "docx_diff_viewer.py"
        if not os.path.exists(cli_path):
            raise Exception(f"CLI não encontrado: {cli_path}")
        
        # Executar comparação
        cmd = [
            'python', cli_path,
            original_path,
            modified_path, 
            result_path
        ]
        
        print(f"    🔧 Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        print(f"    📤 Return code: {result.returncode}")
        
        if result.stdout:
            print(f"    📝 STDOUT: {result.stdout}")
        
        if result.stderr:
            print(f"    ⚠️ STDERR: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f'Erro na comparação (code {result.returncode}): {result.stderr}')
        
        # 5. Verificar resultado
        if os.path.exists(result_path):
            result_size = os.path.getsize(result_path)
            print(f"  ✅ Resultado gerado: {result_path} ({result_size} bytes)")
            
            # Ler primeiras linhas do HTML para verificar se está ok
            with open(result_path, 'r', encoding='utf-8') as f:
                first_lines = f.read(500)
                if '<html' in first_lines.lower():
                    print("    ✅ HTML válido gerado")
                else:
                    print("    ⚠️ HTML pode estar inválido")
        else:
            raise Exception("Arquivo de resultado não foi gerado")
        
        # 6. Limpeza
        print("  🧹 Limpando arquivos temporários...")
        try:
            os.unlink(original_path)
            os.unlink(modified_path)
            print("    ✅ Arquivos temporários removidos")
        except Exception as e:
            print(f"    ⚠️ Erro na limpeza: {e}")
        
        print(f"  🎉 Versão {versao_num} processada com sucesso!")
        return result_path
        
    except Exception as e:
        print(f"  ❌ Erro ao processar versão: {e}")
        return None

def main():
    """Função principal de teste"""
    print("🚀 Teste Completo de Processamento")
    print("=" * 50)
    
    # Verificar diretório de resultados
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"📁 Diretório criado: {RESULTS_DIR}")
    
    # Buscar uma versão para testar
    try:
        url = f"{DIRECTUS_BASE_URL}/items/versao"
        params = {
            'filter[status][_eq]': 'processar',
            'limit': 1,
            'fields': 'id,versao,versiona_ai_request_json'
        }
        
        response = requests.get(url, headers=DIRECTUS_HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            versoes = data.get('data', [])
            
            if versoes:
                versao = versoes[0]
                print(f"📄 Testando com versão: {versao.get('versao', 'N/A')} ({versao.get('id', 'N/A')[:8]}...)")
                print()
                
                # Processar
                resultado = processar_uma_versao(versao)
                
                if resultado:
                    print()
                    print(f"🎉 SUCESSO! Resultado salvo em: {resultado}")
                else:
                    print()
                    print("❌ FALHA no processamento")
            else:
                print("😴 Nenhuma versão encontrada para processar")
        else:
            print(f"❌ Erro na busca: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
