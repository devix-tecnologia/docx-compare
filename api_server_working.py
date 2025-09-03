#!/usr/bin/env python3
"""
API de Comparação de Documentos DOCX - Versão funcional
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurações
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://your-directus-instance.com")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "your-directus-token")
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
LUA_FILTER_PATH = os.getenv("LUA_FILTER_PATH", "comments_html_filter_direct.lua")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB padrão

# Configurações do Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Criar diretório de resultados se não existir
os.makedirs(RESULTS_DIR, exist_ok=True)


@app.route("/health", methods=["GET"])
def health():
    """Endpoint de verificação de saúde da API."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "docx-compare-api",
        }
    )


@app.route("/config", methods=["GET"])
def config():
    """Retorna a configuração atual da API."""
    return jsonify(
        {
            "directus_base_url": DIRECTUS_BASE_URL,
            "results_directory": RESULTS_DIR,
            "lua_filter_path": LUA_FILTER_PATH,
            "lua_filter_exists": os.path.exists(LUA_FILTER_PATH),
            "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        }
    )


@app.route("/compare", methods=["POST"])
def compare():
    """Endpoint de comparação básico - funcionalidade a ser implementada."""
    try:
        # Validar JSON
        if not request.is_json:
            return jsonify(
                {"success": False, "error": "Content-Type deve ser application/json"}
            ), 400

        data = request.get_json()

        # Validar campos obrigatórios
        if "original_file_id" not in data or "modified_file_id" not in data:
            return jsonify(
                {
                    "success": False,
                    "error": "Campos obrigatórios: original_file_id, modified_file_id",
                }
            ), 400

        # Por enquanto, retornar resposta simulada
        return jsonify(
            {
                "success": True,
                "message": "Endpoint /compare funcionando! Funcionalidade completa será implementada.",
                "received_data": data,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify(
            {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}
        ), 500


@app.route("/results/<filename>", methods=["GET"])
def serve_result(filename):
    """Serve os arquivos de resultado HTML."""
    try:
        # Validar nome do arquivo para segurança
        if ".." in filename or "/" in filename:
            return jsonify({"error": "Nome de arquivo inválido"}), 400

        file_path = os.path.join(RESULTS_DIR, filename)

        if not os.path.exists(file_path):
            return jsonify({"error": "Arquivo não encontrado"}), 404

        return send_file(file_path, mimetype="text/html")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Iniciando API do Comparador de Documentos DOCX")
    print(f"📁 Diretório de resultados: {RESULTS_DIR}")
    print(f"🔗 Directus URL: {DIRECTUS_BASE_URL}")
    print(f"🌐 Servidor: http://{FLASK_HOST}:{FLASK_PORT}")
    print("📊 Endpoints disponíveis:")
    print("   GET  /health - Verificação de saúde")
    print("   POST /compare - Comparar documentos (básico)")
    print("   GET  /results/<filename> - Servir resultados")
    print("   GET  /config - Verificar configuração")

    try:
        app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback

        traceback.print_exc()
