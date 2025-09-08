#!/usr/bin/env python3
"""
Utilidades para integração com Directus
Módulo comum para evitar duplicação de código entre os arquivos do projeto
"""

import os
import tempfile
import uuid
from datetime import datetime
from typing import Literal

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DIRECTUS_BASE_URL = (
    os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
    .replace("/admin/", "")
    .rstrip("/")
)
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "your-directus-token")

# Headers para requisições HTTP
DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}

# Timeout padrão para requisições
DEFAULT_REQUEST_TIMEOUT = 30


def buscar_versoes_para_processar(
    verbose_mode=False, request_timeout=DEFAULT_REQUEST_TIMEOUT
):
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

            # Query com filtros usando query parameters - campos corretos
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
                "limit": 10,
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
    file_id: str,
    cache_dir: str | None = None,
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
) -> tuple[str, Literal["downloaded", "cached"]]:
    """
    Baixa um arquivo do Directus usando o caminho do arquivo.
    Verifica cache para evitar downloads desnecessários.

    Args:
        file_id: ID do arquivo no Directus
        cache_dir: Diretório para cache (opcional)
        request_timeout: Timeout das requisições em segundos

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


def upload_file_to_directus(
    file_path,
    filename=None,
    dry_run=False,
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
):
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
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
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
                result_file_path, filename, dry_run, request_timeout
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
