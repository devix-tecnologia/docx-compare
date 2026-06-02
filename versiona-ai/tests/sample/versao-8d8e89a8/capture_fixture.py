#!/usr/bin/env python3
"""
Script para capturar dados reais do Directus e salvar como fixture.
Versão: 8d8e89a8-ba89-4e0e-846c-43e7ad058309
Modelo: 48b43d38-76b4-47a2-93a4-4216ad57defc
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from repositorio import DirectusRepository


def capture_fixture():
    """Captura dados da versão 8d8e89a8 e salva como fixture."""

    versao_id = "8d8e89a8-ba89-4e0e-846c-43e7ad058309"
    modelo_id = "48b43d38-76b4-47a2-93a4-4216ad57defc"
    
    directus_url = "https://contract.devix.co"
    directus_token = "pA7sDYtCMVBhX9jonHaOEM3ujcYtGNsg"

    print(f"🔍 Capturando dados da versão {versao_id}...")

    repo = DirectusRepository(directus_url, directus_token)

    try:
        # 1. Buscar dados da versão com deep parameters
        print("📥 Buscando dados da versão com tags...")
        versao_data = repo.get_versao_para_processar(versao_id)
        
        if not versao_data:
            raise ValueError(f"Versão {versao_id} não encontrada")
        
        # Extrair dados do modelo e tags
        contrato_data = versao_data.get("contrato", {})
        modelo_data = contrato_data.get("modelo_contrato", {}) if isinstance(contrato_data, dict) else {}
        tags_data = modelo_data.get("tags", [])
        
        print(f"   ✓ Tags encontradas: {len(tags_data)}")

        # 2. Baixar arquivos
        print("📥 Identificando arquivos...")
        
        # Arquivo modificado da versão
        arquivo_modificado_id = versao_data.get("arquivo")
        arquivo_modificado_url = f"{directus_url}/assets/{arquivo_modificado_id}" if arquivo_modificado_id else None
        
        # Arquivo com tags do modelo
        arquivo_com_tags_id = modelo_data.get("arquivo_com_tags")
        arquivo_com_tags_url = f"{directus_url}/assets/{arquivo_com_tags_id}" if arquivo_com_tags_id else None
        
        # Arquivo original do modelo (não da versão)
        arquivo_original_id = modelo_data.get("arquivo_original")
        arquivo_original_url = f"{directus_url}/assets/{arquivo_original_id}" if arquivo_original_id else None
        
        print(f"   ✓ Arquivo modificado: {arquivo_modificado_id}")
        print(f"   ✓ Arquivo original: {arquivo_original_id}")
        print(f"   ✓ Arquivo com tags: {arquivo_com_tags_id}")

        # 3. Buscar cláusulas do modelo
        print("📥 Buscando cláusulas...")
        clausulas = repo.get_clausulas_modelo(modelo_id)
        print(f"   ✓ Cláusulas encontradas: {len(clausulas)}")

        # 4. Salvar fixtures
        sample_dir = Path(__file__).parent

        print("\n💾 Salvando fixtures...")

        # 4.1 Metadata completo
        metadata = {
            "versao_id": versao_id,
            "modelo_id": modelo_id,
            "data_captura": datetime.now().isoformat(),
            "versao_data": versao_data,
            "modelo_data": modelo_data,
            "total_tags": len(tags_data),
            "total_clausulas": len(clausulas),
            "arquivos": {
                "arquivo_modificado": arquivo_modificado_id,
                "arquivo_original": arquivo_original_id,
                "arquivo_com_tags": arquivo_com_tags_id,
            },
            "urls": {
                "arquivo_modificado": arquivo_modificado_url,
                "arquivo_original": arquivo_original_url,
                "arquivo_com_tags": arquivo_com_tags_url,
            }
        }
        
        with open(sample_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print("   ✓ metadata.json")

        # 4.2 Tags do modelo
        with open(sample_dir / "tags_modelo.json", "w") as f:
            json.dump(tags_data, f, indent=2, ensure_ascii=False)
        print("   ✓ tags_modelo.json")

        # 4.3 Cláusulas
        with open(sample_dir / "clausulas.json", "w") as f:
            json.dump(clausulas, f, indent=2, ensure_ascii=False)
        print("   ✓ clausulas.json")

        # 4.4 Resumo para teste de regressão
        summary = {
            "versao_id": versao_id,
            "modelo_id": modelo_id,
            "data_captura": datetime.now().isoformat(),
            "metricas_esperadas": {
                "total_tags": len(tags_data),
                "total_clausulas": len(clausulas),
                "taxa_minima_vinculacao": 0.0,  # Baseline: atualmente 0%
                "nota_minima": 0.0,
            },
            "arquivos_gerados": [
                "metadata.json",
                "tags_modelo.json",
                "clausulas.json",
            ]
        }
        
        with open(sample_dir / "fixture_summary.json", "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print("   ✓ fixture_summary.json")

        print("\n✅ Fixtures capturadas com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Baixar os arquivos DOCX manualmente:")
        print(f"      - {arquivo_modificado_url}")
        print(f"      - {arquivo_original_url}")
        print(f"      - {arquivo_com_tags_url}")
        print("   2. Salvar no diretório tests/sample/versao-8d8e89a8/")
        print("   3. Criar teste de regressão test_regressao_versao_8d8e89a8.py")

    except Exception as e:
        print(f"\n❌ Erro ao capturar fixture: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    capture_fixture()
