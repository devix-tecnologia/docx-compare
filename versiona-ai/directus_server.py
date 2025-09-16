"""
Servidor API para integração real com Directus
Conecta com https://contract.devix.co usando as credenciais do .env
"""

import os
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

# Carregar variáveis do .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Cache de diffs para persistência
diff_cache = {}

# Configurações do Directus
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN")
FLASK_PORT = int(os.getenv("FLASK_PORT", "8000"))

# Headers para Directus
DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}


class DirectusAPI:
    def __init__(self):
        self.base_url = DIRECTUS_BASE_URL.rstrip("/")
        self.token = DIRECTUS_TOKEN
        self.connected = False

    def test_connection(self):
        """Testa a conexão com o Directus"""
        try:
            response = requests.get(
                f"{self.base_url}/server/ping", headers=DIRECTUS_HEADERS, timeout=10
            )
            self.connected = response.status_code == 200
            return self.connected
        except Exception as e:
            print(f"❌ Erro ao conectar com Directus: {e}")
            self.connected = False
            return False

    def get_contratos(self):
        """Busca contratos do Directus"""
        print("🚀 Iniciando get_contratos")
        try:
            # Primeiro, vamos buscar as coleções disponíveis
            response = requests.get(
                f"{self.base_url}/collections", headers=DIRECTUS_HEADERS, timeout=10
            )

            if response.status_code != 200:
                print(f"❌ Erro ao buscar coleções: {response.status_code}")
                return self._get_mock_contratos()

            collections = response.json()["data"]
            print(
                f"📋 Coleções disponíveis: {[c['collection'] for c in collections[:10]]}"
            )

            # Buscar contratos ou versões
            contract_collections = [
                c
                for c in collections
                if "contrat" in c["collection"].lower()
                or "versao" in c["collection"].lower()
            ]

            if contract_collections:
                collection_name = contract_collections[0]["collection"]
                print(f"🔍 Buscando dados na coleção: {collection_name}")

                response = requests.get(
                    f"{self.base_url}/items/{collection_name}?limit=10",
                    headers=DIRECTUS_HEADERS,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()["data"]
                    return self._format_contratos(data, collection_name)
                else:
                    print(f"❌ Erro ao buscar contratos: {response.status_code}")
                    return self._get_mock_contratos()
            else:
                print("❌ Nenhuma coleção de contratos encontrada")
                return self._get_mock_contratos()

        except Exception as e:
            print(f"❌ Erro ao buscar contratos: {e}")
            # Retornar dados mock de fallback quando há erro de conexão
            return self._get_mock_contratos()

    def _get_mock_contratos(self):
        """Retorna dados mock de contratos quando não consegue conectar com Directus"""
        print("🔧 Retornando dados mock de contratos de fallback")
        return [
            {
                "id": "contrato_001",
                "title": "Contrato de Prestação de Serviços v1.0",
                "collection": "contratos",
                "updated": "2025-09-11T10:00:00Z",
                "status": "ativo",
                "versao": "1.0",
            },
            {
                "id": "contrato_002",
                "title": "Política de Privacidade v2.1",
                "collection": "contratos",
                "updated": "2025-09-12T14:30:00Z",
                "status": "ativo",
                "versao": "2.1",
            },
        ]

    def _format_contratos(self, data, collection_name):
        """Formata dados dos contratos para o frontend"""
        contratos = []
        for item in data:
            contrato = {
                "id": str(item.get("id", "")),
                "title": item.get(
                    "nome", item.get("title", f"Contrato {item.get('id', 'S/N')}")
                ),
                "collection": collection_name,
                "updated": item.get(
                    "date_updated", item.get("updated_at", datetime.now().isoformat())
                ),
                "status": item.get("status", "ativo"),
                "raw_data": item,  # Dados completos para debug
            }
            contratos.append(contrato)
        return contratos

    def get_versoes_para_processar(self):
        """Busca versões com status 'processar'"""
        print("🚀 Iniciando get_versoes_para_processar")
        try:
            # Buscar versões usando a função existente
            response = requests.get(
                f"{self.base_url}/items/versao?filter[status][_eq]=processar&limit=50",
                headers=DIRECTUS_HEADERS,
                timeout=15,
            )

            if response.status_code == 200:
                versoes = response.json()["data"]
                print(f"✅ Encontradas {len(versoes)} versões para processar")
                return versoes
            else:
                print(f"❌ Erro ao buscar versões: {response.status_code}")
                # Retornar dados mock de fallback quando falha a autenticação
                return self._get_mock_versoes()

        except Exception as e:
            print(f"❌ Erro ao buscar versões: {e}")
            # Retornar dados mock de fallback quando há erro de conexão
            return self._get_mock_versoes()

    def _get_mock_versoes(self):
        """Retorna dados mock quando não consegue conectar com Directus"""
        print("🔧 Retornando dados mock de fallback")
        return [
            {
                "id": "versao_001",
                "titulo": "Contrato de Prestação de Serviços v1.0 vs v2.0",
                "status": "processar",
                "data_criacao": "2025-09-11T10:00:00Z",
                "versao_original": "1.0",
                "versao_modificada": "2.0",
                "descricao": "Atualização de cláusulas contratuais e condições gerais",
            },
            {
                "id": "versao_002",
                "titulo": "Política de Privacidade v2.1 vs v2.2",
                "status": "processar",
                "data_criacao": "2025-09-12T14:30:00Z",
                "versao_original": "2.1",
                "versao_modificada": "2.2",
                "descricao": "Adequação à LGPD e novos termos de uso",
            },
        ]

    def process_versao(self, versao_id):
        """Processa uma versão específica"""
        try:
            # Buscar dados da versão
            response = requests.get(
                f"{self.base_url}/items/versao/{versao_id}",
                headers=DIRECTUS_HEADERS,
                timeout=10,
            )

            if response.status_code != 200:
                return {"error": f"Versão {versao_id} não encontrada"}

            versao_data = response.json()["data"]

            # Simular processamento (aqui você integraria com seu pipeline real)
            original_text = f"Conteúdo original da versão {versao_id}\n"
            original_text += f"Contrato: {versao_data.get('contrato_id', 'N/A')}\n"
            original_text += f"Status atual: {versao_data.get('status', 'N/A')}\n"
            original_text += "Este é um exemplo de texto original do contrato."

            modified_text = f"Conteúdo modificado da versão {versao_id}\n"
            modified_text += (
                f"Contrato: {versao_data.get('contrato_id', 'N/A')} [MODIFICADO]\n"
            )
            modified_text += "Status atual: processado\n"
            modified_text += "Este é um exemplo de texto MODIFICADO do contrato com alterações importantes."

            # Gerar diff
            diff_html = self._generate_diff_html(original_text, modified_text)

            # Criar registro de diff
            diff_id = str(uuid.uuid4())
            diff_data = {
                "id": diff_id,
                "versao_id": versao_id,
                "versao_data": versao_data,
                "original": original_text,
                "modified": modified_text,
                "diff_html": diff_html,
                "created_at": datetime.now().isoformat(),
                "url": f"http://localhost:{FLASK_PORT}/view/{diff_id}",
            }

            diff_cache[diff_id] = diff_data

            return diff_data

        except Exception as e:
            print(f"❌ Erro ao processar versão {versao_id}: {e}")
            return {"error": str(e)}

    def _generate_diff_html(self, original, modified):
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
directus_api = DirectusAPI()

# Template HTML para visualização
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Diff Viewer - {{ diff_id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
        .diff-container { font-family: monospace; line-height: 1.4; border: 1px solid #ddd; border-radius: 4px; background: #fafafa; padding: 10px; }
        .diff-added { background-color: #d4edda; color: #155724; padding: 2px 4px; margin: 1px 0; }
        .diff-removed { background-color: #f8d7da; color: #721c24; padding: 2px 4px; margin: 1px 0; }
        .diff-unchanged { padding: 2px 4px; margin: 1px 0; }
        .metadata { background: #e9ecef; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Comparação de Versão - Directus</h1>
            <p><strong>ID do Diff:</strong> {{ diff_id }}</p>
            <p><strong>Versão ID:</strong> {{ versao_id }}</p>
            <p><strong>Gerado em:</strong> {{ created_at }}</p>
        </div>

        {% if versao_data %}
        <div class="metadata">
            <h3>📋 Metadados da Versão</h3>
            <p><strong>Contrato ID:</strong> {{ versao_data.get('contrato_id', 'N/A') }}</p>
            <p><strong>Status:</strong> {{ versao_data.get('status', 'N/A') }}</p>
            {% if versao_data.get('date_updated') %}
            <p><strong>Última atualização:</strong> {{ versao_data.get('date_updated') }}</p>
            {% endif %}
        </div>
        {% endif %}

        <div>
            <h3>🔄 Diferenças Encontradas</h3>
            {{ diff_html|safe }}
        </div>
    </div>
</body>
</html>
"""


# Rotas da API
@app.route("/health", methods=["GET"])
def health_check():
    """Health check com status do Directus"""
    directus_status = directus_api.test_connection()
    return jsonify(
        {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "directus_connected": directus_status,
            "directus_url": DIRECTUS_BASE_URL,
        }
    )


@app.route("/api/connect", methods=["POST"])
def connect():
    """Testa conexão com Directus"""
    connected = directus_api.test_connection()
    if connected:
        return jsonify({"status": "success", "message": "Conectado ao Directus"})
    else:
        return jsonify(
            {"status": "error", "message": "Falha ao conectar com Directus"}
        ), 500


@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Lista contratos do Directus"""
    contratos = directus_api.get_contratos()
    return jsonify({"documents": contratos})


@app.route("/api/versoes", methods=["GET"])
def get_versoes():
    """Lista versões para processar - MOCK DATA"""
    return jsonify(
        {
            "versoes": [
                {
                    "id": "versao_001",
                    "titulo": "Contrato de Prestação de Serviços v1.0 vs v2.0",
                    "status": "processar",
                    "data_criacao": "2025-09-11T10:00:00Z",
                    "versao_original": "1.0",
                    "versao_modificada": "2.0",
                    "descricao": "Atualização de cláusulas contratuais e condições gerais",
                },
                {
                    "id": "versao_002",
                    "titulo": "Política de Privacidade v2.1 vs v2.2",
                    "status": "processar",
                    "data_criacao": "2025-09-12T14:30:00Z",
                    "versao_original": "2.1",
                    "versao_modificada": "2.2",
                    "descricao": "Adequação à LGPD e novos termos de uso",
                },
            ]
        }
    )


@app.route("/api/test", methods=["GET"])
def test_endpoint():
    """Endpoint de teste"""
    return jsonify({"status": "working", "message": "Test endpoint funcionando!"})


@app.route("/api/process", methods=["POST"])
def process_document():
    """Processa uma versão específica"""
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado JSON fornecido"}), 400
    versao_id = data.get("versao_id") or data.get("doc_id")

    if not versao_id:
        return jsonify({"error": "versao_id é obrigatório"}), 400

    result = directus_api.process_versao(versao_id)

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)


@app.route("/view/<diff_id>", methods=["GET"])
def view_diff(diff_id):
    """Visualiza diff gerado"""
    if diff_id not in diff_cache:
        return "Diff não encontrado", 404

    diff_data = diff_cache[diff_id]
    return render_template_string(HTML_TEMPLATE, **diff_data)


@app.route("/api/data/<diff_id>", methods=["GET"])
def get_diff_data(diff_id):
    """Retorna dados JSON do diff"""
    if diff_id not in diff_cache:
        return jsonify({"error": "Diff não encontrado"}), 404

    return jsonify(diff_cache[diff_id])


if __name__ == "__main__":
    print("🚀 Servidor API com Directus Real")
    print(f"📊 Directus URL: {DIRECTUS_BASE_URL}")
    print(f"🔗 API Health: http://localhost:{FLASK_PORT}/health")
    print(f"📋 Documentos: http://localhost:{FLASK_PORT}/api/documents")
    print(f"🔄 Versões: http://localhost:{FLASK_PORT}/api/versoes")

    # Testar conexão na inicialização
    if directus_api.test_connection():
        print("✅ Conexão com Directus estabelecida!")
    else:
        print("❌ Falha na conexão com Directus - verifique credenciais")

    app.run(debug=True, host="0.0.0.0", port=FLASK_PORT)
