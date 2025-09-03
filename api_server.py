import difflib
import html
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file

# Carregar variáveis de ambiente
load_dotenv()

print("🔧 Carregando configurações...")

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

print(f"📋 Host: {FLASK_HOST}:{FLASK_PORT}")
print(f"🔧 Debug: {FLASK_DEBUG}")

# Criar diretório de resultados se não existir
os.makedirs(RESULTS_DIR, exist_ok=True)


def is_valid_uuid(uuid_string):
    """Verifica se uma string é um UUID v4 válido."""
    try:
        uuid_obj = uuid.UUID(uuid_string, version=4)
        return str(uuid_obj) == uuid_string
    except ValueError:
        return False


def download_file_from_directus(file_id, filename_prefix="file"):
    """Baixa um arquivo do Directus usando o ID do arquivo."""
    try:
        # URL para buscar informações do arquivo
        file_info_url = urljoin(DIRECTUS_BASE_URL, f"/files/{file_id}")

        headers = {
            "Authorization": f"Bearer {DIRECTUS_TOKEN}",
            "Content-Type": "application/json",
        }

        # Buscar informações do arquivo
        response = requests.get(file_info_url, headers=headers)
        response.raise_for_status()

        file_info = response.json()["data"]
        filename = file_info.get("filename_download", f"{filename_prefix}.docx")
        filesize = file_info.get("filesize", 0)

        # Verificar tamanho do arquivo
        if filesize > MAX_FILE_SIZE:
            raise ValueError(
                f"Arquivo muito grande: {filesize} bytes (máximo: {MAX_FILE_SIZE} bytes)"
            )

        # URL para baixar o arquivo
        download_url = urljoin(DIRECTUS_BASE_URL, f"/assets/{file_id}")

        # Baixar o arquivo
        download_response = requests.get(download_url, headers=headers, stream=True)
        download_response.raise_for_status()

        # Salvar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        for chunk in download_response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()

        return temp_file.name, filename, filesize

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao baixar arquivo do Directus: {e}")
    except KeyError as e:
        raise Exception(f"Resposta inválida do Directus: {e}")
    except Exception as e:
        raise Exception(f"Erro inesperado: {e}")


def html_to_text(html_content):
    """Remove todas as tags HTML e retorna apenas o texto."""
    # Remove todas as tags HTML
    text = re.sub(r"<[^>]+>", "", html_content)
    # Decodifica entidades HTML
    text = html.unescape(text)
    # Remove espaços extras
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compare_docx_files(file1_path, file2_path):
    """Compara dois arquivos DOCX usando pandoc e retorna o resultado."""
    try:
        # Converter arquivos para texto usando pandoc
        def docx_to_text(docx_path):
            cmd = ["pandoc", docx_path, "-t", "plain"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8"
            )
            if result.returncode != 0:
                raise Exception(f"Erro ao converter {docx_path}: {result.stderr}")
            return result.stdout

        # Converter para HTML usando pandoc com filtro Lua
        def docx_to_html_with_filter(docx_path):
            cmd = ["pandoc", docx_path, "-t", "html", "--standalone"]
            if os.path.exists(LUA_FILTER_PATH):
                cmd.extend(["--lua-filter", LUA_FILTER_PATH])

            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8"
            )
            if result.returncode != 0:
                raise Exception(f"Erro ao converter {docx_path}: {result.stderr}")
            return result.stdout

        # Converter ambos os arquivos
        original_text = docx_to_text(file1_path)
        modified_text = docx_to_text(file2_path)

        # Converter para HTML para comparação visual
        original_html = docx_to_html_with_filter(file1_path)
        modified_html = docx_to_html_with_filter(file2_path)

        # Analisar diferenças
        statistics = analyze_differences(original_text, modified_text)

        # Gerar HTML de comparação
        html_result = generate_comparison_html(original_html, modified_html, statistics)

        return html_result, statistics

    except Exception as e:
        raise Exception(f"Erro na comparação: {e}")


