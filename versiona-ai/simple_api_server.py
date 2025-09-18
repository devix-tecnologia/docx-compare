"""
Servidor API simplificado para teste com o frontend Vue
"""

import uuid
from datetime import datetime

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cache de diffs para simular persistência
diff_cache = {}


class SimpleAPI:
    def __init__(self):
        self.connected = False

    def connect_directus(self, base_url, token):
        """Simula conexão com Directus"""
        if base_url and token:
            self.connected = True
            return {"status": "success", "message": "Conectado ao Directus"}
        return {"status": "error", "message": "URL ou token inválidos"}

    def get_documents(self):
        """Retorna lista simulada de documentos"""
        return [
            {"id": "1", "title": "Documento 1", "updated": "2024-01-15"},
            {"id": "2", "title": "Documento 2", "updated": "2024-01-16"},
            {"id": "3", "title": "Documento 3", "updated": "2024-01-17"},
        ]

    def process_document(self, doc_id):
        """Processa um documento e gera diff"""
        # Simula processamento
        original_text = f"""Este é o documento {doc_id} original.
Contém várias linhas de texto.
Algumas informações importantes estão aqui.
Final do documento original."""

        modified_text = f"""Este é o documento {doc_id} modificado.
Contém várias linhas de texto alterado.
Algumas informações MUITO importantes estão aqui.
Nova linha adicionada.
Final do documento modificado."""

        # Gerar diff HTML simples
        diff_html = self.generate_diff_html(original_text, modified_text)

        # Gerar ID único para o diff
        diff_id = str(uuid.uuid4())

        # Armazenar no cache
        diff_cache[diff_id] = {
            "id": diff_id,
            "doc_id": doc_id,
            "original": original_text,
            "modified": modified_text,
            "diff_html": diff_html,
            "created_at": datetime.now().isoformat(),
            "url": f"http://localhost:8000/view/{diff_id}",
        }

        return diff_cache[diff_id]

    def generate_diff_html(self, original, modified):
        """Gera HTML de diff simples"""
        orig_lines = original.split("\n")
        mod_lines = modified.split("\n")

        html = "<div class='diff-container'>"
        max_lines = max(len(orig_lines), len(mod_lines))

        for i in range(max_lines):
            orig_line = orig_lines[i] if i < len(orig_lines) else ""
            mod_line = mod_lines[i] if i < len(mod_lines) else ""

            if orig_line != mod_line:
                if orig_line:
                    html += f"<div class='diff-removed'>- {orig_line}</div>"
                if mod_line:
                    html += f"<div class='diff-added'>+ {mod_line}</div>"
            else:
                html += f"<div class='diff-unchanged'>{orig_line}</div>"

        html += "</div>"
        return html


# Instância da API
api = SimpleAPI()

# Template HTML para visualização
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Diff Viewer - {{ diff_id }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        .diff-container {
            font-family: monospace;
            line-height: 1.4;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #fafafa;
            padding: 10px;
        }
        .diff-added {
            background-color: #d4edda;
            color: #155724;
            padding: 2px 4px;
            margin: 1px 0;
        }
        .diff-removed {
            background-color: #f8d7da;
            color: #721c24;
            padding: 2px 4px;
            margin: 1px 0;
        }
        .diff-unchanged {
            padding: 2px 4px;
            margin: 1px 0;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-right: 10px;
        }
        .tab.active {
            border-bottom-color: #007bff;
            color: #007bff;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .text-content {
            white-space: pre-wrap;
            font-family: monospace;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Comparação de Documento</h1>
            <p><strong>ID:</strong> {{ diff_id }}</p>
            <p><strong>Documento:</strong> {{ doc_id }}</p>
            <p><strong>Gerado em:</strong> {{ created_at }}</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="showTab('diff')">Diferenças</div>
            <div class="tab" onclick="showTab('original')">Original</div>
            <div class="tab" onclick="showTab('modified')">Modificado</div>
        </div>

        <div id="diff-tab" class="tab-content active">
            <h3>Diferenças Encontradas</h3>
            {{ diff_html|safe }}
        </div>

        <div id="original-tab" class="tab-content">
            <h3>Texto Original</h3>
            <div class="text-content">{{ original }}</div>
        </div>

        <div id="modified-tab" class="tab-content">
            <h3>Texto Modificado</h3>
            <div class="text-content">{{ modified }}</div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');

            // Add active class to clicked tab
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""


# Rotas da API
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route("/api/connect", methods=["POST"])
def connect():
    data = request.json
    base_url = data.get("base_url")
    token = data.get("token")

    result = api.connect_directus(base_url, token)
    return jsonify(result)


@app.route("/api/documents", methods=["GET"])
def get_documents():
    documents = api.get_documents()
    return jsonify({"documents": documents})


@app.route("/api/process", methods=["POST"])
def process_document():
    data = request.json
    doc_id = data.get("doc_id")

    if not doc_id:
        return jsonify({"error": "doc_id é obrigatório"}), 400

    result = api.process_document(doc_id)
    return jsonify(result)


@app.route("/view/<diff_id>", methods=["GET"])
def view_diff(diff_id):
    if diff_id not in diff_cache:
        return "Diff não encontrado", 404

    diff_data = diff_cache[diff_id]
    return render_template_string(HTML_TEMPLATE, **diff_data)


@app.route("/api/data/<diff_id>", methods=["GET"])
def get_diff_data(diff_id):
    if diff_id not in diff_cache:
        return jsonify({"error": "Diff não encontrado"}), 404

    return jsonify(diff_cache[diff_id])


if __name__ == "__main__":
    print("🚀 Servidor API iniciado em http://localhost:8000")
    print("📊 Health check: http://localhost:8000/health")
    print("🔗 Frontend deve conectar em: http://localhost:8000")
    app.run(debug=True, host="0.0.0.0", port=8000)
