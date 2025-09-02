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
DIRECTUS_BASE_URL = os.getenv('DIRECTUS_BASE_URL', 'https://your-directus-instance.com').replace('/admin/', '/').rstrip('/')
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN', 'your-directus-token')
RESULTS_DIR = os.getenv('RESULTS_DIR', 'results')

# Configurações do Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5001'))

# Criar diretório de resultados
os.makedirs(RESULTS_DIR, exist_ok=True)

def download_file_from_directus(file_id):
    """Baixa um arquivo do Directus usando a API REST"""
    try:
        # URL para baixar o arquivo - usando a URL base sem /admin/
        download_url = f"{DIRECTUS_BASE_URL}/assets/{file_id}"
        
        headers = {
            'Authorization': f'Bearer {DIRECTUS_TOKEN}'
        }
        
        print(f"🔗 Baixando de: {download_url}")
        print(f"🔑 Token: {DIRECTUS_TOKEN[:10]}...")
        
        # Baixar o arquivo
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Salvar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        
        print(f"✅ Arquivo baixado: {temp_file.name}")
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

@app.route('/results/<path:filename>', methods=['GET'])
def serve_result(filename):
    """Serve o arquivo HTML de resultado"""
    try:
        # Proteção contra path traversal - validação rigorosa
        import re
        from urllib.parse import unquote
        
        # Decodificar URL encoding
        filename = unquote(filename)
        
        # Normalizar o path para detectar tentativas de traversal
        normalized_filename = os.path.normpath(filename)
        
        # Verificar se contém sequências de path traversal
        if '..' in normalized_filename or '/' in normalized_filename or '\\' in normalized_filename:
            return jsonify({'error': 'Acesso negado: path traversal detectado'}), 403
        
        # Permitir apenas caracteres seguros no nome do arquivo
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', normalized_filename):
            return jsonify({'error': 'Nome de arquivo contém caracteres inválidos'}), 400
        
        # Verificar se termina com .html (apenas arquivos HTML são permitidos)
        if not normalized_filename.lower().endswith('.html'):
            return jsonify({'error': 'Apenas arquivos HTML são permitidos'}), 400
        
        # Verificar comprimento do nome do arquivo (evitar nomes muito longos)
        if len(normalized_filename) > 255:
            return jsonify({'error': 'Nome de arquivo muito longo'}), 400
        
        # Construir caminho seguro usando apenas o nome do arquivo
        safe_filename = os.path.basename(normalized_filename)
        file_path = os.path.join(RESULTS_DIR, safe_filename)
        
        # Verificar se o caminho resolvido ainda está dentro do diretório results
        results_abs_path = os.path.abspath(RESULTS_DIR)
        file_abs_path = os.path.abspath(file_path)
        
        if not file_abs_path.startswith(results_abs_path + os.sep):
            return jsonify({'error': 'Acesso negado: arquivo fora do diretório permitido'}), 403
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Verificar se é realmente um arquivo (não um diretório)
        if not os.path.isfile(file_path):
            return jsonify({'error': 'Recurso não é um arquivo válido'}), 400
        
        return send_file(file_path, mimetype='text/html')
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 API Simples de Comparação de Documentos")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")
    print(f"🌐 Servidor: http://{FLASK_HOST}:{FLASK_PORT}")
    
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
