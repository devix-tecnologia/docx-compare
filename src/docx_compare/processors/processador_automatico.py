#!/usr/bin/env python3
"""
Processador automático de versões
Verifica a cada minuto se há versões com status 'processar' e as processa automaticamente
"""

import argparse
import builtins
import contextlib
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
from typing import Literal

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

# Variáveis globais para controlar o processador
processador_ativo = True
processador_thread = None
verbose_mode = False
check_interval = 60  # Intervalo de verificação em segundos (padrão: 1 minuto)
request_timeout = 30  # Timeout das requisições HTTP em segundos (padrão: 30s)
ultima_verificacao = None  # Timestamp da última verificação


def signal_handler(signum, _frame):
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
        if verbose_mode:
            print("🧪 Testando conectividade com query simples...")

        url_simple = f"{DIRECTUS_BASE_URL}/items/versao?limit=5"

        if verbose_mode:
            print(f"🔗 URL simples: {url_simple}")
            print(f"🔑 Headers: {DIRECTUS_HEADERS}")
            print("   ----")

        simple_response = requests.get(
            url_simple, headers=DIRECTUS_HEADERS, timeout=request_timeout
        )

        if verbose_mode:
            print("🔍 Resultado RAW da query simples:")
            print(f"   Status: {simple_response.status_code}")
            print(f"   Response: {simple_response.text}")
            print("   ----")

        # Se a query simples funcionar, tentamos com filtro
        if simple_response.status_code == 200:
            if verbose_mode:
                print("✅ Conectividade OK, tentando query com filtro...")

            # Query com filtros usando query parameters padrão do Directus
            url_filtered = f"{DIRECTUS_BASE_URL}/items/versao"

            # Usar array de campos concatenado com vírgula
            fields_array = [
                "id",
                "date_created",
                "status",
                "codigo",
                "contrato.id",
                "contrato.modelo_contrato.arquivo_original",
                "contrato.versoes.arquivo",
                "contrato.versoes.codigo",
                "contrato.versoes.id",
                "contrato.versoes.date_created",
                "arquivo",
            ]

            params = {
                "filter[status][_eq]": "processar",
                "filter[contrato][modelo_contrato][status][_eq]": "publicado",
                "limit": 100,
                "sort": "date_created",
                "fields": ",".join(fields_array),
            }

            if verbose_mode:
                print(f"🔍 URL com filtro: {url_filtered}")
                print(f"🔍 Params: {params}")
                print("   ----")

            versoes_response = requests.get(
                url_filtered,
                headers=DIRECTUS_HEADERS,
                params=params,
                timeout=request_timeout,
            )

            if verbose_mode:
                print("🔍 Resultado RAW da query com filtro:")
                print(f"   Status: {versoes_response.status_code}")
                print(f"   Response: {versoes_response.text}")
                print("   ----")

            if versoes_response.status_code == 200:
                try:
                    response_json = versoes_response.json()
                    versoes = response_json.get("data", [])
                except (ValueError, KeyError):
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


def determine_versao_anterior(versao_data):
    """
    Determina a versão anterior mais próxima baseada na data de criação.

    Args:
        versao_data: Dados da versão atual contendo id, date_created e contrato com versões

    Returns:
        dict ou None: A versão anterior mais próxima ou None se não existir
    """
    versao_id = versao_data.get("id")
    versao_data_criacao = versao_data.get("date_created", "")

    versao_anterior = max(
        (
            v
            for v in versao_data.get("contrato", {}).get("versoes", [])
            if v["id"] != versao_id and v.get("date_created", "") < versao_data_criacao
        ),
        key=lambda v: v.get("date_created", ""),
        default=None,
    )

    if versao_anterior:
        print(
            f"📅 Versão anterior encontrada: ID {versao_anterior['id']} - Data: {versao_anterior['date_created']}"
        )
    else:
        print("⚠️ Nenhuma versão anterior encontrada")

    return versao_anterior