def extract_body_content(html_file):
    """Extrai apenas o conteúdo do body do HTML."""
    with open(html_file, encoding="utf-8") as f:
        content = f.read()

    body_match = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL)
    if body_match:
        return body_match.group(1).strip()
    return content


def analyze_differences(original_text, modified_text):
    """Analisa as diferenças e extrai estatísticas detalhadas."""
    original_lines = original_text.splitlines()
    modified_lines = modified_text.splitlines()

    differ = difflib.unified_diff(original_lines, modified_lines, lineterm="")
    changes = list(differ)

    additions = sum(
        1 for line in changes if line.startswith("+") and not line.startswith("+++")
    )
    deletions = sum(
        1 for line in changes if line.startswith("-") and not line.startswith("---")
    )

    # Encontrar modificações específicas
    modifications = []
    i = 0
    while i < len(changes):
        if changes[i].startswith("-") and not changes[i].startswith("---"):
            original_line = changes[i][1:].strip()
            if (
                i + 1 < len(changes)
                and changes[i + 1].startswith("+")
                and not changes[i + 1].startswith("+++")
            ):
                modified_line = changes[i + 1][1:].strip()
                if original_line and modified_line:
                    modifications.append(
                        {"original": original_line, "modified": modified_line}
                    )
                i += 2
            else:
                i += 1
        else:
            i += 1

    return {
        "total_additions": additions,
        "total_deletions": deletions,
        "total_modifications": len(modifications),
        "modifications": modifications[:10],  # Limitar a 10 exemplos
    }


