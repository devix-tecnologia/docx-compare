#!/usr/bin/env python3
"""
Script para processar versão com coordenadas corrigidas,
buscando tags diretamente do banco e salvando resultados.
"""

import sys
from pathlib import Path

import psycopg2

from docx_utils import analyze_differences, convert_docx_to_text
from repositorio import DirectusRepository
from tests.algoritmos.producao.algoritmo import AlgoritmoProducao


def processar_e_salvar(versao_id: str):
    """Processa versão com coordenadas corrigidas e salva no banco"""

    print("=" * 80)
    print("🚀 PROCESSAMENTO COM COORDENADAS CORRIGIDAS")
    print("=" * 80)
    print(f"Versão: {versao_id}")
    print()

    # Conectar ao banco
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="directus",
        password="directus",
        database="directus",
    )
    cur = conn.cursor()

    # Conectar ao Directus
    repo = DirectusRepository(
        base_url="http://localhost:8065", token="pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"
    )

    # 1. Buscar dados da versão
    print("📥 Buscando dados da versão...")
    versao_data = repo.get_versao_para_processar(versao_id)

    if not versao_data:
        print("❌ Versão não encontrada")
        return False

    arquivo_id = versao_data.get("arquivo")
    modifica_arquivo_id = versao_data.get("modifica_arquivo")
    contrato_id = versao_data["contrato"]["id"]
    modelo_id = versao_data["contrato"]["modelo_contrato"]["id"]

    print(f"✅ Contrato: {contrato_id}")
    print(f"✅ Modelo: {modelo_id}")
    print()

    # 2. Buscar tags do banco
    print("📥 Buscando tags do banco...")
    cur.execute(
        """
        SELECT id, nome, posicao_inicio_texto, posicao_fim_texto, conteudo
        FROM clausula
        WHERE modelo_contrato = %s
        ORDER BY posicao_inicio_texto
    """,
        (modelo_id,),
    )

    tags_raw = cur.fetchall()
    tags_modelo = [
        {
            "id": row[0],
            "nome": row[1],
            "posicao_inicio_texto": row[2],
            "posicao_fim_texto": row[3],
            "conteudo": row[4],
        }
        for row in tags_raw
    ]

    print(f"✅ {len(tags_modelo)} tags encontradas")
    print()

    # 3. Baixar arquivos
    print("📥 Baixando arquivos...")
    temp_dir = Path("/tmp/processar_correcao")
    temp_dir.mkdir(exist_ok=True)

    arquivo_original = temp_dir / f"original_{arquivo_id}.docx"
    arquivo_modificado = temp_dir / f"modificado_{modifica_arquivo_id}.docx"

    repo.download_file(arquivo_id, arquivo_original)
    repo.download_file(modifica_arquivo_id, arquivo_modificado)

    print(f"✅ Original: {arquivo_original}")
    print(f"✅ Modificado: {arquivo_modificado}")
    print()

    # 4. Extrair textos
    print("📖 Extraindo textos...")
    texto_original = convert_docx_to_text(str(arquivo_original))
    texto_modificado = convert_docx_to_text(str(arquivo_modificado))

    print(f"✅ Original: {len(texto_original)} caracteres")
    print(f"✅ Modificado: {len(texto_modificado)} caracteres")
    print()

    # 5. Gerar diff
    print("🔍 Gerando diff...")
    diff_result = analyze_differences(texto_original, texto_modificado)
    modificacoes = diff_result.get("modificacoes", [])
    print(f"✅ {len(modificacoes)} modificações detectadas")
    print()

    # 6. Aplicar algoritmo
    print("🧮 Aplicando algoritmo de vinculação...")
    algoritmo = AlgoritmoProducao(
        texto_original=texto_original, tags_modelo=tags_modelo
    )

    vinculadas = 0
    nao_vinculadas = 0

    # Preparar para inserção em batch
    modificacoes_para_inserir = []

    for mod in modificacoes:
        resultado = algoritmo.vincular_modificacao(mod)

        clausula_id = resultado["clausula_id"]
        if clausula_id:
            vinculadas += 1
        else:
            nao_vinculadas += 1

        modificacoes_para_inserir.append(
            (
                versao_id,
                mod.get("tipo"),
                mod.get("posicao_inicio"),
                mod.get("posicao_fim"),
                mod.get("texto_original", ""),
                mod.get("texto_modificado", ""),
                clausula_id,
                resultado.get("score"),
                resultado.get("metodo_vinculacao"),
            )
        )

    # 7. Salvar no banco
    print(f"💾 Salvando {len(modificacoes_para_inserir)} modificações no banco...")

    insert_query = """
        INSERT INTO modificacao (
            versao, tipo, posicao_inicio, posicao_fim,
            texto_original, texto_modificado,
            clausula, score, metodo_vinculacao
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cur.executemany(insert_query, modificacoes_para_inserir)
    conn.commit()

    print(f"✅ {cur.rowcount} modificações salvas")
    print()

    # 8. Reportar resultados
    total = len(modificacoes)
    taxa = (vinculadas / total * 100) if total > 0 else 0

    print("=" * 80)
    print("📊 RESULTADOS FINAIS")
    print("=" * 80)
    print(f"Total de modificações: {total}")
    print(f"✅ Vinculadas: {vinculadas} ({vinculadas / total * 100:.1f}%)")
    print(f"❌ Não vinculadas: {nao_vinculadas} ({nao_vinculadas / total * 100:.1f}%)")
    print()
    print(f"🎯 Taxa de vinculação alcançada: {taxa:.1f}%")
    print("=" * 80)

    # Limpar
    cur.close()
    conn.close()
    arquivo_original.unlink(missing_ok=True)
    arquivo_modificado.unlink(missing_ok=True)

    return True


if __name__ == "__main__":
    versao_id = "2573b998-63d0-4471-ad85-db6f860c3721"

    try:
        processar_e_salvar(versao_id)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