def determine_template_id(versao_data):
    """
    Determina o ID do arquivo original do modelo do contrato a partir dos dados da versão.

    Args:
        versao_data: Dados da versão contendo a estrutura do contrato

    Returns:
        str ou None: O ID do arquivo original do modelo de contrato ou None se não encontrado
    """
    contrato_data = versao_data.get("contrato", {})

    if isinstance(contrato_data, dict):
        modelo_contrato = contrato_data.get("modelo_contrato", {})
        if isinstance(modelo_contrato, dict):
            arquivo_original_id = modelo_contrato.get("arquivo_original")
            if arquivo_original_id:
                print(f"📄 arquivo_original encontrado: {arquivo_original_id}")
            else:
                print("⚠️ arquivo_original não encontrado no modelo_contrato")
            return arquivo_original_id
        else:
            print("⚠️ modelo_contrato não é um dict válido")
            return None
    else:
        print("⚠️ contrato_data não é um dict válido")
        return None


def determine_original_file_id(versao_data):
    """
    Determina o ID do arquivo original e sua origem.
    Se há versão anterior, DEVE ter arquivo (erro se não tiver).
    Se não há versão anterior, usa o template do modelo.

    Args:
        versao_data: Dados da versão atual

    Returns:
        tuple: (file_id, source) ou (None, None) se erro
    """
    versao_anterior = determine_versao_anterior(versao_data)

    if versao_anterior:
        # Se existe versão anterior, DEVE ter arquivo
        original_file_id = versao_anterior.get("arquivo")
        if original_file_id:
            print(f"📁 Usando arquivo da versão anterior: {original_file_id}")
            return original_file_id, "versao_anterior"
        else:
            print("❌ ERRO: Versão anterior encontrada mas sem arquivo válido")
            return None, None

    # Se não há versão anterior, usa o template
    template_id: str | None = determine_template_id(versao_data)
    if template_id:
        print("ℹ️ Usando template do modelo de contrato (primeira versão)")
        return template_id, "modelo_contrato"
    else:
        print("❌ ERRO: Template do modelo de contrato não encontrado")
        return None, None


def download_file_from_directus(
    file_id: str, cache_dir: str | None = None
) -> tuple[str, Literal["downloaded", "cached"]]:
    """
    Baixa um arquivo do Directus usando o caminho do arquivo.
    Verifica cache para evitar downloads desnecessários.

    Args:
        file_id: ID do arquivo no Directus
        cache_dir: Diretório para cache (opcional)

    Returns:
        Tuple[str, status]: (caminho_arquivo, status)
        - status: "downloaded" se baixou novo arquivo, "cached" se usou cache
    """
    try:
        download_url = f"{DIRECTUS_BASE_URL}/assets/{file_id}"

        # Verificar cache se diretório foi fornecido
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            cached_file_path = os.path.join(cache_dir, f"{file_id}.docx")

            if os.path.exists(cached_file_path):
                # Verificar se arquivo remoto mudou (usando HEAD request)
                head_response = requests.head(
                    download_url, headers=DIRECTUS_HEADERS, timeout=request_timeout
                )

                if head_response.status_code == 200:
                    # Comparar tamanhos ou ETags se disponível
                    remote_size = head_response.headers.get("content-length")
                    local_size = str(os.path.getsize(cached_file_path))

                    if remote_size and remote_size == local_size:
                        print(f"📋 Usando arquivo em cache: {cached_file_path}")
                        return cached_file_path, "cached"

        print(f"📥 Baixando arquivo {file_id}, através do endereço {download_url}")

        # Fazer o download do arquivo
        response = requests.get(
            download_url, headers=DIRECTUS_HEADERS, timeout=request_timeout
        )

        if response.status_code == 200:
            if cache_dir:
                # Salvar no cache com extensão .docx
                file_path = os.path.join(cache_dir, f"{file_id}.docx")
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                # Criar arquivo temporário com extensão .docx
                import tempfile

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".docx"
                ) as temp_file:
                    temp_file.write(response.content)
                    file_path = temp_file.name

            print(f"✅ Arquivo baixado: {file_path}")
            return file_path, "downloaded"
        else:
            raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

    except Exception as e:
        raise Exception(f"Erro ao baixar arquivo {file_id}: {e}")


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


