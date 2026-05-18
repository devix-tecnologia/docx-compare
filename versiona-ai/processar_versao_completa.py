#!/usr/bin/env python3
"""
Script completo para processar versão no Directus com coordenadas corrigidas.
Segue a mesma lógica do directus_server.py mas de forma standalone.
"""

import re
import sys
from pathlib import Path

import requests
from rapidfuzz import fuzz
from repositorio import DirectusRepository

from docx_utils import convert_docx_to_text

DIRECTUS_URL = "http://localhost:8065"
DIRECTUS_TOKEN = "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"
VERSAO_ID = "2573b998-63d0-4471-ad85-db6f860c3721"


def extrair_modificacoes_do_diff_html(
    diff_html: str, texto_original: str, texto_modificado: str
):
    """Extrai modificações do HTML de diff com posições de caracteres."""
    modificacoes = []

    # Pattern para tags <ins> e <del>
    pattern = r"<(ins|del)>([^<]*)</\1>"
    matches = re.finditer(pattern, diff_html, re.DOTALL)

    for match in matches:
        tipo_tag = match.group(1)  # 'ins' ou 'del'
        texto = match.group(2).strip()

        if not texto:
            continue

        tipo_mod = None
        texto_orig = ""
        texto_mod = ""
        posicao_inicio = None
        posicao_fim = None

        if tipo_tag == "ins":
            # INSERCAO: buscar no texto modificado
            tipo_mod = "INSERCAO"
            texto_mod = texto
            pos = texto_modificado.find(texto)
            if pos != -1:
                posicao_inicio = pos
                posicao_fim = pos + len(texto)

        elif tipo_tag == "del":
            # REMOCAO: buscar no texto original
            tipo_mod = "REMOCAO"
            texto_orig = texto
            pos = texto_original.find(texto)
            if pos != -1:
                posicao_inicio = pos
                posicao_fim = pos + len(texto)

        if tipo_mod:
            modificacoes.append(
                {
                    "tipo": tipo_mod,
                    "posicao_inicio": posicao_inicio,
                    "posicao_fim": posicao_fim,
                    "texto_original": texto_orig,
                    "texto_modificado": texto_mod,
                }
            )

    return modificacoes


def vincular_modificacao_clausula(mod: dict, tags: list[dict], texto_original: str):
    """
    Vincula uma modificação a uma cláusula usando overlap + fuzzy matching.
    Lógica baseada no AlgoritmoProducao.
    """
    pos_inicio = mod.get("posicao_inicio")
    pos_fim = mod.get("posicao_fim")

    if pos_inicio is None or pos_fim is None:
        return None, None, None

    texto_mod = mod.get("texto_modificado") or mod.get("texto_original", "")
    if not texto_mod:
        return None, None, None

    melhor_tag = None
    melhor_score = 0
    melhor_metodo = None

    for tag in tags:
        tag_inicio = tag.get("posicao_inicio_texto")
        tag_fim = tag.get("posicao_fim_texto")

        if tag_inicio is None or tag_fim is None:
            continue

        # Calcular overlap
        inicio_intersecao = max(pos_inicio, tag_inicio)
        fim_intersecao = min(pos_fim, tag_fim)

        if inicio_intersecao >= fim_intersecao:
            overlap = 0
        else:
            tamanho_intersecao = fim_intersecao - inicio_intersecao
            tamanho_modificacao = pos_fim - pos_inicio
            overlap = (
                tamanho_intersecao / tamanho_modificacao
                if tamanho_modificacao > 0
                else 0
            )

        # Calcular fuzzy score
        tag_texto = tag.get("conteudo", "").strip()
        if not tag_texto:
            continue

        # 4 métricas do RapidFuzz
        score1 = fuzz.ratio(texto_mod, tag_texto)
        score2 = fuzz.partial_ratio(texto_mod, tag_texto)
        score3 = fuzz.token_sort_ratio(texto_mod, tag_texto)
        score4 = fuzz.token_set_ratio(texto_mod, tag_texto)
        fuzzy_score = (score1 + score2 + score3 + score4) / 4.0

        # Sistema de tiers (baseado no AlgoritmoProducao)
        selecionado = False
        metodo = None

        # Tier 1: Alta sobreposição + fuzzy razoável
        if overlap >= 0.90 and fuzzy_score >= 40:
            selecionado = True
            metodo = "tier1_overlap90_fuzzy40"
        # Tier 2: Boa sobreposição + fuzzy bom
        elif overlap >= 0.70 and fuzzy_score >= 60:
            selecionado = True
            metodo = "tier2_overlap70_fuzzy60"
        # Tier 3: Sobreposição moderada + fuzzy threshold
        elif overlap > 0.50 and fuzzy_score >= 80:
            selecionado = True
            metodo = "tier3_overlap50_fuzzy80"

        if selecionado:
            # Score combinado para desempate
            score_combinado = (overlap * 0.6) + (fuzzy_score / 100.0 * 0.4)

            if score_combinado > melhor_score:
                melhor_score = score_combinado
                melhor_tag = tag
                melhor_metodo = metodo

    if melhor_tag:
        return melhor_tag["id"], melhor_score, melhor_metodo

    return None, None, None


