#!/usr/bin/env python3
"""
Processador automático para modelos de contrato
Compara arquivo_original vs arquivo_com_tags e extrai tags das diferenças
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
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify

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
RESULTS_DIR = os.getenv("MODELO_CONTRATO_RESULTS_DIR", "results_modelo")

# Cliente HTTP para Directus
print("🔧 Inicializando processador de modelo de contrato:")
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
FLASK_PORT = int(os.getenv("MODELO_CONTRATO_FLASK_PORT", "5006"))

# Variáveis globais para controlar o processador
processador_ativo = True
processador_thread = None
verbose_mode = False
check_interval = int(os.getenv("MODELO_CONTRATO_CHECK_INTERVAL", "60"))
request_timeout = 30

# Criar diretório de resultados
os.makedirs(RESULTS_DIR, exist_ok=True)


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

    processador_ativo = False

    if processador_thread and processador_thread.is_alive():
        print("⏳ Aguardando thread do processador terminar...")
        processador_thread.join(timeout=10)
        if processador_thread.is_alive():
            print("⚠️ Thread do processador não terminou no tempo esperado")
        else:
            print("✅ Thread do processador terminada")

    print("✅ Processador de modelo de contrato encerrado graciosamente!")
    sys.exit(0)


def extract_content_between_tags(text: str) -> dict[str, str]:
    """
    Extrai conteúdo entre tags considerando segunda ocorrência como fechamento.
    Se encontrar {{1}} duas vezes, a segunda é considerada tag de fechamento.

    Args:
        text: Texto para analisar

    Returns:
        Dict com nome_tag: conteudo_extraido
    """
    content_map = {}

    # Encontrar todas as tags (abertura e potenciais fechamentos)
    tag_pattern = r'\{\{(?:TAG-)?([a-zA-Z_][a-zA-Z0-9_.]*|\d+(?:\.\d+)*)\s*\}\}'
    all_matches = list(re.finditer(tag_pattern, text, re.IGNORECASE))

    # Agrupar matches por tag name
    tag_groups = {}
    for match in all_matches:
        tag_name = match.group(1).strip().lower()
        if tag_name not in tag_groups:
            tag_groups[tag_name] = []
        tag_groups[tag_name].append(match)

    # Para cada tag, se tiver pelo menos 2 ocorrências, extrair conteúdo entre primeira e segunda
    for tag_name, matches in tag_groups.items():
        if len(matches) >= 2:
            # Primeira ocorrência = abertura, segunda ocorrência = fechamento
            opening_pos = matches[0].end()
            closing_pos = matches[1].start()

            # Extrair conteúdo entre as tags
            raw_content = text[opening_pos:closing_pos].strip()

            # Limpar HTML tags e normalizar texto
            clean_content = re.sub(r'<[^>]+>', '', raw_content)  # Remove tags HTML
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()  # Normaliza espaços

            if clean_content:
                content_map[tag_name] = clean_content
                if verbose_mode:
                    print(f"📄 Conteúdo extraído para tag '{tag_name}': {clean_content[:100]}{'...' if len(clean_content) > 100 else ''}")
            else:
                if verbose_mode:
                    print(f"ℹ️ Tag '{tag_name}' encontrada em pares mas sem conteúdo entre elas")
        else:
            if verbose_mode:
                print(f"⚠️ Tag '{tag_name}' encontrada apenas {len(matches)} vez(es), precisa de pelo menos 2 para extração")

    return content_map


def extract_tags_from_differences(modifications: list[dict]) -> list[dict]:
    """
    Extrai tags das modificações encontradas entre os documentos.

    Padrões suportados:
    - {{tag}} ou {{ tag }} - tags textuais
    - {{1}}, {{1.1}}, {{1.2.3}} - tags numéricas
    - {{tag /}} ou {{ tag /}} - tags auto-fechadas
    - Variações com espaços

    Args:
        modifications: Lista de modificações encontradas na comparação

    Returns:
        List de dicionários com informações detalhadas das tags encontradas
    """
    tag_patterns = [
        # Padrões para tags com prefixo TAG-: {{TAG-nome}}
        r"(?<!\{)\{\{\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",
        # Padrões para tags com prefixo TAG- auto-fechadas: {{TAG-nome /}}
        r"(?<!\{)\{\{\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*\}\}(?!\})",
        # Padrões para tags com prefixo TAG- de fechamento: {{/TAG-nome}}
        r"(?<!\{)\{\{\s*/\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",
        # Padrões para tags textuais: {{tag}} com espaços opcionais
        r"(?<!\{)\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",
        # Padrões para tags textuais auto-fechadas: {{tag /}} com espaços opcionais
        r"(?<!\{)\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*\}\}(?!\})",
        # Padrões para tags de fechamento: {{/tag}} com espaços opcionais
        r"(?<!\{)\{\{\s*/\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",
        # Padrões para tags numéricas: {{1}}, {{1.1}}, {{1.2.3}} etc.
        r"(?<!\{)\{\{\s*(\d+(?:\.\d+)*)\s*\}\}(?!\})",
        # Tags numéricas auto-fechadas: {{1 /}}, {{1.1 /}} etc.
        r"(?<!\{)\{\{\s*(\d+(?:\.\d+)*)\s*/\s*\}\}(?!\})",
        # Tags numéricas de fechamento: {{/1}}, {{/1.1}} etc.
        r"(?<!\{)\{\{\s*/\s*(\d+(?:\.\d+)*)\s*\}\}(?!\})",
    ]

    tags_encontradas = {}  # Usar dict para evitar duplicatas e armazenar info adicional

    for idx, modification in enumerate(modifications):
        # Verificar tanto o conteúdo original quanto a alteração
        textos_para_analisar = [
            ("original", modification.get("conteudo", "")),
            ("alteracao", modification.get("alteracao", "")),
        ]

        for fonte, texto in textos_para_analisar:
            if not texto:
                continue

            # Aplicar todos os padrões de regex
            for pattern in tag_patterns:
                matches = re.finditer(pattern, texto, re.IGNORECASE)
                for match in matches:
                    # Limpar e normalizar o nome da tag
                    tag_nome = match.group(1).strip()

                    # Para tags numéricas, manter formato original
                    if re.match(r"^\d+(?:\.\d+)*$", tag_nome):
                        tag_nome_normalizado = tag_nome  # Manter formato numérico
                    else:
                        tag_nome_normalizado = (
                            tag_nome.lower()
                        )  # Minúscula para tags textuais

                    # Calcular posições no texto
                    pos_inicio = match.start()
                    pos_fim = match.end()
                    texto_completo = match.group(0)

                    # Se a tag já existe, manter a versão com mais contexto
                    if tag_nome_normalizado not in tags_encontradas or len(texto) > len(
                        tags_encontradas[tag_nome_normalizado].get("contexto", "")
                    ):
                        # Calcular linha aproximada
                        linha_aproximada = texto[:pos_inicio].count("\n") + 1

                        tags_encontradas[tag_nome_normalizado] = {
                            "nome": tag_nome_normalizado,
                            "texto_completo": texto_completo,
                            "posicao_inicio": pos_inicio,
                            "posicao_fim": pos_fim,
                            "contexto": texto[max(0, pos_inicio - 100) : pos_fim + 100],
                            "fonte": fonte,
                            "linha_aproximada": linha_aproximada,
                            "modificacao_indice": idx,
                            "caminho_tag_inicio": f"modificacao_{idx}_linha_{linha_aproximada}_pos_{pos_inicio}",
                            "caminho_tag_fim": f"modificacao_{idx}_linha_{linha_aproximada}_pos_{pos_fim}",
                        }

                        if verbose_mode:
                            print(
                                f"🏷️  Tag encontrada: '{tag_nome_normalizado}' em '{texto_completo}' ({fonte})"
                            )

    # Converter dict para lista
    resultado = list(tags_encontradas.values())

    if verbose_mode:
        tags_nomes = [tag["nome"] for tag in resultado]
        print(f"🏷️  Extraídas {len(resultado)} tags únicas: {tags_nomes}")

    return resultado


def buscar_modelos_para_processar():
    """
    Busca modelos de contrato com status 'processar' no Directus
    """
    try:
        print(
            f"🔍 {datetime.now().strftime('%H:%M:%S')} - Buscando modelos para processar..."
        )

        if verbose_mode:
            print("🧪 Testando conectividade com query simples...")

        # Query simples para testar conectividade
        url_simple = f"{DIRECTUS_BASE_URL}/items/modelo_contrato?limit=5"

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

            url_filtered = f"{DIRECTUS_BASE_URL}/items/modelo_contrato"

            # Campos necessários
            fields_array = [
                "id",
                "date_created",
                "status",
                "nome",
                "versao",
                "arquivo_original",
                "arquivo_com_tags",
            ]

            params = {
                "filter[status][_eq]": "processar",
                "filter[arquivo_original][_nnull]": "true",  # Não nulo
                "filter[arquivo_com_tags][_nnull]": "true",  # Não nulo
                "limit": 10,
                "sort": "date_created",
                "fields": ",".join(fields_array),
            }

            if verbose_mode:
                print(f"🔍 URL com filtro: {url_filtered}")
                print(f"🔍 Params: {params}")
                print("   ----")

            modelos_response = requests.get(
                url_filtered,
                headers=DIRECTUS_HEADERS,
                params=params,
                timeout=request_timeout,
            )

            if verbose_mode:
                print("🔍 Resultado RAW da query com filtro:")
                print(f"   Status: {modelos_response.status_code}")
                print(f"   Response: {modelos_response.text}")
                print("   ----")

            if modelos_response.status_code == 200:
                try:
                    response_json = modelos_response.json()
                    modelos = response_json.get("data", [])
                except (ValueError, KeyError):
                    modelos = []
            else:
                modelos = []
        else:
            print("❌ Problema de conectividade detectado")
            modelos = []

        print(f"✅ Encontrados {len(modelos)} modelos para processar")
        return modelos

    except Exception as e:
        print(f"❌ Erro ao buscar modelos: {e}")
        return []


def download_file_from_directus(file_id: str, cache_dir: str = "") -> tuple[str, str]:
    """
    Baixa um arquivo do Directus usando o ID do arquivo.

    Args:
        file_id: ID do arquivo no Directus
        cache_dir: Diretório para cache (opcional)

    Returns:
        Tuple[str, status]: (caminho_arquivo, status)
    """
    try:
        download_url = f"{DIRECTUS_BASE_URL}/assets/{file_id}"

        # Verificar cache se diretório foi fornecido
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            cached_file_path = os.path.join(cache_dir, f"{file_id}.docx")

            if os.path.exists(cached_file_path):
                # Verificar se arquivo remoto mudou
                head_response = requests.head(
                    download_url, headers=DIRECTUS_HEADERS, timeout=request_timeout
                )

                if head_response.status_code == 200:
                    remote_size = head_response.headers.get("content-length")
                    local_size = str(os.path.getsize(cached_file_path))

                    if remote_size and remote_size == local_size:
                        print(f"📋 Usando arquivo em cache: {cached_file_path}")
                        return cached_file_path, "cached"

        print(f"📥 Baixando arquivo {file_id}")

        response = requests.get(
            download_url, headers=DIRECTUS_HEADERS, timeout=request_timeout
        )

        if response.status_code == 200:
            if cache_dir:
                file_path = os.path.join(cache_dir, f"{file_id}.docx")
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
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
    """Converte HTML para texto limpo (reutilizada do processador principal)"""
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
            original_content = line[1:].strip()
            if original_content:
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
                    i += 2
                else:
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
            added_content = line[1:].strip()
            if added_content:
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


def limpar_tags_modelo_contrato(modelo_id: str, dry_run=False):
    """
    Remove todas as tags existentes de um modelo de contrato antes do reprocessamento.

    Args:
        modelo_id: ID do modelo de contrato
        dry_run: Se True, não executa alterações no banco

    Returns:
        int: Número de tags removidas
    """
    try:
        if dry_run:
            print("🏃‍♂️ DRY-RUN: Simulando limpeza de tags existentes")
            return 0

        print("🗑️ Limpando tags existentes...")

        # Buscar o modelo com suas tags associadas
        modelo_response = requests.get(
            f"{DIRECTUS_BASE_URL}/items/modelo_contrato/{modelo_id}",
            params={"fields": "tags"},
            headers=DIRECTUS_HEADERS
        )

        if modelo_response.status_code == 200:
            modelo_data = modelo_response.json().get('data', {})
            tags_ids = modelo_data.get('tags', [])

            if not tags_ids:
                print("ℹ️ Nenhuma tag existente para limpar")
                return 0

            print(f"   Encontradas {len(tags_ids)} tags para remover (via modelo)")
            tags_removidas = 0

            # Deletar cada tag
            for tag_id in tags_ids:
                delete_response = requests.delete(
                    f"{DIRECTUS_BASE_URL}/items/modelo_contrato_tag/{tag_id}",
                    headers=DIRECTUS_HEADERS
                )

                if delete_response.status_code in [200, 204]:
                    print(f"   ✅ Tag 'N/A' removida (ID: {tag_id})")
                    tags_removidas += 1
                else:
                    print(f"   ❌ Erro ao remover tag {tag_id}: {delete_response.status_code}")

            print(f"✅ {tags_removidas} tags removidas com sucesso")
            return tags_removidas

        else:
            print(f"⚠️ Erro ao buscar modelo: {modelo_response.status_code}")
            return 0

    except Exception as e:
        print(f"❌ Erro durante limpeza de tags: {e}")
        return 0


def salvar_tags_modelo_contrato(
    modelo_id: str, tags_encontradas: list[dict], dry_run=False
):
    """
    Salva as tags encontradas na coleção modelo_contrato_tag

    Args:
        modelo_id: ID do modelo de contrato
        tags_encontradas: Lista de dicionários com informações das tags
        dry_run: Se True, não executa alterações no banco

    Returns:
        List de IDs das tags criadas
    """
    try:
        tags_criadas = []

        if not tags_encontradas:
            print("ℹ️ Nenhuma tag encontrada para salvar")
            return tags_criadas

        print(f"💾 Salvando {len(tags_encontradas)} tags para modelo {modelo_id}")

        for tag_info in sorted(tags_encontradas, key=lambda x: x["nome"]):
            tag_data = {
                "modelo_contrato": modelo_id,
                "tag_nome": tag_info["nome"],
                "caminho_tag_inicio": tag_info.get("caminho_tag_inicio", ""),
                "caminho_tag_fim": tag_info.get("caminho_tag_fim", ""),
                "conteudo": tag_info.get("conteudo", ""),  # Campo conteúdo adicionado
                "contexto": tag_info.get("contexto", "")[
                    :500
                ],  # Limitar contexto a 500 chars
                "linha_aproximada": tag_info.get("linha_aproximada", 0),
                "posicao_inicio": tag_info.get("posicao_inicio", 0),
                "posicao_fim": tag_info.get("posicao_fim", 0),
                "status": "published",
            }

            if dry_run:
                print(
                    f"🏃‍♂️ DRY-RUN: Criaria tag '{tag_info['nome']}' para modelo {modelo_id}"
                )
                tags_criadas.append(f"mock-tag-id-{tag_info['nome']}")
                continue

            # Criar tag no Directus
            create_url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato_tag"

            response = requests.post(
                create_url,
                headers=DIRECTUS_HEADERS,
                json=tag_data,
                timeout=request_timeout,
            )

            if response.status_code in [200, 201]:
                tag_criada = response.json().get("data", {})
                tag_id = tag_criada.get("id")
                if tag_id:
                    tags_criadas.append(tag_id)
                    conteudo_preview = tag_info.get("conteudo", "")[:50]
                    print(f"✅ Tag '{tag_info['nome']}' criada com ID: {tag_id}")
                    if conteudo_preview:
                        print(f"   📄 Conteúdo: {conteudo_preview}{'...' if len(tag_info.get('conteudo', '')) > 50 else ''}")
                    if verbose_mode:
                        print(
                            f"   📍 Caminho início: {tag_info.get('caminho_tag_inicio', 'N/A')}"
                        )
                        print(
                            f"   📍 Caminho fim: {tag_info.get('caminho_tag_fim', 'N/A')}"
                        )
                        full_content = tag_info.get("conteudo", "")
                        if full_content:
                            print(f"   📄 Conteúdo completo: {full_content}")
                else:
                    print(f"⚠️ Tag '{tag_info['nome']}' criada mas sem ID retornado")
            else:
                error_text = response.text[:200]
                print(
                    f"❌ Erro ao criar tag '{tag_info['nome']}': {response.status_code} - {error_text}"
                )

        return tags_criadas

    except Exception as e:
        print(f"❌ Erro ao salvar tags: {e}")
        return []


def associar_tags_com_clausulas(modelo_id: str, tags_criadas: list, tags_encontradas: list, dry_run=False):
    """
    Associa tags com cláusulas: se tag.nome == clausula.nome, então clausula.tag = tag.id
    Busca as tags diretamente pelo nome, sem depender de ordem.

    Args:
        modelo_id: ID do modelo de contrato
        tags_criadas: Lista de IDs das tags criadas (não usado - buscamos pelo nome)
        tags_encontradas: Lista dos nomes das tags encontradas (usado apenas para referência)
        dry_run: Se True, não executa alterações no banco

    Returns:
        int: Número de associações criadas
    """
    try:
        if dry_run:
            print("🏃‍♂️ DRY-RUN: Simulando associação de tags com cláusulas")
            return 0

        print("🔗 Associando tags com cláusulas (busca direta pelo nome: tag.nome = clausula.nome → clausula.tag = tag.id)...")

        # Primeiro, buscar todas as cláusulas disponíveis
        clausulas_response = requests.get(
            f"{DIRECTUS_BASE_URL}/items/clausula",
            params={
                "fields": "id,nome,tag",
                "limit": 1000
            },
            headers=DIRECTUS_HEADERS
        )

        if clausulas_response.status_code != 200:
            print(f"⚠️ Erro ao buscar cláusulas: {clausulas_response.status_code}")
            return 0

        clausulas_data = clausulas_response.json().get('data', [])
        print(f"   Encontradas {len(clausulas_data)} cláusulas disponíveis")

        associacoes_criadas = 0

        # Para cada cláusula, buscar a tag correspondente pelo nome
        for clausula in clausulas_data:
            clausula_id = clausula.get('id')
            clausula_nome = str(clausula.get('nome', '') or '').strip()
            clausula_tag_atual = clausula.get('tag')

            if not clausula_nome:
                if verbose_mode:
                    print(f"   🔍 Cláusula {clausula_id} sem nome - ignorando")
                continue

            print(f"   🔍 Buscando tag para cláusula '{clausula_nome}'...")

            # Buscar tag com o mesmo nome da cláusula
            tag_response = requests.get(
                f"{DIRECTUS_BASE_URL}/items/modelo_contrato_tag",
                params={
                    "filter[modelo_contrato][_eq]": modelo_id,
                    "filter[tag_nome][_eq]": clausula_nome,
                    "fields": "id,tag_nome",
                    "limit": 1
                },
                headers=DIRECTUS_HEADERS
            )

            if tag_response.status_code == 200:
                tag_data = tag_response.json().get('data', [])
                if tag_data:
                    tag_id = tag_data[0].get('id')
                    tag_nome = tag_data[0].get('tag_nome', clausula_nome)

                    # Verificar se a cláusula já tem essa tag associada
                    if clausula_tag_atual == tag_id:
                        print(f"     ℹ️ Cláusula '{clausula_nome}' já tem tag '{tag_nome}' associada")
                        continue

                    # Atualizar a cláusula com o tag_id
                    update_data = {
                        "tag": tag_id
                    }

                    update_response = requests.patch(
                        f"{DIRECTUS_BASE_URL}/items/clausula/{clausula_id}",
                        json=update_data,
                        headers=DIRECTUS_HEADERS
                    )

                    if update_response.status_code in [200, 204]:
                        print(f"     ✅ Cláusula '{clausula_nome}' associada com tag '{tag_nome}' (ID: {tag_id})")
                        associacoes_criadas += 1
                    else:
                        print(f"     ❌ Erro ao associar cláusula '{clausula_nome}' com tag '{tag_nome}': {update_response.status_code}")
                        if verbose_mode:
                            print(f"        Response: {update_response.text}")
                else:
                    if verbose_mode:
                        print(f"     🔍 Nenhuma tag encontrada com nome '{clausula_nome}'")
            else:
                print(f"     ❌ Erro ao buscar tag para cláusula '{clausula_nome}': {tag_response.status_code}")
                if verbose_mode:
                    print(f"        Response: {tag_response.text}")

        print(f"✅ {associacoes_criadas} associações tag-cláusula criadas")
        return associacoes_criadas

    except Exception as e:
        print(f"❌ Erro ao associar tags com cláusulas: {e}")
        return 0


def update_modelo_status(
    modelo_id: str,
    status: str,
    total_tags: int = 0,
    error_message: str = "",
    dry_run: bool = False,
):
    """
    Atualiza o status do modelo de contrato

    Args:
        modelo_id: ID do modelo
        status: Novo status ('processando', 'concluido', 'erro')
        total_tags: Número de tags encontradas
        error_message: Mensagem de erro (se houver)
        dry_run: Se True, não executa alterações no banco
    """
    try:
        print(f"📝 Atualizando status do modelo {modelo_id} para '{status}'...")

        if status == "concluido":
            observacao = (
                f"Processamento de tags concluído em {datetime.now().strftime('%d/%m/%Y %H:%M')}. "
                f"Total de tags extraídas: {total_tags}."
            )
        elif status == "erro":
            observacao = (
                f"Erro no processamento em {datetime.now().strftime('%d/%m/%Y %H:%M')}: "
                f"{error_message}"
            )
        else:
            observacao = f"Status atualizado para '{status}' em {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        update_data = {"status": status, "observacao": observacao}

        if dry_run:
            print("🏃‍♂️ DRY-RUN: Não executando atualização no Directus")
            print(f"   Status: {update_data['status']}")
            print(f"   Observação: {update_data['observacao']}")
            return {"id": modelo_id, "status": status, "observacao": observacao}

        # Atualizar modelo no Directus
        update_url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato/{modelo_id}"
        response = requests.patch(
            update_url,
            headers=DIRECTUS_HEADERS,
            json=update_data,
            timeout=request_timeout,
        )

        if response.status_code == 200:
            updated_modelo = response.json().get("data", {})
            print(f"✅ Modelo atualizado com status '{status}' e {total_tags} tags")
            return updated_modelo
        else:
            print(f"❌ Erro ao atualizar modelo: HTTP {response.status_code}")
            if verbose_mode:
                print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao atualizar modelo: {e}")
        return None


def processar_modelo_contrato(modelo_data, dry_run=False):
    """
    Processa um modelo de contrato específico

    Args:
        modelo_data: Dados do modelo de contrato
        dry_run: Se True, executa sem fazer alterações no banco
    """
    modelo_id = modelo_data["id"]

    try:
        if dry_run:
            print(f"\n🏃‍♂️ DRY-RUN: Analisando modelo {modelo_id} (sem alterações)")
        else:
            print(f"\n🚀 Processando modelo de contrato {modelo_id}")

        # Limpar tags existentes antes do processamento (para evitar duplicatas)
        if not dry_run:
            limpar_tags_modelo_contrato(modelo_id, dry_run=dry_run)

        # Atualizar status para 'processando'
        if not dry_run:
            update_modelo_status(modelo_id, "processando", dry_run=dry_run)

        # 1. Obter IDs dos arquivos
        arquivo_original_id = modelo_data.get("arquivo_original")
        arquivo_com_tags_id = modelo_data.get("arquivo_com_tags")

        if not arquivo_original_id or not arquivo_com_tags_id:
            raise Exception(
                "IDs de arquivo original ou arquivo com tags não encontrados"
            )

        print(f"📁 Arquivo original: {arquivo_original_id}")
        print(f"🏷️  Arquivo com tags: {arquivo_com_tags_id}")

        # 2. Baixar arquivos
        original_path, _ = download_file_from_directus(arquivo_original_id)
        tagged_path, _ = download_file_from_directus(arquivo_com_tags_id)

        try:
            # 3. Converter documentos para análise textual
            print("📊 Analisando diferenças textuais...")

            # Converter para HTML temporário
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as original_html_temp:
                original_html_temp_name = original_html_temp.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as tagged_html_temp:
                tagged_html_temp_name = tagged_html_temp.name

            # Converter usando pandoc
            subprocess.run(
                ["pandoc", original_path, "-o", original_html_temp_name], check=True
            )
            subprocess.run(
                ["pandoc", tagged_path, "-o", tagged_html_temp_name], check=True
            )

            # Ler e processar HTML
            with open(original_html_temp_name, encoding="utf-8") as f:
                original_html = f.read()
            with open(tagged_html_temp_name, encoding="utf-8") as f:
                tagged_html = f.read()

            # Converter para texto limpo
            original_text = html_to_text(original_html)
            tagged_text = html_to_text(tagged_html)

            # Analisar diferenças
            modifications = analyze_differences_detailed(original_text, tagged_text)
            print(f"🔍 Encontradas {len(modifications)} modificações")

            # 4. Extrair conteúdo entre tags do arquivo com tags
            content_map = extract_content_between_tags(tagged_text)
            print(f"📄 Extraído conteúdo para {len(content_map)} tags: {sorted(content_map.keys())}")

            # 5. Extrair tags das diferenças
            tags_encontradas = extract_tags_from_differences(modifications)

            # 6. Enriquecer tags encontradas com conteúdo extraído
            for tag_info in tags_encontradas:
                tag_nome = tag_info["nome"]
                if tag_nome in content_map:
                    tag_info["conteudo"] = content_map[tag_nome]
                    if verbose_mode:
                        print(f"✅ Tag '{tag_nome}' enriquecida com conteúdo")
                else:
                    tag_info["conteudo"] = ""
                    if verbose_mode:
                        print(f"ℹ️ Tag '{tag_nome}' sem conteúdo correspondente")

            tag_names = [tag["nome"] for tag in tags_encontradas]
            print(
                f"🏷️  Extraídas {len(tags_encontradas)} tags únicas: {sorted(tag_names)}"
            )

            # 7. Salvar tags no banco
            tags_criadas = salvar_tags_modelo_contrato(
                modelo_id, tags_encontradas, dry_run
            )

            # 8. Associar tags com cláusulas correspondentes
            associacoes_criadas = associar_tags_com_clausulas(
                modelo_id, tags_criadas, tags_encontradas, dry_run
            )

            # 9. Atualizar status do modelo para concluído
            update_modelo_status(
                modelo_id,
                "concluido",
                total_tags=len(tags_encontradas),
                dry_run=dry_run,
            )

            print(f"✅ Modelo {modelo_id} processado com sucesso!")
            print(f"   📊 {len(modifications)} modificações analisadas")
            print(f"   🏷️  {len(tags_encontradas)} tags extraídas")
            print(f"   💾 {len(tags_criadas)} tags salvas no banco")
            print(f"   🔗 {associacoes_criadas} associações tag-cláusula criadas")

            # Limpar arquivos temporários de análise
            for temp_file in [original_html_temp_name, tagged_html_temp_name]:
                with contextlib.suppress(builtins.BaseException):
                    os.unlink(temp_file)

        finally:
            # Limpar arquivos baixados
            for temp_file in [original_path, tagged_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except OSError:
                    pass

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erro ao processar modelo {modelo_id}: {error_msg}")
        if not dry_run:
            update_modelo_status(
                modelo_id, "erro", error_message=error_msg, dry_run=dry_run
            )


def processar_ciclo_unico(dry_run=False):
    """Executa um único ciclo de processamento de modelos"""
    try:
        print(
            f"🔍 {datetime.now().strftime('%H:%M:%S')} - Buscando modelos para processar..."
        )

        # Buscar modelos para processar
        modelos = buscar_modelos_para_processar()

        if modelos:
            print(f"✅ Encontrados {len(modelos)} modelos para processar")

            # Processar cada modelo encontrado
            for modelo in modelos:
                processar_modelo_contrato(modelo, dry_run)

            print(f"🎯 Processamento completado: {len(modelos)} modelos processados")
        else:
            status_msg = "DRY-RUN" if dry_run else "Normal"
            print(f"😴 Nenhum modelo para processar ({status_msg})")

    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        raise


def loop_processador(dry_run=False):
    """
    Loop principal do processador automático de modelos
    """
    mode_text = []
    if dry_run:
        mode_text.append("DRY-RUN")
    if verbose_mode:
        mode_text.append("VERBOSE")

    mode_suffix = f" ({', '.join(mode_text)})" if mode_text else ""
    print(f"🔄 Processador de modelos de contrato iniciado{mode_suffix}!")

    while processador_ativo:
        try:
            # Buscar modelos para processar
            modelos = buscar_modelos_para_processar()

            # Processar cada modelo encontrado
            for modelo in modelos:
                if not processador_ativo:
                    break
                processar_modelo_contrato(modelo, dry_run)

            if not modelos:
                status_msg = "DRY-RUN" if dry_run else "Normal"
                print(
                    f"😴 {datetime.now().strftime('%H:%M:%S')} - Nenhum modelo para processar ({status_msg})"
                )

        except Exception as e:
            print(f"❌ Erro no loop do processador: {e}")

        # Aguardar intervalo configurado
        if processador_ativo:
            for _ in range(check_interval):
                if not processador_ativo:
                    break
                time.sleep(1)

    print("🔄 Loop do processador de modelos finalizado")


# Endpoints Flask para monitoramento
@app.route("/health", methods=["GET"])
def health():
    """Verificação de saúde"""
    return jsonify(
        {
            "status": "healthy",
            "processador_ativo": processador_ativo,
            "tipo": "modelo_contrato",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/status", methods=["GET"])
def status():
    """Status do processador"""
    return jsonify(
        {
            "processador_ativo": processador_ativo,
            "tipo": "modelo_contrato",
            "directus_url": DIRECTUS_BASE_URL,
            "results_dir": RESULTS_DIR,
            "check_interval": check_interval,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/metrics", methods=["GET"])
def metrics():
    """Métricas básicas do processador"""
    try:
        return jsonify(
            {
                "processador_ativo": processador_ativo,
                "tipo": "modelo_contrato",
                "directus_url": DIRECTUS_BASE_URL,
                "results_dir": RESULTS_DIR,
                "check_interval": check_interval,
                "request_timeout": request_timeout,
                "verbose_mode": verbose_mode,
                "flask_port": FLASK_PORT,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """Página inicial com informações do sistema"""
    try:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Processador de Modelo de Contrato</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                .status {{ color: {"green" if processador_ativo else "red"}; }}
                .endpoint {{ background: #f5f5f5; padding: 10px; margin: 5px 0; border-radius: 4px; }}
                .code {{ font-family: monospace; background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🏷️ Processador de Modelo de Contrato</h1>
            <p><strong>Status:</strong> <span class="status">{"🟢 Ativo" if processador_ativo else "🔴 Parado"}</span></p>
            <p><strong>Directus:</strong> <span class="code">{DIRECTUS_BASE_URL}</span></p>
            <p><strong>Intervalo de verificação:</strong> {check_interval}s</p>
            <p><strong>Porta:</strong> {FLASK_PORT}</p>

            <h2>📋 Endpoints Disponíveis</h2>
            <div class="endpoint"><strong>GET /health</strong> - Verificação de saúde</div>
            <div class="endpoint"><strong>GET /status</strong> - Status detalhado do processador</div>
            <div class="endpoint"><strong>GET /metrics</strong> - Métricas do sistema</div>

            <h2>🏷️ Funcionalidade</h2>
            <p>Este processador monitora a coleção <strong>modelo_contrato</strong> em busca de registros com status "processar".</p>
            <p><strong>Processo:</strong></p>
            <ul>
                <li>Compara <code>arquivo_original</code> vs <code>arquivo_com_tags</code></li>
                <li>Extrai tags das diferenças (padrões {{'{"}tag{"}'}} etc.)</li>
                <li>Salva tags na coleção <code>modelo_contrato_tag</code></li>
                <li>Atualiza status para "concluido"</li>
            </ul>

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
        description="Processador automático de modelos de contrato",
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
    verbose_mode = os.getenv("MODELO_CONTRATO_VERBOSE", "false").lower() == "true"
    check_interval = int(os.getenv("MODELO_CONTRATO_CHECK_INTERVAL", "60"))
    request_timeout = int(os.getenv("MODELO_CONTRATO_REQUEST_TIMEOUT", "30"))

    # Registrar handlers de sinais para encerramento gracioso
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal_handler)


if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()

    # Configurar variáveis globais
    verbose_mode = args.verbose
    check_interval = args.interval
    request_timeout = args.timeout

    # Registrar handlers de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal_handler)

    print("🏷️ Processador Automático de Modelos de Contrato")
    print(f"📁 Resultados salvos em: {RESULTS_DIR}")
    print(f"🔗 Directus: {DIRECTUS_BASE_URL}")

    if not args.single_run:
        print(f"🌐 Servidor de monitoramento: http://{args.host}:{args.port}")
        print(f"⏰ Verificação automática a cada {args.interval} segundos")

    print(f"⏱️  Timeout de requisições: {args.timeout} segundos")

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
        print("  • GET  /metrics - Métricas do sistema")
        print("")

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
    # Quando importado (para Gunicorn), inicializar configurações
    init_application()