def upload_file_to_directus(file_path, filename=None, dry_run=False):
    """
    Faz upload de um arquivo para o Directus e retorna o ID do arquivo
    """
    try:
        if not filename:
            filename = os.path.basename(file_path)

        print(f"📤 Fazendo upload do arquivo {filename} para o Directus...")

        if dry_run:
            print("🏃‍♂️ DRY-RUN: Não executando upload real para o Directus")
            return f"mock-file-id-{uuid.uuid4()}"

        # Endpoint para upload de arquivos no Directus
        upload_url = f"{DIRECTUS_BASE_URL}/files"

        # Preparar o arquivo para upload
        with open(file_path, "rb") as file:
            files = {"file": (filename, file, "text/html")}

            # Headers sem Content-Type para upload de arquivo
            upload_headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

            # Fazer o upload
            response = requests.post(
                upload_url, headers=upload_headers, files=files, timeout=request_timeout
            )

            if response.status_code == 200:
                file_data = response.json().get("data", {})
                file_id = file_data.get("id")

                if file_id:
                    print(f"✅ Arquivo enviado com sucesso! ID: {file_id}")
                    return file_id
                else:
                    raise Exception("Resposta do upload não contém ID do arquivo")
            else:
                raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Erro ao fazer upload do arquivo: {e}")
        return None


