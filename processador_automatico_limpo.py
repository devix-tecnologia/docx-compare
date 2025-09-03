#!/usr/bin/env python3
"""
Processador Automático de Versões para Directus - Versão Limpa
"""
import os
import sys
import threading
import time
import signal
import requests
import tempfile
import subprocess
import uuid
import re
from datetime import datetime
from flask import Flask, jsonify, send_file, send_from_directory
from dotenv import load_dotenv

# Carregar configuração
load_dotenv()

# Configuração
DIRECTUS_BASE_URL = os.getenv('DIRECTUS_BASE_URL', 'https://contract.devix.co')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN', 'g52oLdjEmwURNK4KmqjAXEtY3e4DCUzP')

print(f"🔧 Inicializando cliente HTTP para Directus:")
print(f"   URL: {DIRECTUS_BASE_URL}")
print(f"   Token: {DIRECTUS_TOKEN[:10]}...")

DIRECTUS_HEADERS = {
    'Authorization': f'Bearer {DIRECTUS_TOKEN}',
    'Content-Type': 'application/json'
}

print("✅ Cliente HTTP inicializado")

# Diretórios
RESULTS_DIR = "results"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Flask app
app = Flask(__name__)

# Variáveis de controle
running = True
processor_thread = None

def buscar_versoes_para_processar():
    """Busca versões com status 'processar' no Directus"""
    try:
        print(f"🔍 {datetime.now().strftime('%H:%M:%S')} - Buscando versões para processar...")
        
        # Query com filtros
        url = f"{DIRECTUS_BASE_URL}/items/versao"
        params = {
            'filter[status][_eq]': 'processar',
            'limit': 10,
            'sort': 'date_created',
            'fields': 'id,date_created,status,versao,observacao,contrato,versiona_ai_request_json'
        }
        
        response = requests.get(url, headers=DIRECTUS_HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            versoes = data.get('data', [])
            print(f"✅ Encontradas {len(versoes)} versões para processar")
            
            if versoes:
                ids = [v.get('id', 'N/A')[:8] + '...' for v in versoes]
                print(f"📋 IDs encontrados: {', '.join(ids)}")
            
            return versoes
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text[:200]}")
            return []
        
    except Exception as e:
        print(f"❌ Erro ao buscar versões: {e}")
        return []

def determine_original_file_id(versao_data):
    """Determina arquivo original baseado no campo versiona_ai_request_json"""
    try:
        versao_id = versao_data['id']
        request_data = versao_data.get('versiona_ai_request_json', {})
        
        print(f"🧠 Determinando arquivo original para versão {versao_id[:8]}...")
        
        if not request_data:
            raise Exception("Campo versiona_ai_request_json não encontrado")
        
        is_first_version = request_data.get('is_first_version', False)
        versao_comparacao_tipo = request_data.get('versao_comparacao_tipo', '')
        
        if is_first_version or versao_comparacao_tipo == 'modelo_template':
            # Primeira versão: comparar com template
            arquivo_original = request_data.get('arquivoTemplate')
            if arquivo_original:
                print(f"📄 Primeira versão - usando arquivoTemplate: {arquivo_original}")
                return arquivo_original, "modelo_template"
        else:
            # Versão posterior: comparar com versão anterior (arquivoBranco)
            arquivo_original = request_data.get('arquivoBranco')
            if arquivo_original:
                print(f"📄 Versão posterior - usando arquivoBranco: {arquivo_original}")
                return arquivo_original, "versao_anterior"
        
        raise Exception("Não foi possível encontrar arquivo original nos dados da versão")
        
    except Exception as e:
        raise Exception(f"Erro ao determinar arquivo original: {e}")

def download_file_from_directus(file_path):
    """Baixa um arquivo do Directus usando o caminho do arquivo"""
    try:
        print(f"📥 Baixando arquivo {file_path[:50]}...")
        
        # Construir URL completa para download
        if file_path.startswith('/directus/uploads/'):
            file_id = file_path.replace('/directus/uploads/', '')
        else:
            file_id = file_path
            
        download_url = f"{DIRECTUS_BASE_URL}/assets/{file_id}"
        
        # Fazer o download do arquivo
        response = requests.get(download_url, headers=DIRECTUS_HEADERS)
        
        if response.status_code == 200:
            # Criar arquivo temporário com extensão correta
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_file.write(response.content)
            temp_file.close()
            
            print(f"✅ Arquivo baixado: {temp_file.name} (tamanho: {len(response.content)} bytes)")
            return temp_file.name
        else:
            raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
        
    except Exception as e:
        raise Exception(f"Erro ao baixar arquivo {file_path}: {e}")

def update_versao_status(versao_id, status, result_url=None, total_modifications=0, error_message=None):
    """Atualiza o status da versão e adiciona observações"""
    try:
        print(f"📝 Atualizando status da versão {versao_id[:8]}... para '{status}'...")
        
        if status == "concluido":
            observacao = f"Comparação concluída em {datetime.now().strftime('%d/%m/%Y %H:%M')}. " \
                        f"Total de modificações encontradas: {total_modifications}. " \
                        f"Resultado disponível em: {result_url}"
        elif status == "erro":
            observacao = f"Erro no processamento em {datetime.now().strftime('%d/%m/%Y %H:%M')}: {error_message}"
        else:
            observacao = f"Status atualizado para '{status}' em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        update_data = {
            "status": status,
            "observacao": observacao
        }
        
        # Atualizar versão usando HTTP request direto
        update_url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
        response = requests.patch(update_url, headers=DIRECTUS_HEADERS, json=update_data)
        
        if response.status_code == 200:
            print(f"✅ Versão atualizada com status '{status}'")
            return response.json().get('data', {})
        else:
            print(f"❌ Erro ao atualizar versão: HTTP {response.status_code} - {response.text[:200]}")
            return None
        
    except Exception as e:
        print(f"❌ Erro ao atualizar versão: {e}")
        return None

