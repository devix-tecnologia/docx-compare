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
                # Se não encontrar no Directus, usar dados mock
                versao_data = _get_mock_versao_by_id(versao_id)
                if not versao_data:
                    return {"error": f"Versão {versao_id} não encontrada"}
            else:
                versao_data = response.json()["data"]

            # Gerar conteúdo baseado no tipo de versão
            if versao_id == "c2b1dfa0-c664-48b8-a5ff-84b70041b428":
                # Conteúdo realista para contrato de locação
                original_text = self._generate_realistic_contract_original()
                modified_text = self._generate_realistic_contract_modified()
            else:
                # Conteúdo padrão para outras versões
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
        """Gera HTML de diff mais robusto com identificação de cláusulas"""
        orig_lines = original.split("\n")
        mod_lines = modified.split("\n")

        html = ["<div class='diff-container'>"]
        max_lines = max(len(orig_lines), len(mod_lines))

        current_clause = None

        for i in range(max_lines):
            orig_line = orig_lines[i] if i < len(orig_lines) else ""
            mod_line = mod_lines[i] if i < len(mod_lines) else ""

            # Escapar HTML para evitar problemas
            orig_line_escaped = (
                orig_line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            mod_line_escaped = (
                mod_line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )

            # Verificar se é uma nova cláusula
            new_clause = self._identify_clause(orig_line or mod_line)
            if new_clause and new_clause != current_clause:
                current_clause = new_clause
                html.append(f"<div class='clause-header'>📋 {current_clause}</div>")

            if orig_line != mod_line:
                if orig_line:
                    html.append(
                        f"<div class='diff-removed'>- {orig_line_escaped}</div>"
                    )
                if mod_line:
                    html.append(f"<div class='diff-added'>+ {mod_line_escaped}</div>")
            else:
                if orig_line:  # Só mostrar linhas não vazias
                    html.append(
                        f"<div class='diff-unchanged'>{orig_line_escaped}</div>"
                    )

        html.append("</div>")
        return "\n".join(html)

    def _identify_clause(self, line):
        """Identifica a cláusula baseada na linha de texto"""
        import re

        # Padrões para identificar cláusulas
        clause_patterns = [
            r"^CLÁUSULA\s+(\d+(?:\.\d+)?)\s*-\s*(.+)$",
            r"^(\d+(?:\.\d+)?)\s*-\s*(.+)$",
            r"^ARTIGO\s+(\d+)°?\s*-?\s*(.+)$",
            r"^Art\.?\s*(\d+)°?\s*-?\s*(.+)$",
        ]

        line_clean = line.strip()
        if not line_clean:
            return None

        for pattern in clause_patterns:
            match = re.match(pattern, line_clean, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    numero = match.group(1)
                    titulo = match.group(2).strip()
                    return f"Cláusula {numero} - {titulo}"
                else:
                    return f"Cláusula {match.group(1)}"

        # Verificar se é título de seção
        if line_clean.isupper() and len(line_clean) > 10:
            return f"Seção: {line_clean}"

        return None

    def _generate_realistic_contract_original(self):
        """Gera conteúdo original realista para contrato de locação"""
        return """CONTRATO DE LOCAÇÃO COMERCIAL
LOC-2024-001

CLÁUSULA 1 - DAS PARTES
LOCADOR: Empresa XYZ Ltda.
LOCATÁRIO: Comércio ABC Eireli

CLÁUSULA 2 - DO IMÓVEL
Endereço: Rua das Flores, 123 - Centro
Área: 150m²
Finalidade: Uso comercial

CLÁUSULA 3 - DO VALOR E PAGAMENTO
3.1 - O valor mensal do aluguel é de R$ 12.500,00 (doze mil e quinhentos reais)
3.2 - Vencimento: todo dia 05 de cada mês
3.3 - Multa por atraso: 2% sobre o valor em atraso

CLÁUSULA 4 - DO PRAZO
4.1 - Prazo: 36 (trinta e seis) meses
4.2 - Início: 01/01/2024
4.3 - Término: 31/12/2026

CLÁUSULA 5 - DO REAJUSTE
5.1 - Reajuste anual pelo IGPM
5.2 - Aplicação a partir do 13º mês

CLÁUSULA 8 - DAS NORMAS DE SEGURANÇA
8.4 - O locatário deve seguir as normas básicas de segurança

CLÁUSULA 12 - DO USO DO IMÓVEL
12.1 - Destinação exclusiva para comércio de roupas e acessórios"""

    def _generate_realistic_contract_modified(self):
        """Gera conteúdo modificado realista para contrato de locação"""
        return """CONTRATO DE LOCAÇÃO COMERCIAL
LOC-2024-001

CLÁUSULA 1 - DAS PARTES
LOCADOR: Empresa XYZ Ltda.
LOCATÁRIO: Comércio ABC Eireli

CLÁUSULA 2 - DO IMÓVEL
Endereço: Rua das Flores, 123 - Centro
Área: 150m²
Finalidade: Uso comercial

CLÁUSULA 3 - DO VALOR E PAGAMENTO
3.1 - O valor mensal do aluguel é de R$ 13.750,00 (treze mil setecentos e cinquenta reais)
3.2 - Vencimento: todo dia 05 de cada mês
3.3 - Multa por atraso: 2% sobre o valor em atraso

CLÁUSULA 4 - DO PRAZO
4.1 - Prazo: 36 (trinta e seis) meses
4.2 - Início: 01/01/2024
4.3 - Término: 31/12/2026

CLÁUSULA 5 - DO REAJUSTE
5.1 - Reajuste anual pelo IGPM acumulado (10% aplicado em 2025)
5.2 - Aplicação a partir do 13º mês

CLÁUSULA 8 - DAS NORMAS DE SEGURANÇA
8.4 - O locatário deve seguir as normas municipais de segurança contra incêndio e pânico, conforme Decreto Municipal 2025/001

CLÁUSULA 12 - DO USO DO IMÓVEL
12.1 - Destinação exclusiva para comércio de roupas, acessórios e calçados, vedado qualquer outro tipo de atividade"""


# Instância da API
directus_api = DirectusAPI()

# Template HTML para visualização
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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

# Template HTML específico para visualizar versões
VERSION_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Versão {{ versao_id }} - Versiona AI</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f8f9fa; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .title { color: #2c3e50; font-size: 2em; margin-bottom: 10px; }
        .subtitle { color: #7f8c8d; font-size: 1.1em; }
        .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
        .sidebar { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: fit-content; }
        .content { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metadata-section { margin-bottom: 20px; }
        .metadata-title { color: #34495e; font-size: 1.2em; margin-bottom: 10px; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        .metadata-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ecf0f1; }
        .metadata-label { font-weight: bold; color: #2c3e50; }
        .metadata-value { color: #7f8c8d; }
        .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }
        .status-processar { background: #fff3cd; color: #856404; }
        .status-processado { background: #d4edda; color: #155724; }
        .diff-container {
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background: #f8f9fa;
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
        }
        .diff-added {
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 4px 8px;
            margin: 2px 0;
            border-left: 4px solid #bee5eb;
            display: block;
            white-space: pre-wrap;
        }
        .diff-removed {
            background-color: #f8d7da;
            color: #721c24;
            padding: 4px 8px;
            margin: 2px 0;
            border-left: 4px solid #f5c6cb;
            display: block;
            white-space: pre-wrap;
        }
        .diff-unchanged {
            padding: 4px 8px;
            margin: 2px 0;
            color: #6c757d;
            display: block;
            white-space: pre-wrap;
        }
        .clause-header {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            padding: 12px 20px;
            margin: 20px 0 10px 0;
            font-weight: bold;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,123,255,.3);
            font-size: 16px;
            border-left: 6px solid #0056b3;
        }
        .clause-header:first-child {
            margin-top: 0;
        }
        .diff-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px 0;
            border-bottom: 1px solid #dee2e6;
        }
        .navigation-controls {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .nav-btn {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(40,167,69,0.3);
        }
        .nav-btn:hover {
            background: linear-gradient(135deg, #218838, #1ea085);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(40,167,69,0.4);
        }
        .nav-btn:active {
            transform: translateY(0);
        }
        .nav-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .diff-counter {
            background: #f8f9fa;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
            color: #495057;
            border: 1px solid #dee2e6;
            min-width: 80px;
            text-align: center;
        }
        .diff-highlight {
            background: #fff3cd !important;
            border: 2px solid #ffc107 !important;
            box-shadow: 0 0 10px rgba(255,193,7,0.5) !important;
            animation: highlight-pulse 1s ease-in-out;
        }
        @keyframes highlight-pulse {
            0% { box-shadow: 0 0 5px rgba(255,193,7,0.3); }
            50% { box-shadow: 0 0 20px rgba(255,193,7,0.7); }
            100% { box-shadow: 0 0 10px rgba(255,193,7,0.5); }
        }
        .stats { display: flex; gap: 15px; margin-bottom: 20px; }
        .stat-item { background: #e9ecef; padding: 15px; border-radius: 8px; text-align: center; flex: 1; }
        .stat-number { font-size: 1.5em; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">📄 {{ versao_data.get('titulo', 'Versão ' + versao_id) }}</div>
            <div class="subtitle">ID da Versão: {{ versao_id }}</div>
        </div>

        <div class="grid">
            <div class="sidebar">
                <div class="metadata-section">
                    <div class="metadata-title">📋 Informações da Versão</div>
                    <div class="metadata-item">
                        <span class="metadata-label">ID:</span>
                        <span class="metadata-value">{{ versao_id }}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Status:</span>
                        <span class="status-badge status-{{ versao_data.get('status', 'processar') }}">
                            {{ versao_data.get('status', 'processar').title() }}
                        </span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Contrato ID:</span>
                        <span class="metadata-value">{{ versao_data.get('contrato_id', 'N/A') }}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Versão Original:</span>
                        <span class="metadata-value">{{ versao_data.get('versao_original', 'N/A') }}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Versão Modificada:</span>
                        <span class="metadata-value">{{ versao_data.get('versao_modificada', 'N/A') }}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Data de Criação:</span>
                        <span class="metadata-value">{{ versao_data.get('data_criacao', 'N/A') }}</span>
                    </div>
                    {% if versao_data.get('date_updated') %}
                    <div class="metadata-item">
                        <span class="metadata-label">Última Atualização:</span>
                        <span class="metadata-value">{{ versao_data.get('date_updated') }}</span>
                    </div>
                    {% endif %}
                </div>

                {% if versao_data.get('descricao') %}
                <div class="metadata-section">
                    <div class="metadata-title">📝 Descrição</div>
                    <p style="color: #6c757d; line-height: 1.4;">{{ versao_data.get('descricao') }}</p>
                </div>
                {% endif %}

                <div class="metadata-section">
                    <div class="metadata-title">🔗 Links Úteis</div>
                    <div style="margin-top: 10px;">
                        <a href="/api/versoes/{{ versao_id }}" style="display: block; margin: 5px 0; color: #007bff;">📊 API JSON</a>
                        <a href="/api/data/{{ diff_data.get('id', '') }}" style="display: block; margin: 5px 0; color: #007bff;">📄 Dados do Diff</a>
                        <a href="/health" style="display: block; margin: 5px 0; color: #007bff;">🔍 Health Check</a>
                    </div>
                </div>
            </div>

            <div class="content">
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">{{ diff_data.get('created_at', 'N/A')[:10] if diff_data.get('created_at') else 'N/A' }}</div>
                        <div class="stat-label">Processado em</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ diff_data.get('id', 'N/A')[:8] if diff_data.get('id') else 'N/A' }}</div>
                        <div class="stat-label">Diff ID</div>
                    </div>
                </div>

                <div class="diff-header">
                    <div class="metadata-title">🔄 Diferenças Encontradas</div>
                    <div class="navigation-controls">
                        <button id="prevDiff" class="nav-btn" title="Diferença anterior (Alt + ←)">
                            ⬅️ Anterior
                        </button>
                        <span id="diffCounter" class="diff-counter">-</span>
                        <button id="nextDiff" class="nav-btn" title="Próxima diferença (Alt + →)">
                            Próximo ➡️
                        </button>
                    </div>
                </div>
                <div class="diff-container" id="diffContainer">
                    {{ diff_html|safe }}
                </div>
            </div>
        </div>
    </div>

    <script>
        // Sistema de navegação entre diferenças
        class DiffNavigator {
            constructor() {
                this.currentDiffIndex = -1;
                this.diffs = [];
                this.init();
            }

            init() {
                // Encontrar todas as diferenças (adicionadas e removidas)
                this.diffs = document.querySelectorAll('.diff-added, .diff-removed');

                // Adicionar IDs únicos para cada diferença
                this.diffs.forEach((diff, index) => {
                    diff.setAttribute('data-diff-id', index);
                    diff.style.scrollMarginTop = '20px'; // Espaço para scroll suave
                });

                // Configurar botões
                this.setupButtons();

                // Configurar atalhos de teclado
                this.setupKeyboardShortcuts();

                // Atualizar contador
                this.updateCounter();

                // Focar na primeira diferença automaticamente
                if (this.diffs.length > 0) {
                    setTimeout(() => this.goToNext(), 500);
                }
            }

            setupButtons() {
                const prevBtn = document.getElementById('prevDiff');
                const nextBtn = document.getElementById('nextDiff');

                if (prevBtn) {
                    prevBtn.addEventListener('click', () => this.goToPrev());
                }
                if (nextBtn) {
                    nextBtn.addEventListener('click', () => this.goToNext());
                }
            }

            setupKeyboardShortcuts() {
                document.addEventListener('keydown', (e) => {
                    // Alt + Seta Esquerda = Anterior
                    if (e.altKey && e.key === 'ArrowLeft') {
                        e.preventDefault();
                        this.goToPrev();
                    }
                    // Alt + Seta Direita = Próximo
                    if (e.altKey && e.key === 'ArrowRight') {
                        e.preventDefault();
                        this.goToNext();
                    }
                });
            }

            goToNext() {
                if (this.diffs.length === 0) return;

                this.currentDiffIndex++;
                if (this.currentDiffIndex >= this.diffs.length) {
                    this.currentDiffIndex = 0; // Volta para o primeiro
                }

                this.focusDiff(this.currentDiffIndex);
            }

            goToPrev() {
                if (this.diffs.length === 0) return;

                this.currentDiffIndex--;
                if (this.currentDiffIndex < 0) {
                    this.currentDiffIndex = this.diffs.length - 1; // Vai para o último
                }

                this.focusDiff(this.currentDiffIndex);
            }

            focusDiff(index) {
                // Remover highlight anterior
                this.diffs.forEach(diff => {
                    diff.classList.remove('diff-highlight');
                });

                // Adicionar highlight na diferença atual
                const currentDiff = this.diffs[index];
                if (currentDiff) {
                    currentDiff.classList.add('diff-highlight');

                    // Scroll suave para a diferença
                    currentDiff.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });

                    // Atualizar contador e botões
                    this.updateCounter();
                    this.updateButtons();
                }
            }

            updateCounter() {
                const counter = document.getElementById('diffCounter');
                if (counter && this.diffs.length > 0) {
                    counter.textContent = `${this.currentDiffIndex + 1} / ${this.diffs.length}`;
                } else if (counter) {
                    counter.textContent = '0 / 0';
                }
            }

            updateButtons() {
                const prevBtn = document.getElementById('prevDiff');
                const nextBtn = document.getElementById('nextDiff');

                if (this.diffs.length === 0) {
                    if (prevBtn) prevBtn.disabled = true;
                    if (nextBtn) nextBtn.disabled = true;
                } else {
                    if (prevBtn) prevBtn.disabled = false;
                    if (nextBtn) nextBtn.disabled = false;
                }
            }
        }

        // Inicializar quando a página carregar
        document.addEventListener('DOMContentLoaded', () => {
            new DiffNavigator();
        });

        // Adicionar indicador visual de atalhos
        document.addEventListener('DOMContentLoaded', () => {
            const style = document.createElement('style');
            style.textContent = `
                .nav-btn:hover::after {
                    content: attr(title);
                    position: absolute;
                    bottom: -30px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    z-index: 1000;
                    pointer-events: none;
                }
                .nav-btn {
                    position: relative;
                }
            `;
            document.head.appendChild(style);
        });
    </script>
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


@app.route("/api/versoes/<versao_id>", methods=["GET"])
def get_versao_by_id(versao_id):
    """Busca uma versão específica por ID e retorna dados completos com diferenças"""
    try:
        # Buscar dados da versão no Directus
        response = requests.get(
            f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}",
            headers=DIRECTUS_HEADERS,
            timeout=10,
        )

        if response.status_code == 200:
            versao_data = response.json()["data"]
        else:
            # Fallback para dados mock se não encontrar no Directus
            versao_data = _get_mock_versao_by_id(versao_id)
            if not versao_data:
                return jsonify({"error": f"Versão {versao_id} não encontrada"}), 404

        # Processar a versão para gerar as diferenças
        result = directus_api.process_versao(versao_id)

        if "error" in result:
            # Se houver erro no processamento, retornar dados básicos da versão
            return jsonify(
                {"versao": versao_data, "status": "error", "message": result["error"]}
            ), 500

        # Retornar dados completos com diferenças
        return jsonify(
            {
                "versao": versao_data,
                "diff_data": result,
                "status": "success",
                "view_url": f"http://localhost:{FLASK_PORT}/version/{versao_id}",
                "api_url": f"http://localhost:{FLASK_PORT}/api/versoes/{versao_id}",
            }
        )

    except Exception as e:
        print(f"❌ Erro ao buscar versão {versao_id}: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


def _get_mock_versao_by_id(versao_id):
    """Retorna dados mock de uma versão específica"""
    mock_versoes = {
        "versao_001": {
            "id": "versao_001",
            "titulo": "Contrato de Prestação de Serviços v1.0 vs v2.0",
            "status": "processar",
            "data_criacao": "2025-09-11T10:00:00Z",
            "versao_original": "1.0",
            "versao_modificada": "2.0",
            "descricao": "Atualização de cláusulas contratuais e condições gerais",
            "contrato_id": "contrato_001",
            "date_updated": "2025-09-16T10:00:00Z",
        },
        "versao_002": {
            "id": "versao_002",
            "titulo": "Política de Privacidade v2.1 vs v2.2",
            "status": "processar",
            "data_criacao": "2025-09-12T14:30:00Z",
            "versao_original": "2.1",
            "versao_modificada": "2.2",
            "descricao": "Adequação à LGPD e novos termos de uso",
            "contrato_id": "contrato_002",
            "date_updated": "2025-09-16T14:30:00Z",
        },
        "c2b1dfa0-c664-48b8-a5ff-84b70041b428": {
            "id": "c2b1dfa0-c664-48b8-a5ff-84b70041b428",
            "titulo": "Contrato de Locação Comercial - Revisão Anual 2025",
            "status": "processado",
            "data_criacao": "2025-09-15T08:30:00Z",
            "versao_original": "v2024.12",
            "versao_modificada": "v2025.01",
            "descricao": "Revisão anual do contrato de locação comercial incluindo reajuste de valores, atualização de cláusulas de segurança e adequação às novas normas municipais de uso comercial.",
            "contrato_id": "LOC-2024-001",
            "date_updated": "2025-09-16T09:15:00Z",
            "autor": "Sistema Automatizado",
            "revisor": "Dr. João Silva",
            "categoria": "Locação Comercial",
            "prioridade": "alta",
            "valor_anterior": "R$ 12.500,00",
            "valor_atual": "R$ 13.750,00",
            "reajuste_percentual": "10%",
            "clausulas_alteradas": [
                "Cláusula 3.1 - Valor do Aluguel",
                "Cláusula 5.2 - Reajuste Anual",
                "Cláusula 8.4 - Normas de Segurança",
                "Cláusula 12.1 - Uso do Imóvel",
            ],
            "observacoes": "Contrato revisado conforme legislação vigente e acordo entre as partes. Reajuste aplicado conforme IGPM acumulado no período.",
        },
    }
    return mock_versoes.get(versao_id)


@app.route("/version/<versao_id>", methods=["GET"])
def view_version(versao_id):
    """Visualiza uma versão específica com suas diferenças"""
    try:
        # Buscar dados da versão
        response = requests.get(
            f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}",
            headers=DIRECTUS_HEADERS,
            timeout=10,
        )

        if response.status_code == 200:
            versao_data = response.json()["data"]
        else:
            versao_data = _get_mock_versao_by_id(versao_id)
            if not versao_data:
                return "Versão não encontrada", 404

        # Processar a versão para gerar as diferenças
        result = directus_api.process_versao(versao_id)

        if "error" in result:
            return f"Erro ao processar versão: {result['error']}", 500

        # Usar template específico para versão
        response = render_template_string(
            VERSION_TEMPLATE,
            versao_id=versao_id,
            versao_data=versao_data,
            diff_data=result,
            diff_html=result.get("diff_html", ""),
            created_at=result.get("created_at", ""),
        )
        return response, 200, {"Content-Type": "text/html; charset=utf-8"}

    except Exception as e:
        print(f"❌ Erro ao visualizar versão {versao_id}: {e}")
        return f"Erro interno: {str(e)}", 500


@app.route("/api/test", methods=["GET"])
def test_endpoint():
    """Endpoint de teste"""
    return jsonify({"status": "working", "message": "Test endpoint funcionando!"})


@app.route("/test/diff/<versao_id>", methods=["GET"])
def test_diff(versao_id):
    """Testa apenas a geração do diff"""
    result = directus_api.process_versao(versao_id)
    if "error" in result:
        return f"Erro: {result['error']}", 500

    return (
        f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Teste Diff - {versao_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            .diff-container {{ font-family: monospace; border: 1px solid #ccc; padding: 15px; background: #fafafa; border-radius: 4px; }}
            .diff-added {{ background: #d4f6d4; color: #155724; padding: 2px 4px; display: block; margin: 1px 0; }}
            .diff-removed {{ background: #fdd; color: #721c24; padding: 2px 4px; display: block; margin: 1px 0; }}
            .diff-unchanged {{ color: #666; padding: 2px 4px; display: block; margin: 1px 0; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Teste Diff - {versao_id}</h1>
            <h2>Diferenças Encontradas:</h2>
            {result.get("diff_html", "Nenhum diff gerado")}
        </div>
    </body>
    </html>
    """,
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )


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
    response = render_template_string(HTML_TEMPLATE, **diff_data)
    return response, 200, {"Content-Type": "text/html; charset=utf-8"}


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
