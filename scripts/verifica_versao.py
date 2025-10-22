#!/usr/bin/env python3
"""
Script para verificar o estado de processamento de uma versão no Directus.

Uso:
    python scripts/verifica_versao.py <versao_id>

Exemplo:
    python scripts/verifica_versao.py 73b215cb-7e38-4e8c-80a7-4be90f21d654

Exit codes:
    0 - Versão processada com sucesso e possui modificações
    1 - Versão não possui modificações ou erro na consulta
    2 - Argumentos inválidos
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "versiona-ai"))

from repositorio import DirectusRepository

import config


def print_resumo(resumo: dict) -> None:
    """Imprime o resumo de forma formatada e legível."""
    print("\n" + "=" * 70)
    print(f"RESUMO DO PROCESSAMENTO DA VERSÃO: {resumo['versao_id']}")
    print("=" * 70)

    print(f"\n📊 STATUS: {resumo['status']}")
    print(f"📅 Data Processamento: {resumo['data_processamento'] or 'N/A'}")
    print(f"📝 Total Modificações: {resumo['total_modificacoes']}")
    print(f"🔗 Modificações com Cláusula: {resumo['modificacoes_com_clausula']}")
    print(f"📈 Taxa de Vinculação: {resumo['taxa_vinculacao']}%")

    if resumo["modificacoes_por_categoria"]:
        print("\n📂 Por Categoria:")
        for categoria, count in sorted(resumo["modificacoes_por_categoria"].items()):
            print(f"   - {categoria}: {count}")

    if resumo["modificacoes_sample"]:
        print("\n🔍 Amostra de Modificações (primeiras 3):")
        for i, mod in enumerate(resumo["modificacoes_sample"], 1):
            print(f"   {i}. ID: {mod['id']}")
            print(f"      Categoria: {mod.get('categoria', 'N/A')}")
            print(f"      Cláusula: {mod.get('clausula') or 'Sem vinculação'}")
            print(
                f"      Posição: {mod.get('posicao_inicio', '?')} - {mod.get('posicao_fim', '?')}"
            )

    print("\n" + "=" * 70)


def verificar_versao(versao_id: str) -> int:
    """
    Verifica o estado de processamento de uma versão.

    Args:
        versao_id: ID da versão no Directus

    Returns:
        Exit code (0 = sucesso, 1 = erro)
    """
    try:
        # Criar repositório
        repo = DirectusRepository(
            base_url=config.DIRECTUS_BASE_URL, token=config.DIRECTUS_TOKEN
        )

        print(f"\n🔍 Consultando versão {versao_id}...")

        # Verificação rápida primeiro
        verificacao = repo.verificar_modificacoes_versao(versao_id)

        if verificacao["erro"]:
            print(f"\n❌ ERRO: {verificacao['erro']}")
            return 1

        if not verificacao["sucesso"]:
            print("\n⚠️  AVISO: Versão não possui modificações registradas")
            print(f"   Status: {verificacao['status_versao']}")
            print(f"   Total Modificações: {verificacao['total_modificacoes']}")
            return 1

        # Buscar resumo completo
        resumo = repo.get_resumo_processamento_versao(versao_id)
        print_resumo(resumo)

        # Avaliar sucesso
        if resumo["total_modificacoes"] > 0:
            print("\n✅ SUCESSO: Versão processada corretamente!")
            return 0
        else:
            print("\n❌ ERRO: Versão sem modificações")
            return 1

    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    """Função principal do script."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/verifica_versao.py <versao_id>")
        print("\nExemplo:")
        print(
            "  python scripts/verifica_versao.py 73b215cb-7e38-4e8c-80a7-4be90f21d654"
        )
        return 2

    versao_id = sys.argv[1].strip()

    if not versao_id:
        print("❌ ERRO: versao_id não pode ser vazio")
        return 2

    return verificar_versao(versao_id)


if __name__ == "__main__":
    sys.exit(main())
