#!/usr/bin/env python3
"""
API simples para comparação de documentos DOCX
Baixa arquivos do Directus e executa docx_diff_viewer.py
"""

import os
import uuid
import tempfile
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurações
DIRECTUS_BASE_URL = os.getenv('DIRECTUS_BASE_URL', 'https://your-directus-instance.com')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN', 'your-directus-token')
RESULTS_DIR = os.getenv('RESULTS_DIR', 'results')

# Configurações do Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5001'))

# Criar diretório de resultados
os.makedirs(RESULTS_DIR, exist_ok=True)

def download_file_from_directus(file_id):
    """Baixa um arquivo do Directus e salva temporariamente"""
    try:
        # URL para baixar o arquivo
        download_url = urljoin(DIRECTUS_BASE_URL, f"/assets/{file_id}")
        
        headers = {
            'Authorization': f'Bearer {DIRECTUS_TOKEN}'
        }
        
        # Baixar o arquivo
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Salvar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        raise Exception(f"Erro ao baixar arquivo {file_id}: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Verificação de saúde"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/compare', methods=['POST'])
def compare():
    """Compara dois documentos DOCX"""
    try:
        data = request.get_json()
        
        if not data or 'original_file_id' not in data or 'modified_file_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Campos obrigatórios: original_file_id, modified_file_id'
            }), 400
        
        original_id = data['original_file_id']
        modified_id = data['modified_file_id']
        
        print(f"🔄 Baixando arquivos do Directus...")
        
        # Baixar arquivos do Directus
        original_path = download_file_from_directus(original_id)
        modified_path = download_file_from_directus(modified_id)
        
        try:
            # Gerar nome único para o resultado
            result_id = str(uuid.uuid4())
            result_filename = f"comparison_{result_id}.html"
            result_path = os.path.join(RESULTS_DIR, result_filename)
            
            print(f"� Executando comparação...")
            
            # Executar o docx_diff_viewer.py
            cmd = [
                'python', 'docx_diff_viewer.py',
                original_path,
                modified_path, 
                result_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return jsonify({
                    'success': False,
                    'error': f'Erro na comparação: {result.stderr}'
                }), 500
            
            # URL do resultado
            result_url = f"http://{FLASK_HOST}:{FLASK_PORT}/results/{result_filename}"
            
            print(f"✅ Comparação concluída: {result_url}")
            
            return jsonify({
                'success': True,
                'result_url': result_url,
                'result_filename': result_filename,
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            # Limpar arquivos temporários
            for temp_file in [original_path, modified_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
                    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/results/<filename>', methods=['GET'])
def serve_result(filename):
    """Serve o arquivo HTML de resultado"""
    try:
        file_path = os.path.join(RESULTS_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(file_path, mimetype='text/html')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 API Simples de Comparação de Documentos")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")
    print(f"🌐 Servidor: http://{FLASK_HOST}:{FLASK_PORT}")
    
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
