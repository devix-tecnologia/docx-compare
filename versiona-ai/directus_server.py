"""
Servidor API para integração real com Directus
Conecta com https://contract.devix.co usando as credenciais do .env
Inclui agrupamento posicional para cálculo preciso de blocos
Implementa algoritmo unificado de vinculação de modificações às cláusulas
"""

import difflib
import os
import re
import signal
import sys
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    render_template_string,
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

    vinculadas: list[tuple[dict, str, float]] = field(
        default_factory=list
    )  # (modificacao, clausula_id, score)
    nao_vinculadas: list[dict] = field(
        default_factory=list
    )  # modificacoes sem candidatos
    revisao_manual: list[tuple[dict, list[dict], float]] = field(
        default_factory=list
    )  # (mod, candidatos, score)

    def taxa_sucesso(self) -> float:
        """Retorna a taxa de vinculação automática."""
        total = (
            len(self.vinculadas) + len(self.nao_vinculadas) + len(self.revisao_manual)
        )
        return len(self.vinculadas) / total if total > 0 else 0.0

    def taxa_cobertura(self) -> float:
        """Retorna a taxa de cobertura (inclui revisão manual como potencial sucesso)."""
        total = (
            len(self.vinculadas) + len(self.nao_vinculadas) + len(self.revisao_manual)
        )
        cobertos = len(self.vinculadas) + len(self.revisao_manual)
        return cobertos / total if total > 0 else 0.0


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
    """
    if not texto1 or not texto2:
        return 0.0

    # Calcular e retornar similaridade diretamente
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
                                "limit": 100,
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

            # Extrair modificações do diff
            modificacoes = self._extrair_modificacoes_do_diff(diff_html)

            # Vincular modificações às cláusulas usando tags (somente em modo real)
            if not mock and tags_modelo:
                # Usar arquivo_com_tags_text se disponível
                if arquivo_com_tags_text:
                    texto_para_mapear_tags = arquivo_com_tags_text
                    # As modificações agora estão no sistema de coordenadas correto!
                    print("🔍 Mapeando tags com coordenadas alinhadas")
                else:
                    texto_para_mapear_tags = modified_text
                    print("⚠️ Sem arquivo_com_tags - posições podem não alinhar")

                modificacoes = self._vincular_modificacoes_clausulas(
                    modificacoes,
                    tags_modelo,
                    texto_para_mapear_tags,
                    original_text,
                    modified_text,
                )

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
            for mod in modificacoes:
                try:
                    modificacao_data = self._converter_modificacao_para_directus(
                        versao_id, mod
                    )
                    modificacoes_directus.append(modificacao_data)
                    print(f"✅ Modificação {mod['id']} convertida para Directus")
                except Exception as e:
                    print(f"❌ Erro ao converter modificação {mod['id']}: {e}")

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
                timeout=30,  # Timeout maior para transação
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
        conteudo_original = conteudo_obj.get("original", "")
        conteudo_novo = conteudo_obj.get("novo", "")

        # Extrair posição
        posicao = mod.get("posicao", {})
        linha = posicao.get("linha", 0)
        coluna = posicao.get("coluna", 0)

        # Construir caminho (usando linha e coluna como referência)
        caminho_inicio = f"L{linha}:C{coluna}"
        # Para o fim, assumir que vai até o final do conteúdo
        caminho_fim = f"L{linha}:C{coluna + len(conteudo_original)}"

        # Montar objeto para Directus
        directus_mod = {
            "versao": versao_id,
            "status": "draft",
            "categoria": categoria,
            "conteudo": conteudo_original if conteudo_original else None,
            "alteracao": conteudo_novo if conteudo_novo else None,
            "caminho_inicio": caminho_inicio,
            "caminho_fim": caminho_fim,
            "posicao_inicio": linha * 1000 + coluna,  # Posição linear aproximada
            "posicao_fim": linha * 1000 + coluna + len(conteudo_original),
        }

        # Adicionar cláusula se disponível (UUID obtido via vinculação com tags)
        if "clausula_id" in mod and mod["clausula_id"]:
            # Campo clausula é uma FK para tabela clausula (tipo uuid)
            directus_mod["clausula"] = mod["clausula_id"]
            print(
                f"📋 Cláusula vinculada para modificação {mod.get('id')}: {mod.get('clausula_numero')} - {mod.get('clausula_nome')}"
            )
        else:
            # Se não há clausula_id, não enviar o campo (deixar null no banco)
            print(
                f"⚠️  Modificação {mod.get('id')} sem cláusula vinculada (nenhuma tag correspondente encontrada)"
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

    def _inferir_posicoes_via_conteudo_com_contexto(
        self,
        tags: list[dict],
        arquivo_original_text: str,
        arquivo_com_tags_text: str,
        tamanho_contexto: int = 50,
    ) -> list[TagMapeada]:
        """
        Infere posições das tags no arquivo original usando busca por conteúdo + contexto.

        Este método é usado no "Caminho Real" quando os documentos são diferentes.
        Extrai o conteúdo de cada tag e busca no arquivo original usando contexto
        de vizinhança para desambiguar.

        Args:
            tags: Lista de tags do modelo com posições no arquivo COM tags
            arquivo_original_text: Texto do arquivo original (da versão)
            arquivo_com_tags_text: Texto completo do arquivo COM tags (do modelo)
            tamanho_contexto: Quantos caracteres antes/depois extrair como contexto

        Returns:
            Lista de TagMapeada com posições inferidas no arquivo original
        """
        print("🎯 Inferindo posições via conteúdo (Caminho Real)")

        tags_mapeadas = []

        for tag in tags:
            pos_inicio = tag.get("posicao_inicio_texto", 0)
            pos_fim = tag.get("posicao_fim_texto", 0)

            # Extrair conteúdo da tag (SEM normalizar - trabalhar com texto literal)
            conteudo_tag = arquivo_com_tags_text[pos_inicio:pos_fim]

            if not conteudo_tag:
                print(f"   ⚠️  Tag {tag.get('tag_nome')} sem conteúdo, pulando")
                continue

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
                            # Não encontrou!
                            print(
                                f"   ❌ Tag {tag.get('tag_nome')} não encontrada no arquivo original"
                            )
                            continue

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

            tags_mapeadas.append(tag_mapeada)

        print(f"   ✅ {len(tags_mapeadas)}/{len(tags)} tags inferidas com sucesso")
        return tags_mapeadas

    # ============================================================================
    # FIM FASE 3
    # ============================================================================

    def _vincular_modificacoes_clausulas(
        self,
        modificacoes,
        tags_modelo,
        texto_com_tags,
        texto_original=None,
        texto_modificado=None,
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

        # Dividir em parágrafos para melhor granularidade
        orig_paragraphs = self._split_into_semantic_units(original)
        mod_paragraphs = self._split_into_semantic_units(modified)

        print(f"📝 Original: {len(orig_paragraphs)} unidades semânticas")
        print(f"📝 Modificado: {len(mod_paragraphs)} unidades semânticas")

        html = ["<div class='diff-container'>"]
        current_clause = None

        # Usar SequenceMatcher para comparação mais inteligente
        matcher = difflib.SequenceMatcher(None, orig_paragraphs, mod_paragraphs)

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
                # Conteúdo substituído - criar pares de modificação
                orig_content = " ".join(orig_paragraphs[i1:i2]).strip()
                mod_content = " ".join(mod_paragraphs[j1:j2]).strip()

                if orig_content and mod_content:
                    # Verificar se é preenchimento de campos (placeholders)
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
        """Divide texto em unidades semânticas (frases, parágrafos)"""

        # Dividir por quebras de linha duplas (parágrafos)
        paragraphs = text.split("\n\n")
        units = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Se o parágrafo é muito longo, dividir por frases
            if len(para) > 200:
                sentences = re.split(r"[.!?]\s+", para)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and len(sentence) > 10:
                        units.append(sentence)
            else:
                units.append(para)

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

    def _is_field_replacement(self, original, modified):
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

    def _extrair_modificacoes_do_diff(self, diff_html):
        """Extrai modificações do HTML diff, similar ao algoritmo do frontend"""
        modificacoes = []
        modificacao_id = 1

        print("🔍 Iniciando extração de modificações do diff HTML")

        try:
            # Usar regex para encontrar elementos de diff
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

            # Processar pares de remoção/adição
            max_elements = max(len(removed_matches), len(added_matches))

            for i in range(max_elements):
                removed_match = removed_matches[i] if i < len(removed_matches) else None
                added_match = added_matches[i] if i < len(added_matches) else None

                removed_text = removed_match.group(1).strip() if removed_match else None
                added_text = added_match.group(1).strip() if added_match else None

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
                            "conteudo": {"original": removed_text},
                            "tags_relacionadas": self._extrair_palavras_chave(
                                removed_text
                            ),
                        }
                    )

                modificacao_id += 1

            print(f"✅ {len(modificacoes)} modificações extraídas do diff")
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


@app.route("/api/process-modelo", methods=["POST"])
def process_modelo():
    """Processa um modelo de contrato e extrai suas tags

    Body JSON esperado:
    {
        "modelo_id": "id_do_modelo",
        "dry_run": true/false (opcional, default: false)
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado JSON fornecido"}), 400

    modelo_id = data.get("modelo_id")
    dry_run = data.get("dry_run", False)

    if not modelo_id:
        return jsonify({"error": "modelo_id é obrigatório"}), 400

    print(f"🔍 Processando modelo {modelo_id} (dry_run: {dry_run})")

    try:
        # Criar processador
        processador = ProcessadorTagsModelo(
            directus_base_url=DIRECTUS_BASE_URL, directus_token=DIRECTUS_TOKEN or ""
        )

        # Processar modelo
        resultado = processador.processar_modelo(modelo_id, dry_run=dry_run)

        if resultado.get("status") == "erro":
            return jsonify(resultado), 500

        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ Erro ao processar modelo: {e}")
        return jsonify({"error": str(e), "modelo_id": modelo_id}), 500


@app.route("/view/<diff_id>", methods=["GET"])
def view_diff(diff_id):
    """Visualiza diff gerado (somente leitura - não processa)

    Este endpoint NÃO processa versões, apenas exibe diffs já processados no cache.

    Fluxo correto:
    1. Processar versão: GET /api/versoes/<versao_id>
    2. Receber diff_id na resposta JSON
    3. Visualizar: GET /view/<diff_id>
    """
    if diff_id not in diff_cache:
        return (
            f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Diff não encontrado</title></head>
        <body>
            <h1>❌ Diff não encontrado no cache</h1>
            <p>O diff_id <code>{diff_id}</code> não existe no cache do servidor.</p>

            <h2>📝 Como processar e visualizar:</h2>
            <ol>
                <li><strong>Listar versões:</strong> <code>GET /api/versoes</code></li>
                <li><strong>Processar versão:</strong> <code>GET /api/versoes/&lt;versao_id&gt;</code></li>
                <li><strong>Usar o diff_id retornado para visualizar aqui</strong></li>
            </ol>

            <h3>🔗 Links úteis:</h3>
            <ul>
                <li><a href="/api/debug/cache">Ver diffs disponíveis no cache</a></li>
                <li><a href="/api/versoes">Ver versões disponíveis</a></li>
            </ul>
        </body>
        </html>
        """,
            404,
        )

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
