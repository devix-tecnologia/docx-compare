#!/usr/bin/env python3
"""
Processa versão do Directus fazendo diff e vinculação, salvando diretamente no banco.
Substitui a API Flask que está retornando null.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "tests"))

import re
import tempfile

from algoritmos.hibrido.algoritmo import AlgoritmoHibrido

from docx_utils import convert_docx_to_text
from processador_tags_modelo import PATTERN_REMOVER_TAGS
from repositorio import DirectusRepository


def processar_versao_direta(versao_id: str, directus_url: str, directus_token: str):
    """
    Processa uma versão fazendo diff e vinculação, salvando no banco.

    Args:
        versao_id: ID da versão
        directus_url: URL do Directus
        directus_token: Token de autenticação
    """
    print("=" * 80)
    print("🚀 PROCESSAMENTO DIRETO DE VERSÃO")
    print("=" * 80)
    print(f"Versão: {versao_id}")
    print(f"Directus: {directus_url}")
    print("=" * 80)

    repo = DirectusRepository(directus_url, directus_token)

    # 1. Buscar versão com dados nested
    print("\n📥 Buscando versão...")
    versao_data = repo.get_versao_para_processar(versao_id)

    if not versao_data:
        raise ValueError(f"Versão {versao_id} não encontrada")

    print("✅ Versão encontrada")

    # Extrair dados nested
    contrato_data = versao_data.get("contrato", {})
    modelo_data = contrato_data.get("modelo_contrato", {})
    tags_modelo = modelo_data.get("tags", [])

    # LÓGICA: Usar método centralizado do repositório
    # 1. Se existe versão anterior → comparar com versão anterior
    # 2. Se é primeira versão → comparar com modelo.arquivo_original
    print("\n🔍 Determinando arquivo original/anterior...")
    arquivo_modificado_id = versao_data.get("arquivo")
    arquivo_original_id = repo.get_arquivo_original(versao_data)
    arquivo_com_tags_id = modelo_data.get("arquivo_com_tags")

    print(f"📊 Contrato: {contrato_data.get('id')}")
    print(f"📊 Modelo: {modelo_data.get('id')}")
    print(f"📊 Tags: {len(tags_modelo)}")
    print(f"📊 Arquivo original: {arquivo_original_id}")
    print(f"📊 Arquivo modificado: {arquivo_modificado_id}")
    print(f"📊 Arquivo com tags: {arquivo_com_tags_id}")

    if not arquivo_original_id or not arquivo_modificado_id:
        raise ValueError("Versão sem arquivos configurados")

    # 2. Baixar e extrair textos
    print("\n📥 Baixando arquivos...")

    def baixar_e_extrair(arquivo_id: str) -> str:
        url = f"{directus_url}/assets/{arquivo_id}"
        import requests

        headers = {"Authorization": f"Bearer {directus_token}"}
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            raise ValueError(
                f"Erro ao baixar {arquivo_id}: HTTP {response.status_code}"
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            f.write(response.content)
            temp_path = f.name

        try:
            return convert_docx_to_text(temp_path)
        finally:
            os.unlink(temp_path)

    texto_original = baixar_e_extrair(arquivo_original_id)
    texto_modificado = baixar_e_extrair(arquivo_modificado_id)

    print(f"✅ Texto original: {len(texto_original)} caracteres")
    print(f"✅ Texto modificado: {len(texto_modificado)} caracteres")

    # Se tem arquivo_com_tags, usá-lo como base (sem tags) para coordenadas alinhadas
    if arquivo_com_tags_id:
        print("\n🔄 Usando arquivo_com_tags como base...")
        texto_com_tags = baixar_e_extrair(arquivo_com_tags_id)
        print(f"📊 Texto com tags: {len(texto_com_tags)} caracteres")

        # Remover marcações usando o padrão definido em PATTERN_REMOVER_TAGS
        # para garantir coordenadas alinhadas com processador_tags_modelo.py
        texto_original = re.sub(PATTERN_REMOVER_TAGS, "", texto_com_tags)
        print(f"✅ Texto original (sem tags): {len(texto_original)} caracteres")

    # 3. Fazer diff
    print("\n🔬 Gerando diff...")
    import difflib

    linhas_original = texto_original.splitlines()
    linhas_modificado = texto_modificado.splitlines()

    matcher = difflib.SequenceMatcher(None, linhas_original, linhas_modificado)

    modificacoes = []
    pos_original = 0
    pos_modificado = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # Atualizar posições
            for linha in linhas_original[i1:i2]:
                pos_original += len(linha) + 1  # +1 para \n
        elif tag == "replace":
            conteudo_original = "\n".join(linhas_original[i1:i2])
            conteudo_modificado = "\n".join(linhas_modificado[j1:j2])

            modificacoes.append(
                {
                    "categoria": "modificacao",
                    "conteudo": conteudo_original,
                    "alteracao": conteudo_modificado,
                    "posicao_inicio": pos_original,
                    "posicao_fim": pos_original + len(conteudo_original),
                }
            )

            pos_original += len(conteudo_original) + (i2 - i1)  # +newlines
        elif tag == "delete":
            conteudo = "\n".join(linhas_original[i1:i2])

            modificacoes.append(
                {
                    "categoria": "remocao",
                    "conteudo": conteudo,
                    "alteracao": "",
                    "posicao_inicio": pos_original,
                    "posicao_fim": pos_original + len(conteudo),
                }
            )

            pos_original += len(conteudo) + (i2 - i1)
        elif tag == "insert":
            conteudo = "\n".join(linhas_modificado[j1:j2])

            modificacoes.append(
                {
                    "categoria": "insercao",
                    "conteudo": "",
                    "alteracao": conteudo,
                    "posicao_inicio": pos_modificado,
                    "posicao_fim": pos_modificado + len(conteudo),
                }
            )

    print(f"✅ {len(modificacoes)} modificações encontradas")

    # 4. Extrair dados para algoritmo
    print("\n🏷️  Preparando dados para vinculação...")

    tags_data = []
    for tag in tags_modelo:
        tags_data.append(
            {
                "tag_nome": tag.get("tag_nome"),
                "texto": tag.get("conteudo", ""),  # Algoritmo espera "texto"
                "posicao_inicio": tag.get(
                    "posicao_inicio_texto", 0
                ),  # Algoritmo espera "posicao_inicio"
                "posicao_fim": tag.get(
                    "posicao_fim_texto", 0
                ),  # Algoritmo espera "posicao_fim"
                "clausula_id": tag.get("clausulas", [{}])[0].get("id")
                if tag.get("clausulas")
                else None,
            }
        )

    print(f"🔍 Debug: {len(tags_data)} tags preparadas")
    print(f"🔍 Debug: Primeira tag: {tags_data[0] if tags_data else 'Nenhuma'}")
    print(
        f"🔍 Debug: Primeira modificação: {modificacoes[0] if modificacoes else 'Nenhuma'}"
    )
    print(
        f"🔍 Debug: Tamanho texto_original usado no diff: {len(texto_original)} caracteres"
    )

    # 5. Executar algoritmo
    print("\n🔬 Executando algoritmo de vinculação...")
    algoritmo = AlgoritmoHibrido()

    # Calcular posições
    modificacoes_com_pos = algoritmo.calcular_posicoes(modificacoes, texto_original)

    # Vincular cláusulas
    modificacoes_vinculadas = algoritmo.vincular_clausulas(
        modificacoes_com_pos, tags_data, texto_original
    )

    vinculadas = sum(1 for m in modificacoes_vinculadas if m.get("tag_vinculada"))
    nao_vinculadas = len(modificacoes_vinculadas) - vinculadas
    taxa = (
        (vinculadas / len(modificacoes_vinculadas) * 100)
        if modificacoes_vinculadas
        else 0
    )

    print("✅ Vinculação concluída:")
    print(f"   Vinculadas: {vinculadas}/{len(modificacoes_vinculadas)} ({taxa:.1f}%)")

    # 6. Salvar modificações no Directus
    print("\n💾 Salvando modificações no Directus...")

    import requests

    headers = {
        "Authorization": f"Bearer {directus_token}",
        "Content-Type": "application/json",
    }

    salvas = 0
    erros = 0

    for mod in modificacoes_vinculadas:
        tag_vinculada = mod.get("tag_vinculada")
        clausula_id = tag_vinculada.get("clausula_id") if tag_vinculada else None

        dados_mod = {
            "versao": versao_id,
            "categoria": mod["categoria"],
            "conteudo": mod.get("conteudo", ""),
            "alteracao": mod.get("alteracao", ""),
            "posicao_inicio": mod.get("posicao_inicio"),
            "posicao_fim": mod.get("posicao_fim"),
            "clausula": clausula_id,
        }

        url = f"{directus_url}/items/modificacao"
        response = requests.post(url, headers=headers, json=dados_mod, timeout=10)

        if response.status_code in [200, 201]:
            salvas += 1
        else:
            erros += 1
            if erros <= 3:
                print(f"  ❌ Erro ao salvar modificação: HTTP {response.status_code}")

    print(f"✅ {salvas} modificações salvas")
    if erros > 0:
        print(f"⚠️  {erros} erros")

    # Relatório final
    print("\n" + "=" * 80)
    print("✅ PROCESSAMENTO CONCLUÍDO")
    print("=" * 80)
    print(f"Modificações totais: {len(modificacoes)}")
    print(f"Vinculadas: {vinculadas} ({taxa:.1f}%)")
    print(f"Não vinculadas: {nao_vinculadas}")
    print(f"Salvas no banco: {salvas}")

    return {
        "total": len(modificacoes),
        "vinculadas": vinculadas,
        "nao_vinculadas": nao_vinculadas,
        "taxa": taxa,
        "salvas": salvas,
        "erros": erros,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Processar versão diretamente")
    parser.add_argument("--versao", required=True, help="ID da versão")
    parser.add_argument(
        "--directus-url", default="http://localhost:8065", help="URL do Directus"
    )
    parser.add_argument(
        "--directus-token",
        default="pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP",
        help="Token do Directus",
    )

    args = parser.parse_args()

    try:
        resultado = processar_versao_direta(
            versao_id=args.versao,
            directus_url=args.directus_url,
            directus_token=args.directus_token,
        )

        if resultado["erros"] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# FUNÇÕES AUXILIARES PARA TESTES (sem Directus)
# ============================================================================


def processar_versao_com_tags(
    arquivo_original_bytes: bytes,
    arquivo_modificado_bytes: bytes,
    tags_modelo: list[dict],
) -> dict:
    """
    Processa versão localmente sem usar Directus (para testes).

    Args:
        arquivo_original_bytes: Bytes do arquivo DOCX original
        arquivo_modificado_bytes: Bytes do arquivo DOCX modificado
        tags_modelo: Lista de tags do modelo com posições mapeadas

    Returns:
        dict com resultado do processamento incluindo modificações vinculadas
    """
    import tempfile
    from pathlib import Path

    # Converter arquivos DOCX para texto
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(arquivo_original_bytes)
        tmp_original = tmp.name

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(arquivo_modificado_bytes)
        tmp_modificado = tmp.name

    try:
        # Extrair texto
        texto_original = convert_docx_to_text(tmp_original)
        texto_modificado = convert_docx_to_text(tmp_modificado)

        # Remover tags do texto original (se houver)
        texto_original = re.sub(PATTERN_REMOVER_TAGS, "", texto_original)

        print(f"📊 Texto original: {len(texto_original)} caracteres")
        print(f"📊 Texto modificado: {len(texto_modificado)} caracteres")

        # Fazer diff
        modificacoes = _fazer_diff_standalone(texto_original, texto_modificado)
        print(f"🔍 Encontradas {len(modificacoes)} modificações")

        # Calcular posições e vincular com algoritmo híbrido
        algoritmo = AlgoritmoHibrido()

        # Preparar tags no formato esperado pelo algoritmo
        tags_data = []
        for tag in tags_modelo:
            tags_data.append(
                {
                    "tag_nome": tag["tag_nome"],
                    "texto": tag["texto"],
                    "posicao_inicio": tag["posicao_inicio"],
                    "posicao_fim": tag["posicao_fim"],
                    "clausula_id": tag["clausula_id"],
                }
            )

        # Calcular posições das modificações
        modificacoes_com_pos = algoritmo.calcular_posicoes(modificacoes, texto_original)

        # Vincular com cláusulas
        modificacoes_vinculadas = algoritmo.vincular_clausulas(
            modificacoes_com_pos, tags_data, texto_original
        )

        total_vinculadas = len(
            [m for m in modificacoes_vinculadas if m.get("clausula_id")]
        )
        print(f"✅ Vinculadas: {total_vinculadas}/{len(modificacoes_vinculadas)}")

        return {
            "modificacoes": modificacoes_vinculadas,
            "texto_original": texto_original,
            "texto_modificado": texto_modificado,
            "total_tags": len(tags_data),
        }

    finally:
        # Limpar arquivos temporários
        Path(tmp_original).unlink(missing_ok=True)
        Path(tmp_modificado).unlink(missing_ok=True)


def _fazer_diff_standalone(texto_original: str, texto_modificado: str) -> list[dict]:
    """Faz diff entre dois textos e retorna modificações."""
    import difflib

    linhas_original = texto_original.splitlines(keepends=True)
    linhas_modificado = texto_modificado.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, linhas_original, linhas_modificado)
    modificacoes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            modificacoes.append(
                {
                    "categoria": "modificacao",
                    "conteudo": "".join(linhas_original[i1:i2]),
                    "alteracao": "".join(linhas_modificado[j1:j2]),
                }
            )
        elif tag == "insert":
            modificacoes.append(
                {
                    "categoria": "adicao",
                    "conteudo": "",
                    "alteracao": "".join(linhas_modificado[j1:j2]),
                }
            )
        elif tag == "delete":
            modificacoes.append(
                {
                    "categoria": "remocao",
                    "conteudo": "".join(linhas_original[i1:i2]),
                    "alteracao": "",
                }
            )

    return modificacoes