def generate_comparison_html(original_html, modified_html, statistics):
    """Gera HTML de comparação com melhor visualização."""
    # Extrair texto limpo para comparação
    original_text = html_to_text(original_html)
    modified_text = html_to_text(modified_html)

    # Comparar linha por linha
    original_lines = original_text.split("\n")
    modified_lines = modified_text.split("\n")

    differ = difflib.unified_diff(original_lines, modified_lines, lineterm="", n=3)
    diff_lines = list(differ)

    # CSS melhorado
    css = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .title {
            color: #007acc;
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }
        .subtitle {
            color: #666;
            font-size: 16px;
            margin: 5px 0 0 0;
        }
        .statistics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            display: block;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .comparison-section {
            margin: 30px 0;
        }
        .section-title {
            color: #333;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .diff-container {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
        }
        .diff-line {
            margin: 2px 0;
            padding: 2px 5px;
            border-radius: 3px;
        }
        .diff-added {
            background-color: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }
        .diff-removed {
            background-color: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }
        .diff-context {
            color: #6c757d;
        }
        .modifications-list {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }
        .modification-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .modification-item:last-child {
            border-bottom: none;
        }
        .modification-original {
            background: #fff3cd;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px 0;
            border-left: 4px solid #ffc107;
        }
        .modification-new {
            background: #d1ecf1;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px 0;
            border-left: 4px solid #17a2b8;
        }
        .timestamp {
            color: #6c757d;
            font-size: 14px;
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
    </style>
    """

    # Construir HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comparação de Documentos DOCX</title>
        {css}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">Relatório de Comparação de Documentos</h1>
                <p class="subtitle">Análise detalhada das diferenças entre os documentos</p>
            </div>
            
            <div class="statistics">
                <div class="stat-card">
                    <span class="stat-number">{statistics["total_additions"]}</span>
                    <span class="stat-label">Adições</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{statistics["total_deletions"]}</span>
                    <span class="stat-label">Remoções</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{statistics["total_modifications"]}</span>
                    <span class="stat-label">Modificações</span>
                </div>
            </div>
    """

    # Seção de modificações específicas
    if statistics["modifications"]:
        html_content += """
            <div class="comparison-section">
                <h2 class="section-title">Principais Modificações</h2>
                <div class="modifications-list">
        """

        for i, mod in enumerate(statistics["modifications"]):
            html_content += f"""
                <div class="modification-item">
                    <strong>Modificação {i + 1}:</strong>
                    <div class="modification-original">
                        <strong>Original:</strong> {html.escape(mod["original"])}
                    </div>
                    <div class="modification-new">
                        <strong>Modificado:</strong> {html.escape(mod["modified"])}
                    </div>
                </div>
            """

        html_content += """
                </div>
            </div>
        """

    # Seção de diff completo
    html_content += """
        <div class="comparison-section">
            <h2 class="section-title">Diferenças Detalhadas</h2>
            <div class="diff-container">
    """

    for line in diff_lines:
        if line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            html_content += (
                f'<div class="diff-line diff-added">+ {html.escape(line[1:])}</div>'
            )
        elif line.startswith("-"):
            html_content += (
                f'<div class="diff-line diff-removed">- {html.escape(line[1:])}</div>'
            )
        elif line.startswith("@@"):
            html_content += f'<div class="diff-line diff-context"><strong>{html.escape(line)}</strong></div>'
        else:
            html_content += (
                f'<div class="diff-line diff-context">{html.escape(line)}</div>'
            )

    html_content += f"""
            </div>
        </div>
        
        <div class="timestamp">
            Relatório gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
        </div>
    </div>
    </body>
    </html>
    """

    return html_content


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
    """Endpoint principal para comparar dois documentos DOCX."""
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

        original_id = data["original_file_id"]
        modified_id = data["modified_file_id"]

        # Validar UUIDs
        if not is_valid_uuid(original_id) or not is_valid_uuid(modified_id):
            return jsonify(
                {"success": False, "error": "IDs devem ser UUIDs v4 válidos"}
            ), 400

        # Baixar arquivos do Directus
        original_path, original_filename, original_size = download_file_from_directus(
            original_id, "original"
        )
        modified_path, modified_filename, modified_size = download_file_from_directus(
            modified_id, "modified"
        )

        try:
            # Comparar arquivos
            html_result, statistics = compare_docx_files(original_path, modified_path)

            # Salvar resultado
            result_id = str(uuid.uuid4())
            result_filename = f"comparison_result_{result_id}.html"
            result_path = os.path.join(RESULTS_DIR, result_filename)

            with open(result_path, "w", encoding="utf-8") as f:
                f.write(html_result)

            # Construir URL do resultado
            result_url = f"http://{FLASK_HOST}:{FLASK_PORT}/results/{result_filename}"

            # Resposta de sucesso
            response = {
                "success": True,
                "result_url": result_url,
                "original_file": {
                    "id": original_id,
                    "filename": original_filename,
                    "size_bytes": original_size,
                },
                "modified_file": {
                    "id": modified_id,
                    "filename": modified_filename,
                    "size_bytes": modified_size,
                },
                "statistics": statistics,
                "generated_at": datetime.now().isoformat(),
            }

            return jsonify(response)

        finally:
            # Limpar arquivos temporários
            for temp_file in [original_path, modified_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass

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
    print("🔄 Executando como script principal...")

    # Verificar dependências
    if not os.path.exists(LUA_FILTER_PATH):
        print(f"⚠️  AVISO: Filtro Lua não encontrado em '{LUA_FILTER_PATH}'")

    print("🚀 Iniciando API do Comparador de Documentos DOCX")
    print(f"📁 Diretório de resultados: {RESULTS_DIR}")
    print(f"🔗 Directus URL: {DIRECTUS_BASE_URL}")
    print(f"🌐 Servidor: http://{FLASK_HOST}:{FLASK_PORT}")
    print("📊 Endpoints disponíveis:")
    print("   GET  /health - Verificação de saúde")
    print("   POST /compare - Comparar documentos")
    print("   GET  /results/<filename> - Servir resultados")
    print("   GET  /config - Verificar configuração")
    print("🔥 Iniciando servidor Flask...")

    try:
        app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback

        traceback.print_exc()
