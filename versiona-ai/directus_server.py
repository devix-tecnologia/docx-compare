"""
Servidor API para integração real com Directus
Conecta com https://contract.devix.co usando as credenciais do .env
"""

import os
import signal
import sys
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, render_template_string, request
from flask_cors import CORS

# Carregar variáveis do .env
load_dotenv()

app = Flask(__name__, template_folder="templates")
CORS(app)

# Cache de diffs para persistência
diff_cache = {}

# Configurações do Directus
DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN")
FLASK_PORT = int(os.getenv("FLASK_PORT", "8001"))
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# Headers para Directus
DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}


def setup_signal_handlers():
    """Configura handlers para encerramento gracioso"""

    def signal_handler(sig, _frame):
        print(f"\n🛑 Recebido sinal {sig}. Encerrando servidor graciosamente...")
        print("🔄 Limpando recursos...")

        # Limpar cache se necessário
        if diff_cache:
            print(f"🗑️  Limpando {len(diff_cache)} items do cache...")
            diff_cache.clear()

        print("✅ Servidor encerrado com sucesso!")
        sys.exit(0)

    # Registrar handlers para sinais comuns
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination
    if hasattr(signal, "SIGHUP"):  # Unix only
        signal.signal(signal.SIGHUP, signal_handler)  # Hangup


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
        """Busca todas as versões (removido filtro de status)"""
        print("🚀 Iniciando get_versoes_para_processar")
        try:
            # Buscar versões usando a função existente - sem filtro de status
            response = requests.get(
                f"{self.base_url}/items/versao?limit=50",
                headers=DIRECTUS_HEADERS,
                timeout=15,
            )

            if response.status_code == 200:
                versoes = response.json()["data"]
                print(f"✅ Encontradas {len(versoes)} versões disponíveis")
                return versoes
            else:
                print(f"❌ Erro ao buscar versões: {response.status_code}")
                # No modo real, erro do Directus é erro - não usar mock como fallback
                raise Exception(f"Falha no Directus: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ Erro ao buscar versões: {e}")
            # No modo real, erro de conexão é erro - não usar mock como fallback
            raise e

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

    def process_versao(self, versao_id, mock=False):
        """Processa uma versão específica

        Args:
            versao_id: ID da versão a ser processada
            mock: Se True, usa dados mockados. Se False ou não informado, usa dados reais do Directus
        """
        global diff_cache  # Declarar acesso à variável global

        try:
            if mock:
                # Usar dados mock quando solicitado
                print(f"🔧 Modo mock ativado - usando dados simulados para {versao_id}")
                versao_data = _get_mock_versao_by_id(versao_id)
                if not versao_data:
                    return {"error": f"Versão mock {versao_id} não encontrada"}
            else:
                # Buscar dados reais do Directus
                # Usar apenas campos que sabemos que existem baseado na listagem
                fields = "id,status,date_created,date_updated,versao,observacao,origem,arquivo,modifica_arquivo,contrato"
                response = requests.get(
                    f"{self.base_url}/items/versao/{versao_id}?fields={fields}",
                    headers=DIRECTUS_HEADERS,
                    timeout=10,
                )

                if response.status_code != 200:
                    # No modo real, falha do Directus é erro (não usar mock como fallback)
                    print(
                        f"❌ Falha no Directus para versão {versao_id}: HTTP {response.status_code}"
                    )
                    return {
                        "error": f"Versão {versao_id} não encontrada no Directus (HTTP {response.status_code})"
                    }
                else:
                    versao_data = response.json()["data"]

            # Gerar conteúdo baseado no modo (mock ou real)
            if mock:
                print("🔧 Gerando conteúdo mock...")
                original_text, modified_text = self._generate_mock_content(
                    versao_id, versao_data
                )
            else:
                print("🔍 Processando arquivos reais...")
                original_text, modified_text = self._process_real_documents(versao_data)

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
                "mode": "mock" if mock else "real",
            }

            diff_cache[diff_id] = diff_data
            return diff_data

        except Exception as e:
            print(f"❌ Erro ao processar versão {versao_id}: {e}")
            return {"error": str(e)}

    def _generate_mock_content(self, versao_id, versao_data):
        """Gera conteúdo mock para demonstração"""
        if versao_id == "c2b1dfa0-c664-48b8-a5ff-84b70041b42833":
            # Conteúdo realista para contrato de locação
            original_text = self._generate_realistic_contract_original()
            modified_text = self._generate_realistic_contract_modified()
        else:
            # Conteúdo padrão para outras versões
            original_text = "CLÁUSULA 1 - DAS PARTES\n"
            original_text += f"Conteúdo original da versão {versao_id}\n"
            original_text += "CLÁUSULA 2 - PARTICIPANTES\n"
            original_text += f"Contrato: {versao_data.get('contrato_id', 'N/A')}\n"
            original_text += f"Status atual: {versao_data.get('status', 'N/A')}\n"
            original_text += "Este é um exemplo de texto original do contrato."

            modified_text = f"Conteúdo modificado da versão {versao_id}\n"
            modified_text += (
                f"Contrato: {versao_data.get('contrato_id', 'N/A')} [MODIFICADO]\n"
            )
            modified_text += "Status atual: processado\n"
            modified_text += "Este é um exemplo de texto MODIFICADO do contrato com alterações importantes."

        return original_text, modified_text

    def _process_real_documents(self, versao_data):
        """Processa documentos reais obtidos do Directus"""
        try:
            # LÓGICA CORRETA:
            # versao.arquivo = NOVO/MODIFICADO (versão atual)
            # Arquivo anterior = versão anterior (date_created menor) OU contrato.modelo_contrato.arquivo_original

            arquivo_novo_id = versao_data.get("arquivo")  # Arquivo MODIFICADO/NOVO

            if not arquivo_novo_id:
                error_msg = "❌ ID do arquivo novo/modificado não encontrado nos dados da versão"
                print(error_msg)
                raise ValueError(
                    "Arquivo novo não encontrado - use mock=true para dados simulados"
                )

            # Buscar arquivo original (anterior)
            arquivo_original_id = self._get_arquivo_original(versao_data)

            if not arquivo_original_id:
                error_msg = "❌ Não foi possível determinar o arquivo original/anterior"
                print(error_msg)
                raise ValueError(
                    "Arquivo original não encontrado - use mock=true para dados simulados"
                )

            print(f"📁 Arquivo Original (anterior): {arquivo_original_id}")
            print(f"📁 Arquivo Modificado (novo): {arquivo_novo_id}")

            # Baixar e processar arquivo original (anterior)
            original_text = self._download_and_extract_text(arquivo_original_id)

            # Baixar e processar arquivo modificado (novo)
            modified_text = self._download_and_extract_text(arquivo_novo_id)

            if not original_text:
                error_msg = "❌ Falha ao extrair texto do arquivo original"
                print(error_msg)
                raise ValueError(
                    "Não foi possível extrair texto do arquivo original - use mock=true para dados simulados"
                )

            if not modified_text:
                error_msg = "❌ Falha ao extrair texto do arquivo modificado"
                print(error_msg)
                raise ValueError(
                    "Não foi possível extrair texto do arquivo modificado - use mock=true para dados simulados"
                )

            return original_text, modified_text

        except Exception as e:
            print(f"❌ Erro ao processar documentos reais: {e}")
            raise e

    def _get_arquivo_original(self, versao_data):
        """Busca o arquivo original/anterior baseado na lógica de negócio"""
        try:
            contrato_id = versao_data.get("contrato")
            versao_atual_date = versao_data.get("date_created")

            if not contrato_id or not versao_atual_date:
                print("❌ Dados insuficientes para buscar arquivo original")
                return None

            # 1. Tentar buscar versão anterior (date_created menor)
            print(f"🔍 Buscando versão anterior do contrato {contrato_id}")

            # Buscar todas as versões do mesmo contrato, ordenadas por data
            response = requests.get(
                f"{self.base_url}/items/versao",
                headers=DIRECTUS_HEADERS,
                params={
                    "filter[contrato][_eq]": contrato_id,
                    "filter[date_created][_lt]": versao_atual_date,
                    "sort": "-date_created",  # Mais recente primeiro
                    "limit": 1,
                    "fields": "id,arquivo,date_created",
                },
                timeout=10,
            )

            if response.status_code == 200:
                versoes_anteriores = response.json().get("data", [])
                if versoes_anteriores:
                    versao_anterior = versoes_anteriores[0]
                    arquivo_anterior_id = versao_anterior.get("arquivo")
                    if arquivo_anterior_id:
                        print(f"✅ Encontrada versão anterior: {versao_anterior['id']}")
                        return arquivo_anterior_id

            # 2. Se não encontrou versão anterior, buscar modelo_contrato.arquivo_original
            print("🔍 Não encontrou versão anterior, buscando modelo do contrato")

            response = requests.get(
                f"{self.base_url}/items/contrato/{contrato_id}",
                headers=DIRECTUS_HEADERS,
                params={"fields": "modelo_contrato.arquivo_original"},
                timeout=10,
            )

            if response.status_code == 200:
                contrato_data = response.json().get("data", {})
                modelo_contrato = contrato_data.get("modelo_contrato")
                if modelo_contrato:
                    arquivo_original_id = modelo_contrato.get("arquivo_original")
                    if arquivo_original_id:
                        print(
                            f"✅ Encontrado arquivo original do modelo: {arquivo_original_id}"
                        )
                        return arquivo_original_id

            print("❌ Não foi possível encontrar arquivo original/anterior")
            return None

        except Exception as e:
            print(f"❌ Erro ao buscar arquivo original: {e}")
            return None

    def _download_and_extract_text(self, arquivo_id):
        """Baixa um arquivo do Directus e extrai o texto"""
        try:
            # URL para download do arquivo
            download_url = f"{self.base_url}/assets/{arquivo_id}"

            response = requests.get(download_url, headers=DIRECTUS_HEADERS, timeout=30)

            if response.status_code != 200:
                print(f"❌ Erro ao baixar arquivo {arquivo_id}: {response.status_code}")
                return None

            # Salvar arquivo temporariamente
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name

            try:
                # Usar o módulo docx_utils existente para extrair texto
                import sys

                sys.path.append("/Users/sidarta/repositorios/docx-compare")
                from docx_utils import convert_docx_to_text

                text = convert_docx_to_text(temp_path)
                return text
            except ImportError as e:
                print(f"❌ Erro ao importar docx_utils: {e}")
                # Fallback: usar python-docx diretamente
                try:
                    from docx import Document

                    doc = Document(temp_path)
                    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                    return "\n".join(paragraphs)
                except ImportError:
                    print("❌ python-docx não instalado, retornando None")
                    return None
            finally:
                # Limpar arquivo temporário
                os.unlink(temp_path)

        except Exception as e:
            print(f"❌ Erro ao processar arquivo {arquivo_id}: {e}")
            return None

    def _get_fallback_real_content(self, versao_data):
        """Conteúdo de fallback quando não consegue processar arquivos reais"""
        titulo = versao_data.get("titulo", "Documento")

        original_text = f"DOCUMENTO ORIGINAL - {titulo}\n\n"
        original_text += "CLÁUSULA 1 - DAS PARTES\n"
        original_text += f"Contrato ID: {versao_data.get('contrato_id', 'N/A')}\n"
        original_text += f"Versão: {versao_data.get('versao_original', '1.0')}\n"
        original_text += "Status: ativo\n\n"
        original_text += (
            "Este é o conteúdo original do documento baseado nos metadados disponíveis."
        )

        modified_text = f"DOCUMENTO MODIFICADO - {titulo}\n\n"
        modified_text += "CLÁUSULA 1 - DAS PARTES [ATUALIZADA]\n"
        modified_text += f"Contrato ID: {versao_data.get('contrato_id', 'N/A')}\n"
        modified_text += f"Versão: {versao_data.get('versao_modificada', '2.0')}\n"
        modified_text += "Status: processado\n\n"
        modified_text += (
            "Este é o conteúdo modificado do documento com as alterações aplicadas."
        )

        return original_text, modified_text

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


