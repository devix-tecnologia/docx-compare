"""
Servidor API para integração real com Directus
Conecta com https://contract.devix.co usando as credenciais do .env
Inclui agrupamento posicional para cálculo preciso de blocos
Implementa algoritmo unificado de vinculação de modificações às cláusulas
"""

import copy
import difflib
import os
import re
import signal
import sys
import tempfile
import unicodedata
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime

import requests
from dotenv import load_dotenv

# RapidFuzz para matching ultra-rápido (221x mais rápido que difflib)
try:
    from rapidfuzz import fuzz

    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("⚠️ RapidFuzz não disponível - usando difflib (mais lento)")
from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
)
from flask_cors import CORS

# Importar agrupador posicional
try:
    from agrupador_posicional import AgrupadorPosicional
except ImportError:
    print("⚠️ Agrupador posicional não disponível - usando contagem padrão")
    AgrupadorPosicional = None

# Importar processador de tags de modelo
from processador_tags_modelo import ProcessadorTagsModelo

# Carregar variáveis do .env
load_dotenv()

# ============================================================================
# CLASSES PARA PROCESSAMENTO AST DO PANDOC
# ============================================================================


class PandocASTProcessor:
    """Processa AST do Pandoc para extração de parágrafos estruturados."""

    @staticmethod
    def convert_docx_to_ast(docx_path: str) -> dict:
        """Converte DOCX para AST JSON usando Pandoc."""
        import json
        import subprocess

        try:
            result = subprocess.run(
                ["pandoc", docx_path, "-t", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Erro no Pandoc: {result.stderr}")

            return json.loads(result.stdout)

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Timeout na conversão do arquivo {docx_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Erro ao parsear JSON do Pandoc: {e}")

    @staticmethod
    def extract_paragraphs_from_ast(ast_json: dict) -> list[dict]:
        """Extrai parágrafos estruturados do AST."""
        paragraphs = []
        blocks = ast_json.get("blocks", [])

        for block in blocks:
            block_type = block.get("t")

            if block_type == "Para":
                para_info = PandocASTProcessor._extract_paragraph(block)
                if para_info["text"].strip():
                    paragraphs.append(para_info)

            elif block_type == "Header":
                para_info = PandocASTProcessor._extract_header(block)
                if para_info["text"].strip():
                    paragraphs.append(para_info)

        return paragraphs

    @staticmethod
    def _extract_paragraph(block: dict) -> dict:
        """Extrai texto e metadados de um parágrafo."""
        content = block.get("c", [])
        text, formatting = PandocASTProcessor._extract_inline_content(content)

        # Detectar número de cláusula
        clause_match = re.match(r"^(\d+\.(?:\d+)?)\s", text)
        clause_number = clause_match.group(1) if clause_match else None

        return {
            "text": text,
            "type": "Para",
            "formatting": formatting,
            "clause_number": clause_number,
        }

    @staticmethod
    def _extract_header(block: dict) -> dict:
        """Extrai texto de um cabeçalho."""
        level = block.get("c", [None])[0]
        content = block.get("c", [None, []])[1]
        text, formatting = PandocASTProcessor._extract_inline_content(content)

        return {
            "text": text,
            "type": f"Header{level}",
            "formatting": formatting,
            "clause_number": None,
        }

    @staticmethod
    def _extract_inline_content(content: list) -> tuple[str, list[str]]:
        """Extrai texto e formatações de conteúdo inline."""
        text_parts = []
        formatting_types = set()

        def process_inline(inline_elem):
            elem_type = inline_elem.get("t")

            if elem_type == "Str":
                text_parts.append(inline_elem.get("c", ""))
            elif elem_type == "Space":
                text_parts.append(" ")
            elif elem_type == "SoftBreak" or elem_type == "LineBreak":
                text_parts.append("\n")
            elif elem_type == "Strong":
                formatting_types.add("Bold")
                for inner in inline_elem.get("c", []):
                    process_inline(inner)
            elif elem_type == "Emph":
                formatting_types.add("Italic")
                for inner in inline_elem.get("c", []):
                    process_inline(inner)

        for elem in content:
            process_inline(elem)

        return "".join(text_parts), list(formatting_types)


app = Flask(__name__, template_folder="templates")
CORS(app)

# Registrar documentação Swagger
try:
    from swagger_docs import docs_blueprint

    app.register_blueprint(docs_blueprint)
    print("✅ Documentação Swagger disponível em /docs/")
except ImportError as e:
    print(f"⚠️  Não foi possível carregar documentação Swagger: {e}")
except Exception as e:
    print(f"❌ Erro ao registrar Swagger: {e}")

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


# ============================================================================
# ESTRUTURAS DE DADOS PARA VINCULAÇÃO UNIFICADA
# ============================================================================


@dataclass
class TagMapeada:
    """Tag com posições recalculadas no sistema de coordenadas original."""

    tag_id: str
    tag_nome: str
    posicao_inicio_original: int  # Posição no arquivo SEM tags
    posicao_fim_original: int
    clausulas: list[dict]
    score_inferencia: float  # 1.0 (offset), 0.9-0.5 (contexto)
    metodo: str  # "offset", "contexto_completo", "contexto_parcial", "conteudo"


@dataclass
class ResultadoVinculacao:
    """Resultado da vinculação com categorização por confiança."""

    vinculadas: list[dict] = field(default_factory=list)
    nao_vinculadas: list[dict] = field(default_factory=list)
    revisao_manual: list[dict] = field(default_factory=list)

    def taxa_sucesso(self) -> float:
        """Retorna a taxa de vinculação automática (em %)."""
        total = (
            len(self.vinculadas) + len(self.nao_vinculadas) + len(self.revisao_manual)
        )
        return (len(self.vinculadas) / total * 100) if total > 0 else 0.0

    def taxa_cobertura(self) -> float:
        """Retorna a taxa de cobertura (inclui revisão manual como potencial sucesso, em %)."""
        total = (
            len(self.vinculadas) + len(self.nao_vinculadas) + len(self.revisao_manual)
        )
        cobertos = len(self.vinculadas) + len(self.revisao_manual)
        return (cobertos / total * 100) if total > 0 else 0.0


# ============================================================================
# FUNÇÕES UTILITÁRIAS DE NORMALIZAÇÃO E SIMILARIDADE
# ============================================================================


def normalizar_texto(texto: str) -> str:
    """
    Normalização padronizada para todo o sistema.
    Garante consistência em tags, modificações e contexto.
    """
    if not texto:
        return ""

    # 1. Unicode normalization (NFC) - garante forma canônica composta
    # "é" pode ser: U+00E9 (único) OU U+0065 + U+0301 (e + acento)
    # NFC garante sempre U+00E9
    texto = unicodedata.normalize("NFC", texto)

    # 2. Remover variações de espaço (nbsp, thin space, etc)
    texto = re.sub(r"[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000]", " ", texto)

    # 3. Normalizar espaços múltiplos, tabs, quebras de linha → espaço único
    texto = re.sub(r"\s+", " ", texto)

    # 4. Remover espaços no início/fim
    texto = texto.strip()

    return texto


def calcular_similaridade(texto1: str, texto2: str) -> float:
    """
    Calcula similaridade entre dois textos normalizados.
    Retorna valor entre 0.0 (totalmente diferentes) e 1.0 (idênticos).

    Usa RapidFuzz se disponível (221x mais rápido), senão usa difflib.
    """
    if not texto1 or not texto2:
        return 0.0

    if RAPIDFUZZ_AVAILABLE:
        # RapidFuzz: ~221x mais rápido que difflib
        return fuzz.ratio(texto1, texto2) / 100.0
    else:
        # Fallback para difflib (mais lento)
        return difflib.SequenceMatcher(None, texto1, texto2).ratio()


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
            url = f"{self.base_url}/items/versao?limit=50"
            print(f"📡 URL: {url}")
            print(f"🔑 Headers: Authorization Bearer existe: {bool(DIRECTUS_TOKEN)}")

            # Buscar versões usando a função existente - sem filtro de status
            response = requests.get(
                url,
                headers=DIRECTUS_HEADERS,
                timeout=15,
            )

            print(f"🔍 Status Code: {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"📄 Erro detalhado: {error_data}")
                except Exception:
                    print(f"📄 Resposta raw: {response.text[:500]}")

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

    def process_versao(self, versao_id, mock=False, use_ast=True):
        """Processa uma versão específica

        Args:
            versao_id: ID da versão a ser processada
            mock: Se True, usa dados mockados. Se False ou não informado, usa dados reais do Directus
            use_ast: Se True (PADRÃO), usa implementação AST do Pandoc (59.3% precisão). Se False, usa texto plano (51.9% precisão)
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
                url = f"{self.base_url}/items/versao/{versao_id}?fields={fields}"
                print(f"🔍 Buscando versão no Directus: {url}")
                print(
                    f"🔍 Headers configurados: Authorization presente = {bool(DIRECTUS_HEADERS.get('Authorization'))}"
                )

                response = requests.get(
                    url,
                    headers=DIRECTUS_HEADERS,
                    timeout=10,
                )

                print(f"📡 Resposta do Directus: HTTP {response.status_code}")
                if response.status_code != 200:
                    print(f"📄 Corpo da resposta: {response.text[:500]}")

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

            # Se use_ast=True, usar processamento AST
            if use_ast and not mock:
                print("=" * 100)
                print("🔬 USANDO IMPLEMENTAÇÃO AST (59.3% precisão)")
                print("=" * 100)
                return self._process_versao_com_ast(versao_id, versao_data)

            # Gerar conteúdo baseado no modo (mock ou real)
            if mock:
                print("🔧 Gerando conteúdo mock...")
                original_text, modified_text = self._generate_mock_content(
                    versao_id, versao_data
                )
            else:
                print("🔍 Processando arquivos reais...")
                original_text, modified_text = self._process_real_documents(versao_data)

            # Buscar tags do modelo de contrato (somente em modo real)
            tags_modelo = []
            modelo_id = None
            arquivo_com_tags_text = None
            print(f"🔍 DEBUG: mock={mock}, verificando busca de tags")
            if not mock:
                try:
                    # Buscar modelo_id da versão através do contrato
                    contrato_id = versao_data.get("contrato")
                    print(f"🔍 DEBUG: contrato_id={contrato_id}")
                    if contrato_id:
                        print(f"🔍 Buscando modelo do contrato {contrato_id}...")
                        contrato_response = requests.get(
                            f"{self.base_url}/items/contrato/{contrato_id}",
                            headers=DIRECTUS_HEADERS,
                            params={"fields": "modelo_contrato"},
                            timeout=10,
                        )
                        print(
                            f"🔍 DEBUG: contrato response status={contrato_response.status_code}"
                        )
                        if contrato_response.status_code == 200:
                            modelo_id = contrato_response.json()["data"].get(
                                "modelo_contrato"
                            )
                            print(f"🔍 DEBUG: modelo_id encontrado={modelo_id}")

                    if modelo_id:
                        # Buscar arquivo_com_tags do modelo para mapear posições corretas
                        print(f"🔍 Buscando arquivo_com_tags do modelo {modelo_id}...")
                        modelo_response = requests.get(
                            f"{self.base_url}/items/modelo_contrato/{modelo_id}",
                            headers=DIRECTUS_HEADERS,
                            params={"fields": "arquivo_com_tags"},
                            timeout=10,
                        )
                        if modelo_response.status_code == 200:
                            arquivo_com_tags_id = modelo_response.json()["data"].get(
                                "arquivo_com_tags"
                            )
                            if arquivo_com_tags_id:
                                print(
                                    f"📥 Baixando arquivo_com_tags {arquivo_com_tags_id} para mapear posições..."
                                )
                                arquivo_com_tags_text = self._download_and_extract_text(
                                    arquivo_com_tags_id
                                )
                                if arquivo_com_tags_text:
                                    print(
                                        f"✅ Arquivo com tags carregado ({len(arquivo_com_tags_text)} caracteres)"
                                    )
                                else:
                                    print(
                                        "⚠️ Não foi possível extrair texto do arquivo_com_tags"
                                    )
                            else:
                                print("⚠️ modelo não tem arquivo_com_tags")

                        print(f"🔍 Buscando tags do modelo {modelo_id}...")
                        tags_response = requests.get(
                            f"{self.base_url}/items/modelo_contrato_tag",
                            headers=DIRECTUS_HEADERS,
                            params={
                                "filter[modelo_contrato][_eq]": modelo_id,
                                "fields": "id,tag_nome,caminho_tag_inicio,caminho_tag_fim,posicao_inicio_texto,posicao_fim_texto,conteudo,clausulas.id,clausulas.numero,clausulas.nome",
                                "limit": -1,
                            },
                            timeout=10,
                        )
                        if tags_response.status_code == 200:
                            tags_modelo = tags_response.json().get("data", [])
                            print(
                                f"✅ Encontradas {len(tags_modelo)} tags do modelo para vinculação"
                            )
                    else:
                        print(
                            "⚠️ modelo_id não encontrado, não será possível vincular cláusulas"
                        )
                except Exception as e:
                    print(f"⚠️ Erro ao buscar tags do modelo: {e}")
                    import traceback

                    traceback.print_exc()

            # Gerar diff
            # Se temos arquivo_com_tags, usar ele (sem tags) como original para ter mesmas coordenadas
            if arquivo_com_tags_text:
                print("🔄 Usando arquivo_com_tags (sem tags) como base para diff")
                # Remover tags do arquivo_com_tags para usar como original
                original_text_para_diff = re.sub(
                    r"\{\{/?TAG-[^}]+\}\}", "", arquivo_com_tags_text
                )
                original_text_para_diff = re.sub(
                    r"\{\{/?[^}]+\}\}", "", original_text_para_diff
                )
                print(
                    f"📝 Texto original (sem tags): {len(original_text_para_diff)} caracteres"
                )
                print(f"📝 Texto modificado: {len(modified_text)} caracteres")
                diff_html = self._generate_diff_html(
                    original_text_para_diff, modified_text
                )
            else:
                diff_html = self._generate_diff_html(original_text, modified_text)

            # Extrair modificações do diff (com posições de caracteres)
            # Passar textos para calcular posições exatas
            texto_original_limpo = (
                original_text_para_diff if arquivo_com_tags_text else original_text
            )
            modificacoes = self._extrair_modificacoes_do_diff(
                diff_html,
                texto_original=texto_original_limpo,
                texto_modificado=modified_text,
            )

            # Vincular modificações às cláusulas usando tags (somente em modo real)
            resultado_vinculacao = None
            if not mock and tags_modelo:
                # Usar arquivo_com_tags_text se disponível
                if arquivo_com_tags_text:
                    texto_para_mapear_tags = arquivo_com_tags_text
                    # IMPORTANTE: Modificações estão em coordenadas SEM tags (texto_original_limpo)
                    # Tags precisam ser mapeadas para o mesmo sistema de coordenadas
                    print("🔍 Usando NOVO ALGORITMO UNIFICADO de vinculação")
                else:
                    texto_para_mapear_tags = modified_text
                    print("⚠️ Sem arquivo_com_tags - usando texto modificado")

                # NOVO: Usar algoritmo unificado inteligente
                # IMPORTANTE: Passar modified_text como texto_original
                # - texto_com_tags = modelo COM tags (para offset calcular)
                # - texto_original = versão modificada (para calcular similaridade e posicionar modificações)
                # - modificações estão em coordenadas: modelo_sem_tags → modified_text
                resultado_vinculacao = self._vincular_modificacoes_clausulas_novo(
                    modificacoes=modificacoes,
                    tags_modelo=tags_modelo,
                    texto_com_tags=texto_para_mapear_tags,  # modelo COM tags
                    texto_original=modified_text,  # versão modificada (base das modificações)
                )

                # Atualizar modificacoes com as vinculadas
                # O novo algoritmo já categorizou, mas mantemos formato antigo por compatibilidade
                modificacoes_vinculadas = resultado_vinculacao.get("modificacoes")
                if modificacoes_vinculadas is not None:
                    modificacoes = modificacoes_vinculadas

            # Calcular blocos usando agrupamento posicional
            resultado_blocos = self._calcular_blocos_avancado(versao_id, diff_html)

            # Criar registro de diff
            diff_id = str(uuid.uuid4())
            diff_data = {
                "id": diff_id,
                "versao_id": versao_id,
                "versao_data": versao_data,
                "original": original_text,
                "modified": modified_text,
                "diff_html": diff_html,
                "modificacoes": modificacoes,
                "total_blocos": resultado_blocos.get("total_blocos", 1),
                "blocos_detalhados": resultado_blocos.get("blocos_detalhados", []),
                "metodo_calculo": resultado_blocos.get("metodo", "unknown"),
                "created_at": datetime.now().isoformat(),
                "url": f"http://localhost:{FLASK_PORT}/view/{diff_id}",
                "mode": "mock" if mock else "real",
            }

            # Adicionar métricas do novo algoritmo de vinculação
            if resultado_vinculacao:
                diff_data["vinculacao_metrics"] = {
                    "metodo_usado": resultado_vinculacao["metodo_usado"],
                    "similaridade": resultado_vinculacao["similaridade"],
                    "tags_mapeadas": len(resultado_vinculacao["tags_mapeadas"]),
                    "vinculadas": len(resultado_vinculacao["resultado"].vinculadas),
                    "revisao_manual": len(
                        resultado_vinculacao["resultado"].revisao_manual
                    ),
                    "nao_vinculadas": len(
                        resultado_vinculacao["resultado"].nao_vinculadas
                    ),
                    "taxa_sucesso": resultado_vinculacao["resultado"].taxa_sucesso(),
                    "taxa_cobertura": resultado_vinculacao[
                        "resultado"
                    ].taxa_cobertura(),
                }

            diff_cache[diff_id] = diff_data

            # Persistir modificações no Directus (somente em modo real)
            if not mock:
                try:
                    # Obter arquivo_original_id para atualizar na versão
                    arquivo_original_id = None
                    if not mock:
                        arquivo_original_id = self._get_arquivo_original(versao_data)

                    self._persistir_modificacoes_directus(
                        versao_id, modificacoes, arquivo_original_id
                    )
                except Exception as persist_error:
                    print(
                        f"⚠️ Erro ao persistir modificações no Directus: {persist_error}"
                    )
                    # Não falhar o processamento se a persistência falhar

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

    def _persistir_modificacoes_directus(
        self, versao_id, modificacoes, arquivo_original_id=None
    ):
        """
        Persiste as modificações no Directus e atualiza o status da versão
        Cria todas as modificações de uma vez via PATCH na versão

        Args:
            versao_id: ID da versão processada
            modificacoes: Lista de modificações extraídas
            arquivo_original_id: ID do arquivo original para atualizar modifica_arquivo
        """
        print(
            f"💾 Iniciando persistência de {len(modificacoes)} modificações no Directus..."
        )

        try:
            # Converter todas as modificações para o formato Directus
            modificacoes_directus = []
            for idx, mod in enumerate(modificacoes):
                try:
                    modificacao_data = self._converter_modificacao_para_directus(
                        versao_id, mod
                    )
                    modificacoes_directus.append(modificacao_data)
                    print(
                        f"✅ Modificação {idx + 1}/{len(modificacoes)} convertida para Directus"
                    )
                except Exception as e:
                    print(f"❌ Erro ao converter modificação {idx + 1}: {e}")

            # Atualizar versão com todas as modificações de uma vez (transação única)
            update_data = {
                "status": "concluido",
                "modificacoes": {"create": modificacoes_directus},
            }

            # Adicionar arquivo_original se disponível
            if arquivo_original_id:
                update_data["modifica_arquivo"] = arquivo_original_id
                print(f"📝 Atualizando modifica_arquivo: {arquivo_original_id}")

            print(
                f"📡 Enviando PATCH para versão {versao_id} com {len(modificacoes_directus)} modificações..."
            )

            response = requests.patch(
                f"{self.base_url}/items/versao/{versao_id}",
                headers=DIRECTUS_HEADERS,
                json=update_data,
                timeout=300,  # Timeout maior para transação (5 minutos)
            )

            if response.status_code == 200:
                print(f"✅ Versão {versao_id} atualizada para status 'concluido'")
                print(
                    f"📊 Total: {len(modificacoes_directus)} modificações criadas em transação única"
                )

                # Extrair IDs das modificações criadas da resposta
                response_data = response.json().get("data", {})
                modificacoes_criadas = response_data.get("modificacoes", [])

                return {
                    "criadas": len(modificacoes_criadas),
                    "erros": len(modificacoes) - len(modificacoes_directus),
                    "ids_criados": [
                        m if isinstance(m, str) else m.get("id")
                        for m in modificacoes_criadas
                    ]
                    if modificacoes_criadas
                    else [],
                    "metodo": "transacao_unica",
                }
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get("errors", [{}])[0].get(
                        "message", error_msg
                    )
                    print(f"� Erro detalhado: {error_detail}")
                except Exception:
                    print(f"📄 Resposta: {response.text[:500]}")

                print(f"❌ Erro ao atualizar versão: {error_msg}")
                raise Exception(f"Falha ao persistir modificações: {error_msg}")

        except Exception as e:
            print(f"❌ Exceção ao persistir modificações: {e}")
            raise e

    def _converter_modificacao_para_directus(self, versao_id, mod):
        """
        Converte uma modificação do formato interno para o formato do Directus

        Args:
            versao_id: ID da versão
            mod: Objeto de modificação no formato interno

        Returns:
            dict: Objeto formatado para criação no Directus
        """
        # Mapear tipo interno para categoria do Directus
        tipo_para_categoria = {
            "ALTERACAO": "modificacao",
            "INSERCAO": "inclusao",
            "REMOCAO": "remocao",
            "COMENTARIO": "comentario",
            "FORMATACAO": "formatacao",
        }

        categoria = tipo_para_categoria.get(mod.get("tipo", "ALTERACAO"), "modificacao")

        # Extrair conteúdo original e novo
        conteudo_obj = mod.get("conteudo", {})
        if isinstance(conteudo_obj, dict):
            conteudo_original = conteudo_obj.get("original", "")
            conteudo_novo = conteudo_obj.get("novo", "")
        else:
            # Se conteudo não é dict, pode ser string direta (tag sem matching)
            conteudo_novo = str(conteudo_obj) if conteudo_obj else ""
            conteudo_original = ""

        # Usar posições reais se disponíveis (vindas do diff ou vinculação)
        # Se não, usar posição aproximada baseada em linha/coluna
        posicao_inicio_real = mod.get("posicao_inicio")
        posicao_fim_real = mod.get("posicao_fim")

        if posicao_inicio_real is not None and posicao_fim_real is not None:
            # Posições reais disponíveis (do diff ou vinculação)
            posicao_inicio = posicao_inicio_real
            posicao_fim = posicao_fim_real
        else:
            # Fallback: calcular aproximado por linha/coluna
            posicao = mod.get("posicao", {})
            linha = posicao.get("linha", 0)
            coluna = posicao.get("coluna", 0)
            posicao_inicio = linha * 1000 + coluna
            posicao_fim = linha * 1000 + coluna + len(conteudo_original)

        # Construir caminho baseado nas posições reais
        # Converter posição linear de volta para linha:coluna aproximado
        linha_inicio = posicao_inicio // 1000
        coluna_inicio = posicao_inicio % 1000
        linha_fim = posicao_fim // 1000
        coluna_fim = posicao_fim % 1000

        caminho_inicio = f"L{linha_inicio}:C{coluna_inicio}"
        caminho_fim = f"L{linha_fim}:C{coluna_fim}"

        # Montar objeto para Directus
        directus_mod = {
            "versao": versao_id,
            "status": "draft",
            "categoria": categoria,
            "conteudo": conteudo_original if conteudo_original else None,
            "alteracao": conteudo_novo if conteudo_novo else None,
            "caminho_inicio": caminho_inicio,
            "caminho_fim": caminho_fim,
            "posicao_inicio": posicao_inicio,
            "posicao_fim": posicao_fim,
        }

        # Adicionar cláusula se disponível (UUID obtido via vinculação com tags)
        if "clausula_id" in mod and mod["clausula_id"]:
            # Campo clausula é uma FK para tabela clausula (tipo uuid)
            directus_mod["clausula"] = mod["clausula_id"]
            print(
                f"📋 Cláusula vinculada: {mod.get('clausula_numero')} - {mod.get('clausula_nome')}"
            )
        else:
            # Se não há clausula_id, não enviar o campo (deixar null no banco)
            print(
                "⚠️  Modificação sem cláusula vinculada (nenhuma tag correspondente encontrada)"
            )

        # Adicionar campos opcionais se disponíveis
        if "confianca" in mod:
            # Converter confiança (0-1) para percentual se necessário
            confianca = mod["confianca"]
            if confianca <= 1.0:
                confianca = int(confianca * 100)
            directus_mod["confianca"] = confianca

        if "tags_relacionadas" in mod and mod["tags_relacionadas"]:
            # Juntar tags em string se for array
            tags = mod["tags_relacionadas"]
            if isinstance(tags, list):
                directus_mod["tags"] = ", ".join(tags)
            else:
                directus_mod["tags"] = str(tags)

        return directus_mod

    # ============================================================================
    # FASE 2: CAMINHO FELIZ - MAPEAMENTO VIA OFFSET
    # ============================================================================

    def _mapear_tags_via_offset(
        self, tags: list[dict], arquivo_com_tags_text: str
    ) -> list[TagMapeada]:
        """
        Mapeia tags para o sistema de coordenadas original usando cálculo de offset.

        Este método é usado no "Caminho Feliz" quando os documentos são idênticos.
        Calcula o offset acumulado removendo as tags e recalculando as posições.

        Args:
            tags: Lista de tags do modelo com posições no arquivo COM tags
            arquivo_com_tags_text: Texto completo do arquivo COM tags

        Returns:
            Lista de TagMapeada com posições recalculadas no arquivo SEM tags
        """
        print("🎯 Mapeando tags via offset (Caminho Feliz)")

        # 1. Encontrar todas as tags no texto e calcular offsets acumulados
        # Pattern para encontrar tags: {{TAG-xxx}} ou {{/TAG-xxx}} ou qualquer {{...}}
        tag_pattern = re.compile(r"\{\{/?[^}]+\}\}")

        # Lista de (posição_inicio_tag, tamanho_tag, conteudo_tag)
        tags_encontradas = []
        for match in tag_pattern.finditer(arquivo_com_tags_text):
            tags_encontradas.append(
                (match.start(), match.end() - match.start(), match.group())
            )

        print(f"   📍 Encontradas {len(tags_encontradas)} tags no texto")

        # 2. Construir mapa de offsets: posicao_com_tags → offset_acumulado
        # Cada tag adiciona seu tamanho ao offset
        offset_map = []  # Lista de (posicao, offset_acumulado)
        offset_atual = 0

        for pos_inicio, tamanho, _ in tags_encontradas:
            # Antes desta tag, o offset é o acumulado até agora
            offset_map.append((pos_inicio, offset_atual))
            # Depois desta tag, acumular seu tamanho
            offset_atual += tamanho

        # Adicionar ponto final
        offset_map.append((len(arquivo_com_tags_text), offset_atual))

        print(f"   📊 Offset final acumulado: {offset_atual} caracteres de tags")

        # 3. Mapear cada tag para o sistema de coordenadas original
        tags_mapeadas = []
        for tag in tags:
            # Posições originais (no arquivo COM tags)
            pos_inicio_com_tags = tag.get("posicao_inicio_texto", 0)
            pos_fim_com_tags = tag.get("posicao_fim_texto", 0)

            # Encontrar offset aplicável no início
            # Pegar o maior offset de uma tag que começa ANTES do início desta tag
            offset_inicio = 0
            for pos, offset in offset_map:
                if pos < pos_inicio_com_tags:  # Menor que (não menor ou igual)
                    offset_inicio = offset
                else:
                    break

            # Encontrar offset aplicável no fim
            # Pegar o maior offset de uma tag que começa ANTES OU NO fim desta tag
            offset_fim = 0
            for pos, offset in offset_map:
                if pos < pos_fim_com_tags:  # Menor que (não menor ou igual)
                    offset_fim = offset
                else:
                    break

            # Calcular posições no arquivo SEM tags
            pos_inicio_original = pos_inicio_com_tags - offset_inicio
            pos_fim_original = pos_fim_com_tags - offset_fim

            # Criar TagMapeada
            tag_mapeada = TagMapeada(
                tag_id=tag.get("id", ""),
                tag_nome=tag.get("tag_nome", ""),
                posicao_inicio_original=pos_inicio_original,
                posicao_fim_original=pos_fim_original,
                clausulas=tag.get("clausulas", []),
                score_inferencia=1.0,  # Caminho Feliz = confiança máxima
                metodo="offset",
            )

            tags_mapeadas.append(tag_mapeada)

        print(f"   ✅ {len(tags_mapeadas)} tags mapeadas com sucesso")
        return tags_mapeadas

    # ============================================================================
    # FASE 3: CAMINHO REAL - INFERÊNCIA POR CONTEÚDO COM CONTEXTO
    # ============================================================================

    def _processar_tag_individual(
        self,
        tag: dict,
        arquivo_original_text: str,
        arquivo_com_tags_text: str,
        tamanho_contexto: int,
    ) -> TagMapeada | None:
        """
        Processa uma tag individual para inferir sua posição.
        Função auxiliar para permitir processamento paralelo.

        Returns:
            TagMapeada se encontrou, None se não encontrou
        """
        # CORREÇÃO: Usar campo 'conteudo' da tag se disponível (já vem limpo do Directus)
        # Só extrair do texto COM tags se não vier o conteúdo
        conteudo_tag = tag.get("conteudo")

        # Obter posições SEMPRE (necessárias para extrair contexto)
        pos_inicio = tag.get("posicao_inicio_texto", 0)
        pos_fim = tag.get("posicao_fim_texto", 0)

        if not conteudo_tag:
            # Fallback: extrair do texto usando posições
            conteudo_tag = arquivo_com_tags_text[pos_inicio:pos_fim]

        if not conteudo_tag:
            print(f"   ⚠️  Tag {tag.get('tag_nome')} sem conteúdo, pulando")
            return None

        # Extrair contexto antes e depois (SEM normalizar)
        contexto_antes_start = max(0, pos_inicio - tamanho_contexto)
        contexto_antes = arquivo_com_tags_text[contexto_antes_start:pos_inicio]

        contexto_depois_end = min(
            len(arquivo_com_tags_text), pos_fim + tamanho_contexto
        )
        contexto_depois = arquivo_com_tags_text[pos_fim:contexto_depois_end]

        # Tentar encontrar com contexto completo (score 0.9)
        sequencia_completa = f"{contexto_antes}{conteudo_tag}{contexto_depois}"
        pos_encontrada = arquivo_original_text.find(sequencia_completa)

        if pos_encontrada >= 0:
            # Encontrou com contexto completo!
            offset_conteudo = len(contexto_antes)
            pos_inicio_original = pos_encontrada + offset_conteudo
            pos_fim_original = pos_inicio_original + len(conteudo_tag)
            score = 0.9
            metodo = "contexto_completo"
        else:
            # Tentar com contexto parcial (apenas antes OU depois)
            sequencia_antes = f"{contexto_antes}{conteudo_tag}"
            pos_encontrada = arquivo_original_text.find(sequencia_antes)

            if pos_encontrada >= 0:
                offset_conteudo = len(contexto_antes)
                pos_inicio_original = pos_encontrada + offset_conteudo
                pos_fim_original = pos_inicio_original + len(conteudo_tag)
                score = 0.7
                metodo = "contexto_parcial_antes"
            else:
                sequencia_depois = f"{conteudo_tag}{contexto_depois}"
                pos_encontrada = arquivo_original_text.find(sequencia_depois)

                if pos_encontrada >= 0:
                    pos_inicio_original = pos_encontrada
                    pos_fim_original = pos_inicio_original + len(conteudo_tag)
                    score = 0.7
                    metodo = "contexto_parcial_depois"
                else:
                    # Último recurso: apenas conteúdo
                    pos_encontrada = arquivo_original_text.find(conteudo_tag)

                    if pos_encontrada >= 0:
                        pos_inicio_original = pos_encontrada
                        pos_fim_original = pos_encontrada + len(conteudo_tag)
                        score = 0.5
                        metodo = "conteudo_apenas"
                    else:
                        # OTIMIZADO: Fuzzy matching com step adaptativo
                        tamanho_tag = len(conteudo_tag)
                        tamanho_min = int(tamanho_tag * 0.8)
                        tamanho_max = int(tamanho_tag * 1.2)

                        melhor_ratio = 0.0
                        melhor_pos = (0, 0)

                        # OTIMIZAÇÃO: Step adaptativo baseado no tamanho da tag
                        if tamanho_tag < 100:
                            step = max(20, tamanho_min // 8)
                        elif tamanho_tag < 500:
                            step = max(50, tamanho_min // 4)
                        else:
                            step = max(100, tamanho_min // 2)

                        # Criar chunks com overlap para não perder matches
                        for i in range(
                            0, len(arquivo_original_text) - tamanho_min, step
                        ):
                            # Testar 3 tamanhos estratégicos ao invés de todos
                            for tam in [
                                tamanho_min,
                                (tamanho_min + tamanho_max) // 2,
                                tamanho_max,
                            ]:
                                if i + tam > len(arquivo_original_text):
                                    continue

                                chunk = arquivo_original_text[i : i + tam]

                                # Usa RapidFuzz (221x mais rápido) ou difflib
                                ratio = calcular_similaridade(conteudo_tag, chunk)

                                if ratio > melhor_ratio:
                                    melhor_ratio = ratio
                                    melhor_pos = (i, i + tam)

                                # Early exit se encontrar match excelente
                                if melhor_ratio >= 0.95:
                                    break

                            if melhor_ratio >= 0.95:
                                break

                        # Aceitar se similaridade ≥ 85%
                        if melhor_ratio >= 0.85:
                            pos_inicio_original, pos_fim_original = melhor_pos
                            score = 0.4 + (melhor_ratio - 0.85) * 2
                            metodo = f"fuzzy_match_{melhor_ratio:.0%}"
                            print(
                                f"   🔍 Tag {tag.get('tag_nome')} encontrada via fuzzy matching (similaridade: {melhor_ratio:.1%})"
                            )
                        else:
                            # Não encontrou mesmo com fuzzy
                            print(
                                f"   ❌ Tag {tag.get('tag_nome')} não encontrada (melhor match: {melhor_ratio:.1%})"
                            )
                            return None

        # Criar TagMapeada
        tag_mapeada = TagMapeada(
            tag_id=tag.get("id", ""),
            tag_nome=tag.get("tag_nome", ""),
            posicao_inicio_original=pos_inicio_original,
            posicao_fim_original=pos_fim_original,
            clausulas=tag.get("clausulas", []),
            score_inferencia=score,
            metodo=metodo,
        )

        return tag_mapeada

    def _inferir_posicoes_via_conteudo_com_contexto(
        self,
        tags: list[dict],
        arquivo_original_text: str,
        arquivo_com_tags_text: str,
        tamanho_contexto: int = 50,
        max_workers: int | None = None,
    ) -> list[TagMapeada]:
        """
        Infere posições das tags no arquivo original usando busca por conteúdo + contexto.
        VERSÃO PARALELIZADA para aproveitar múltiplos CPUs.

        Este método é usado no "Caminho Real" quando os documentos são diferentes.
        Extrai o conteúdo de cada tag e busca no arquivo original usando contexto
        de vizinhança para desambiguar.

        Args:
            tags: Lista de tags do modelo com posições no arquivo COM tags
            arquivo_original_text: Texto do arquivo original (da versão)
            arquivo_com_tags_text: Texto completo do arquivo COM tags (do modelo)
            tamanho_contexto: Quantos caracteres antes/depois extrair como contexto
            max_workers: Número máximo de workers (None = usar CPU count)

        Returns:
            Lista de TagMapeada com posições inferidas no arquivo original
        """
        import multiprocessing

        if max_workers is None:
            max_workers = multiprocessing.cpu_count()

        print(
            f"🎯 Inferindo posições via conteúdo (Caminho Real) - {max_workers} workers (PROCESSOS)"
        )

        tags_mapeadas_ordenadas: list[tuple[int, TagMapeada]] = []
        total_tags = len(tags)

        # Métricas de progresso
        inicio_processamento = datetime.now()
        tags_processadas = 0
        tags_encontradas = 0

        # Processar tags em paralelo usando ProcessPoolExecutor (processos, não threads!)
        # ProcessPoolExecutor contorna o GIL do Python para tarefas CPU-bound
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tags para processamento
            future_to_tag = {
                executor.submit(
                    self._processar_tag_individual,
                    tag,
                    arquivo_original_text,
                    arquivo_com_tags_text,
                    tamanho_contexto,
                ): (index, tag)
                for index, tag in enumerate(tags)
            }

            # Coletar resultados conforme vão ficando prontos
            for future in as_completed(future_to_tag):
                index, tag = future_to_tag[future]
                tags_processadas += 1

                try:
                    tag_mapeada = future.result()
                    if tag_mapeada:
                        tags_mapeadas_ordenadas.append((index, tag_mapeada))
                        tags_encontradas += 1
                except Exception as exc:
                    print(f"   ❌ Tag {tag.get('tag_nome')} gerou exceção: {exc}")

                # Calcular métricas a cada 10 tags ou no final
                if tags_processadas % 10 == 0 or tags_processadas == total_tags:
                    tempo_decorrido = (
                        datetime.now() - inicio_processamento
                    ).total_seconds()
                    velocidade = (
                        tags_processadas / tempo_decorrido if tempo_decorrido > 0 else 0
                    )
                    tags_restantes = total_tags - tags_processadas
                    tempo_estimado = (
                        tags_restantes / velocidade if velocidade > 0 else 0
                    )
                    taxa_sucesso = (
                        (tags_encontradas / tags_processadas * 100)
                        if tags_processadas > 0
                        else 0
                    )

                    print(
                        f"   📊 Progresso: {tags_processadas}/{total_tags} tags "
                        f"({tags_processadas / total_tags * 100:.1f}%) | "
                        f"✅ {tags_encontradas} encontradas ({taxa_sucesso:.1f}%) | "
                        f"⚡ {velocidade:.2f} tags/s | "
                        f"⏱️  ETA: {tempo_estimado:.0f}s (~{tempo_estimado / 60:.1f}min)"
                    )

        tempo_total = (datetime.now() - inicio_processamento).total_seconds()
        velocidade_media = total_tags / tempo_total if tempo_total > 0 else 0

        tags_mapeadas_ordenadas.sort(key=lambda item: item[0])
        tags_mapeadas = [item[1] for item in tags_mapeadas_ordenadas]

        print(
            f"\n   ✅ Processamento concluído em {tempo_total:.1f}s "
            f"({tempo_total / 60:.2f} min) | "
            f"Velocidade média: {velocidade_media:.2f} tags/s"
        )
        print(
            f"   📈 Resultado: {len(tags_mapeadas)}/{len(tags)} tags inferidas com sucesso ({len(tags_mapeadas) / len(tags) * 100:.1f}%)"
        )

        return tags_mapeadas

    # ============================================================================
    # FIM FASE 3
    # ============================================================================

    # ============================================================================
    # FASE 4: SCORE E CATEGORIZAÇÃO
    # ============================================================================

    def _vincular_por_sobreposicao_com_score(
        self,
        tags_mapeadas: list[TagMapeada],
        modificacoes: list[dict],
    ) -> ResultadoVinculacao:
        """
        Vincula tags às modificações baseado em sobreposição de posições.

        Para cada modificação, calcula a sobreposição com cada tag mapeada.
        Aplica thresholds para categorizar a vinculação:
        - Alta confiança (score ≥ 0.8): vinculação automática
        - Média confiança (0.5 ≤ score < 0.8): revisão manual recomendada
        - Baixa confiança (score < 0.5): não vinculada

        Args:
            tags_mapeadas: Lista de tags com posições recalculadas no original
            modificacoes: Lista de modificações detectadas com posições

        Returns:
            ResultadoVinculacao com listas de vinculadas, revisao_manual, nao_vinculadas
        """
        print("🔗 Vinculando tags às modificações por sobreposição")
        print(f"   Total de tags mapeadas: {len(tags_mapeadas)}")
        print(f"   Total de modificações: {len(modificacoes)}")

        # Debug: mostrar primeiras 3 tags
        if tags_mapeadas and len(tags_mapeadas) >= 3:
            print("\n🏷️  Exemplo de tags mapeadas (primeiras 3):")
            for i, tag in enumerate(tags_mapeadas[:3]):
                print(
                    f"   Tag {i + 1}: {tag.tag_nome} [{tag.posicao_inicio_original}-{tag.posicao_fim_original}] método={tag.metodo}"
                )

        vinculadas = []
        revisao_manual = []
        nao_vinculadas = []

        for idx, modificacao in enumerate(modificacoes):
            mod_inicio = modificacao.get("posicao_inicio", 0)
            mod_fim = modificacao.get("posicao_fim", 0)
            mod_tipo = modificacao.get("tipo", "")

            # Debug: primeiras 3 modificações
            if idx < 3:
                print(
                    f"\n📝 Modificação {idx + 1}: tipo={mod_tipo} [{mod_inicio}-{mod_fim}]"
                )

            melhor_tag = None
            melhor_score = 0.0
            melhor_sobreposicao = 0

            # Calcular sobreposição com cada tag
            for tag in tags_mapeadas:
                # Calcular sobreposição das posições
                inicio_sobreposicao = max(mod_inicio, tag.posicao_inicio_original)
                fim_sobreposicao = min(mod_fim, tag.posicao_fim_original)
                tamanho_sobreposicao = max(0, fim_sobreposicao - inicio_sobreposicao)

                if tamanho_sobreposicao == 0:
                    continue  # Sem sobreposição

                # Debug: log TODAS as sobreposições (não só primeiras 3)
                if tamanho_sobreposicao > 0:
                    print(
                        f"      → Mod[{mod_inicio}-{mod_fim}] ∩ Tag {tag.tag_nome}[{tag.posicao_inicio_original}-{tag.posicao_fim_original}]: {tamanho_sobreposicao} chars"
                    )

                # Calcular tamanhos
                tamanho_modificacao = mod_fim - mod_inicio
                tamanho_tag = tag.posicao_fim_original - tag.posicao_inicio_original

                # Score de sobreposição: percentual da menor região coberta
                # Exemplo: se mod=10 chars e tag=100 chars, e sobreposição=10,
                # então score = 10/10 = 1.0 (modificação inteira dentro da tag)
                tamanho_menor = min(tamanho_modificacao, tamanho_tag)
                score_sobreposicao = (
                    tamanho_sobreposicao / tamanho_menor if tamanho_menor > 0 else 0.0
                )

                # Combinar com score de inferência da tag
                # Score final = média ponderada (70% sobreposição + 30% inferência)
                score_final = (0.7 * score_sobreposicao) + (0.3 * tag.score_inferencia)

                if score_final > melhor_score:
                    melhor_score = score_final
                    melhor_tag = tag
                    melhor_sobreposicao = tamanho_sobreposicao

            # Categorizar baseado no score
            if melhor_tag is None:
                # Nenhuma tag encontrada
                nao_vinculadas.append(
                    {
                        "modificacao": modificacao,
                        "motivo": "sem_sobreposicao",
                        "score": 0.0,
                    }
                )
                print(
                    f"   ❌ Modificação [{mod_inicio}-{mod_fim}] tipo={mod_tipo}: sem tag correspondente"
                )

            elif melhor_score >= 0.8:
                # Alta confiança - vinculação automática
                vinculadas.append(
                    {
                        "modificacao": modificacao,
                        "tag": melhor_tag,
                        "score": melhor_score,
                        "sobreposicao_chars": melhor_sobreposicao,
                        "metodo_inferencia": melhor_tag.metodo,
                    }
                )
                print(
                    f"   ✅ Modificação [{mod_inicio}-{mod_fim}] → Tag {melhor_tag.tag_nome} "
                    f"(score={melhor_score:.2f}, método={melhor_tag.metodo})"
                )

            elif melhor_score >= 0.5:
                # Média confiança - revisão manual
                revisao_manual.append(
                    {
                        "modificacao": modificacao,
                        "tag": melhor_tag,
                        "score": melhor_score,
                        "sobreposicao_chars": melhor_sobreposicao,
                        "metodo_inferencia": melhor_tag.metodo,
                        "motivo": "score_medio",
                    }
                )
                print(
                    f"   ⚠️  Modificação [{mod_inicio}-{mod_fim}] → Tag {melhor_tag.tag_nome} "
                    f"(score={melhor_score:.2f}) - REQUER REVISÃO"
                )

            else:
                # Baixa confiança - não vinculada
                nao_vinculadas.append(
                    {
                        "modificacao": modificacao,
                        "tag_proxima": melhor_tag,
                        "score": melhor_score,
                        "motivo": "score_baixo",
                    }
                )
                print(
                    f"   ❌ Modificação [{mod_inicio}-{mod_fim}]: score muito baixo ({melhor_score:.2f})"
                )

        resultado = ResultadoVinculacao(
            vinculadas=vinculadas,
            nao_vinculadas=nao_vinculadas,
            revisao_manual=revisao_manual,
        )

        print("\n📊 Resultado da vinculação:")
        print(f"   ✅ Vinculadas: {len(vinculadas)}")
        print(f"   ⚠️  Revisão manual: {len(revisao_manual)}")
        print(f"   ❌ Não vinculadas: {len(nao_vinculadas)}")
        print(f"   📈 Taxa de sucesso: {resultado.taxa_sucesso():.1f}%")
        print(f"   📊 Taxa de cobertura: {resultado.taxa_cobertura():.1f}%")

        return resultado

    # ============================================================================
    # FIM FASE 4
    # ============================================================================

    def _consolidar_modificacoes_vinculacao(
        self, resultado: ResultadoVinculacao
    ) -> list[dict]:
        """Converte o resultado da vinculação em uma lista plana de modificações."""

        modificacoes_enriquecidas: list[dict] = []

        def extrair_modificacao(item: dict) -> tuple[dict, dict]:
            if isinstance(item, dict) and "modificacao" in item:
                return copy.deepcopy(item["modificacao"]), item
            return copy.deepcopy(item), item if isinstance(item, dict) else {}

        def aplicar_tag(mod: dict, tag: TagMapeada | None) -> None:
            if not tag:
                return

            mod["tag_nome"] = getattr(tag, "tag_nome", None)

            if getattr(tag, "clausulas", None):
                primeira = tag.clausulas[0] if tag.clausulas else None
                if isinstance(primeira, dict):
                    mod.setdefault("clausula_id", primeira.get("id"))
                    mod.setdefault("clausula_numero", primeira.get("numero"))
                    mod.setdefault("clausula_nome", primeira.get("nome"))

        for item in resultado.vinculadas:
            modificacao, meta = extrair_modificacao(item)
            aplicar_tag(modificacao, meta.get("tag"))
            if "score" in meta:
                modificacao["score_vinculacao"] = meta["score"]
            if "sobreposicao_chars" in meta:
                modificacao["sobreposicao_chars"] = meta["sobreposicao_chars"]
            if "metodo_inferencia" in meta:
                modificacao["metodo_vinculacao"] = meta["metodo_inferencia"]
            modificacao["status_vinculacao"] = "automatico"
            modificacoes_enriquecidas.append(modificacao)

        for item in resultado.revisao_manual:
            modificacao, meta = extrair_modificacao(item)
            aplicar_tag(modificacao, meta.get("tag"))
            if "score" in meta:
                modificacao["score_vinculacao"] = meta["score"]
            if "motivo" in meta:
                modificacao["motivo_vinculacao"] = meta["motivo"]
            modificacao["status_vinculacao"] = "revisao_manual"
            modificacoes_enriquecidas.append(modificacao)

        for item in resultado.nao_vinculadas:
            modificacao, meta = extrair_modificacao(item)
            if "tag_proxima" in meta:
                aplicar_tag(modificacao, meta.get("tag_proxima"))

            # Garantir que conteudo seja preenchido com o texto da tag se disponível
            tag = meta.get("tag") or meta.get("tag_proxima")
            if tag and not modificacao.get("conteudo"):
                # Extrair conteudo da tag se disponível
                if hasattr(tag, "conteudo_tag"):
                    modificacao["conteudo"] = tag.conteudo_tag
                elif isinstance(tag, dict) and "conteudo_tag" in tag:
                    modificacao["conteudo"] = tag["conteudo_tag"]

            if "score" in meta:
                modificacao["score_vinculacao"] = meta["score"]
            if "motivo" in meta:
                modificacao["motivo_vinculacao"] = meta["motivo"]
            modificacao["status_vinculacao"] = "nao_vinculada"
            modificacoes_enriquecidas.append(modificacao)

        return modificacoes_enriquecidas

    # ============================================================================
    # FASE 5: ROBUSTEZ E INTEGRAÇÃO
    # ============================================================================

    def _vincular_modificacoes_clausulas_novo(
        self,
        modificacoes: list[dict],
        tags_modelo: list[dict],
        texto_com_tags: str,
        texto_original: str,
    ) -> dict:
        """
        NOVO ALGORITMO UNIFICADO: Vincula modificações às cláusulas usando algoritmo inteligente.

        Este é o novo método que substitui _vincular_modificacoes_clausulas() antigo.
        Decide automaticamente entre Caminho Feliz (offset) e Caminho Real (conteúdo)
        baseado na similaridade entre os documentos.

        Fluxo:
        1. Calcula similaridade entre arquivo COM tags e arquivo ORIGINAL
        2. Se similaridade ≥ 0.95 → Caminho Feliz (mapeamento por offset)
        3. Se similaridade < 0.95 → Caminho Real (inferência por conteúdo)
        4. Vincula modificações às tags mapeadas por sobreposição
        5. Categoriza em vinculadas/revisao_manual/nao_vinculadas

        Args:
            modificacoes: Lista de modificações detectadas com posições
            tags_modelo: Lista de tags do modelo com posições no arquivo COM tags
            texto_com_tags: Texto completo do arquivo COM tags do modelo
            texto_original: Texto completo do arquivo original da versão

        Returns:
            Dict com:
                - resultado: ResultadoVinculacao com categorização
                - metodo_usado: "offset" ou "conteudo"
                - similaridade: float entre 0.0 e 1.0
                - tags_mapeadas: list[TagMapeada]
        """
        print("\n" + "=" * 70)
        print("🚀 NOVO ALGORITMO DE VINCULAÇÃO INTELIGENTE")
        print("=" * 70)

        # Validações
        if not tags_modelo:
            print("⚠️  Nenhuma tag do modelo disponível")
            return {
                "resultado": ResultadoVinculacao(
                    vinculadas=[], nao_vinculadas=modificacoes, revisao_manual=[]
                ),
                "metodo_usado": "none",
                "similaridade": 0.0,
                "tags_mapeadas": [],
                "modificacoes": modificacoes,
            }

        if not modificacoes:
            print("ℹ️  Nenhuma modificação para vincular")
            return {
                "resultado": ResultadoVinculacao(
                    vinculadas=[], nao_vinculadas=[], revisao_manual=[]
                ),
                "metodo_usado": "none",
                "similaridade": 0.0,
                "tags_mapeadas": [],
                "modificacoes": [],
            }

        # PASSO 1: Remover tags do texto_com_tags para criar versão limpa
        print("\n📝 Passo 1: Preparando textos...")
        texto_sem_tags = re.sub(r"\{\{/?[^}]+\}\}", "", texto_com_tags)
        print(f"   Texto COM tags: {len(texto_com_tags)} caracteres")
        print(f"   Texto SEM tags: {len(texto_sem_tags)} caracteres")
        print(f"   Texto ORIGINAL: {len(texto_original)} caracteres")

        # PASSO 2: Calcular similaridade para decidir método
        print("\n🔍 Passo 2: Calculando similaridade entre documentos...")
        similaridade = calcular_similaridade(texto_sem_tags, texto_original)
        print(f"   Similaridade: {similaridade:.2%}")

        # PASSO 3: Decisão de método
        # IMPORTANTE: Após investigação profunda, descobrimos que o método de CONTEÚDO
        # funciona 2.5x melhor (41.8% vs 16.4%) porque:
        # - Busca diretamente no texto correto (versão modificada)
        # - Não sofre de desalinhamento de coordenadas
        # - Usa contexto para desambiguação
        #
        # O método offset sofre de desalinhamento porque mapeia:
        #   modelo COM tags → modelo SEM tags
        # Mas modificações estão em:
        #   modelo SEM tags → versão modificada
        #
        # Solução: Sempre usar CONTEÚDO (mais robusto para documentos modificados)
        metodo_usado = "conteudo"

        print("\n🎯 Passo 3: Decisão de método")
        print("   ✅ Usando CONTEÚDO (mais robusto para documentos modificados)")
        print(
            "   💡 Offset desabilitado temporariamente (desalinhamento de coordenadas)"
        )

        # PASSO 4: Mapear tags para coordenadas do arquivo original
        print(f"\n🗺️  Passo 4: Mapeando {len(tags_modelo)} tags...")
        # Sempre usar inferência por conteúdo (provou ser 2.5x melhor)
        tags_mapeadas = self._inferir_posicoes_via_conteudo_com_contexto(
            tags=tags_modelo,
            arquivo_original_text=texto_original,
            arquivo_com_tags_text=texto_com_tags,
            tamanho_contexto=50,
        )

        if not tags_mapeadas:
            print("   ❌ Nenhuma tag foi mapeada com sucesso!")
            return {
                "resultado": ResultadoVinculacao(
                    vinculadas=[], nao_vinculadas=modificacoes, revisao_manual=[]
                ),
                "metodo_usado": metodo_usado,
                "similaridade": similaridade,
                "tags_mapeadas": [],
                "modificacoes": modificacoes,
            }

        print(f"   ✅ {len(tags_mapeadas)} tags mapeadas com sucesso")

        # PASSO 5: Vincular modificações às tags por sobreposição
        print(f"\n🔗 Passo 5: Vinculando {len(modificacoes)} modificações...")
        resultado = self._vincular_por_sobreposicao_com_score(
            tags_mapeadas=tags_mapeadas, modificacoes=modificacoes
        )

        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESULTADO FINAL")
        print("=" * 70)
        print(f"Método usado: {metodo_usado.upper()}")
        print(f"Similaridade: {similaridade:.2%}")
        print(f"Tags mapeadas: {len(tags_mapeadas)}")
        print(f"Modificações processadas: {len(modificacoes)}")
        print(f"  ✅ Vinculadas (alta confiança): {len(resultado.vinculadas)}")
        print(f"  ⚠️  Revisão manual (média confiança): {len(resultado.revisao_manual)}")
        print(f"  ❌ Não vinculadas (baixa confiança): {len(resultado.nao_vinculadas)}")
        print(f"Taxa de sucesso: {resultado.taxa_sucesso():.1f}%")
        print(f"Taxa de cobertura: {resultado.taxa_cobertura():.1f}%")
        print("=" * 70)

        modificacoes_enriquecidas = self._consolidar_modificacoes_vinculacao(resultado)

        return {
            "resultado": resultado,
            "metodo_usado": metodo_usado,
            "similaridade": similaridade,
            "tags_mapeadas": tags_mapeadas,
            "modificacoes": modificacoes_enriquecidas,
        }

    # ============================================================================
    # FIM FASE 5
    # ============================================================================

    def _vincular_modificacoes_clausulas(
        self,
        modificacoes,
        tags_modelo,
        texto_com_tags,
        _texto_original=None,
        _texto_modificado=None,
    ):
        """
        Vincula cada modificação à cláusula correspondente baseado nas tags do modelo

        Args:
            modificacoes: Lista de modificações extraídas
            tags_modelo: Lista de tags do modelo de contrato com cláusulas (DEVEM ter posicoes)
            texto_com_tags: Texto do arquivo COM TAGS do modelo (usado como referência de posições)
            texto_original: Texto original da versão (para buscar modificações)
            texto_modificado: Texto modificado da versão (para buscar modificações)

        Returns:
            Lista de modificações atualizada com informação de cláusula
        """
        print(f"\n🔗 Vinculando {len(modificacoes)} modificações às cláusulas...")

        if not tags_modelo:
            print("⚠️ Nenhuma tag do modelo disponível para vinculação")
            return modificacoes

        # Remover tags do texto_com_tags para criar versão limpa (similar ao arquivo original da versão)
        texto_sem_tags = re.sub(r"\{\{/?TAG-[^}]+\}\}", "", texto_com_tags)
        texto_sem_tags = re.sub(r"\{\{/?[^}]+\}\}", "", texto_sem_tags)
        print(f"📝 Texto com tags: {len(texto_com_tags)} caracteres")
        print(f"📝 Texto sem tags: {len(texto_sem_tags)} caracteres")

        # Construir mapa de posições das tags - TODAS devem ter posição
        tag_positions = []
        tags_sem_posicao = []

        for tag in tags_modelo:
            tag_nome = tag.get("tag_nome")
            clausulas = tag.get("clausulas", [])
            posicao_inicio = tag.get("posicao_inicio_texto")
            posicao_fim = tag.get("posicao_fim_texto")

            if not tag_nome:
                continue

            # EXIGIR posições - não há fallback
            if posicao_inicio is None or posicao_fim is None:
                tags_sem_posicao.append(tag_nome)
                print(
                    f"❌ Tag '{tag_nome}': SEM POSIÇÃO (erro no processamento do modelo)"
                )
                continue

            tag_info = {
                "tag_nome": tag_nome,
                "posicao_inicio": posicao_inicio,
                "posicao_fim": posicao_fim,
                "clausulas": clausulas if isinstance(clausulas, list) else [],
            }
            tag_positions.append(tag_info)

        if tags_sem_posicao:
            print(f"\n⚠️  AVISO: {len(tags_sem_posicao)} tags sem posição encontradas:")
            for tag_nome in tags_sem_posicao[:10]:  # Mostrar até 10
                print(f"   - {tag_nome}")
            if len(tags_sem_posicao) > 10:
                print(f"   ... e mais {len(tags_sem_posicao) - 10} tags")
            print("   ⚠️  Essas tags NÃO serão usadas para vinculação.")
            print("   ⚠️  Verifique o processamento do modelo de contrato!\n")

        # Ordenar tags por posição
        tag_positions.sort(key=lambda x: x["posicao_inicio"])

        print(f"✅ {len(tag_positions)} tags com posições válidas para vinculação")

        # Construir mapa de cláusulas por tag para estatísticas
        tags_com_clausulas = sum(1 for t in tag_positions if t["clausulas"])
        print(f"📚 {tags_com_clausulas} tags possuem cláusulas vinculadas")

        # Vincular cada modificação à tag/cláusula baseado nas posições
        # ESTRATÉGIA:
        # 1. Normalizar texto COM tags (para ter base consistente de posições)
        # 2. Mapear posições das tags no texto normalizado COM tags
        # 3. Remover tags e buscar modificações no texto normalizado SEM tags
        # 4. Ajustar posições das tags para compensar remoção das tags

        # PASSO 1: Normalizar texto COM tags (preservando as tags)
        texto_com_tags_normalizado = re.sub(r"\s+", " ", texto_com_tags).strip()
        print(
            f"📝 Texto COM tags normalizado: {len(texto_com_tags_normalizado)} caracteres"
        )

        # PASSO 2: Mapear posições das tags no texto COM tags normalizado
        tag_positions_normalized = []
        for tag_info in tag_positions:
            tag_nome = tag_info["tag_nome"]

            # Buscar tag no texto COM tags normalizado
            # Formato: {{TAG-nome}} ... {{/TAG-nome}} ou {{nome}} ... {{/nome}}
            tag_abertura = f"{{{{TAG-{tag_nome}}}}}"
            tag_fechamento = f"{{{{/TAG-{tag_nome}}}}}"

            if tag_abertura not in texto_com_tags_normalizado:
                tag_abertura = f"{{{{{tag_nome}}}}}"
                tag_fechamento = f"{{{{/{tag_nome}}}}}"

            pos_abertura = texto_com_tags_normalizado.find(tag_abertura)
            pos_fechamento = texto_com_tags_normalizado.find(tag_fechamento)

            if pos_abertura < 0 or pos_fechamento < 0:
                print(
                    f"⚠️ Tag '{tag_nome}': não encontrada no texto normalizado COM tags"
                )
                continue

            # Posição do conteúdo: após tag abertura, antes tag fechamento
            pos_inicio_conteudo = pos_abertura + len(tag_abertura)
            pos_fim_conteudo = pos_fechamento

            tag_positions_normalized.append(
                {
                    "tag_nome": tag_nome,
                    "posicao_inicio_com_tags": pos_inicio_conteudo,
                    "posicao_fim_com_tags": pos_fim_conteudo,
                    "tag_abertura": tag_abertura,
                    "tag_fechamento": tag_fechamento,
                    "clausulas": tag_info["clausulas"],
                }
            )

        print(f"✅ {len(tag_positions_normalized)} tags mapeadas no texto normalizado")

        # PASSO 3: Criar texto SEM tags normalizado e mapear posições
        # Para cada tag, calcular quanto de "tamanho de tags" existe ANTES dela
        texto_sem_tags_normalizado = re.sub(
            r"\{\{/?TAG-[^}]+\}\}", "", texto_com_tags_normalizado
        )
        texto_sem_tags_normalizado = re.sub(
            r"\{\{/?[^}]+\}\}", "", texto_sem_tags_normalizado
        ).strip()
        print(
            f"📝 Texto SEM tags normalizado: {len(texto_sem_tags_normalizado)} caracteres"
        )

        # PASSO 4: Recalcular posições das tags no texto SEM tags
        # A ideia é: se uma tag começa na posição 100 no texto COM tags,
        # e há 30 caracteres de tags antes dela, ela começa na posição 70 no texto SEM tags
        tag_positions_final = []

        for tag_info in tag_positions_normalized:
            tag_nome = tag_info["tag_nome"]

            # Contar TODOS os caracteres de tags que aparecem ANTES desta tag
            texto_antes_da_tag = texto_com_tags_normalizado[
                : tag_info["posicao_inicio_com_tags"]
            ]

            # Encontrar todas as tags no texto antes
            todas_tags_antes = re.findall(r"\{\{/?[^}]+\}\}", texto_antes_da_tag)
            tamanho_tags_antes = sum(len(t) for t in todas_tags_antes)

            # A posição no texto SEM tags é: posição COM tags - tamanho das tags removidas antes
            pos_inicio_sem_tags = (
                tag_info["posicao_inicio_com_tags"] - tamanho_tags_antes
            )

            # Para a posição final, fazer o mesmo cálculo
            texto_ate_fim_tag = texto_com_tags_normalizado[
                : tag_info["posicao_fim_com_tags"]
            ]
            todas_tags_ate_fim = re.findall(r"\{\{/?[^}]+\}\}", texto_ate_fim_tag)
            tamanho_tags_ate_fim = sum(len(t) for t in todas_tags_ate_fim)

            pos_fim_sem_tags = tag_info["posicao_fim_com_tags"] - tamanho_tags_ate_fim

            # Garantir posições válidas
            pos_inicio_sem_tags = max(0, pos_inicio_sem_tags)
            pos_fim_sem_tags = min(len(texto_sem_tags_normalizado), pos_fim_sem_tags)

            tag_positions_final.append(
                {
                    "tag_nome": tag_nome,
                    "posicao_inicio": pos_inicio_sem_tags,
                    "posicao_fim": pos_fim_sem_tags,
                    "clausulas": tag_info["clausulas"],
                }
            )

        print("✅ Posições das tags ajustadas para texto SEM tags")

        modificacoes_sem_conteudo = []

        for idx, mod in enumerate(modificacoes):
            conteudo_mod = mod.get("conteudo", {})

            # Buscar texto da modificação (original ou novo, dependendo do tipo)
            texto_mod = conteudo_mod.get("original") or conteudo_mod.get("novo", "")

            if not texto_mod or len(texto_mod.strip()) == 0:
                modificacoes_sem_conteudo.append(idx)
                continue

            # NORMALIZAR o texto da modificação também (para comparação justa)
            texto_mod_normalizado = re.sub(r"\s+", " ", texto_mod).strip()

            # Buscar posição no texto NORMALIZADO SEM tags
            pos_inicio_mod = texto_sem_tags_normalizado.find(texto_mod_normalizado)

            if pos_inicio_mod < 0:
                # Tentar busca parcial (primeiros 50 caracteres)
                texto_parcial = (
                    texto_mod_normalizado[:50]
                    if len(texto_mod_normalizado) > 50
                    else texto_mod_normalizado
                )
                pos_inicio_mod = texto_sem_tags_normalizado.find(texto_parcial)
                if pos_inicio_mod >= 0:
                    texto_mod_normalizado = texto_parcial

            if pos_inicio_mod < 0:
                print(f"⚠️ Mod #{idx}: texto não encontrado no documento")
                continue

            pos_fim_mod = pos_inicio_mod + len(texto_mod_normalizado)

            # Encontrar a tag que contém esta posição (agora no mesmo espaço de coordenadas!)
            vinculada = False
            for tag_info in tag_positions_final:
                # Verificar se há sobreposição entre a modificação e a tag
                if (
                    tag_info["posicao_inicio"]
                    <= pos_inicio_mod
                    <= tag_info["posicao_fim"]
                ) or (
                    tag_info["posicao_inicio"] <= pos_fim_mod <= tag_info["posicao_fim"]
                ):
                    mod["tag_nome"] = tag_info["tag_nome"]
                    mod["posicao_inicio"] = pos_inicio_mod
                    mod["posicao_fim"] = pos_fim_mod

                    # Se há cláusulas associadas, usar a primeira
                    if tag_info["clausulas"]:
                        primeira_clausula = tag_info["clausulas"][0]
                        mod["clausula_id"] = primeira_clausula.get("id")
                        mod["clausula_numero"] = primeira_clausula.get("numero")
                        mod["clausula_nome"] = primeira_clausula.get("nome")

                        print(
                            f"✅ Mod #{idx} (pos {pos_inicio_mod}-{pos_fim_mod}) → "
                            f"Tag '{tag_info['tag_nome']}' (pos {tag_info['posicao_inicio']}-{tag_info['posicao_fim']}) → "
                            f"Cláusula {primeira_clausula.get('numero')}"
                        )
                        vinculada = True
                    else:
                        print(
                            f"⚠️ Mod #{idx} → Tag '{tag_info['tag_nome']}' (sem cláusula associada)"
                        )
                    break

            if not vinculada:
                print(
                    f"⚠️ Mod #{idx}: posição {pos_inicio_mod}-{pos_fim_mod} não encontrada em nenhuma tag"
                )

        if modificacoes_sem_conteudo:
            print(
                f"\n⚠️  {len(modificacoes_sem_conteudo)} modificações sem conteúdo (não vinculadas)"
            )

        # Resumo
        mods_com_clausula = sum(1 for m in modificacoes if m.get("clausula_id"))
        print(
            f"\n📊 Resumo: {mods_com_clausula}/{len(modificacoes)} modificações vinculadas a cláusulas via tags"
        )

        return modificacoes

    def _process_versao_com_ast(self, versao_id, versao_data):
        """Processa versão usando implementação AST do Pandoc

        Args:
            versao_id: ID da versão
            versao_data: Dados da versão do Directus

        Returns:
            dict: Resultado do processamento com modificações e métricas
        """
        from pathlib import Path

        global diff_cache

        try:
            # 1. Baixar arquivos DOCX
            arquivo_novo_id = versao_data.get("arquivo")
            arquivo_original_id = self._get_arquivo_original(versao_data)

            if not arquivo_novo_id or not arquivo_original_id:
                return {"error": "Arquivos DOCX não encontrados para processamento AST"}

            print(f"📥 Baixando arquivo original {arquivo_original_id}...")
            original_docx = self._download_docx_to_temp(arquivo_original_id)

            print(f"📥 Baixando arquivo modificado {arquivo_novo_id}...")
            modified_docx = self._download_docx_to_temp(arquivo_novo_id)

            # 2. Processar com AST
            print("🔬 Processando documentos com AST do Pandoc...")

            # Extrair parágrafos estruturados usando AST
            print("📥 Convertendo documento original para AST...")
            ast_original = PandocASTProcessor.convert_docx_to_ast(original_docx)
            original_paras = PandocASTProcessor.extract_paragraphs_from_ast(
                ast_original
            )
            print(
                f"✅ AST do documento original extraído: {len(original_paras)} parágrafos"
            )

            print("📥 Convertendo documento modificado para AST...")
            ast_modified = PandocASTProcessor.convert_docx_to_ast(modified_docx)
            modified_paras = PandocASTProcessor.extract_paragraphs_from_ast(
                ast_modified
            )
            print(
                f"✅ AST do documento modificado extraído: {len(modified_paras)} parágrafos"
            )

            # Gerar diff usando parágrafos estruturados
            print("🔍 Gerando HTML de comparação...")
            diff_html = self._generate_diff_html_from_ast(
                original_paras, modified_paras
            )
            print(f"✅ HTML de comparação gerado: {len(diff_html)} caracteres")

            # Extrair modificações do diff
            print("🔬 Extraindo modificações do HTML...")
            modificacoes = self._extrair_modificacoes_do_diff_ast(
                diff_html, original_paras, modified_paras
            )

            # Calcular métricas
            tipos = {"ALTERACAO": 0, "REMOCAO": 0, "INSERCAO": 0}
            for mod in modificacoes:
                tipos[mod["tipo"]] = tipos.get(mod["tipo"], 0) + 1

            print(f"✅ Total de modificações extraídas: {len(modificacoes)}")
            print(f"  - ALTERACAO: {tipos['ALTERACAO']}")
            print(f"  - REMOCAO: {tipos['REMOCAO']}")
            print(f"  - INSERCAO: {tipos['INSERCAO']}")

            resultado_ast = {
                "modificacoes": modificacoes,
                "metricas": {
                    "total_modificacoes": len(modificacoes),
                    "alteracoes": tipos["ALTERACAO"],
                    "remocoes": tipos["REMOCAO"],
                    "insercoes": tipos["INSERCAO"],
                },
                "diff_html": diff_html,
                "texto_original": "\n".join(p["text"] for p in original_paras),
                "texto_modificado": "\n".join(p["text"] for p in modified_paras),
            }

            # 3. Buscar tags do modelo para vinculação (igual ao processo normal)
            tags_modelo = []
            modelo_id = None

            try:
                contrato_id = versao_data.get("contrato")
                if contrato_id:
                    print(f"🔍 Buscando modelo do contrato {contrato_id}...")
                    contrato_response = requests.get(
                        f"{self.base_url}/items/contrato/{contrato_id}",
                        headers=DIRECTUS_HEADERS,
                        params={"fields": "modelo_contrato"},
                        timeout=10,
                    )
                    if contrato_response.status_code == 200:
                        modelo_id = contrato_response.json()["data"].get(
                            "modelo_contrato"
                        )

                if modelo_id:
                    print(f"🔍 Buscando tags do modelo {modelo_id}...")
                    tags_response = requests.get(
                        f"{self.base_url}/items/modelo_contrato_tag",
                        headers=DIRECTUS_HEADERS,
                        params={
                            "filter[modelo_contrato][_eq]": modelo_id,
                            "fields": "id,tag_nome,caminho_tag_inicio,caminho_tag_fim,posicao_inicio_texto,posicao_fim_texto,conteudo,clausulas.id,clausulas.numero,clausulas.nome",
                            "limit": -1,
                        },
                        timeout=10,
                    )
                    if tags_response.status_code == 200:
                        tags_modelo = tags_response.json().get("data", [])
                        print(
                            f"✅ Encontradas {len(tags_modelo)} tags do modelo para vinculação"
                        )
            except Exception as e:
                print(f"⚠️ Erro ao buscar tags: {e}")

            # 4. Vincular modificações AST às cláusulas
            modificacoes = resultado_ast["modificacoes"]
            if tags_modelo:
                print("🔗 Vinculando modificações AST às cláusulas...")
                # Extrair texto do arquivo modificado para vinculação
                modified_text = self._download_and_extract_text(arquivo_novo_id)

                if modified_text:
                    resultado_vinculacao = self._vincular_modificacoes_clausulas_novo(
                        modificacoes=modificacoes,
                        tags_modelo=tags_modelo,
                        texto_com_tags=modified_text,
                        texto_original=modified_text,
                    )

                    if resultado_vinculacao and resultado_vinculacao.get(
                        "modificacoes"
                    ):
                        modificacoes = resultado_vinculacao["modificacoes"]

            # 5. Calcular blocos (usar HTML do AST)
            diff_html = resultado_ast.get("diff_html", "")
            resultado_blocos = self._calcular_blocos_avancado(versao_id, diff_html)

            # 6. Criar registro no cache
            diff_id = str(uuid.uuid4())
            diff_data = {
                "id": diff_id,
                "versao_id": versao_id,
                "versao_data": versao_data,
                "original": resultado_ast.get("texto_original", ""),
                "modified": resultado_ast.get("texto_modificado", ""),
                "diff_html": diff_html,
                "modificacoes": modificacoes,
                "total_blocos": resultado_blocos.get("total_blocos", 1),
                "blocos_detalhados": resultado_blocos.get("blocos_detalhados", []),
                "metodo_calculo": resultado_blocos.get("metodo", "unknown"),
                "metodo_deteccao": "AST_PANDOC",
                "created_at": datetime.now().isoformat(),
                "url": f"http://localhost:{FLASK_PORT}/view/{diff_id}",
                "mode": "ast",
                "metricas": resultado_ast.get("metricas", {}),
            }

            diff_cache[diff_id] = diff_data

            # 7. Gravar resultados no Directus
            print("\n" + "=" * 100)
            print("💾 GRAVANDO RESULTADOS AST NO DIRECTUS")
            print("=" * 100)

            try:
                # Atualizar versão com métricas AST
                metricas = resultado_ast.get("metricas", {})
                versao_update = {
                    "total_modificacoes": metricas.get(
                        "total_modificacoes", len(modificacoes)
                    ),
                    "alteracoes": metricas.get("alteracoes", 0),
                    "remocoes": metricas.get("remocoes", 0),
                    "insercoes": metricas.get("insercoes", 0),
                    "metodo_deteccao": "AST_PANDOC",
                    "status": "processada",
                    "total_blocos": resultado_blocos.get("total_blocos", 1),
                }

                print(f"📝 Atualizando versão {versao_id} com métricas AST...")
                versao_response = requests.patch(
                    f"{self.base_url}/items/versao/{versao_id}",
                    headers=DIRECTUS_HEADERS,
                    json=versao_update,
                    timeout=10,
                )

                if versao_response.status_code in [200, 204]:
                    print("✅ Versão atualizada com métricas AST")
                    print(
                        f"   - Total modificações: {versao_update['total_modificacoes']}"
                    )
                    print(f"   - ALTERACAO: {versao_update['alteracoes']}")
                    print(f"   - REMOCAO: {versao_update['remocoes']}")
                    print(f"   - INSERCAO: {versao_update['insercoes']}")
                    print(f"   - Blocos: {versao_update['total_blocos']}")
                else:
                    print(
                        f"⚠️ Erro ao atualizar versão: HTTP {versao_response.status_code}"
                    )
                    print(f"   Resposta: {versao_response.text[:200]}")

                # Gravar modificações individuais no Directus
                print(f"\n📝 Gravando {len(modificacoes)} modificações no Directus...")
                modificacoes_criadas = 0

                for idx, mod in enumerate(modificacoes, 1):
                    # Mapear campos corretamente para o schema do Directus
                    # categoria = tipo (ALTERACAO, REMOCAO, INSERCAO)
                    # conteudo = texto original
                    # alteracao = texto novo/modificado
                    # clausula = ID da cláusula vinculada (se houver)
                    mod_data = {
                        "versao": versao_id,
                        "categoria": mod.get("tipo", "ALTERACAO"),  # tipo → categoria
                        "conteudo": mod.get("conteudo", {}).get(
                            "original"
                        ),  # conteudo_original → conteudo
                        "alteracao": mod.get("conteudo", {}).get(
                            "novo"
                        ),  # conteudo_novo → alteracao
                        "clausula": mod.get("clausula_id"),  # ID da cláusula vinculada
                        "caminho_inicio": mod.get("posicao", {}).get(
                            "linha"
                        ),  # posicao_linha → caminho_inicio
                        "caminho_fim": mod.get("posicao", {}).get(
                            "coluna"
                        ),  # posicao_coluna → caminho_fim
                    }

                    # Limpar campos None
                    mod_data = {k: v for k, v in mod_data.items() if v is not None}

                    try:
                        mod_response = requests.post(
                            f"{self.base_url}/items/modificacao",
                            headers=DIRECTUS_HEADERS,
                            json=mod_data,
                            timeout=10,
                        )

                        if mod_response.status_code in [200, 201]:
                            modificacoes_criadas += 1
                            if (
                                idx <= 5 or idx % 10 == 0
                            ):  # Mostrar primeiras 5 e múltiplos de 10
                                print(f"  ✅ Modificação #{idx} ({mod['tipo']}) criada")
                        else:
                            print(
                                f"  ⚠️ Erro ao criar modificação #{idx}: HTTP {mod_response.status_code}"
                            )

                    except Exception as e:
                        print(f"  ⚠️ Erro ao gravar modificação #{idx}: {e}")

                print(
                    f"\n✅ Gravação concluída: {modificacoes_criadas}/{len(modificacoes)} modificações salvas no Directus"
                )

            except Exception as e:
                print(f"⚠️ Erro ao gravar no Directus: {e}")
                import traceback

                traceback.print_exc()

            # Limpar arquivos temporários
            Path(original_docx).unlink(missing_ok=True)
            Path(modified_docx).unlink(missing_ok=True)

            print("✅ Processamento AST concluído!")
            print(
                f"📊 Resultados: {len(modificacoes)} modificações detectadas usando AST"
            )

            return {
                "success": True,
                "diff_id": diff_id,
                "url": diff_data["url"],
                "modificacoes": modificacoes,
                "metricas": resultado_ast.get("metricas", {}),
                "total_blocos": resultado_blocos.get("total_blocos", 1),
                "metodo": "AST_PANDOC",
            }

        except Exception as e:
            print(f"❌ Erro no processamento AST: {e}")
            import traceback

            traceback.print_exc()
            return {"error": f"Erro no processamento AST: {str(e)}"}

    def _generate_diff_html_from_ast(
        self, original_paras: list[dict], modified_paras: list[dict]
    ) -> str:
        """Gera HTML de diff baseado em parágrafos estruturados do AST."""
        html = ["<div class='diff-container'>"]

        # Usar SequenceMatcher para comparar parágrafos
        orig_texts = [p["text"] for p in original_paras]
        mod_texts = [p["text"] for p in modified_paras]

        matcher = difflib.SequenceMatcher(None, orig_texts, mod_texts, autojunk=False)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                # Parágrafos inalterados
                for i in range(i1, i2):
                    para = original_paras[i]
                    text = self._escape_html(para["text"])
                    if para.get("clause_number"):
                        html.append(
                            f"<div class='diff-unchanged clause-{para['clause_number']}'>{text}</div>"
                        )
                    else:
                        html.append(f"<div class='diff-unchanged'>{text}</div>")

            elif tag == "delete":
                # Parágrafos removidos
                for i in range(i1, i2):
                    para = original_paras[i]
                    text = self._escape_html(para["text"])
                    clause_attr = (
                        f" data-clause='{para['clause_number']}'"
                        if para.get("clause_number")
                        else ""
                    )
                    html.append(
                        f"<div class='diff-removed'{clause_attr}>- {text}</div>"
                    )

            elif tag == "insert":
                # Parágrafos adicionados
                for j in range(j1, j2):
                    para = modified_paras[j]
                    text = self._escape_html(para["text"])
                    clause_attr = (
                        f" data-clause='{para['clause_number']}'"
                        if para.get("clause_number")
                        else ""
                    )
                    html.append(f"<div class='diff-added'{clause_attr}>+ {text}</div>")

            elif tag == "replace":
                # Parágrafos modificados
                for idx in range(max(i2 - i1, j2 - j1)):
                    orig_idx = i1 + idx
                    mod_idx = j1 + idx

                    orig_para = original_paras[orig_idx] if orig_idx < i2 else None
                    mod_para = modified_paras[mod_idx] if mod_idx < j2 else None

                    if orig_para and mod_para:
                        # Ambos existem - é uma alteração
                        orig_text = self._escape_html(orig_para["text"])
                        mod_text = self._escape_html(mod_para["text"])

                        orig_clause = (
                            f" data-clause='{orig_para['clause_number']}'"
                            if orig_para.get("clause_number")
                            else ""
                        )
                        mod_clause = (
                            f" data-clause='{mod_para['clause_number']}'"
                            if mod_para.get("clause_number")
                            else ""
                        )

                        html.append(
                            f"<div class='diff-removed'{orig_clause}>- {orig_text}</div>"
                        )
                        html.append(
                            f"<div class='diff-added'{mod_clause}>+ {mod_text}</div>"
                        )

                    elif orig_para and not mod_para:
                        # Só original - remoção
                        orig_text = self._escape_html(orig_para["text"])
                        clause_attr = (
                            f" data-clause='{orig_para['clause_number']}'"
                            if orig_para.get("clause_number")
                            else ""
                        )
                        html.append(
                            f"<div class='diff-removed'{clause_attr}>- {orig_text}</div>"
                        )

                    elif not orig_para and mod_para:
                        # Só modificado - inserção
                        mod_text = self._escape_html(mod_para["text"])
                        clause_attr = (
                            f" data-clause='{mod_para['clause_number']}'"
                            if mod_para.get("clause_number")
                            else ""
                        )
                        html.append(
                            f"<div class='diff-added'{clause_attr}>+ {mod_text}</div>"
                        )

        html.append("</div>")
        return "\n".join(html)

    def _extrair_modificacoes_do_diff_ast(
        self, diff_html: str, _original_paras: list[dict], _modified_paras: list[dict]
    ) -> list[dict]:
        """Extrai modificações do HTML de diff (versão AST)."""
        modificacoes = []
        modificacao_id = 1

        # Parse HTML simples para extrair divs
        removed_pattern = r"<div class='diff-removed'[^>]*>- (.*?)</div>"
        added_pattern = r"<div class='diff-added'[^>]*>\+ (.*?)</div>"

        removed_matches = list(re.finditer(removed_pattern, diff_html))
        added_matches = list(re.finditer(added_pattern, diff_html))

        # Extrair data-clause attributes
        removed_with_clause = []
        for match in removed_matches:
            full_tag = diff_html[match.start() : match.end()]
            clause_match = re.search(r"data-clause='([^']+)'", full_tag)
            removed_with_clause.append(
                {
                    "text": match.group(1),
                    "clause": clause_match.group(1) if clause_match else None,
                    "position": match.start(),
                }
            )

        added_with_clause = []
        for match in added_matches:
            full_tag = diff_html[match.start() : match.end()]
            clause_match = re.search(r"data-clause='([^']+)'", full_tag)
            added_with_clause.append(
                {
                    "text": match.group(1),
                    "clause": clause_match.group(1) if clause_match else None,
                    "position": match.start(),
                }
            )

        # Agrupar modificações por proximidade
        i = 0
        j = 0

        while i < len(removed_with_clause) or j < len(added_with_clause):
            if i < len(removed_with_clause) and j < len(added_with_clause):
                removed = removed_with_clause[i]
                added = added_with_clause[j]

                # Verificar se são pares relacionados
                is_pair = False

                # Critério 1: Mesma cláusula
                if (
                    removed.get("clause")
                    and added.get("clause")
                    and removed["clause"] == added["clause"]
                ):
                    is_pair = True

                # Critério 2: Próximos no documento
                if (
                    not is_pair
                    and abs(removed["position"] - added["position"]) < 200
                    and added["position"] > removed["position"]
                ):
                    is_pair = True

                if is_pair:
                    # É uma ALTERACAO
                    modificacoes.append(
                        {
                            "id": modificacao_id,
                            "tipo": "ALTERACAO",
                            "css_class": "diff-alteracao",
                            "confianca": 0.95,
                            "posicao": {"linha": modificacao_id, "coluna": 1},
                            "clausula_original": removed.get("clause"),
                            "clausula_modificada": added.get("clause"),
                            "conteudo": {
                                "original": self._unescape_html(removed["text"]),
                                "novo": self._unescape_html(added["text"]),
                            },
                        }
                    )
                    i += 1
                    j += 1
                    modificacao_id += 1

                elif removed["position"] < added["position"]:
                    # Remoção pura
                    modificacoes.append(
                        {
                            "id": modificacao_id,
                            "tipo": "REMOCAO",
                            "css_class": "diff-remocao",
                            "confianca": 0.85,
                            "posicao": {"linha": modificacao_id, "coluna": 1},
                            "clausula_original": removed.get("clause"),
                            "conteudo": {
                                "original": self._unescape_html(removed["text"])
                            },
                        }
                    )
                    i += 1
                    modificacao_id += 1

                else:
                    # Inserção pura
                    modificacoes.append(
                        {
                            "id": modificacao_id,
                            "tipo": "INSERCAO",
                            "css_class": "diff-insercao",
                            "confianca": 0.9,
                            "posicao": {"linha": modificacao_id, "coluna": 1},
                            "clausula_modificada": added.get("clause"),
                            "conteudo": {"novo": self._unescape_html(added["text"])},
                        }
                    )
                    j += 1
                    modificacao_id += 1

            elif i < len(removed_with_clause):
                # Só remoções restantes
                removed = removed_with_clause[i]
                modificacoes.append(
                    {
                        "id": modificacao_id,
                        "tipo": "REMOCAO",
                        "css_class": "diff-remocao",
                        "confianca": 0.85,
                        "posicao": {"linha": modificacao_id, "coluna": 1},
                        "clausula_original": removed.get("clause"),
                        "conteudo": {"original": self._unescape_html(removed["text"])},
                    }
                )
                i += 1
                modificacao_id += 1

            elif j < len(added_with_clause):
                # Só inserções restantes
                added = added_with_clause[j]
                modificacoes.append(
                    {
                        "id": modificacao_id,
                        "tipo": "INSERCAO",
                        "css_class": "diff-insercao",
                        "confianca": 0.9,
                        "posicao": {"linha": modificacao_id, "coluna": 1},
                        "clausula_modificada": added.get("clause"),
                        "conteudo": {"novo": self._unescape_html(added["text"])},
                    }
                )
                j += 1
                modificacao_id += 1

        return modificacoes

    def _download_docx_to_temp(self, file_id):
        """Baixa arquivo DOCX do Directus para arquivo temporário"""
        url = f"{self.base_url}/assets/{file_id}"
        response = requests.get(url, headers=DIRECTUS_HEADERS, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"Erro ao baixar arquivo {file_id}: HTTP {response.status_code}"
            )

        # Salvar em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            f.write(response.content)
            return f.name

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
            print(f"   Versão atual date_created: {versao_atual_date}")

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

            print(f"🔍 DEBUG: Busca versão anterior - status={response.status_code}")
            if response.status_code == 200:
                versoes_anteriores = response.json().get("data", [])
                print(
                    f"🔍 DEBUG: Versões anteriores encontradas: {len(versoes_anteriores)}"
                )
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

            print(f"🔍 DEBUG: Response status={response.status_code}")
            if response.status_code == 200:
                contrato_data = response.json().get("data", {})
                print(f"🔍 DEBUG: contrato_data={contrato_data}")
                modelo_contrato = contrato_data.get("modelo_contrato")
                print(f"🔍 DEBUG: modelo_contrato={modelo_contrato}")
                if modelo_contrato:
                    arquivo_original_id = modelo_contrato.get("arquivo_original")
                    print(f"🔍 DEBUG: arquivo_original_id={arquivo_original_id}")
                    if arquivo_original_id:
                        print(
                            f"✅ Encontrado arquivo original do modelo: {arquivo_original_id}"
                        )
                        return arquivo_original_id
                    else:
                        print("⚠️  arquivo_original está NULL no modelo_contrato")
                else:
                    print("⚠️  modelo_contrato não encontrado ou NULL")
            else:
                print(f"❌ Erro ao buscar contrato: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")

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

            response = requests.get(download_url, headers=DIRECTUS_HEADERS, timeout=300)

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
                    from docx import Document  # type: ignore

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
        """Gera HTML de diff inteligente com agrupamento semântico"""
        print("🔍 Iniciando geração de diff inteligente")

        # Usar algoritmo de diff mais sofisticado
        import difflib

        # Dividir em unidades semânticas (cláusulas individuais)
        orig_paragraphs = self._split_into_semantic_units(original)
        mod_paragraphs = self._split_into_semantic_units(modified)

        print(f"📝 Original: {len(orig_paragraphs)} unidades semânticas")
        print(f"📝 Modificado: {len(mod_paragraphs)} unidades semânticas")

        html = ["<div class='diff-container'>"]
        current_clause = None

        # Usar SequenceMatcher para comparação mais inteligente
        # autojunk=False para não ignorar linhas repetidas
        matcher = difflib.SequenceMatcher(
            None, orig_paragraphs, mod_paragraphs, autojunk=False
        )

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                # Conteúdo inalterado
                for i in range(i1, i2):
                    para = orig_paragraphs[i]
                    if para.strip():
                        # Verificar se é nova cláusula
                        new_clause = self._identify_clause(para)
                        if new_clause and new_clause != current_clause:
                            current_clause = new_clause
                            html.append(
                                f"<div class='clause-header'>📋 {current_clause}</div>"
                            )

                        para_escaped = self._escape_html(para)
                        html.append(f"<div class='diff-unchanged'>{para_escaped}</div>")

            elif tag == "delete":
                # Conteúdo removido
                for i in range(i1, i2):
                    para = orig_paragraphs[i]
                    if para.strip():
                        para_escaped = self._escape_html(para)
                        html.append(f"<div class='diff-removed'>- {para_escaped}</div>")

            elif tag == "insert":
                # Conteúdo adicionado
                for j in range(j1, j2):
                    para = mod_paragraphs[j]
                    if para.strip():
                        # Verificar se é nova cláusula
                        new_clause = self._identify_clause(para)
                        if new_clause and new_clause != current_clause:
                            current_clause = new_clause
                            html.append(
                                f"<div class='clause-header'>📋 {current_clause}</div>"
                            )

                        para_escaped = self._escape_html(para)
                        html.append(f"<div class='diff-added'>+ {para_escaped}</div>")

            elif tag == "replace":
                # Conteúdo substituído - processar cada unidade individualmente
                # para evitar agrupar modificações distintas
                max_len = max(i2 - i1, j2 - j1)

                for idx in range(max_len):
                    orig_idx = i1 + idx
                    mod_idx = j1 + idx

                    # Obter conteúdo original e modificado desta unidade
                    orig_content = (
                        orig_paragraphs[orig_idx].strip() if orig_idx < i2 else ""
                    )
                    mod_content = (
                        mod_paragraphs[mod_idx].strip() if mod_idx < j2 else ""
                    )

                    # Se ambos vazios, pular
                    if not orig_content and not mod_content:
                        continue

                    # Se apenas um lado tem conteúdo, é inserção ou remoção
                    if not orig_content and mod_content:
                        new_clause = self._identify_clause(mod_content)
                        if new_clause and new_clause != current_clause:
                            current_clause = new_clause
                            html.append(
                                f"<div class='clause-header'>📋 {current_clause}</div>"
                            )
                        html.append(
                            f"<div class='diff-added'>+ {self._escape_html(mod_content)}</div>"
                        )
                        continue

                    if orig_content and not mod_content:
                        html.append(
                            f"<div class='diff-removed'>- {self._escape_html(orig_content)}</div>"
                        )
                        continue

                    # Ambos têm conteúdo - é substituição real
                    if self._is_field_replacement(orig_content, mod_content):
                        # Melhor apresentação para preenchimento de campos
                        field_info = self._extract_field_info(orig_content, mod_content)
                        html.append("<div class='diff-field-replacement'>")
                        html.append(
                            f"  <div class='field-name'>📝 {field_info['field_name']}</div>"
                        )
                        html.append(
                            f"  <div class='diff-removed'>- {self._escape_html(orig_content)}</div>"
                        )
                        html.append(
                            f"  <div class='diff-added'>+ {self._escape_html(mod_content)}</div>"
                        )
                        html.append("</div>")
                    else:
                        # Modificação normal
                        html.append(
                            f"<div class='diff-removed'>- {self._escape_html(orig_content)}</div>"
                        )
                        html.append(
                            f"<div class='diff-added'>+ {self._escape_html(mod_content)}</div>"
                        )

        html.append("</div>")
        result = "\n".join(html)
        print(f"✅ Diff HTML gerado: {len(result)} caracteres")
        return result

    def _split_into_semantic_units(self, text):
        """Divide texto em unidades semânticas (cláusulas individuais)"""

        # Padrão para identificar cláusulas: número.número no início de linha
        # Exemplos: 1.1, 1.2, 2.1, 2.2, etc.
        # Também captura seções como "1." ou "2."
        # Aceita espaço (\s) ou letra maiúscula ([A-Z]) após o número (para casos como "2.5Todas")
        clause_pattern = r"\n(?=\d+\.(?:\d+)?[\s[A-Z])"

        # Dividir pelo padrão mantendo o delimitador
        segments = re.split(clause_pattern, text)

        units = []
        for segment in segments:
            segment = segment.strip()
            if not segment or len(segment) < 10:
                continue

            # Cada segmento é uma unidade (cláusula individual)
            units.append(segment)

        return units

    def _escape_html(self, text):
        """Escapa caracteres HTML"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _unescape_html(self, text: str) -> str:
        """Reverte escape de HTML"""
        return (
            text.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
        )

    def _is_field_replacement(self, original, _modified):
        """Detecta se é preenchimento de campo (placeholder -> valor)"""
        # Detectar padrões de placeholder

        placeholder_patterns = [
            r"_+",  # Underscores
            r"\[.*?\]",  # Colchetes
            r"\{.*?\}",  # Chaves
            r"____+",  # Múltiplos underscores
        ]

        return any(re.search(pattern, original) for pattern in placeholder_patterns)

    def _extract_field_info(self, original, modified):
        """Extrai informações sobre o campo sendo preenchido"""

        # Tentar identificar o tipo de campo
        field_type = "Campo"

        if "R.G." in original or "RG" in original:
            field_type = "RG"
        elif "CPF" in original:
            field_type = "CPF"
        elif "residente" in original or "domiciliado" in original:
            field_type = "Endereço"
        elif "LOCADOR" in original or "LOCATÁRIO" in original:
            field_type = "Identificação da Parte"

        return {"field_name": field_type, "original": original, "modified": modified}

    def _identify_clause(self, line):
        """Identifica a cláusula baseada na linha de texto"""

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

    def _calcular_blocos_avancado(self, versao_id, diff_html):
        """
        Calcula blocos usando agrupamento posicional se disponível,
        senão usa contagem de clause-headers do HTML
        Retorna tanto o total quanto os detalhes dos blocos
        """
        try:
            if AgrupadorPosicional:
                print("🔍 Usando agrupamento posicional para cálculo de blocos")
                agrupador = AgrupadorPosicional()
                resultado = agrupador.processar_agrupamento_posicional_versao(versao_id)

                if "erro" not in resultado:
                    total_blocos = resultado.get("total_blocos", 1)
                    blocos_detalhados = resultado.get("blocos", [])
                    print(
                        f"✅ Agrupamento posicional: {total_blocos} blocos identificados"
                    )
                    return {
                        "total_blocos": max(total_blocos, 1),
                        "blocos_detalhados": blocos_detalhados,
                        "metodo": "agrupamento_posicional",
                    }
                else:
                    print(f"⚠️ Erro no agrupamento posicional: {resultado['erro']}")

            # Fallback: contar clause-headers no HTML
            print("🔍 Usando contagem de clause-headers como fallback")
            import re

            clause_matches = re.findall(r"<div class='clause-header'>", diff_html)
            total_blocos = len(clause_matches)
            print(f"✅ Fallback: {total_blocos} clause-headers encontrados")

            return {
                "total_blocos": max(total_blocos, 1),
                "blocos_detalhados": [],
                "metodo": "clause_headers",
            }

        except Exception as e:
            print(f"❌ Erro no cálculo de blocos: {e}")
            return {"total_blocos": 1, "blocos_detalhados": [], "metodo": "fallback"}

    def _extrair_modificacoes_do_diff(
        self, diff_html, texto_original=None, texto_modificado=None
    ):
        """
        Extrai modificações do HTML diff com posições de caracteres.

        Args:
            diff_html: HTML gerado pelo diff
            texto_original: Texto original completo (para calcular posições)
            texto_modificado: Texto modificado completo (para calcular posições)

        Returns:
            Lista de modificações com posicao_inicio e posicao_fim
        """
        modificacoes = []
        modificacao_id = 1

        print("🔍 Iniciando extração de modificações do diff HTML")

        try:
            # Usar regex para encontrar elementos de diff
            import difflib
            import re

            # Encontrar cabeçalhos de cláusulas (mantido apenas para logs/debug)
            clause_pattern = r"<div class='clause-header'>📋 (.*?)</div>"
            clause_matches = list(re.finditer(clause_pattern, diff_html))
            print(f"📋 Cabeçalhos de cláusula no diff: {len(clause_matches)}")

            # Encontrar elementos removidos (usando aspas simples como no HTML real)
            removed_pattern = r"<div class='diff-removed'>-\s*(.*?)</div>"
            removed_matches = list(re.finditer(removed_pattern, diff_html, re.DOTALL))
            print(f"📝 Elementos removidos encontrados: {len(removed_matches)}")

            # Encontrar elementos adicionados
            added_pattern = r"<div class='diff-added'>\+\s*(.*?)</div>"
            added_matches = list(re.finditer(added_pattern, diff_html, re.DOTALL))
            print(f"📝 Elementos adicionados encontrados: {len(added_matches)}")

            # Criar SequenceMatcher para mapear posições
            matcher = None
            if texto_original and texto_modificado:
                matcher = difflib.SequenceMatcher(
                    None, texto_original, texto_modificado
                )
                print("✅ SequenceMatcher criado para calcular posições exatas")

            # Processar pares de remoção/adição
            max_elements = max(len(removed_matches), len(added_matches))

            for i in range(max_elements):
                removed_match = removed_matches[i] if i < len(removed_matches) else None
                added_match = added_matches[i] if i < len(added_matches) else None

                removed_text = removed_match.group(1).strip() if removed_match else None
                added_text = added_match.group(1).strip() if added_match else None

                # Calcular posições usando difflib
                posicao_inicio = 0
                posicao_fim = 0

                if matcher and removed_text and texto_original:
                    # Tentar encontrar o texto removido no original
                    pos = texto_original.find(removed_text)
                    if pos >= 0:
                        posicao_inicio = pos
                        posicao_fim = pos + len(removed_text)
                    else:
                        # Busca fuzzy com primeiros 50 chars
                        trecho_busca = (
                            removed_text[:50]
                            if len(removed_text) > 50
                            else removed_text
                        )
                        pos = texto_original.find(trecho_busca)
                        if pos >= 0:
                            posicao_inicio = pos
                            posicao_fim = pos + len(removed_text)

                elif matcher and added_text and texto_modificado:
                    # Para inserções, usar posição no texto modificado
                    pos = texto_modificado.find(added_text)
                    if pos >= 0:
                        # Mapear posição do modificado de volta para o original
                        # Encontrar bloco correspondente no original
                        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                            if tag == "insert" and j1 <= pos < j2:
                                posicao_inicio = i1
                                posicao_fim = i1
                                break
                            elif tag == "replace" and j1 <= pos < j2:
                                posicao_inicio = i1
                                posicao_fim = i2
                                break
                            elif tag == "equal" and j1 <= pos < j2:
                                offset = pos - j1
                                posicao_inicio = i1 + offset
                                posicao_fim = i1 + offset
                                break

                # Não popular campo 'clausula' aqui - isso será feito pela vinculação com tags
                # A vinculação correta acontece em _vincular_modificacoes_clausulas()

                if removed_text and added_text:
                    # Alteração
                    modificacoes.append(
                        {
                            "id": modificacao_id,
                            "tipo": "ALTERACAO",
                            "css_class": "diff-alteracao",
                            "confianca": 0.95,
                            "posicao": {"linha": i + 1, "coluna": 1},
                            "posicao_inicio": posicao_inicio,
                            "posicao_fim": posicao_fim,
                            "conteudo": {"original": removed_text, "novo": added_text},
                            "tags_relacionadas": self._extrair_palavras_chave(
                                removed_text + " " + added_text
                            ),
                        }
                    )
                elif added_text:
                    # Inserção
                    modificacoes.append(
                        {
                            "id": modificacao_id,
                            "tipo": "INSERCAO",
                            "css_class": "diff-insercao",
                            "confianca": 0.9,
                            "posicao": {"linha": i + 1, "coluna": 1},
                            "posicao_inicio": posicao_inicio,
                            "posicao_fim": posicao_fim,
                            "conteudo": {"novo": added_text},
                            "tags_relacionadas": self._extrair_palavras_chave(
                                added_text
                            ),
                        }
                    )
                elif removed_text:
                    # Remoção
                    modificacoes.append(
                        {
                            "id": modificacao_id,
                            "tipo": "REMOCAO",
                            "css_class": "diff-remocao",
                            "confianca": 0.85,
                            "posicao": {"linha": i + 1, "coluna": 1},
                            "posicao_inicio": posicao_inicio,
                            "posicao_fim": posicao_fim,
                            "conteudo": {"original": removed_text},
                            "tags_relacionadas": self._extrair_palavras_chave(
                                removed_text
                            ),
                        }
                    )

                modificacao_id += 1

            print(f"✅ {len(modificacoes)} modificações extraídas do diff")
            if modificacoes and modificacoes[0].get("posicao_inicio") is not None:
                print("📍 Posições de caracteres calculadas para vinculação")
            print("ℹ️  Vinculação com cláusulas será feita através das tags do modelo")
            print("ℹ️  Vinculação com cláusulas será feita através das tags do modelo")
            return modificacoes

        except Exception as e:
            print(f"❌ Erro ao extrair modificações: {e}")
            return []

    def _extrair_palavras_chave(self, texto):
        """Extrai palavras-chave de um texto para tags relacionadas"""
        if not texto:
            return []

        # Palavras comuns a ignorar
        stop_words = {
            "de",
            "da",
            "do",
            "das",
            "dos",
            "a",
            "o",
            "as",
            "os",
            "e",
            "ou",
            "para",
            "com",
            "por",
            "em",
            "na",
            "no",
            "nas",
            "nos",
            "se",
            "que",
            "mais",
            "será",
            "são",
            "foi",
            "foram",
            "tem",
            "ter",
            "uma",
            "um",
            "umas",
            "uns",
        }

        # Extrair palavras significativas (mais de 3 caracteres, não números)

        palavras = re.findall(r"\b[a-záêçõã]{4,}\b", texto.lower())
        palavras_filtradas = [p for p in palavras if p not in stop_words]

        # Retornar até 5 palavras mais relevantes
        return list(set(palavras_filtradas))[:5]

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
@app.route("/", methods=["GET"])
def index():
    """Página principal - serve a interface Vue.js"""
    try:
        # Caminho para o arquivo dist/index.html
        dist_path = os.path.join(os.path.dirname(__file__), "web", "dist", "index.html")
        if os.path.exists(dist_path):
            with open(dist_path, encoding="utf-8") as f:
                return f.read()
        else:
            return jsonify(
                {
                    "message": "Interface web não encontrada",
                    "api_endpoints": {
                        "health": "/health",
                        "versoes": "/api/versoes",
                        "documents": "/api/documents",
                    },
                }
            )
    except Exception as e:
        return jsonify({"error": f"Erro ao carregar interface: {str(e)}"}), 500


@app.route("/assets/<path:filename>", methods=["GET"])
def serve_assets(filename):
    """Serve arquivos estáticos CSS/JS da interface Vue.js"""
    try:
        assets_path = os.path.join(os.path.dirname(__file__), "web", "dist", "assets")
        return send_from_directory(assets_path, filename)
    except Exception as e:
        return jsonify({"error": f"Asset não encontrado: {str(e)}"}), 404


@app.route("/health", methods=["GET"])
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


@app.route("/view/<versao_id>", methods=["GET"])
def view_version(versao_id):
    """
    Serve a interface Vue.js do visualizador de diff.
    O frontend fará chamadas para /api/versao/<versao_id> para obter os dados do Directus.
    """
    try:
        dist_path = os.path.join(os.path.dirname(__file__), "web", "dist", "index.html")
        if os.path.exists(dist_path):
            with open(dist_path, encoding="utf-8") as f:
                html = f.read()
                # Adicionar script para carregar dados da versão automaticamente
                script = f"""
                <script>
                    window.VERSAO_ID = '{versao_id}';
                    window.LOAD_FROM_API = true;
                </script>
                """
                # Inserir o script antes do </head>
                html = html.replace("</head>", f"{script}</head>")
                return html
        else:
            return jsonify(
                {
                    "error": "Frontend não encontrado. Execute o build do Vue.js primeiro."
                }
            ), 404
    except Exception as e:
        print(f"❌ Erro ao servir interface: {e}")
        return jsonify({"error": str(e)}), 500


def _get_versao_json(versao_id):
    """Função auxiliar para buscar dados da versão do Directus e retornar JSON"""
    # Verificar se é um diff_id do cache antigo (para retrocompatibilidade)
    if versao_id in diff_cache:
        diff_data = diff_cache[versao_id]
        return jsonify(diff_data)

    # Caso contrário, buscar do Directus
    try:
        # Buscar versão COM TODOS os relacionamentos em UMA requisição
        params = {
            "fields": "*,modificacoes.*,modificacoes.clausula.*,contrato.*,contrato.modelo_contrato.*"
        }

        response = requests.get(
            f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}",
            headers=DIRECTUS_HEADERS,
            params=params,
            timeout=30,
        )

        print(f"🔍 Buscando versão {versao_id} com relacionamentos...")
        print(f"📡 Status: {response.status_code}")

        if response.status_code != 200:
            return jsonify({"error": "Versão não encontrada"}), 404

        versao_completa = response.json().get("data")

        if not versao_completa:
            return jsonify({"error": "Versão não encontrada"}), 404

        # Verificar status do processamento
        if versao_completa.get("status") != "concluido":
            return jsonify(
                {
                    "error": "Versão ainda não processada",
                    "status": versao_completa.get("status"),
                    "progresso": versao_completa.get("progresso"),
                }
            ), 202

        # Validar que contrato e modelo estão presentes (obrigatórios)
        if not versao_completa.get("contrato"):
            print(f"❌ Versão {versao_id} sem contrato vinculado")
            return jsonify({"error": "Dados inconsistentes: versão sem contrato"}), 500

        if not versao_completa["contrato"].get("modelo_contrato"):
            print(f"❌ Contrato da versão {versao_id} sem modelo vinculado")
            return jsonify({"error": "Dados inconsistentes: contrato sem modelo"}), 500

        # Modificações já vêm no objeto versao_completa["modificacoes"]
        modificacoes = versao_completa.get("modificacoes", [])

        # Formatar dados para visualização
        dados_view = _formatar_para_view(versao_completa, modificacoes)

        # Sempre retornar JSON (este é um endpoint de API)
        return jsonify(dados_view)

    except requests.RequestException as e:
        print(f"❌ Erro de rede ao carregar versão {versao_id}: {e}")
        return jsonify({"error": f"Erro ao conectar com Directus: {str(e)}"}), 500
    except Exception as e:
        print(f"❌ Erro ao carregar view para versão {versao_id}: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/versao/<versao_id>", methods=["GET"])
@app.route("/versao/<versao_id>", methods=["GET"])
def api_get_versao(versao_id):
    """
    API endpoint para buscar dados de uma versão específica do Directus.
    Usado pelo frontend Vue.js para carregar os dados.

    Disponível em:
    - /api/versao/<versao_id> (recomendado para API)
    - /versao/<versao_id> (compatibilidade)
    """
    return _get_versao_json(versao_id)


def _extrair_chave_ordenacao_clausula(numero: str | None) -> tuple:
    """
    Extrai chave de ordenação para números de cláusula (ex: "1.1.1.e", "2.3.a").
    Converte partes numéricas em int e mantém letras como strings.

    Exemplos:
        "1.1.1" -> (1, 1, 1)
        "1.1.1.e" -> (1, 1, 1, 'e')
        "2.3.a" -> (2, 3, 'a')
    """
    if not numero:
        return (float("inf"),)  # Cláusulas sem número vão para o final

    partes = []
    for parte in str(numero).split("."):
        try:
            # Tentar converter para inteiro
            partes.append(int(parte))
        except ValueError:
            # Se não for número, manter como string (letra)
            partes.append(parte.lower())

    return tuple(partes)


def _formatar_para_view(versao_completa: dict, modificacoes: list[dict]) -> dict:
    """
    Formata dados do Directus para o formato esperado pelo frontend.

    Args:
        versao_completa: Objeto versão com todos os relacionamentos carregados
        modificacoes: Lista de modificações (já vem em versao_completa["modificacao"])

    Returns:
        Dicionário formatado para o frontend
    """
    # Ordenar modificações pelo número da cláusula associada (ordenação natural)
    # Modificações sem cláusula vão para o final
    modificacoes_ordenadas = sorted(
        modificacoes,
        key=lambda m: (
            _extrair_chave_ordenacao_clausula(
                m.get("clausula", {}).get("numero") if m.get("clausula") else None
            ),
            m.get("posicao_inicio", 0),  # Segunda ordenação: posição no documento
        ),
    )

    modificacoes_formatadas = []

    for mod in modificacoes_ordenadas:
        mod_formatada = {
            "id": mod["id"],
            "tipo": _categoria_para_tipo(mod.get("categoria", "modificacao")),
            "conteudo": {
                "original": mod.get("conteudo", ""),
                "novo": mod.get("alteracao", ""),
            },
            "posicao": {
                "inicio": mod.get("posicao_inicio", 0),
                "fim": mod.get("posicao_fim", 0),
            },
            "caminho": {
                "inicio": mod.get("caminho_inicio"),
                "fim": mod.get("caminho_fim"),
            },
        }

        # Adicionar cláusula se vinculada (já vem em mod["clausula"])
        if mod.get("clausula"):
            clausula = mod["clausula"]
            mod_formatada["clausula"] = {
                "id": clausula.get("id"),
                "numero": clausula.get("numero"),
                "nome": clausula.get("nome"),
            }

            # Dados de vinculação (OPCIONAIS - serão adicionados na task-005)
            # Estes campos ainda não estão na coleção modificacao do Directus
            if (
                mod.get("metodo_vinculacao")
                or mod.get("score_vinculacao")
                or mod.get("status_vinculacao")
            ):
                mod_formatada["vinculacao"] = {
                    "metodo": mod.get("metodo_vinculacao", "conteudo"),
                    "score": mod.get("score_vinculacao"),
                    "status": mod.get("status_vinculacao", "automatico"),
                }

        modificacoes_formatadas.append(mod_formatada)

    # Dados do contrato e modelo (OBRIGATÓRIOS - sempre devem estar presentes)
    contrato = versao_completa["contrato"]  # Não usa .get() - deve existir
    modelo = contrato["modelo_contrato"]  # Não usa .get() - deve existir

    return {
        "versao_id": versao_completa["id"],
        "status": versao_completa["status"],
        "data_processamento": versao_completa.get("data_hora_processamento"),
        "contrato": {
            "id": contrato["id"],
            "nome": contrato.get("nome"),
            "numero": contrato.get("numero"),
        },
        "modelo": {
            "id": modelo["id"],
            "nome": modelo.get("nome"),
            "versao": modelo.get("versao"),
        },
        "modificacoes": modificacoes_formatadas,
        "metricas": _calcular_metricas(modificacoes),
    }


def _categoria_para_tipo(categoria: str) -> str:
    """Mapeia categoria do Directus para tipo do frontend."""
    mapa = {
        "modificacao": "ALTERACAO",
        "inclusao": "INSERCAO",
        "remocao": "REMOCAO",
        "comentario": "COMENTARIO",
        "formatacao": "FORMATACAO",
    }
    return mapa.get(categoria, "ALTERACAO")


def _calcular_metricas(modificacoes: list[dict]) -> dict:
    """Calcula métricas agregadas das modificações."""
    total = len(modificacoes)
    vinculadas = sum(1 for m in modificacoes if m.get("clausula"))

    return {
        "total_modificacoes": total,
        "vinculadas": vinculadas,
        "nao_vinculadas": total - vinculadas,
        "taxa_vinculacao": round((vinculadas / total * 100), 2) if total > 0 else 0,
    }


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
        "mock": true/false (opcional, default: false),
        "use_ast": true/false (opcional, default: TRUE - AST 59.3% vs Texto 51.9%)
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado JSON fornecido"}), 400

    versao_id = data.get("versao_id") or data.get("doc_id")
    mock = data.get("mock", False)  # Default: usar dados reais
    use_ast = data.get("use_ast", True)  # Default: USAR AST (melhor precisão)

    if not versao_id:
        return jsonify({"error": "versao_id é obrigatório"}), 400

    metodo = "AST (59.3%)" if use_ast else "Texto (51.9%)"
    print(
        f"🔍 Processando versão {versao_id} (modo: {'mock' if mock else 'real'}, método: {metodo})"
    )
    result = directus_api.process_versao(versao_id, mock=mock, use_ast=use_ast)

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


@app.route("/api/process-modelo", methods=["POST"])
def process_modelo():
    """Processa um modelo de contrato e extrai suas tags

    Body JSON esperado:
    {
        "modelo_id": "id_do_modelo",
        "dry_run": true/false (opcional, default: false),
        "use_ast": true/false (opcional, default: true),
        "process_versions": true/false (opcional, default: true)
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado JSON fornecido"}), 400

    modelo_id = data.get("modelo_id")
    dry_run = data.get("dry_run", False)
    use_ast = data.get("use_ast", True)  # AST como padrão
    process_tags = data.get("process_tags", True)  # Processar tags por padrão
    process_versions = data.get(
        "process_versions", True
    )  # Processar versões por padrão

    if not modelo_id:
        return jsonify({"error": "modelo_id é obrigatório"}), 400

    # Validar configuração do Directus
    if not DIRECTUS_BASE_URL or not DIRECTUS_TOKEN:
        print(
            f"❌ Configuração inválida: DIRECTUS_BASE_URL={DIRECTUS_BASE_URL}, DIRECTUS_TOKEN={'SET' if DIRECTUS_TOKEN else 'NOT SET'}"
        )
        return jsonify(
            {
                "error": "Configuração do Directus não encontrada (DIRECTUS_BASE_URL ou DIRECTUS_TOKEN)"
            }
        ), 500

    print(f"🔍 Processando modelo {modelo_id}")
    print(
        f"   ⚙️  Configurações: dry_run={dry_run}, use_ast={use_ast}, process_tags={process_tags}, process_versions={process_versions}"
    )

    try:
        resultado_final = {
            "modelo_id": modelo_id,
            "dry_run": dry_run,
            "use_ast": use_ast,
            "process_tags": process_tags,
            "status": "sucesso",
        }

        # 1. Processar tags do modelo (opcional)
        if process_tags:
            print("\n📋 ETAPA 1: Processando tags do modelo...")
            print(f"   🔑 Directus URL: {DIRECTUS_BASE_URL}")
            print(
                f"   🔑 Directus Token: {'SET (' + DIRECTUS_TOKEN[:20] + '...)' if DIRECTUS_TOKEN else 'NOT SET'}"
            )

            processador = ProcessadorTagsModelo(
                directus_base_url=DIRECTUS_BASE_URL, directus_token=DIRECTUS_TOKEN
            )
            resultado_tags = processador.processar_modelo(modelo_id, dry_run=dry_run)

            if resultado_tags.get("status") == "erro":
                print(f"   ⚠️  Erro ao processar tags: {resultado_tags.get('erro')}")
                print("   📋 Continuando sem processamento de tags...")
                # Não falhar aqui, apenas logar
                resultado_final.update(
                    {"tags_encontradas": 0, "tags_criadas": 0, "tags_orfas": 0}
                )
            else:
                # Adicionar resultados das tags
                resultado_final.update(
                    {
                        "tags_encontradas": resultado_tags.get("tags_encontradas", 0),
                        "tags_criadas": resultado_tags.get("tags_criadas", 0),
                        "tags_orfas": resultado_tags.get("tags_orfas", 0),
                    }
                )
        else:
            print("\n⏭️  Pulando processamento de tags (process_tags=false)")
            resultado_final.update(
                {"tags_encontradas": 0, "tags_criadas": 0, "tags_orfas": 0}
            )

        # 2. Processar versões (se solicitado)
        if process_versions:
            print("\n📋 ETAPA 2: Processando versões do modelo...")

            # Buscar versões do modelo
            versoes = _buscar_versoes_do_modelo(modelo_id)
            print(f"   ✅ Encontradas {len(versoes)} versões")

            if versoes:
                versoes_processadas = 0
                versoes_com_erro = 0
                total_modificacoes = 0

                # Criar instância da API (usa variáveis globais DIRECTUS_BASE_URL e DIRECTUS_TOKEN)
                api = DirectusAPI()

                # Processar cada versão
                for versao in versoes:
                    versao_id = versao.get("id")
                    versao_numero = versao.get("versao", "N/A")

                    try:
                        print(
                            f"\n   🔄 Processando versão {versao_numero} ({versao_id})..."
                        )

                        if use_ast:
                            print("      🔬 Usando implementação AST")
                        else:
                            print("      📝 Usando implementação original")

                        # Processar versão com ou sem AST
                        resultado_versao = api.process_versao(
                            versao_id, mock=False, use_ast=use_ast
                        )

                        # AST retorna success=True, modo original retorna status="sucesso"
                        sucesso = (
                            resultado_versao
                            and (
                                resultado_versao.get("success") is True
                                or resultado_versao.get("status") == "sucesso"
                            )
                            and "error" not in resultado_versao
                        )

                        if sucesso:
                            versoes_processadas += 1
                            modificacoes_versao = len(
                                resultado_versao.get("modificacoes", [])
                            )
                            total_modificacoes += modificacoes_versao
                            print(
                                f"      ✅ Versão processada: {modificacoes_versao} modificações"
                            )
                        else:
                            versoes_com_erro += 1
                            erro_msg = resultado_versao.get(
                                "error", "status diferente de sucesso"
                            )
                            print(f"      ⚠️  Versão com erro: {erro_msg}")

                    except Exception as e:
                        versoes_com_erro += 1
                        print(f"      ❌ Erro ao processar versão {versao_numero}: {e}")

                # Adicionar resultados do processamento de versões
                resultado_final.update(
                    {
                        "versoes_encontradas": len(versoes),
                        "versoes_processadas": versoes_processadas,
                        "versoes_com_erro": versoes_com_erro,
                        "total_modificacoes": total_modificacoes,
                    }
                )
            else:
                print("   ⚠️  Nenhuma versão encontrada para processar")
                resultado_final.update(
                    {
                        "versoes_encontradas": 0,
                        "versoes_processadas": 0,
                        "versoes_com_erro": 0,
                        "total_modificacoes": 0,
                    }
                )
        else:
            print("\n⏭️  ETAPA 2: Pulada (process_versions=False)")

        # 3. Resultados finais
        print("\n" + "=" * 80)
        print("✅ PROCESSAMENTO CONCLUÍDO")
        print("=" * 80)
        print("📊 Resumo:")
        print(f"   • Tags encontradas: {resultado_final.get('tags_encontradas', 0)}")
        print(f"   • Tags criadas: {resultado_final.get('tags_criadas', 0)}")
        if process_versions:
            print(
                f"   • Versões processadas: {resultado_final.get('versoes_processadas', 0)}/{resultado_final.get('versoes_encontradas', 0)}"
            )
            print(
                f"   • Total de modificações: {resultado_final.get('total_modificacoes', 0)}"
            )
            print(
                f"   • Método: {'AST (Pandoc)' if use_ast else 'Original (SequenceMatcher)'}"
            )
        print("=" * 80)

        return jsonify(resultado_final), 200

    except Exception as e:
        print(f"❌ Erro ao processar modelo: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e), "modelo_id": modelo_id, "status": "erro"}), 500


def _buscar_versoes_do_modelo(modelo_id: str) -> list[dict]:
    """Busca todas as versões de um modelo no Directus

    Estrutura: modelo_contrato → contrato → versao
    Busca: versao.contrato.modelo_contrato = modelo_id
    """
    try:
        url = f"{DIRECTUS_BASE_URL}/items/versao"
        params = {
            "filter[contrato][modelo_contrato][_eq]": modelo_id,  # Deep filter: versao → contrato → modelo_contrato
            "fields": "id,versao,status,date_created,contrato.id,contrato.numero",
            "sort": "versao",
            "limit": -1,  # Sem limite
        }
        headers = {
            "Authorization": f"Bearer {DIRECTUS_TOKEN}",
            "Content-Type": "application/json",
        }

        print(f"🔍 Buscando versões do modelo {modelo_id}")
        print(f"   Filtro: contrato.modelo_contrato = {modelo_id}")

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            versoes = data.get("data", [])
            print(f"✅ Encontradas {len(versoes)} versões")

            # Log das versões encontradas
            for v in versoes:
                contrato_info = v.get("contrato", {})
                contrato_numero = (
                    contrato_info.get("numero", "N/A")
                    if isinstance(contrato_info, dict)
                    else "N/A"
                )
                print(
                    f"   • Versão {v.get('versao', 'N/A')} (Contrato: {contrato_numero})"
                )

            return versoes
        else:
            print(f"⚠️  Erro ao buscar versões: HTTP {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return []

    except Exception as e:
        print(f"❌ Erro ao buscar versões do modelo: {e}")
        import traceback

        traceback.print_exc()
        return []


@app.route("/api/data/<diff_id>", methods=["GET"])
def get_diff_data(diff_id):
    """
    Retorna dados JSON do diff.
    Busca primeiro no cache, se não encontrar busca do Directus.
    """
    print(f"🔍 Buscando diff_id: {diff_id}")
    print(f"📊 Cache atual tem {len(diff_cache)} items: {list(diff_cache.keys())}")

    # Verificar cache primeiro
    if diff_id in diff_cache:
        print("✅ Encontrado no cache!")
        return jsonify(diff_cache[diff_id])

    # Se não estiver no cache, buscar do Directus usando o endpoint /api/versao
    print("⚠️ Não encontrado no cache, buscando do Directus...")
    return api_get_versao(diff_id)


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
