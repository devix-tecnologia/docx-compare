#!/usr/bin/env python3
"""
Processador automático de versões
Verifica a cada minuto se há versões com status 'processar' e as processa automaticamente
"""

import argparse
import difflib
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurações
DIRECTUS_BASE_URL = (
    os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
    .replace("/admin/", "")
    .rstrip("/")
)
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "your-directus-token")
DIRECTUS_EMAIL = os.getenv("DIRECTUS_EMAIL", "")
DIRECTUS_PASSWORD = os.getenv("DIRECTUS_PASSWORD", "")
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")

# Cliente HTTP para Directus
print("🔧 Inicializando cliente HTTP para Directus:")
print(f"   URL: {DIRECTUS_BASE_URL}")
print(f"   Token: {DIRECTUS_TOKEN[:10]}...")

# Headers para requisições HTTP
DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}

print("✅ Cliente HTTP inicializado")

# Configurações do Flask
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5005

# Variável global para controlar o processador
processador_ativo = True
processador_thread = None


def signal_handler(signum, frame):
    """
    Manipula sinais para encerramento gracioso da aplicação
    """
    global processador_ativo, processador_thread

    signal_names = {
        signal.SIGINT: "SIGINT (Ctrl+C)",
        signal.SIGTERM: "SIGTERM",
        signal.SIGHUP: "SIGHUP",
    }

    signal_name = signal_names.get(signum, f"Sinal {signum}")
    print(f"\n🛑 Recebido {signal_name} - Iniciando encerramento gracioso...")

    # Parar o processador
    processador_ativo = False

    # Aguardar a thread do processador terminar
    if processador_thread and processador_thread.is_alive():
        print("⏳ Aguardando thread do processador terminar...")
        processador_thread.join(timeout=10)
        if processador_thread.is_alive():
            print("⚠️ Thread do processador não terminou no tempo esperado")
        else:
            print("✅ Thread do processador terminada")

    print("✅ Aplicação encerrada graciosamente!")
    sys.exit(0)


# Criar diretório de resultados
os.makedirs(RESULTS_DIR, exist_ok=True)


def buscar_versoes_para_processar():
    """
    Busca versões com status 'processar' no Directus usando requisições HTTP diretas
    """
    try:
        print(
            f"🔍 {datetime.now().strftime('%H:%M:%S')} - Buscando versões para processar..."
        )

        # Primeiro, vamos testar uma query simples sem filtros
        print("🧪 Testando conectividade com query simples...")

        url_simple = f"{DIRECTUS_BASE_URL}/items/versao?limit=5"
        print(f"� URL simples: {url_simple}")
        print(f"� Headers: {DIRECTUS_HEADERS}")
        print("   ----")

        simple_response = requests.get(url_simple, headers=DIRECTUS_HEADERS)

        print("🔍 Resultado RAW da query simples:")
        print(f"   Status: {simple_response.status_code}")
        print(f"   Response: {simple_response.text}")
        print("   ----")

        # Se a query simples funcionar, tentamos com filtro
        if simple_response.status_code == 200:
            print("✅ Conectividade OK, tentando query com filtro...")

            # Query com filtros usando query parameters - campos corretos
            url_filtered = f"{DIRECTUS_BASE_URL}/items/versao"
            params = {
                "filter[status][_eq]": "processar",
                "limit": 10,
                "sort": "date_created",
                "fields": "id,date_created,status,versao,observacao,contrato,versiona_ai_request_json",
            }

            print(f"🔍 URL com filtro: {url_filtered}")
            print(f"🔍 Params: {params}")
            print("   ----")

            versoes_response = requests.get(
                url_filtered, headers=DIRECTUS_HEADERS, params=params
            )

            print("🔍 Resultado RAW da query com filtro:")
            print(f"   Status: {versoes_response.status_code}")
            print(f"   Response: {versoes_response.text}")
            print("   ----")

            if versoes_response.status_code == 200:
                try:
                    response_json = versoes_response.json()
                    versoes = response_json.get("data", [])
                except:
                    versoes = []
            else:
                versoes = []
        else:
            print("❌ Problema de conectividade detectado")
            versoes = []

        print(f"✅ Encontradas {len(versoes)} versões para processar")
        return versoes

    except Exception as e:
        print(f"❌ Erro ao buscar versões: {e}")
        return []