@app.route("/api/versoes", methods=["GET", "POST"])
def get_versoes():
    """Lista versões para processar

    Aceita parâmetro mock via:
    - Query parameter: GET /api/versoes?mock=true
    - JSON body: POST /api/versoes {"mock": true}
    """
    try:
        # Verificar se mock foi solicitado
        if request.method == "GET":
            mock = request.args.get("mock", "false").lower() == "true"
        else:  # POST
            data = request.json or {}
            mock = data.get("mock", False)

        print(f"🔍 Buscando versões (modo: {'mock' if mock else 'real'})")

        if mock:
            print("🔧 Retornando dados mock conforme solicitado")
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
                    ],
                    "mode": "mock",
                }
            )
        else:
            # Buscar dados reais do Directus
            versoes = directus_api.get_versoes_para_processar()

            # Se conseguiu dados reais, usar eles
            if versoes and len(versoes) > 0 and not _is_mock_data(versoes[0]):
                print(f"✅ Retornando {len(versoes)} versões reais do Directus")
                return jsonify({"versoes": versoes, "mode": "real"})
            else:
                print("❌ Falha ao obter dados reais do Directus")
                return jsonify(
                    {"error": "Não foi possível obter versões do Directus"}
                ), 500

    except Exception as e:
        print(f"❌ Erro ao buscar versões: {e}")
        return jsonify({"error": f"Erro ao buscar versões: {str(e)}"}), 500