def update_versao_status(
    versao_id,
    status,
    modifica_arquivo=None,
    result_url=None,
    total_modifications=0,
    error_message=None,
    modifications=None,
    result_file_path=None,
    dry_run=False,
):
    """Atualiza o status da versão, adiciona observações, salva modificações e faz upload do relatório HTML"""
    try:
        print(f"📝 Atualizando status da versão {versao_id} para '{status}'...")

        # Upload do arquivo HTML se fornecido e status for concluído
        relatorio_diff_id = None
        if (
            result_file_path
            and status == "concluido"
            and os.path.exists(result_file_path)
        ):
            filename = f"relatorio_diff_{versao_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            relatorio_diff_id = upload_file_to_directus(
                result_file_path, filename, dry_run
            )

            if relatorio_diff_id:
                print(
                    f"✅ Relatório HTML enviado para o Directus com ID: {relatorio_diff_id}"
                )
                # Atualizar URL do resultado para usar o Directus
                result_url = f"{DIRECTUS_BASE_URL}/assets/{relatorio_diff_id}"
            else:
                print("❌ Falha no upload do relatório HTML")

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

        # Adicionar ID do arquivo original se fornecido
        if modifica_arquivo:
            update_data["modifica_arquivo"] = modifica_arquivo
            print(
                f"📄 Incluindo arquivo original no campo modifica_arquivo: {modifica_arquivo}"
            )

        # Adicionar ID do relatório se disponível
        if relatorio_diff_id:
            update_data["relatorio_diff"] = relatorio_diff_id
            print(
                f"📄 Incluindo relatório HTML no campo relatorio_diff: {relatorio_diff_id}"
            )

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
                    "status": "draft",
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
            if relatorio_diff_id:
                print(f"   Relatório HTML: {relatorio_diff_id} (não salvo)")
            if modifications and status == "concluido":
                print(f"   Modificações: {len(modifications)} itens (não salvos)")
            return {"id": versao_id, "status": status, "observacao": observacao}

        # Atualizar versão usando HTTP request direto
        try:
            update_url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
            response = requests.patch(
                update_url,
                headers=DIRECTUS_HEADERS,
                json=update_data,
                timeout=request_timeout,
            )

            if response.status_code == 200:
                updated_versao = response.json().get("data", {})
                if relatorio_diff_id:
                    print(
                        f"✅ Versão atualizada com status '{status}', relatório HTML ID {relatorio_diff_id}, e {len(modifications) if modifications else 0} modificações"
                    )
                elif modifications and status == "concluido":
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
    original_file_id = None  # Inicializar para uso no tratamento de erro

    try:
        if dry_run:
            print(f"\n🏃‍♂️ DRY-RUN: Analisando versão {versao_id} (sem alterações)")
        else:
            print(f"\n🚀 Processando versão {versao_id}")

        # Atualizar status para 'processando' (apenas se não for dry-run)
        if not dry_run:
            update_versao_status(
                versao_id,
                "processando",
                modifica_arquivo=None,
                result_url=None,
                total_modifications=0,
                error_message=None,
                modifications=None,
                result_file_path=None,
                dry_run=dry_run,
            )
        else:
            print("🏃‍♂️ DRY-RUN: Pulando atualização de status para 'processando'")

        # 1. Determinar arquivo original e modificado
        original_file_id, original_source = determine_original_file_id(versao_data)
        modificado_file_id = versao_data.get("arquivo")

        if not original_file_id or not modificado_file_id:
            raise Exception("IDs de arquivo original ou modificado não encontrados")

        print(f"📁 Original: {original_file_id} (fonte: {original_source})")
        print(f"📄 Modificado: {modificado_file_id}")

        # 2. Baixar arquivos
        original_path, _ = download_file_from_directus(original_file_id)
        modified_path, _ = download_file_from_directus(modificado_file_id)

        try:
            # 3. Gerar comparação HTML usando a função interna em vez do CLI
            result_id = str(uuid.uuid4())
            result_filename = f"comparison_{result_id}.html"
            result_path = os.path.join(RESULTS_DIR, result_filename)

            print("🔄 Executando comparação visual usando função interna...")

            # Usar a função do docx_diff_viewer diretamente
            from src.docx_compare.core.docx_diff_viewer import generate_diff_html

            try:
                print(
                    f"🔍 Analisando: {os.path.basename(original_path)} vs {os.path.basename(modified_path)}"
                )
                stats = generate_diff_html(original_path, modified_path, result_path)
                print(f"✅ Comparação visual concluída: {stats}")
            except Exception as e:
                print(f"❌ Erro na comparação visual: {e}")
                raise Exception(f"Erro na comparação: {e}")

            # 4. Converter documentos para análise textual
            print("📊 Analisando diferenças textuais...")

            # Converter para HTML temporário para análise
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as original_html_temp:
                original_html_temp_name = original_html_temp.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as modified_html_temp:
                modified_html_temp_name = modified_html_temp.name

            # Converter usando pandoc
            subprocess.run(
                ["pandoc", original_path, "-o", original_html_temp_name], check=True
            )
            subprocess.run(
                ["pandoc", modified_path, "-o", modified_html_temp_name], check=True
            )

            # Ler e processar HTML
            with open(original_html_temp_name, encoding="utf-8") as f:
                original_html = f.read()
            with open(modified_html_temp_name, encoding="utf-8") as f:
                modified_html = f.read()

            # Converter para texto limpo
            original_text = html_to_text(original_html)
            modified_text = html_to_text(modified_html)

            # Analisar diferenças
            modifications = analyze_differences_detailed(original_text, modified_text)

            # 5. Atualizar status da versão para concluído e salvar modificações em uma única transação
            result_url = f"http://{FLASK_HOST}:{FLASK_PORT}/results/{result_filename}"
            update_versao_status(
                versao_id,
                "concluido",
                modifica_arquivo=original_file_id,
                result_url=result_url,
                total_modifications=len(modifications),
                modifications=modifications,
                result_file_path=result_path,
                dry_run=dry_run,
            )

            print(
                f"✅ Versão {versao_id} processada com sucesso! {len(modifications)} modificações encontradas"
            )

            # Limpar arquivos temporários de análise
            for temp_file in [original_html_temp_name, modified_html_temp_name]:
                with contextlib.suppress(builtins.BaseException):
                    os.unlink(temp_file)

        finally:
            # Limpar arquivos temporários principais
            for temp_file in [original_path, modified_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except OSError:
                    pass

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erro ao processar versão {versao_id}: {error_msg}")
        if not dry_run:
            update_versao_status(
                versao_id,
                "erro",
                modifica_arquivo=original_file_id,
                error_message=error_msg,
            )
        else:
            print("🏃‍♂️ DRY-RUN: Não atualizando status de erro no Directus")


def processar_ciclo_unico(dry_run=False):
    """Executa um único ciclo de processamento"""
    try:
        print(
            f"🔍 {datetime.now().strftime('%H:%M:%S')} - Buscando versões para processar..."
        )

        # Buscar versões para processar
        versoes = buscar_versoes_para_processar()

        if versoes:
            print(f"✅ Encontradas {len(versoes)} versões para processar")

            # Processar cada versão encontrada
            for versao in versoes:
                processar_versao(versao, dry_run)

            print(f"🎯 Processamento completado: {len(versoes)} versões processadas")
        else:
            status_msg = "DRY-RUN" if dry_run else "Normal"
            print(f"😴 Nenhuma versão para processar ({status_msg})")

    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        raise


def loop_processador(dry_run=False):
    """
    Loop principal do processador automático
    """
    global ultima_verificacao

    mode_text = []
    if dry_run:
        mode_text.append("DRY-RUN")
    if verbose_mode:
        mode_text.append("VERBOSE")

    mode_suffix = f" ({', '.join(mode_text)})" if mode_text else ""
    print(f"🔄 Processador automático iniciado{mode_suffix}!")

    while processador_ativo:
        try:
            # Registrar horário da verificação
            ultima_verificacao = datetime.now()

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

        # Aguardar intervalo configurado antes da próxima verificação
        # Dividir em intervalos menores para ser mais responsivo aos sinais
        if processador_ativo:
            for _ in range(
                check_interval
            ):  # check_interval segundos divididos em intervalos de 1 segundo
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


@app.route("/results/<path:filename>", methods=["GET"])
def serve_result(filename):
    """Serve arquivos de resultado HTML."""
    try:
        return send_from_directory(RESULTS_DIR, filename)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo não encontrado"}), 404


@app.route("/metrics", methods=["GET"])
def metrics():
    """Métricas básicas do processador"""
    try:
        # Contar arquivos de resultado
        result_files = os.listdir(RESULTS_DIR) if os.path.exists(RESULTS_DIR) else []
        html_files = [f for f in result_files if f.endswith(".html")]

        # Calcular próxima verificação
        proxima_verificacao = None
        if ultima_verificacao and processador_ativo:
            from datetime import timedelta

            proxima_verificacao = (
                ultima_verificacao + timedelta(seconds=check_interval)
            ).isoformat()

        # Informações básicas
        return jsonify(
            {
                "processador_ativo": processador_ativo,
                "directus_url": DIRECTUS_BASE_URL,
                "results_dir": RESULTS_DIR,
                "total_result_files": len(html_files),
                "check_interval": check_interval,
                "request_timeout": request_timeout,
                "verbose_mode": verbose_mode,
                "ultima_verificacao": ultima_verificacao.isoformat()
                if ultima_verificacao
                else None,
                "proxima_verificacao": proxima_verificacao,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results", methods=["GET"])
def list_results():
    """Lista todos os arquivos de resultado disponíveis"""
    try:
        if not os.path.exists(RESULTS_DIR):
            return jsonify({"results": []})

        result_files = os.listdir(RESULTS_DIR)
        html_files = [f for f in result_files if f.endswith(".html")]

        results = []
        for filename in sorted(html_files, reverse=True):  # Mais recentes primeiro
            file_path = os.path.join(RESULTS_DIR, filename)
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                results.append(
                    {
                        "filename": filename,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "url": f"/results/{filename}",
                    }
                )

        return jsonify(
            {
                "total": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """Página inicial com informações do sistema"""
    try:
        # Calcular horário da próxima verificação
        proxima_verificacao_texto = "Não disponível"
        if ultima_verificacao and processador_ativo:
            from datetime import timedelta

            proxima_verificacao = ultima_verificacao + timedelta(seconds=check_interval)
            proxima_verificacao_texto = proxima_verificacao.strftime("%H:%M:%S")
        elif processador_ativo:
            proxima_verificacao_texto = "Em breve (primeira verificação)"

        # Retornar HTML simples para facilitar visualização
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DOCX Compare - Processador Automático</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                .status {{ color: {"green" if processador_ativo else "red"}; }}
                .endpoint {{ background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 4px; }}
                .code {{ font-family: monospace; background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🚀 DOCX Compare - Processador Automático</h1>
            <p><strong>Status:</strong> <span class="status">{"🟢 Ativo" if processador_ativo else "🔴 Parado"}</span></p>
            <p><strong>Directus:</strong> <span class="code">{DIRECTUS_BASE_URL}</span></p>
            <p><strong>Intervalo de verificação:</strong> {check_interval}s</p>
            <p><strong>Próxima verificação:</strong> {proxima_verificacao_texto}</p>

            <h2>📋 Endpoints Disponíveis</h2>
            <div class="endpoint"><strong>GET /health</strong> - Verificação de saúde</div>
            <div class="endpoint"><strong>GET /status</strong> - Status detalhado do processador</div>
            <div class="endpoint"><strong>GET /metrics</strong> - Métricas do sistema</div>
            <div class="endpoint"><strong>GET /results</strong> - Lista de resultados processados</div>
            <div class="endpoint"><strong>GET /results/&lt;filename&gt;</strong> - Visualizar resultado específico</div>

            <h2>ℹ️ Informações</h2>
            <p>Este serviço monitora automaticamente o Directus em busca de versões com status "processar" e gera comparações visuais entre documentos.</p>
            <p><strong>Última atualização:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
        </body>
        </html>
        """

        return html
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        "--single-run",
        action="store_true",
        help="Executar apenas um ciclo de processamento e encerrar",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ativar modo verbose com logs detalhados das consultas HTTP",
    )

    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=60,
        help="Intervalo de verificação em segundos (padrão: 60s)",
    )

    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=30,
        help="Timeout das requisições HTTP em segundos (padrão: 30s)",
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


def init_application():
    """Inicializa a aplicação com configurações padrão"""
    global verbose_mode, check_interval, request_timeout

    # Configurações padrão para produção
    verbose_mode = os.getenv("VERBOSE_MODE", "false").lower() == "true"
    check_interval = int(os.getenv("CHECK_INTERVAL", "60"))
    request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Registrar handlers de sinais para encerramento gracioso
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Comando kill
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal_handler)  # Hang up


if __name__ == "__main__":
    # Configurar argumentos da linha de comando
    parser = create_arg_parser()
    args = parser.parse_args()

    # Configurar variáveis globais
    verbose_mode = args.verbose
    check_interval = args.interval
    request_timeout = args.timeout

    # Registrar handlers de sinais para encerramento gracioso
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Comando kill
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal_handler)  # Hang up

    print("🚀 Processador Automático de Versões")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")

    if not args.single_run:
        print(f"🌐 Servidor de monitoramento: http://{args.host}:{args.port}")
        print(f"⏰ Verificação automática a cada {args.interval} segundos")

    print(f"⏱️  Timeout de requisições: {args.timeout} segundos")
    print("🔒 Monitoramento de sinais ativo (SIGINT, SIGTERM, SIGHUP)")

    mode_flags = []
    if args.dry_run:
        mode_flags.append("DRY-RUN (sem alterações no banco)")
    if args.verbose:
        mode_flags.append("VERBOSE (logs detalhados)")
    if args.single_run:
        mode_flags.append("SINGLE-RUN (execução única)")

    if mode_flags:
        print(f"🏃‍♂️ Modo: {' + '.join(mode_flags)}")

    if args.single_run:
        print("\n🎯 Executando ciclo único...")
        processar_ciclo_unico(args.dry_run)
        print("✅ Execução única completada")
        sys.exit(0)  # Encerrar aqui no modo single-run
    else:
        print("")
        print("📋 Endpoints de monitoramento:")
        print("  • GET  /health - Verificação de saúde")
        print("  • GET  /status - Status do processador")
        print("  • GET  /results/<filename> - Visualizar resultados")
        print("")

    # Verificar se deve usar servidor de produção
    if args.dry_run or args.verbose or args.interval != 60 or args.timeout != 30:
        # Modo desenvolvimento/debug - usar Flask development server
        print("🔧 Modo desenvolvimento detectado - usando Flask dev server")

        # Iniciar o processador em uma thread separada
        processador_thread = threading.Thread(
            target=lambda: loop_processador(args.dry_run), daemon=True
        )
        processador_thread.start()

        # Iniciar o servidor Flask para monitoramento
        try:
            app.run(host=args.host, port=args.port, debug=True)
        except KeyboardInterrupt:
            print("\n🛑 Parando processador...")
            processador_ativo = False
            print("✅ Processador parado!")
    else:
        # Modo produção - sugerir Gunicorn
        print("🚀 Para produção, use:")
        print("   gunicorn -c gunicorn.conf.py wsgi:app")
        print("   ou")
        print(
            "   docker build -t docx-compare . && docker run -p 5005:5005 docx-compare"
        )

        # Executar mesmo assim em desenvolvimento
        init_application()

        # Iniciar o processador em uma thread separada
        processador_thread = threading.Thread(
            target=lambda: loop_processador(args.dry_run), daemon=True
        )
        processador_thread.start()

        try:
            app.run(host=args.host, port=args.port, debug=True)
        except KeyboardInterrupt:
            print("\n🛑 Parando processador...")
            processador_ativo = False
            print("✅ Processador parado!")
else:
    # Quando importado (para Gunicorn), inicializar configurações
    init_application()
