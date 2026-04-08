"""
Servidor API para integração com Directus
"""

import logging
import os
import sys
from datetime import datetime

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS


# Classes simplificadas para desenvolvimento
class DirectusIntegration:
    def __init__(self):
        self.base_url = "http://localhost:8055"
        self.api_token = os.getenv("DIRECTUS_TOKEN", "")

    def conectar(self):
        """Conecta com o Directus e valida a conexão"""
        # Simula conexão bem-sucedida por enquanto
        return True

    def get_document(self, doc_id):
        """Simula obtenção de documento do Directus"""
        return {
            "id": doc_id,
            "title": f"Documento {doc_id}",
            "content": f"Este é o conteúdo do documento {doc_id} obtido do Directus.",
            "original_content": f"Conteúdo original do documento {doc_id}",
            "modified_content": f"Conteúdo modificado do documento {doc_id} com algumas alterações importantes.",
        }


class DocxUtils:
    @staticmethod
    def extract_text(file_path):
        """Simula extração de texto"""
        return f"Texto extraído de {file_path}"

    @staticmethod
    def compare_texts(text1, text2):
        """Simula comparação de textos"""
        lines1 = text1.split("\n")
        lines2 = text2.split("\n")

        diff_html = "<div class='diff-container'>"
        max_lines = max(len(lines1), len(lines2))

        for i in range(max_lines):
            line1 = lines1[i] if i < len(lines1) else ""
            line2 = lines2[i] if i < len(lines2) else ""

            if line1 != line2:
                if line1:
                    diff_html += f"<div class='diff-removed'>- {line1}</div>"
                if line2:
                    diff_html += f"<div class='diff-added'>+ {line2}</div>"
            else:
                diff_html += f"<div class='diff-unchanged'>{line1}</div>"

        diff_html += "</div>"

        return {"original": text1, "modified": text2, "diff_html": diff_html}


class ProcessadorTags:
    """Classe simplificada para processamento de tags"""

    def processar(self, _text):
        """Simula processamento de tags"""
        return ["tag1", "tag2"]

    def processar_documento(self, _conteudo_original, _conteudo_modificado):
        """Simula processamento de documento"""
        return {"success": True, "modificacoes": [], "documento_id": "mock_doc"}


class AgrupadorPosicional:
    """Classe simplificada para agrupamento posicional"""

    def agrupar(self, modificacoes):
        """Simula agrupamento de modificações"""
        return modificacoes

    def agrupar_modificacoes(self, modificacoes):
        """Simula agrupamento de modificações com método específico"""
        return modificacoes