def _is_mock_data(versao):
    """Verifica se uma versão é dados mock"""
    return versao.get("id", "").startswith("versao_")


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
                "view_url": f"http://localhost:{FLASK_PORT}/versao/{versao_id}",
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


@app.route("/versao/<versao_id>", methods=["GET"])
def view_version(versao_id):
    """Visualiza uma versão específica com suas diferenças"""
    try:
        # Buscar dados da versão
        response = requests.get(
            f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}",
            headers=DIRECTUS_HEADERS,
            timeout=10,
        )

        print(f"🔍 Buscando versão {versao_id} no Directus...")
        print(f"📡 URL: {DIRECTUS_BASE_URL}/items/versao/{versao_id}")
        print("Resultado da requisição:", response.status_code, response.text)

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
        response = render_template(
            "version_template.html",
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
    """Processa uma versão específica

    Body JSON esperado:
    {
        "versao_id": "id_da_versao",
        "mock": true/false (opcional, default: false)
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado JSON fornecido"}), 400

    versao_id = data.get("versao_id") or data.get("doc_id")
    mock = data.get("mock", False)  # Default: usar dados reais

    if not versao_id:
        return jsonify({"error": "versao_id é obrigatório"}), 400

    print(f"🔍 Processando versão {versao_id} (modo: {'mock' if mock else 'real'})")
    result = directus_api.process_versao(versao_id, mock=mock)

    if "error" in result:
        return jsonify(result), 500

    # Debug: verificar o resultado
    print(
        f"🔍 Resultado do processamento: {type(result)}, chaves: {list(result.keys()) if isinstance(result, dict) else 'não é dict'}"
    )

    # Garantir que o resultado seja armazenado no cache global
    if "id" in result:
        diff_cache[result["id"]] = result
        print(f"💾 Diff {result['id']} salvo no cache (total: {len(diff_cache)} items)")
    else:
        print("⚠️  Resultado não tem campo 'id', não salvando no cache")

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
    print(f"🔍 Buscando diff_id: {diff_id}")
    print(f"📊 Cache atual tem {len(diff_cache)} items: {list(diff_cache.keys())}")

    if diff_id not in diff_cache:
        return jsonify({"error": "Diff não encontrado"}), 404

    return jsonify(diff_cache[diff_id])


@app.route("/api/debug/cache", methods=["GET"])
def debug_cache():
    """Debug: mostra conteúdo do cache"""
    return jsonify(
        {
            "total_items": len(diff_cache),
            "cache_keys": list(diff_cache.keys()),
            "timestamp": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    print("🚀 Servidor API com Directus Real")
    print(f"📊 Directus URL: {DIRECTUS_BASE_URL}")
    print(f"🔗 API Health: http://localhost:{FLASK_PORT}/health")
    print(f"📋 Documentos: http://localhost:{FLASK_PORT}/api/documents")
    print(f"🔄 Versões: http://localhost:{FLASK_PORT}/api/versoes")

    # Configurar modo de desenvolvimento
    if DEV_MODE:
        print("🔧 Modo DEV ativo - Watch & Reload habilitado")
        print("📝 Arquivos monitorados para auto-reload")
    else:
        print("🏭 Modo PRODUÇÃO")

    # Configurar encerramento gracioso
    setup_signal_handlers()

    # Testar conexão na inicialização
    if directus_api.test_connection():
        print("✅ Conexão com Directus estabelecida!")
    else:
        print("❌ Falha na conexão com Directus - verifique credenciais")

    try:
        print(f"🎯 Iniciando servidor na porta {FLASK_PORT}...")
        app.run(
            debug=DEV_MODE,
            host="0.0.0.0",
            port=FLASK_PORT,
            use_reloader=DEV_MODE,
            use_debugger=DEV_MODE,
        )
    except KeyboardInterrupt:
        print("\n🛑 Interrupção pelo usuário (Ctrl+C)")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    finally:
        print("🔄 Encerrando servidor...")
