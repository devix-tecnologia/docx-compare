#!/usr/bin/env python3
"""
API simples para comparação de documentos DOCX
Integração completa com Directus usando lógica de negócio
"""

import difflib
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

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
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")

# Configurações do Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5002"))

# Criar diretório de resultados
os.makedirs(RESULTS_DIR, exist_ok=True)


def get_directus_headers():
    """Retorna headers para requisições ao Directus"""
    return {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}",
        "Content-Type": "application/json",
    }


def get_versao_complete_data(versao_id):
    """
    Busca dados completos da versão com todos os relacionamentos necessários
    """
    try:
        print(f"🔍 Buscando dados da versão {versao_id}...")

        url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
        params = {
            "fields": ",".join(
                [
                    "id",
                    "date_created",
                    "arquivo",
                    "status",
                    "observacao",
                    "contrato.id",
                    "contrato.modelo_contrato.modelo_contrato",
                    "contrato.versoes.id",
                    "contrato.versoes.date_created",
                    "contrato.versoes.arquivo",
                ]
            )
        }

        response = requests.get(url, headers=get_directus_headers(), params=params)
        response.raise_for_status()

        versao_data = response.json()["data"]
        print("✅ Dados da versão obtidos")
        return versao_data

    except Exception as e:
        raise Exception(f"Erro ao buscar versão {versao_id}: {e}")


def determine_original_file_id(versao_data):
    """
    Determina qual arquivo usar como original baseado na lógica de negócio:
    1. versao.contrato.modelo_contrato.modelo_contrato
    2. OU versão mais recente (maior date_created) diferente da atual
    """
    try:
        current_versao_id = versao_data["id"]
        contrato = versao_data.get("contrato", {})

        print(f"🧠 Determinando arquivo original para versão {current_versao_id}...")

        # Primeira opção: modelo do contrato
        modelo_contrato = contrato.get("modelo_contrato")
        if modelo_contrato and modelo_contrato.get("modelo_contrato"):
            original_file_id = modelo_contrato["modelo_contrato"]
            print(f"📄 Usando modelo do contrato: {original_file_id}")
            return original_file_id, "modelo_contrato"

        # Segunda opção: versão mais recente
        versoes = contrato.get("versoes", [])
        if not versoes:
            raise Exception("Nenhuma versão encontrada no contrato")

        # Filtrar versões diferentes da atual que tenham arquivo
        outras_versoes = [
            v for v in versoes if v["id"] != current_versao_id and v.get("arquivo")
        ]

        if not outras_versoes:
            raise Exception("Nenhuma versão anterior encontrada para comparação")

        # Ordenar por date_created (mais recente primeiro)
        outras_versoes.sort(key=lambda x: x["date_created"], reverse=True)
        versao_mais_recente = outras_versoes[0]

        original_file_id = versao_mais_recente["arquivo"]
        print(
            f"📄 Usando versão mais recente: {original_file_id} (data: {versao_mais_recente['date_created']})"
        )

        return original_file_id, "versao_anterior"

    except Exception as e:
        raise Exception(f"Erro ao determinar arquivo original: {e}")


def download_file_from_directus(file_id):
    """
    Baixa um arquivo do Directus usando a API REST
    """
    try:
        print(f"📥 Baixando arquivo {file_id}...")

        # URL para baixar o arquivo
        download_url = f"{DIRECTUS_BASE_URL}/assets/{file_id}"

        headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

        print(f"🔗 Baixando de: {download_url}")

        # Baixar o arquivo
        response = requests.get(download_url, headers=headers, stream=True)
        response.raise_for_status()

        # Salvar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()

        print(f"✅ Arquivo baixado: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        raise Exception(f"Erro ao baixar arquivo {file_id}: {e}")


def clean_html_for_diff(html_content):
    """Remove tags HTML desnecessárias e normaliza o conteúdo"""
    html_content = re.sub(r"\n\s*\n", "\n", html_content)
    html_content = re.sub(r"\s+", " ", html_content)
    html_content = re.sub(r"</?html[^>]*>", "", html_content)
    html_content = re.sub(r"</?head[^>]*>", "", html_content)
    html_content = re.sub(r"</?body[^>]*>", "", html_content)
    html_content = re.sub(r"<meta[^>]*>", "", html_content)
    html_content = re.sub(r"<title[^>]*>.*?</title>", "", html_content)
    return html_content.strip()


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


def save_modifications_to_directus(versao_id, modifications):
    """Salva as modificações na coleção modificacao do Directus"""
    try:
        print(f"💾 Salvando {len(modifications)} modificações...")

        headers = get_directus_headers()
        saved_modifications = []

        for mod in modifications:
            modification_data = {
                "versao": versao_id,
                "categoria": mod["categoria"],
                "conteudo": mod["conteudo"],
                "alteracao": mod["alteracao"],
                "sort": mod["sort"],
                "status": "draft",
            }

            # Criar modificação usando a API do Directus
            response = requests.post(
                f"{DIRECTUS_BASE_URL}/items/modificacao",
                headers=headers,
                json=modification_data,
            )

            if response.status_code == 200:
                saved_modifications.append(response.json()["data"])
                print(f"✅ Modificação {mod['sort']} salva: {mod['categoria']}")
            else:
                print(
                    f"❌ Erro ao salvar modificação {mod['sort']}: {response.status_code}"
                )
                print(f"Response: {response.text}")

        return saved_modifications

    except Exception as e:
        print(f"❌ Erro ao salvar modificações: {e}")
        return []


def update_versao_status(versao_id, result_url, total_modifications):
    """Atualiza o status da versão para 'concluido' e adiciona observações"""
    try:
        print(f"📝 Atualizando status da versão {versao_id}...")

        observacao = (
            f"Comparação concluída em {datetime.now().strftime('%d/%m/%Y %H:%M')}. "
            f"Total de modificações encontradas: {total_modifications}. "
            f"Resultado disponível em: {result_url}"
        )

        update_data = {"status": "concluido", "observacao": observacao}

        # Atualizar versão usando a API do Directus
        response = requests.patch(
            f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}",
            headers=get_directus_headers(),
            json=update_data,
        )

        if response.status_code == 200:
            print("✅ Versão atualizada com status 'concluido'")
            return response.json()["data"]
        else:
            print(f"❌ Erro ao atualizar versão: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro ao atualizar versão: {e}")
        return None


