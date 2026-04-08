#!/usr/bin/env python3
"""
Script para confirmar se reprocessamento substitui modificações ao invés de acumular.

Este script processa uma versão duas vezes e verifica se o número de modificações
permanece o mesmo (substitui) ou aumenta (acumula).

Uso:
    python scripts/confirma_reprocessamento_substitui.py <versao_id>

Exemplo:
    python scripts/confirma_reprocessamento_substitui.py 73b215cb-7e38-4e8c-80a7-4be90f21d654

Exit codes:
    0 - Reprocessamento SUBSTITUI modificações (comportamento esperado)
    1 - Reprocessamento ACUMULA modificações (comportamento incorreto)
    2 - Erro na execução ou argumentos inválidos
"""

import sys
import time
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "versiona-ai"))

from repositorio import DirectusRepository  # noqa: E402

import config  # noqa: E402


def processar_versao_api(versao_id: str, base_url: str) -> bool:
    """
    Aciona o processamento de uma versão via API.

    Args:
        versao_id: ID da versão
        base_url: URL base da API

    Returns:
        True se iniciou com sucesso, False caso contrário
    """
    import requests

    try:
        response = requests.post(
            f"{base_url}/api/process",
            json={"versao_id": versao_id, "use_ast": True},
            timeout=300,  # 5 minutos
        )

        if response.status_code in {200, 202}:
            print(f"✅ Processamento iniciado (status {response.status_code})")
            return True
        else:
            print(f"❌ Erro ao iniciar processamento: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Erro ao chamar API: {e}")
        return False


def aguardar_processamento(
    repo: DirectusRepository, versao_id: str, timeout: int = 300
) -> bool:
    """
    Aguarda até que o processamento seja concluído.

    Args:
        repo: Repositório do Directus
        versao_id: ID da versão
        timeout: Tempo máximo de espera em segundos

    Returns:
        True se concluiu, False se timeout
    """
    print("\n⏳ Aguardando conclusão do processamento...")

    inicio = time.time()
    ultimo_total = 0

    while (time.time() - inicio) < timeout:
        try:
            verificacao = repo.verificar_modificacoes_versao(versao_id)

            if verificacao["erro"]:
                print(f"   ⚠️  Erro na verificação: {verificacao['erro']}")
                time.sleep(5)
                continue

            total = verificacao["total_modificacoes"]

            if total > 0 and total != ultimo_total:
                print(f"   📝 Modificações encontradas: {total}")
                ultimo_total = total
                # Aguardar mais um pouco para garantir que terminou
                time.sleep(10)
                return True

            time.sleep(5)

        except Exception as e:
            print(f"   ⚠️  Erro: {e}")
            time.sleep(5)

    print(f"   ⏱️  Timeout após {timeout}s")
    return False


def comparar_processamentos(versao_id: str, api_base_url: str) -> int:
    """
    Compara dois processamentos da mesma versão.

    Args:
        versao_id: ID da versão
        api_base_url: URL base da API

    Returns:
        Exit code
    """
    print("\n" + "=" * 70)
    print("TESTE: REPROCESSAMENTO SUBSTITUI OU ACUMULA?")
    print("=" * 70)

    try:
        repo = DirectusRepository(
            base_url=config.DIRECTUS_BASE_URL, token=config.DIRECTUS_TOKEN
        )

        # 1. Verificar estado inicial
        print("\n📊 ETAPA 1: Verificando estado inicial...")
        inicial = repo.verificar_modificacoes_versao(versao_id)

        if inicial["erro"]:
            print(f"❌ Erro ao verificar estado inicial: {inicial['erro']}")
            return 2

        print(f"   Total modificações inicial: {inicial['total_modificacoes']}")

        if inicial["total_modificacoes"] == 0:
            print("\n⚠️  AVISO: Versão ainda não foi processada")
            print("   Processando pela primeira vez...")

            if not processar_versao_api(versao_id, api_base_url):
                return 2

            if not aguardar_processamento(repo, versao_id):
                print("\n❌ Timeout aguardando primeiro processamento")
                return 2

            # Atualizar contagem inicial
            inicial = repo.verificar_modificacoes_versao(versao_id)
            print(
                f"   Total modificações após 1º processamento: {inicial['total_modificacoes']}"
            )

        total_antes = inicial["total_modificacoes"]

        # 2. Processar novamente
        print("\n📊 ETAPA 2: Iniciando reprocessamento...")

        if not processar_versao_api(versao_id, api_base_url):
            return 2

        if not aguardar_processamento(repo, versao_id, timeout=300):
            print("\n❌ Timeout aguardando reprocessamento")
            return 2

        # 3. Comparar resultados
        print("\n📊 ETAPA 3: Comparando resultados...")
        final = repo.verificar_modificacoes_versao(versao_id)

        if final["erro"]:
            print(f"❌ Erro ao verificar estado final: {final['erro']}")
            return 2

        total_depois = final["total_modificacoes"]

        print(f"\n📈 Total modificações ANTES: {total_antes}")
        print(f"📈 Total modificações DEPOIS: {total_depois}")
        print(f"📊 Diferença: {total_depois - total_antes}")

        # 4. Conclusão
        print("\n" + "=" * 70)

        if total_depois == total_antes:
            print("✅ SUCESSO: Reprocessamento SUBSTITUI modificações!")
            print("   Comportamento correto - não acumula duplicatas")
            print("=" * 70)
            return 0
        elif total_depois > total_antes:
            print("❌ ERRO: Reprocessamento ACUMULA modificações!")
            print(
                f"   Foram adicionadas {total_depois - total_antes} modificações duplicadas"
            )
            print("=" * 70)
            return 1
        else:
            print("⚠️  AVISO: Reprocessamento REMOVEU modificações!")
            print(f"   Foram removidas {total_antes - total_depois} modificações")
            print("=" * 70)
            return 1

    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback

        traceback.print_exc()
        return 2


def main() -> int:
    """Função principal do script."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/confirma_reprocessamento_substitui.py <versao_id>")
        print("\nExemplo:")
        print(
            "  python scripts/confirma_reprocessamento_substitui.py 73b215cb-7e38-4e8c-80a7-4be90f21d654"
        )
        return 2

    versao_id = sys.argv[1].strip()

    if not versao_id:
        print("❌ ERRO: versao_id não pode ser vazio")
        return 2

    # URL da API (pode ser local ou produção)
    api_base_url = (
        config.API_BASE_URL
        if hasattr(config, "API_BASE_URL")
        else "http://localhost:5005"
    )

    print(f"🌐 Usando API: {api_base_url}")

    return comparar_processamentos(versao_id, api_base_url)


if __name__ == "__main__":
    sys.exit(main())