def processar_versao_completa():
    """Processa versão completa e salva resultados no Directus."""

    print("=" * 80)
    print("🚀 PROCESSAMENTO COMPLETO DA VERSÃO NO DIRECTUS")
    print("=" * 80)
    print(f"Versão: {VERSAO_ID}")
    print()

    # Conectar ao Directus
    repo = DirectusRepository(base_url=DIRECTUS_URL, token=DIRECTUS_TOKEN)

    # 1. Buscar dados da versão
    print("📥 Buscando versão com todos os dados...")
    versao_data = repo.get_versao_para_processar(VERSAO_ID)

    if not versao_data:
        print("❌ Versão não encontrada")
        return False

    # Extrair IDs
    arquivo_id = versao_data.get("arquivo")
    modifica_arquivo_id = versao_data.get("modifica_arquivo")
    contrato_data = versao_data.get("contrato", {})
    modelo_data = contrato_data.get("modelo_contrato", {})
    modelo_id = modelo_data.get("id")
    arquivo_com_tags_id = modelo_data.get("arquivo_com_tags")
    tags_nested = modelo_data.get("tags", [])

    print(f"✅ Versão: {VERSAO_ID}")
    print(f"✅ Contrato: {contrato_data.get('id')}")
    print(f"✅ Modelo: {modelo_id}")
    print(f"✅ Tags nested: {len(tags_nested)}")
    print(f"✅ Arquivo com tags: {arquivo_com_tags_id}")
    print()

    # 2. Baixar arquivos
    print("📥 Baixando arquivos...")
    temp_dir = Path("/tmp/processar_completo")
    temp_dir.mkdir(exist_ok=True)

    arquivo_original = temp_dir / f"original_{arquivo_id}.docx"
    arquivo_modificado = temp_dir / f"modificado_{modifica_arquivo_id}.docx"
    arquivo_com_tags = temp_dir / f"com_tags_{arquivo_com_tags_id}.docx"

    repo.download_file(arquivo_id, arquivo_original)
    repo.download_file(modifica_arquivo_id, arquivo_modificado)
    repo.download_file(arquivo_com_tags_id, arquivo_com_tags)

    print("✅ Baixados 3 arquivos")
    print()

    # 3. Extrair textos
    print("📖 Extraindo textos...")
    texto_original = convert_docx_to_text(str(arquivo_original))
    texto_modificado = convert_docx_to_text(str(arquivo_modificado))
    texto_com_tags = convert_docx_to_text(str(arquivo_com_tags))

    # Remover marcações do texto_com_tags para ter mesma coordenada do diff
    texto_original_limpo = re.sub(r"\{\{/?TAG-[^}]+\}\}", "", texto_com_tags)
    texto_original_limpo = re.sub(r"\{\{/?[^}]+\}\}", "", texto_original_limpo)

    print(f"✅ Original: {len(texto_original)} caracteres")
    print(f"✅ Modificado: {len(texto_modificado)} caracteres")
    print(f"✅ Com tags: {len(texto_com_tags)} caracteres")
    print(f"✅ Original limpo (sem tags): {len(texto_original_limpo)} caracteres")
    print()

    # 4. Gerar diff usando difflib
    print("🔍 Gerando diff com difflib...")
    from difflib import SequenceMatcher

    matcher = SequenceMatcher(None, texto_original_limpo, texto_modificado)
    modificacoes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            # MODIFICACAO
            modificacoes.append(
                {
                    "tipo": "MODIFICACAO",
                    "posicao_inicio": i1,
                    "posicao_fim": i2,
                    "texto_original": texto_original_limpo[i1:i2],
                    "texto_modificado": texto_modificado[j1:j2],
                }
            )
        elif tag == "delete":
            # REMOCAO
            modificacoes.append(
                {
                    "tipo": "REMOCAO",
                    "posicao_inicio": i1,
                    "posicao_fim": i2,
                    "texto_original": texto_original_limpo[i1:i2],
                    "texto_modificado": "",
                }
            )
        elif tag == "insert":
            # INSERCAO - buscar posição no texto modificado
            modificacoes.append(
                {
                    "tipo": "INSERCAO",
                    "posicao_inicio": j1,
                    "posicao_fim": j2,
                    "texto_original": "",
                    "texto_modificado": texto_modificado[j1:j2],
                }
            )

    print(f"✅ {len(modificacoes)} modificações extraídas")
    print()

    # 5. Vincular modificações às cláusulas
    print("🧮 Vinculando modificações às cláusulas...")
    vinculadas = 0
    nao_vinculadas = 0

    for mod in modificacoes:
        clausula_id, score, metodo = vincular_modificacao_clausula(
            mod, tags_nested, texto_original_limpo
        )

        mod["clausula_id"] = clausula_id
        mod["score"] = score
        mod["metodo_vinculacao"] = metodo

        if clausula_id:
            vinculadas += 1
        else:
            nao_vinculadas += 1

    total = len(modificacoes)
    taxa = (vinculadas / total * 100) if total > 0 else 0

    print(f"✅ Vinculação concluída: {vinculadas}/{total} ({taxa:.1f}%)")
    print()

    # 6. Salvar modificações no Directus via API
    print(f"💾 Salvando {len(modificacoes)} modificações no Directus...")

    headers = {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}",
        "Content-Type": "application/json",
    }

    salvos = 0
    erros = 0

    for mod in modificacoes:
        payload = {
            "versao": VERSAO_ID,
            "tipo": mod["tipo"],
            "posicao_inicio": mod.get("posicao_inicio"),
            "posicao_fim": mod.get("posicao_fim"),
            "texto_original": mod.get("texto_original", ""),
            "texto_modificado": mod.get("texto_modificado", ""),
            "clausula": mod.get("clausula_id"),
            "score": mod.get("score"),
            "metodo_vinculacao": mod.get("metodo_vinculacao"),
        }

        try:
            response = requests.post(
                f"{DIRECTUS_URL}/items/modificacao",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if response.status_code in [200, 201]:
                salvos += 1
            else:
                erros += 1
                if erros <= 3:  # Mostrar apenas os 3 primeiros erros
                    print(
                        f"⚠️ Erro ao salvar modificação: {response.status_code} - {response.text[:100]}"
                    )

        except Exception as e:
            erros += 1
            if erros <= 3:
                print(f"⚠️ Exceção ao salvar: {e}")

    print(f"✅ Salvos: {salvos}/{total}")
    if erros > 0:
        print(f"❌ Erros: {erros}/{total}")
    print()

    # 7. Reportar resultados finais
    print("=" * 80)
    print("📊 RESULTADOS FINAIS")
    print("=" * 80)
    print(f"Total de modificações: {total}")
    print(f"✅ Vinculadas: {vinculadas} ({taxa:.1f}%)")
    print(
        f"❌ Não vinculadas: {nao_vinculadas} ({(nao_vinculadas / total * 100):.1f}%)"
    )
    print(f"💾 Salvos no Directus: {salvos}/{total}")
    print()
    print(f"🎯 TAXA DE VINCULAÇÃO ALCANÇADA: {taxa:.1f}%")
    print("=" * 80)

    # Limpar arquivos temporários
    arquivo_original.unlink(missing_ok=True)
    arquivo_modificado.unlink(missing_ok=True)
    arquivo_com_tags.unlink(missing_ok=True)

    return True


if __name__ == "__main__":
    try:
        processar_versao_completa()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