# Adicionar o caminho do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração da aplicação Flask
app = Flask(__name__)
CORS(app)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Template HTML simples para quando acessar diretamente a URL
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Versiona AI - Diff Viewer</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .diff-link {
            background: #4f46e5;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
            margin: 10px 0;
        }
        .diff-link:hover {
            background: #3730a3;
        }
        .info {
            background: #eff6ff;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Versiona AI - Diff Viewer</h1>
            <p>Visualizador de Diferenças de Documentos do Directus</p>
        </div>

        <div class="info">
            <h3>📋 Informações do Diff</h3>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>Total de Documentos:</strong> {{ total_docs }}</p>
            <p><strong>Total de Modificações:</strong> {{ total_mods }}</p>
        </div>

        <div style="text-align: center;">
            <a href="{{ viewer_url }}" class="diff-link">
                🔍 Abrir Visualizador Interativo
            </a>
        </div>

        <div style="margin-top: 30px;">
            <h3>📊 APIs Disponíveis:</h3>
            <ul>
                <li><code>GET /api/documents</code> - Lista documentos do Directus</li>
                <li><code>GET /api/diff/{doc_id}</code> - Diff de um documento específico</li>
                <li><code>POST /api/process</code> - Processa diff de novos documentos</li>
                <li><code>GET /view/{diff_id}</code> - Visualiza diff em HTML</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""


class DiffAPI:
    def __init__(self):
        """Inicializa a API com conexões necessárias"""
        self.directus = DirectusIntegration()
        self.processador = ProcessadorTags()
        self.agrupador = AgrupadorPosicional()
        self.diffs_cache = {}  # Cache para diffs processados

    def conectar_directus(self):
        """Conecta com o Directus e valida a conexão"""
        try:
            if self.directus.conectar():
                logger.info("✅ Conectado ao Directus com sucesso")
                return True
            else:
                logger.error("❌ Falha ao conectar com Directus")
                return False
        except Exception as e:
            logger.error(f"❌ Erro na conexão Directus: {e}")
            return False

    def obter_documentos(self):
        """Obtém lista de documentos do Directus"""
        try:
            # Implementar busca de documentos do Directus
            # Por enquanto, retorna dados mock
            return {
                "success": True,
                "documentos": [
                    {
                        "id": "doc_001",
                        "titulo": "Contrato v1.0 vs v2.0",
                        "data_criacao": "2025-09-11T10:00:00Z",
                        "status": "processado",
                        "versao_original": "1.0",
                        "versao_modificada": "2.0",
                    },
                    {
                        "id": "doc_002",
                        "titulo": "Política de Privacidade v2.1 vs v2.2",
                        "data_criacao": "2025-09-12T14:30:00Z",
                        "status": "pendente",
                        "versao_original": "2.1",
                        "versao_modificada": "2.2",
                    },
                ],
            }
        except Exception as e:
            logger.error(f"Erro ao obter documentos: {e}")
            return {"success": False, "error": str(e)}

    def processar_diff(
        self, doc_id=None, conteudo_original=None, conteudo_modificado=None
    ):
        """Processa diff de documentos"""
        try:
            # Se doc_id fornecido, buscar do Directus
            if doc_id:
                # TODO: Implementar busca real do Directus
                conteudo_original = self._get_conteudo_mock("original")
                conteudo_modificado = self._get_conteudo_mock("modificado")

            # Processar tags e diferenças
            resultado = self.processador.processar_documento(
                conteudo_original, conteudo_modificado
            )

            # Agrupar modificações
            if resultado.get("success"):
                modificacoes_agrupadas = self.agrupador.agrupar_modificacoes(
                    resultado["modificacoes"]
                )

                # Preparar dados para o frontend
                diff_data = {
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "total_documentos": 1,
                        "versao_sistema": "2.0.0",
                    },
                    "documentos": [
                        {
                            "id": doc_id or "temp_doc",
                            "estatisticas": {
                                "total_modificacoes": len(modificacoes_agrupadas),
                                "total_blocos": 1,
                                "tempo_processamento": 0.025,
                            },
                            "conteudo_comparacao": {
                                "original": conteudo_original,
                                "modificado": conteudo_modificado,
                                "diff_highlights": self._criar_highlights(
                                    modificacoes_agrupadas
                                ),
                            },
                            "modificacoes": modificacoes_agrupadas,
                        }
                    ],
                }

                # Salvar no cache
                diff_id = f"diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.diffs_cache[diff_id] = diff_data

                return {
                    "success": True,
                    "diff_id": diff_id,
                    "data": diff_data,
                    "viewer_url": f"http://localhost:3001?diff_id={diff_id}",
                }

            return {"success": False, "error": "Falha no processamento"}

        except Exception as e:
            logger.error(f"Erro ao processar diff: {e}")
            return {"success": False, "error": str(e)}

    def _get_conteudo_mock(self, tipo):
        """Retorna conteúdo mock para demonstração"""
        if tipo == "original":
            return """Contrato de Prestação de Serviços

O presente contrato estabelece que o prazo para entrega será de 30 dias úteis a partir da assinatura, com {{valor}} especificado no anexo I.

As condições de pagamento seguem o cronograma estabelecido no documento principal.

Cláusula 1: Objeto do contrato
Cláusula 2: Prazo de execução
Cláusula 3: Valor e forma de pagamento"""
        else:
            return """Contrato de Prestação de Serviços

O presente contrato estabelece que o prazo para entrega alterado será de 30 dias corridos a partir da assinatura, com {{preco}} especificado no anexo I.

As condições de pagamento seguem o cronograma estabelecido no documento principal.

Cláusula 1: Objeto do contrato revisado
Cláusula 2: Prazo de execução estendido
Cláusula 3: Valor e forma de pagamento atualizada
Cláusula 4: Nova cláusula de garantias"""

    def _criar_highlights(self, modificacoes):
        """Cria highlights para o diff visual"""
        highlights = []
        for mod in modificacoes:
            highlights.append(
                {
                    "tipo": mod.get("tipo", "alteracao"),
                    "inicio": mod.get("posicao", {}).get("offset", 0),
                    "fim": mod.get("posicao", {}).get("offset", 0) + 10,
                    "texto_original": mod.get("conteudo", {}).get("original", ""),
                    "texto_novo": mod.get("conteudo", {}).get("novo", ""),
                    "confianca": mod.get("confianca", 0.9),
                }
            )
        return highlights


