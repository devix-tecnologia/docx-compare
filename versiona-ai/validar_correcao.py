#!/usr/bin/env python3
"""
Script para validar a correção das coordenadas processando localmente
e reportando a taxa de vinculação sem salvar no banco.
"""

import sys
from pathlib import Path

from docx_utils import analyze_differences, convert_docx_to_text
from repositorio import DirectusRepository
from tests.algoritmos.producao.algoritmo import AlgoritmoProducao


def validar_correcao(versao_id: str):
    """Valida correção processando localmente e reportando taxa"""

    print("=" * 80)
    print("🔬 VALIDAÇÃO DA CORREÇÃO DE COORDENADAS")
    print("=" * 80)
    print(f"Versão: {versao_id}")
    print()

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

    # 2. Buscar tags do modelo
    print("📥 Buscando tags do modelo...")
    tags_modelo = repo.get_clausulas_modelo(
        modelo_id,
        fields=["id", "nome", "posicao_inicio_texto", "posicao_fim_texto", "conteudo"],
    )
    print(f"✅ {len(tags_modelo)} tags encontradas")
    print()

    # 3. Baixar arquivos
    print("📥 Baixando arquivos...")
    temp_dir = Path("/tmp/validacao_correcao")
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

    for mod in modificacoes:
        resultado = algoritmo.vincular_modificacao(mod)
        if resultado["clausula_id"]:
            vinculadas += 1
        else:
            nao_vinculadas += 1

    total = len(modificacoes)
    taxa = (vinculadas / total * 100) if total > 0 else 0

    # 7. Reportar resultados
    print()
    print("=" * 80)
    print("📊 RESULTADOS DA VALIDAÇÃO")
    print("=" * 80)
    print(f"Total de modificações: {total}")
    print(f"✅ Vinculadas: {vinculadas} ({vinculadas / total * 100:.1f}%)")
    print(f"❌ Não vinculadas: {nao_vinculadas} ({nao_vinculadas / total * 100:.1f}%)")
    print()
    print(f"🎯 Taxa de vinculação: {taxa:.1f}%")
    print("=" * 80)

    # Limpar arquivos temporários
    arquivo_original.unlink(missing_ok=True)
    arquivo_modificado.unlink(missing_ok=True)

    return True


if __name__ == "__main__":
    versao_id = "2573b998-63d0-4471-ad85-db6f860c3721"

    try:
        validar_correcao(versao_id)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
