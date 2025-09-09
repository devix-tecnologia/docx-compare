#!/usr/bin/env python3
"""
Script para testar o agrupamento de modificações por capítulo
"""

import importlib.util
import os
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

# Carregar configurações diretamente do config.py
config_path = os.path.join(os.path.dirname(__file__), "config.py")
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

from src.docx_compare.utils.agrupador_modificacoes_v2 import AgrupadorModificacoes


def main():
    """Função principal para teste do agrupador"""

    print("🎯 Teste do Agrupador de Modificações por Capítulo")
    print("=" * 60)

    # Inicializar agrupador
    agrupador = AgrupadorModificacoes(
        directus_base_url=config.DIRECTUS_BASE_URL,
        directus_token=config.DIRECTUS_TOKEN
    )

    # Solicitar ID da versão
    versao_id = input("\n📝 Digite o ID da versão para agrupar modificações: ").strip()

    if not versao_id:
        print("❌ ID da versão é obrigatório")
        return

    # Perguntar sobre threshold de similaridade
    threshold_input = input("🎚️ Threshold de similaridade (0.0-1.0, padrão 0.6): ").strip()
    try:
        threshold = float(threshold_input) if threshold_input else 0.6
        if threshold < 0 or threshold > 1:
            threshold = 0.6
    except ValueError:
        threshold = 0.6

    # Perguntar sobre dry-run
    dry_run_input = input("🏃‍♂️ Executar em modo dry-run? (s/N): ").strip().lower()
    dry_run = dry_run_input in ["s", "sim", "y", "yes"]

    print("\n⚙️ Configuração:")
    print(f"   📋 Versão ID: {versao_id}")
    print(f"   🎚️ Threshold: {threshold}")
    print(f"   🏃‍♂️ Dry-run: {'Sim' if dry_run else 'Não'}")

    # Executar agrupamento
    print(f"\n{'🏃‍♂️ EXECUTANDO EM MODO DRY-RUN' if dry_run else '🚀 EXECUTANDO AGRUPAMENTO'}")
    print("-" * 60)

    resultado = agrupador.processar_agrupamento_versao(
        versao_id=versao_id,
        threshold=threshold,
        dry_run=dry_run
    )

    if "erro" in resultado:
        print(f"\n❌ Erro no processamento: {resultado['erro']}")
        return

    # Mostrar resultado detalhado
    print("\n📊 RESULTADO FINAL:")
    print("-" * 30)
    print(f"📝 Total de modificações: {resultado.get('total_modificacoes', 0)}")
    print(f"✅ Associações {'simuladas' if dry_run else 'criadas'}: {resultado.get('associacoes_criadas', 0)}")
    print(f"❌ Associações falharam: {resultado.get('associacoes_falharam', 0)}")
    print(f"🔍 Modificações sem correspondência: {resultado.get('modificacoes_sem_correspondencia', 0)}")

    # Mostrar detalhes se houver
    detalhes = resultado.get("detalhes", [])
    if detalhes:
        print("\n📋 DETALHES DAS ASSOCIAÇÕES:")
        print("-" * 40)

        for i, detalhe in enumerate(detalhes[:10], 1):  # Mostrar apenas as 10 primeiras
            status = detalhe.get("status", "N/A")
            mod_id = detalhe.get("modificacao_id", "N/A")
            tag_nome = detalhe.get("tag_nome", "N/A")
            clausula_nome = detalhe.get("clausula_nome", "N/A")
            score = detalhe.get("score", 0.0)

            status_emoji = {
                "associada": "✅",
                "dry_run": "🏃‍♂️",
                "falha_associacao": "❌",
                "sem_clausula": "⚠️",
                "sem_correspondencia": "🔍"
            }.get(status, "❓")

            print(f"{i:2d}. {status_emoji} Modificação {mod_id}")
            if tag_nome != "N/A":
                print(f"     📌 Tag: {tag_nome}")
            if clausula_nome:
                print(f"     📋 Cláusula: {clausula_nome}")
            if score > 0:
                print(f"     🎯 Score: {score:.2f}")
            print()

        if len(detalhes) > 10:
            print(f"... e mais {len(detalhes) - 10} modificações")

    # Perguntar se quer listar agrupamentos após o processamento
    if not dry_run and resultado.get("associacoes_criadas", 0) > 0:
        listar_input = input("\n📋 Deseja listar os agrupamentos atuais da versão? (s/N): ").strip().lower()
        if listar_input in ["s", "sim", "y", "yes"]:
            print(f"\n📋 LISTANDO AGRUPAMENTOS ATUAIS DA VERSÃO {versao_id}")
            print("=" * 60)

            agrupamentos = agrupador.listar_agrupamentos_versao(versao_id)

            if "erro" not in agrupamentos:
                # Mostrar agrupamentos por cláusula
                for _clausula_id, info in agrupamentos.get("agrupamentos", {}).items():
                    clausula_nome = info.get("clausula_nome", "N/A")
                    clausula_numero = info.get("clausula_numero", "N/A")
                    modificacoes = info.get("modificacoes", [])

                    print(f"\n📋 Cláusula {clausula_numero}: {clausula_nome}")
                    print(f"     ({len(modificacoes)} modificações)")

                    for mod in modificacoes[:3]:  # Mostrar apenas as 3 primeiras
                        categoria = mod.get("categoria", "N/A")
                        conteudo = mod.get("conteudo", "")[:60] + "..." if len(mod.get("conteudo", "")) > 60 else mod.get("conteudo", "")
                        print(f"     • [{categoria}] {conteudo}")

                    if len(modificacoes) > 3:
                        print(f"     ... e mais {len(modificacoes) - 3} modificações")

                # Mostrar modificações sem cláusula
                sem_clausula = agrupamentos.get("sem_clausula", [])
                if sem_clausula:
                    print(f"\n🔍 Modificações sem cláusula ({len(sem_clausula)}):")
                    for mod in sem_clausula[:5]:  # Mostrar apenas as 5 primeiras
                        categoria = mod.get("categoria", "N/A")
                        conteudo = mod.get("conteudo", "")[:60] + "..." if len(mod.get("conteudo", "")) > 60 else mod.get("conteudo", "")
                        print(f"     • [{categoria}] {conteudo}")

                    if len(sem_clausula) > 5:
                        print(f"     ... e mais {len(sem_clausula) - 5} modificações")

    print("\n✨ Processamento concluído!")

if __name__ == "__main__":
    main()