def determine_original_file_id(versao_data):
    """
    Determina qual arquivo usar como original baseado no campo versiona_ai_request_json:
    1. Se is_first_version=true: usa arquivoTemplate (modelo_template)
    2. Se is_first_version=false: usa arquivoBranco (versao_anterior)
    """
    try:
        versao_id = versao_data["id"]
        versao_request = versao_data.get("versiona_ai_request_json", {})

        print(f"🧠 Determinando arquivo original para versão {versao_id}...")
        print(f"🔗 Dados do contrato: {versao_data.get('contrato')}")

        # Verificar se temos os dados de request
        if not versao_request:
            raise Exception("Campo versiona_ai_request_json não encontrado")

        is_first_version = versao_request.get("is_first_version", False)
        versao_comparacao_tipo = versao_request.get("versao_comparacao_tipo", "")

        if is_first_version or versao_comparacao_tipo == "modelo_template":
            # Primeira versão: comparar com template
            arquivo_original = versao_request.get("arquivoTemplate")
            if arquivo_original:
                print(f"� Primeira versão - usando arquivoTemplate: {arquivo_original}")
                return arquivo_original, "modelo_template"
        else:
            # Versão posterior: comparar com versão anterior (arquivoBranco)
            arquivo_original = versao_request.get("arquivoBranco")
            if arquivo_original:
                print(f"📄 Versão posterior - usando arquivoBranco: {arquivo_original}")
                return arquivo_original, "versao_anterior"

        raise Exception(
            "Não foi possível encontrar arquivo original nos dados da versão"
        )

    except Exception as e:
        raise Exception(f"Erro ao determinar arquivo original: {e}")


def download_file_from_directus(file_path):
    """
    Baixa um arquivo do Directus usando o caminho do arquivo
    """
    try:
        print(f"📥 Baixando arquivo {file_path}...")

        # Construir URL completa para download
        if file_path.startswith("/directus/uploads/"):
            file_id = file_path.replace("/directus/uploads/", "")
        else:
            file_id = file_path

        download_url = f"{DIRECTUS_BASE_URL}/assets/{file_id}"

        # Fazer o download do arquivo
        response = requests.get(download_url, headers=DIRECTUS_HEADERS)

        if response.status_code == 200:
            # Criar arquivo temporário com extensão correta
            import tempfile

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
            temp_file.write(response.content)
            temp_file.close()

            print(f"✅ Arquivo baixado: {temp_file.name}")
            return temp_file.name
        else:
            raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

    except Exception as e:
        raise Exception(f"Erro ao baixar arquivo {file_path}: {e}")


