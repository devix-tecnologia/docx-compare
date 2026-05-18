#!/usr/bin/env python3
"""
Script simplificado para processar versão com tags do JSON exportado.
"""

import json
import subprocess
import sys
from pathlib import Path

from repositorio import DirectusRepository

from docx_utils import analyze_differences, convert_docx_to_text
from tests.algoritmos.producao.algoritmo import AlgoritmoProducao


def processar_com_tags_json(versao_id: str, tags_json_path: str):
    """Processa versão usando tags de arquivo JSON"""

    print("=" * 80)
    print("🚀 PROCESSAMENTO COM COORDENADAS CORRIGIDAS")
    print("=" * 80)
    print(f"Versão: {versao_id}")
    print()

    # Conectar ao Directus
    repo = DirectusRepository(
        base_url="http://localhost:8065", token="pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"
    )

    # 1. Carregar tags do JSON
    print("📥 Carregando tags do JSON...")
    with open(tags_json_path) as f:
        content = f.read().strip()
        tags_modelo = json.loads(content)

    print(f"✅ {len(tags_modelo)} tags carregadas")
    print()

    # 2. Buscar dados da versão
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

    # Preparar SQL INSERT
    inserts = []

    for mod in modificacoes:
        resultado = algoritmo.vincular_modificacao(mod)

        clausula_id = resultado["clausula_id"]
        if clausula_id:
            vinculadas += 1
        else:
            nao_vinculadas += 1

        # Escapar valores para SQL
        texto_orig = mod.get("texto_original", "").replace("'", "''")
        texto_mod = mod.get("texto_modificado", "").replace("'", "''")
        metodo = (
            resultado.get("metodo_vinculacao", "").replace("'", "''")
            if resultado.get("metodo_vinculacao")
            else None
        )

        clausula_sql = f"'{clausula_id}'" if clausula_id else "NULL"
        score_sql = str(resultado.get("score")) if resultado.get("score") else "NULL"
        metodo_sql = f"'{metodo}'" if metodo else "NULL"

        insert = f"""('{versao_id}', '{mod.get("tipo")}', {mod.get("posicao_inicio")}, {mod.get("posicao_fim")}, '{texto_orig}', '{texto_mod}', {clausula_sql}, {score_sql}, {metodo_sql})"""
        inserts.append(insert)

    # 7. Salvar no banco via SQL
    print(f"💾 Salvando {len(inserts)} modificações no banco...")

    sql_insert = f"""
INSERT INTO modificacao (versao, tipo, posicao_inicio, posicao_fim, texto_original, texto_modificado, clausula, score, metodo_vinculacao)
VALUES {", ".join(inserts)};
"""

    # Executar via docker exec
    result = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "e2e-ui-postgres",
            "psql",
            "-U",
            "directus",
            "-d",
            "directus",
        ],
        input=sql_insert,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ Modificações salvas com sucesso")
    else:
        print(f"❌ Erro ao salvar: {result.stderr}")
        return False

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
    arquivo_original.unlink(missing_ok=True)
    arquivo_modificado.unlink(missing_ok=True)

    return True


if __name__ == "__main__":
    versao_id = "2573b998-63d0-4471-ad85-db6f860c3721"
    tags_json = "/tmp/tags_modelo.json"

    try:
        processar_com_tags_json(versao_id, tags_json)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