@app.route("/health", methods=["GET"])
def health():
    """Verificação de saúde"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/compare", methods=["POST"])
def compare():
    """Compara dois documentos DOCX"""
    try:
        data = request.get_json()

        if not data or "original_file_id" not in data or "modified_file_id" not in data:
            return jsonify(
                {
                    "success": False,
                    "error": "Campos obrigatórios: original_file_id, modified_file_id",
                }
            ), 400

        original_id = data["original_file_id"]
        modified_id = data["modified_file_id"]

        print("🔄 Baixando arquivos do Directus...")

        # Baixar arquivos do Directus
        original_path = download_file_from_directus(original_id)
        modified_path = download_file_from_directus(modified_id)

        try:
            # Gerar nome único para o resultado
            result_id = str(uuid.uuid4())
            result_filename = f"comparison_{result_id}.html"
            result_path = os.path.join(RESULTS_DIR, result_filename)

            print("� Executando comparação...")

            # Executar o docx_diff_viewer.py
            cmd = [
                "python",
                "docx_diff_viewer.py",
                original_path,
                modified_path,
                result_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return jsonify(
                    {"success": False, "error": f"Erro na comparação: {result.stderr}"}
                ), 500

            # URL do resultado
            result_url = f"http://{FLASK_HOST}:{FLASK_PORT}/outputs/{result_filename}"

            print(f"✅ Comparação concluída: {result_url}")

            return jsonify(
                {
                    "success": True,
                    "result_url": result_url,
                    "result_filename": result_filename,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        finally:
            # Limpar arquivos temporários
            for temp_file in [original_path, modified_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/compare_versao", methods=["POST"])
def compare_versao():
    """
    Endpoint principal que implementa toda a lógica de negócio:
    1. Recebe ID da versão
    2. Determina automaticamente qual arquivo usar como original
    3. Executa comparação usando o CLI
    4. Salva modificações no Directus
    5. Atualiza status da versão
    """
    try:
        data = request.get_json()

        if not data or "versao_id" not in data:
            return jsonify(
                {"success": False, "error": "Campo obrigatório: versao_id"}
            ), 400

        versao_id = data["versao_id"]

        print(f"🚀 Iniciando comparação para versão {versao_id}")

        # 1. Buscar dados completos da versão
        versao_data = get_versao_complete_data(versao_id)

        # 2. Determinar arquivo original
        original_file_id, original_source = determine_original_file_id(versao_data)
        modified_file_id = versao_data["arquivo"]

        if not modified_file_id:
            return jsonify(
                {"success": False, "error": "Versão não possui arquivo anexado"}
            ), 400

        print(f"📁 Original: {original_file_id} (fonte: {original_source})")
        print(f"📄 Modificado: {modified_file_id}")

        # 3. Baixar arquivos
        original_path = download_file_from_directus(original_file_id)
        modified_path = download_file_from_directus(modified_file_id)

        try:
            # 4. Gerar comparação HTML usando o CLI existente
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
                return jsonify(
                    {"success": False, "error": f"Erro na comparação: {result.stderr}"}
                ), 500

            # 5. Converter documentos para análise textual (para extrair modificações)
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

            # 6. Salvar modificações no Directus
            saved_modifications = save_modifications_to_directus(
                versao_id, modifications
            )

            # 7. Atualizar status da versão
            result_url = f"http://{FLASK_HOST}:{FLASK_PORT}/outputs/{result_filename}"
            update_versao_status(versao_id, result_url, len(modifications))

            print(
                f"✅ Processo completo! {len(modifications)} modificações encontradas"
            )

            # Limpar arquivos temporários de análise
            for temp_file in [original_html_temp.name, modified_html_temp.name]:
                try:
                    os.unlink(temp_file)
                except:
                    pass

            return jsonify(
                {
                    "success": True,
                    "versao_id": versao_id,
                    "result_url": result_url,
                    "result_filename": result_filename,
                    "original_source": original_source,
                    "total_modifications": len(modifications),
                    "modifications_saved": len(saved_modifications),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        finally:
            # Limpar arquivos temporários principais
            for temp_file in [original_path, modified_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/outputs/<path:filename>", methods=["GET"])
def serve_result(filename):
    """Servir arquivos HTML de resultado"""
    try:
        return send_from_directory("outputs", filename)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo não encontrado"}), 404


if __name__ == "__main__":
    print("🚀 API Completa de Comparação de Documentos")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")
    print(f"🌐 Servidor: http://{FLASK_HOST}:{FLASK_PORT}")
    print("")
    print("📋 Endpoints disponíveis:")
    print("  • POST /compare - Comparação com lógica de negócio (versao_id)")
    print(
        "  • POST /compare_simple - Comparação simples (original_file_id, modified_file_id)"
    )
    print("  • GET  /outputs/<filename> - Visualizar resultados")
    print("  • GET  /health - Verificação de saúde")
    print("")
    print("💡 Como usar:")
    print(
        "  1. Para lógica de negócio: POST /compare com {'versao_id': 'id-da-versao'}"
    )
    print(
        "  2. Para comparação simples: POST /compare_simple com original_file_id e modified_file_id"
    )

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