def processar_versao(versao_data):
    """Processa uma versão específica"""
    versao_id = versao_data['id']
    
    try:
        print(f"\n🚀 Processando versão {versao_id[:8]}...")
        
        # Atualizar status para 'processando'
        update_versao_status(versao_id, "processando")
        
        # 1. Determinar arquivo original e modificado
        original_file_path, original_source = determine_original_file_id(versao_data)
        
        # Obter arquivo modificado (preenchido) dos dados de request
        versao_request = versao_data.get('versiona_ai_request_json', {})
        modified_file_path = versao_request.get('arquivoPreenchido')
        
        if not modified_file_path:
            raise Exception('Versão não possui arquivoPreenchido nos dados de request')
        
        print(f"📁 Original: {original_file_path} (fonte: {original_source})")
        print(f"📄 Modificado: {modified_file_path}")
        
        # 2. Baixar arquivos
        original_path = download_file_from_directus(original_file_path)
        modified_path = download_file_from_directus(modified_file_path)
        
        try:
            # 3. Gerar comparação HTML usando o CLI existente
            result_id = str(uuid.uuid4())
            result_filename = f"comparison_{result_id}.html"
            result_path = os.path.join(RESULTS_DIR, result_filename)
            
            print(f"🔄 Executando comparação visual usando CLI...")
            
            # Executar o docx_diff_viewer.py para HTML visual
            cmd = [
                'python', 'docx_diff_viewer.py',
                original_path,
                modified_path, 
                result_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f'Erro na comparação: {result.stderr}')
            
            print(f"✅ Comparação concluída: {result_filename}")
            
            # 4. Contar modificações no HTML gerado
            total_modifications = 0
            try:
                with open(result_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Contar spans com classes de modificação
                    total_modifications = len(re.findall(r'<span[^>]*class[^>]*insertion[^>]*>', content))
                    total_modifications += len(re.findall(r'<span[^>]*class[^>]*deletion[^>]*>', content))
            except:
                total_modifications = 0
            
            # 5. URL do resultado
            result_url = f"http://127.0.0.1:5005/outputs/{result_filename}"
            
            # 6. Atualizar status para concluído
            update_versao_status(versao_id, "concluido", result_url, total_modifications)
            
            print(f"🎉 Versão {versao_id[:8]}... processada com sucesso!")
            
        finally:
            # Limpeza dos arquivos temporários
            try:
                os.unlink(original_path)
                os.unlink(modified_path)
            except:
                pass
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erro ao processar versão {versao_id[:8]}...: {error_msg}")
        update_versao_status(versao_id, "erro", error_message=error_msg)

def processor_loop():
    """Loop principal do processador"""
    global running
    
    while running:
        try:
            versoes = buscar_versoes_para_processar()
            
            if versoes:
                for versao in versoes:
                    if not running:
                        break
                    processar_versao(versao)
            else:
                print(f"😴 {datetime.now().strftime('%H:%M:%S')} - Nenhuma versão para processar")
            
            # Aguardar 1 minuto antes da próxima verificação
            for _ in range(60):
                if not running:
                    break
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Erro no loop do processador: {e}")
            time.sleep(10)  # Aguardar um pouco antes de tentar novamente
    
    print("🔄 Loop do processador finalizado")

# Flask endpoints
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "directus_url": DIRECTUS_BASE_URL,
        "processor_running": running,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/status')
def status():
    return jsonify({
        "processor_running": running,
        "directus_connected": True,  # Podemos melhorar isso testando a conexão
        "results_directory": RESULTS_DIR,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/outputs/<filename>')
def get_result(filename):
    result_path = os.path.join('outputs', filename)
    if os.path.exists(result_path):
        return send_file(result_path, mimetype='text/html')
    else:
        return jsonify({"error": "Arquivo não encontrado"}), 404

# Signal handlers
def signal_handler(signum, frame):
    global running, processor_thread
    
    print(f"\n🛑 Recebido {signal.Signals(signum).name} - Iniciando encerramento gracioso...")
    running = False
    
    if processor_thread and processor_thread.is_alive():
        print("⏳ Aguardando thread do processador terminar...")
        processor_thread.join(timeout=10)
        print("✅ Thread do processador terminada")
    
    print("✅ Aplicação encerrada graciosamente!")
    sys.exit(0)

def main():
    global processor_thread
    
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if hasattr(signal, 'SIGHUP'):
        signal.signal(signal.SIGHUP, signal_handler)
    
    print("🚀 Processador Automático de Versões")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")
    print("🌐 Servidor de monitoramento: http://127.0.0.1:5005")
    print("⏰ Verificação automática a cada 1 minuto")
    print("🔒 Monitoramento de sinais ativo (SIGINT, SIGTERM, SIGHUP)")
    print()
    print("📋 Endpoints de monitoramento:")
    print("  • GET  /health - Verificação de saúde")
    print("  • GET  /status - Status do processador")
    print("  • GET  /outputs/<filename> - Visualizar resultados")
    print()
    
    # Iniciar thread do processador
    processor_thread = threading.Thread(target=processor_loop, daemon=True)
    processor_thread.start()
    
    print("🔄 Processador automático iniciado!")
    
    # Iniciar servidor Flask
    app.run(host='127.0.0.1', port=5005, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
