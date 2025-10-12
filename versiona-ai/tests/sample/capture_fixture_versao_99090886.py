#!/usr/bin/env python3
"""
Script para capturar dados reais do Directus e salvar como fixture.
Versão: 99090886-7f43-45c9-bfe4-ec6eddd6cde0
"""

import json
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from directus_server import DirectusService


def capture_fixture():
    """Captura dados da versão 99090886 e salva como fixture."""

    versao_id = "99090886-7f43-45c9-bfe4-ec6eddd6cde0"

    print(f"🔍 Capturando dados da versão {versao_id}...")

    service = DirectusService()

    try:
        # 1. Buscar dados da versão
        print("📥 Buscando dados da versão...")
        versao_data = service.get_versao(versao_id)

        # 2. Buscar modificações
        print("📥 Buscando modificações...")
        modificacoes = service.get_modificacoes(versao_id)

        # 3. Buscar contrato e modelo
        print("📥 Buscando contrato e modelo...")
        contrato_id = versao_data["contrato"]
        contrato_data = service.directus.items("contratos").read(contrato_id)

        # 4. Baixar arquivos
        print("📥 Baixando arquivos...")

        # Arquivo modificado
        arquivo_modificado_id = versao_data["arquivo"]
        modified_bytes = service.directus.files.read(arquivo_modificado_id)

        # Arquivo com tags do modelo
        modelo_id = contrato_data["modelo_contrato"]
        modelo_data = service.directus.items("modelos_contrato").read(modelo_id)
        arquivo_com_tags_id = modelo_data["arquivo_com_tags"]
        tagged_bytes = service.directus.files.read(arquivo_com_tags_id)

        # 5. Processar e obter resultado
        print("⚙️  Processando versão...")
        resultado = service.process_version(versao_id)

        # 6. Salvar fixtures
        sample_dir = Path(__file__).parent

        print("💾 Salvando fixtures...")

        # Salvar metadados da versão
        with open(sample_dir / "versao_99090886_metadata.json", "w") as f:
            json.dump(
                {
                    "versao_id": versao_id,
                    "versao_data": versao_data,
                    "contrato_data": contrato_data,
                    "modelo_data": modelo_data,
                    "total_modificacoes": len(modificacoes),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        # Salvar modificações
        with open(sample_dir / "versao_99090886_modificacoes.json", "w") as f:
            json.dump(modificacoes, f, indent=2, ensure_ascii=False)

        # Salvar resultado esperado (métricas de vinculação)
        with open(sample_dir / "versao_99090886_resultado_esperado.json", "w") as f:
            json.dump(
                {
                    "vinculacao_metrics": resultado.get("vinculacao_metrics", {}),
                    "total_blocos": resultado.get("total_blocos", 0),
                    "metodo_usado": resultado.get("vinculacao_metrics", {}).get(
                        "metodo_usado", ""
                    ),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        # Salvar arquivos binários
        with open(sample_dir / "versao_99090886_arquivo_modificado.docx", "wb") as f:
            f.write(modified_bytes)

        with open(sample_dir / "versao_99090886_arquivo_com_tags.docx", "wb") as f:
            f.write(tagged_bytes)

        print("\n✅ Fixtures capturadas com sucesso!")
        print(f"📊 Total de modificações: {len(modificacoes)}")
        print("📈 Métricas de vinculação:")
        metrics = resultado.get("vinculacao_metrics", {})
        print(
            f"   - Vinculadas: {metrics.get('vinculadas', 0)}/{len(modificacoes)} ({metrics.get('taxa_sucesso', 0):.1f}%)"
        )
        print(f"   - Revisão manual: {metrics.get('revisao_manual', 0)}")
        print(f"   - Não vinculadas: {metrics.get('nao_vinculadas', 0)}")
        print(f"   - Taxa de cobertura: {metrics.get('taxa_cobertura', 0):.1f}%")
        print(f"   - Método usado: {metrics.get('metodo_usado', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ Erro ao capturar fixture: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = capture_fixture()
    sys.exit(0 if success else 1)