def html_to_text(html_content):
    """Converte HTML para texto limpo"""
    html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
    html_content = re.sub(
        r"<strong[^>]*>(.*?)</strong>", r"\1", html_content, flags=re.DOTALL
    )
    html_content = re.sub(r"<b[^>]*>(.*?)</b>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(r"<em[^>]*>(.*?)</em>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(r"<i[^>]*>(.*?)</i>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(r"<u[^>]*>(.*?)</u>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(
        r"<mark[^>]*>(.*?)</mark>", r"\1", html_content, flags=re.DOTALL
    )
    html_content = re.sub(
        r"<li[^>]*><p[^>]*>(.*?)</p></li>", r"• \1", html_content, flags=re.DOTALL
    )
    html_content = re.sub(
        r"<li[^>]*>(.*?)</li>", r"• \1", html_content, flags=re.DOTALL
    )
    html_content = re.sub(r"<ol[^>]*>|</ol>", "", html_content)
    html_content = re.sub(r"<ul[^>]*>|</ul>", "", html_content)
    html_content = re.sub(r"<blockquote[^>]*>|</blockquote>", "", html_content)
    html_content = re.sub(r"<p[^>]*>|</p>", "\n", html_content)
    html_content = re.sub(r"<br[^>]*/?>", "\n", html_content)
    html_content = re.sub(r"<[^>]+>", "", html_content)
    html_content = re.sub(r"&nbsp;", " ", html_content)
    html_content = re.sub(r"&amp;", "&", html_content)
    html_content = re.sub(r"&lt;", "<", html_content)
    html_content = re.sub(r"&gt;", ">", html_content)
    html_content = re.sub(r"&quot;", '"', html_content)
    html_content = re.sub(r"\n\s*\n", "\n", html_content)
    return html_content.strip()


def analyze_differences_detailed(original_text, modified_text):
    """Analisa as diferenças e retorna modificações detalhadas"""
    original_lines = original_text.split("\n")
    modified_lines = modified_text.split("\n")

    diff = list(
        difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile="Original",
            tofile="Modificado",
            lineterm="",
        )
    )

    modifications = []
    modification_count = 1

    i = 0
    while i < len(diff):
        line = diff[i]

        if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            i += 1
            continue
        elif line.startswith("-"):
            # Linha removida
            original_content = line[1:].strip()
            if original_content:  # Ignorar linhas vazias
                # Verificar se a próxima linha é uma adição (modificação)
                if i + 1 < len(diff) and diff[i + 1].startswith("+"):
                    modified_content = diff[i + 1][1:].strip()
                    modifications.append(
                        {
                            "categoria": "modificacao",
                            "conteudo": original_content,
                            "alteracao": modified_content,
                            "sort": modification_count,
                        }
                    )
                    i += 2  # Pular a próxima linha pois já processamos
                else:
                    # Apenas remoção
                    modifications.append(
                        {
                            "categoria": "remocao",
                            "conteudo": original_content,
                            "alteracao": "",
                            "sort": modification_count,
                        }
                    )
                    i += 1
                modification_count += 1
        elif line.startswith("+"):
            # Linha adicionada (que não foi processada como modificação)
            added_content = line[1:].strip()
            if added_content:  # Ignorar linhas vazias
                modifications.append(
                    {
                        "categoria": "adicao",
                        "conteudo": "",
                        "alteracao": added_content,
                        "sort": modification_count,
                    }
                )
                modification_count += 1
            i += 1
        else:
            i += 1

    return modifications


def update_versao_status(
    versao_id,
    status,
    result_url=None,
    total_modifications=0,
    error_message=None,
    modifications=None,
    dry_run=False,
):
    """Atualiza o status da versão, adiciona observações e salva modificações em uma única transação"""
    try:
        print(f"📝 Atualizando status da versão {versao_id} para '{status}'...")

        if status == "concluido":
            observacao = (
                f"Comparação concluída em {datetime.now().strftime('%d/%m/%Y %H:%M')}. "
                f"Total de modificações encontradas: {total_modifications}. "
                f"Resultado disponível em: {result_url}"
            )
        elif status == "erro":
            observacao = f"Erro no processamento em {datetime.now().strftime('%d/%m/%Y %H:%M')}: {error_message}"
        else:
            observacao = f"Status atualizado para '{status}' em {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        update_data = {"status": status, "observacao": observacao}

        # Se há modificações para salvar, incluir no update_data
        if modifications and status == "concluido":
            print(f"💾 Incluindo {len(modifications)} modificações na transação...")

            # Preparar dados das modificações
            modifications_data = []
            for mod in modifications:
                modification_data = {
                    "versao": versao_id,
                    "categoria": mod["categoria"],
                    "conteudo": mod["conteudo"],
                    "alteracao": mod["alteracao"],
                    "sort": mod["sort"],
                    "status": "published",
                }
                modifications_data.append(modification_data)

            update_data["modificacoes"] = modifications_data
            print(
                f"✅ {len(modifications_data)} modificações preparadas para salvar em uma única transação"
            )

        if dry_run:
            print("🏃‍♂️ DRY-RUN: Não executando atualização no Directus")
            print(f"   Status: {update_data['status']}")
            print(f"   Observação: {update_data['observacao']}")
            if modifications and status == "concluido":
                print(f"   Modificações: {len(modifications)} itens (não salvos)")
            return {"id": versao_id, "status": status, "observacao": observacao}

        # Atualizar versão usando HTTP request direto
        try:
            update_url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
            response = requests.patch(
                update_url, headers=DIRECTUS_HEADERS, json=update_data
            )

            if response.status_code == 200:
                updated_versao = response.json().get("data", {})
                if modifications and status == "concluido":
                    print(
                        f"✅ Versão atualizada com status '{status}' e {len(modifications)} modificações salvas em uma única transação"
                    )
                else:
                    print(f"✅ Versão atualizada com status '{status}'")
                return updated_versao
            else:
                print(
                    f"❌ Erro ao atualizar versão: HTTP {response.status_code} - {response.text}"
                )
                return None
        except Exception as e:
            print(f"❌ Erro ao atualizar versão: {e}")
            return None

    except Exception as e:
        print(f"❌ Erro ao atualizar versão: {e}")
        return None


def processar_versao(versao_data, dry_run=False):
    """
    Processa uma versão específica
    """
    versao_id = versao_data["id"]

    try:
        if dry_run:
            print(f"\n🏃‍♂️ DRY-RUN: Analisando versão {versao_id} (sem alterações)")
        else:
            print(f"\n🚀 Processando versão {versao_id}")

        # Atualizar status para 'processando' (apenas se não for dry-run)
        if not dry_run:
            update_versao_status(versao_id, "processando")
        else:
            print("🏃‍♂️ DRY-RUN: Pulando atualização de status para 'processando'")

        # 1. Determinar arquivo original e modificado
        original_file_path, original_source = determine_original_file_id(versao_data)

        # Obter arquivo modificado (preenchido) dos dados de request
        versao_request = versao_data.get("versiona_ai_request_json", {})
        modified_file_path = versao_request.get("arquivoPreenchido")

        if not modified_file_path:
            raise Exception("Versão não possui arquivoPreenchido nos dados de request")

        print(f"📁 Original: {original_file_path} (fonte: {original_source})")
        print(f"📄 Modificado: {modified_file_path}")

        # 2. Baixar arquivos
        original_path = download_file_from_directus(original_file_path)
        modified_path = download_file_from_directus(modified_file_path)

        try:
            # 3. Gerar comparação HTML usando o CLI existente
            result_id = str(uuid.uuid4())
            result_filename = f"comparison_{result_id}.html"
            result_path = os.path.join(RESULTS_DIR, result_filename)

            print("🔄 Executando comparação visual usando CLI...")

            # Executar o docx_diff_viewer.py para HTML visual
            cmd = [
                "python",
                "docx_diff_viewer.py",
                original_path,
                modified_path,
                result_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"Erro na comparação: {result.stderr}")

            # 4. Converter documentos para análise textual
            print("📊 Analisando diferenças textuais...")

            # Converter para HTML temporário para análise
            original_html_temp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            )
            modified_html_temp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            )

            # Converter usando pandoc
            subprocess.run(
                ["pandoc", original_path, "-o", original_html_temp.name], check=True
            )
            subprocess.run(
                ["pandoc", modified_path, "-o", modified_html_temp.name], check=True
            )

            # Ler e processar HTML
            with open(original_html_temp.name, encoding="utf-8") as f:
                original_html = f.read()
            with open(modified_html_temp.name, encoding="utf-8") as f:
                modified_html = f.read()

            # Converter para texto limpo
            original_text = html_to_text(original_html)
            modified_text = html_to_text(modified_html)

            # Analisar diferenças
            modifications = analyze_differences_detailed(original_text, modified_text)

            # 5. Atualizar status da versão para concluído e salvar modificações em uma única transação
            result_url = f"http://{FLASK_HOST}:{FLASK_PORT}/outputs/{result_filename}"
            update_versao_status(
                versao_id,
                "concluido",
                result_url,
                len(modifications),
                modifications=modifications,
                dry_run=dry_run,
            )

            print(
                f"✅ Versão {versao_id} processada com sucesso! {len(modifications)} modificações encontradas"
            )

            # Limpar arquivos temporários de análise
            for temp_file in [original_html_temp.name, modified_html_temp.name]:
                try:
                    os.unlink(temp_file)
                except:
                    pass

        finally:
            # Limpar arquivos temporários principais
            for temp_file in [original_path, modified_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erro ao processar versão {versao_id}: {error_msg}")
        if not dry_run:
            update_versao_status(versao_id, "erro", error_message=error_msg)
        else:
            print("🏃‍♂️ DRY-RUN: Não atualizando status de erro no Directus")


def loop_processador(dry_run=False):
    """
    Loop principal do processador automático
    """
    if dry_run:
        print("🏃‍♂️ Processador automático iniciado em modo DRY-RUN!")
    else:
        print("🔄 Processador automático iniciado!")

    while processador_ativo:
        try:
            # Buscar versões para processar
            versoes = buscar_versoes_para_processar()

            # Processar cada versão encontrada
            for versao in versoes:
                if not processador_ativo:
                    break
                processar_versao(versao, dry_run)

            if not versoes:
                status_msg = "DRY-RUN" if dry_run else "Normal"
                print(
                    f"😴 {datetime.now().strftime('%H:%M:%S')} - Nenhuma versão para processar ({status_msg})"
                )

        except Exception as e:
            print(f"❌ Erro no loop do processador: {e}")

        # Aguardar 1 minuto antes da próxima verificação
        # Dividir em intervalos menores para ser mais responsivo aos sinais
        if processador_ativo:
            for _ in range(60):  # 60 segundos divididos em intervalos de 1 segundo
                if not processador_ativo:
                    break
                time.sleep(1)

    print("🔄 Loop do processador finalizado")


# Endpoints da API para monitoramento
@app.route("/health", methods=["GET"])
def health():
    """Verificação de saúde"""
    return jsonify(
        {
            "status": "healthy",
            "processador_ativo": processador_ativo,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/status", methods=["GET"])
def status():
    """Status do processador"""
    return jsonify(
        {
            "processador_ativo": processador_ativo,
            "directus_url": DIRECTUS_BASE_URL,
            "results_dir": RESULTS_DIR,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/outputs/<path:filename>", methods=["GET"])
def serve_result(filename):
    """Servir arquivos HTML de resultado"""
    try:
        return send_from_directory("outputs", filename)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo não encontrado"}), 404


def create_arg_parser():
    """Criar parser de argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Processador automático de versões",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executar em modo de análise sem modificar registros no Directus",
    )

    parser.add_argument(
        "--host",
        default=FLASK_HOST,
        help=f"Host para o servidor Flask de monitoramento (padrão: {FLASK_HOST})",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=FLASK_PORT,
        help=f"Porta para o servidor Flask de monitoramento (padrão: {FLASK_PORT})",
    )

    return parser


if __name__ == "__main__":
    # Configurar argumentos da linha de comando
    parser = create_arg_parser()
    args = parser.parse_args()

    # Registrar handlers de sinais para encerramento gracioso
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Comando kill
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal_handler)  # Hang up

    print("🚀 Processador Automático de Versões")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")
    print(f"🌐 Servidor de monitoramento: http://{args.host}:{args.port}")
    print("⏰ Verificação automática a cada 1 minuto")
    print("🔒 Monitoramento de sinais ativo (SIGINT, SIGTERM, SIGHUP)")
    if args.dry_run:
        print("🏃‍♂️ Modo: DRY-RUN (sem alterações no banco)")
    print("")
    print("📋 Endpoints de monitoramento:")
    print("  • GET  /health - Verificação de saúde")
    print("  • GET  /status - Status do processador")
    print("  • GET  /outputs/<filename> - Visualizar resultados")
    print("")

    # Iniciar o processador em uma thread separada
    processador_thread = threading.Thread(
        target=lambda: loop_processador(args.dry_run), daemon=True
    )
    processador_thread.start()

    # Iniciar o servidor Flask para monitoramento
    try:
        app.run(host=args.host, port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Parando processador...")
        processador_ativo = False
        print("✅ Processador parado!")