# Instância da API
diff_api = DiffAPI()


# Rotas da API
@app.route("/health", methods=["GET"])
def health_check():
    """Health check da API"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
        }
    )


@app.route("/api/connect", methods=["POST"])
def conectar():
    """Conecta com o Directus"""
    resultado = diff_api.conectar_directus()
    return jsonify(
        {
            "success": resultado,
            "message": "Conectado ao Directus" if resultado else "Falha na conexão",
        }
    )


@app.route("/api/documents", methods=["GET"])
def listar_documentos():
    """Lista documentos disponíveis do Directus"""
    resultado = diff_api.obter_documentos()
    return jsonify(resultado)


@app.route("/api/versoes", methods=["GET"])
def listar_versoes():
    """Lista versões disponíveis (alias para documents)"""
    # Retorna o mesmo formato que o frontend espera
    resultado = diff_api.obter_documentos()
    # Convertendo para o formato esperado pelo frontend
    return jsonify({"versoes": resultado.get("documentos", [])})


@app.route("/api/diff/<doc_id>", methods=["GET"])
def obter_diff(doc_id):
    """Obtém diff de um documento específico"""
    resultado = diff_api.processar_diff(doc_id=doc_id)
    return jsonify(resultado)


@app.route("/api/process", methods=["POST"])
def processar_novo_diff():
    """Processa diff de novos documentos"""
    dados = request.get_json()

    resultado = diff_api.processar_diff(
        conteudo_original=dados.get("original"),
        conteudo_modificado=dados.get("modificado"),
    )

    return jsonify(resultado)


@app.route("/view/<diff_id>", methods=["GET"])
def visualizar_diff(diff_id):
    """Serve página HTML para visualizar diff"""
    if diff_id not in diff_api.diffs_cache:
        return jsonify({"error": "Diff não encontrado"}), 404

    diff_data = diff_api.diffs_cache[diff_id]
    doc = diff_data["documentos"][0]

    return render_template_string(
        HTML_TEMPLATE,
        timestamp=diff_data["metadata"]["timestamp"],
        total_docs=diff_data["metadata"]["total_documentos"],
        total_mods=doc["estatisticas"]["total_modificacoes"],
        viewer_url=f"http://localhost:3001?diff_id={diff_id}",
    )


@app.route("/api/data/<diff_id>", methods=["GET"])
def obter_dados_diff(diff_id):
    """Retorna dados JSON do diff para o frontend"""
    if diff_id not in diff_api.diffs_cache:
        return jsonify({"error": "Diff não encontrado"}), 404

    return jsonify(diff_api.diffs_cache[diff_id])


@app.route("/", methods=["GET"])
def index():
    """Página inicial da API"""
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().isoformat(),
        total_docs=0,
        total_mods=0,
        viewer_url="http://localhost:3001",
    )


if __name__ == "__main__":
    print("🚀 Iniciando Versiona AI API...")
    print("📋 Endpoints disponíveis:")
    print("   - http://localhost:5000/health")
    print("   - http://localhost:5000/api/documents")
    print("   - http://localhost:5000/api/diff/{doc_id}")
    print("   - http://localhost:5000/view/{diff_id}")
    print("🔗 Frontend Vue: http://localhost:3001")

    app.run(debug=True, host="0.0.0.0", port=5000)
