#!/usr/bin/env python3
"""
CLI para operações de processamento e verificação de versões.

Este CLI centraliza as operações mais comuns de processamento e verificação,
permitindo automação e integração com outros scripts.

Uso:
    python versiona_cli.py <comando> [argumentos]

Comandos disponíveis:
    processa <versao_id> [--use-ast]
        Processa uma versão e retorna o resultado

    verifica <versao_id>
        Verifica se uma versão foi processada corretamente

    reprocessa <versao_id>
        Reprocessa uma versão e compara com estado anterior

    resumo <versao_id>
        Exibe resumo detalhado do processamento

Exemplos:
    python versiona_cli.py processa 73b215cb-7e38-4e8c-80a7-4be90f21d654
    python versiona_cli.py verifica 73b215cb-7e38-4e8c-80a7-4be90f21d654
    python versiona_cli.py reprocessa 73b215cb-7e38-4e8c-80a7-4be90f21d654 --use-ast
    python versiona_cli.py resumo 73b215cb-7e38-4e8c-80a7-4be90f21d654

Exit codes:
    0 - Sucesso
    1 - Erro na operação (processamento falhou, versão sem modificações, etc)
    2 - Erro de argumentos ou uso incorreto
    3 - Erro inesperado (exception)
"""

import argparse
import sys
import time
from pathlib import Path

# Adicionar versiona-ai ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "versiona-ai"))

from repositorio import DirectusRepository

import config


def processar_versao(
    versao_id: str, use_ast: bool = True, api_base_url: str | None = None
) -> dict:
    """
    Processa uma versão via API e aguarda conclusão.

    Args:
        versao_id: ID da versão
        use_ast: Se deve usar AST no processamento
        api_base_url: URL base da API (None = usar config)

    Returns:
        dict com:
            - sucesso: bool
            - total_modificacoes: int
            - tempo_espera: float (segundos)
            - erro: str | None
    """
    import requests

    if api_base_url is None:
        api_base_url = getattr(config, "API_BASE_URL", "http://localhost:5005")

    print(f"\n🚀 Iniciando processamento da versão {versao_id}...")
    print(f"   API: {api_base_url}")
    print(f"   use_ast: {use_ast}")

    try:
        # Iniciar processamento
        inicio = time.time()

        response = requests.post(
            f"{api_base_url}/api/process",
            json={"versao_id": versao_id, "use_ast": use_ast},
            timeout=300,
        )

        if response.status_code not in {200, 202}:
            return {
                "sucesso": False,
                "total_modificacoes": 0,
                "tempo_espera": 0,
                "erro": f"API retornou status {response.status_code}: {response.text[:200]}",
            }

        print("   ✅ Processamento iniciado")

        # Aguardar conclusão
        repo = DirectusRepository(
            base_url=config.DIRECTUS_BASE_URL, token=config.DIRECTUS_TOKEN
        )

        print("   ⏳ Aguardando conclusão...")

        timeout = 300
        ultimo_total = 0

        while (time.time() - inicio) < timeout:
            verificacao = repo.verificar_modificacoes_versao(versao_id)

            if verificacao["erro"]:
                print(f"      ⚠️  Erro: {verificacao['erro']}")
                time.sleep(5)
                continue

            total = verificacao["total_modificacoes"]

            if total > 0 and total != ultimo_total:
                print(f"      📝 Modificações: {total}")
                ultimo_total = total
                time.sleep(10)  # Aguardar estabilização

                # Confirmar que não está mais mudando
                verificacao2 = repo.verificar_modificacoes_versao(versao_id)
                if verificacao2["total_modificacoes"] == total:
                    tempo_total = time.time() - inicio
                    print(f"   ✅ Processamento concluído em {tempo_total:.1f}s")

                    return {
                        "sucesso": True,
                        "total_modificacoes": total,
                        "tempo_espera": tempo_total,
                        "erro": None,
                    }

            time.sleep(5)

        return {
            "sucesso": False,
            "total_modificacoes": ultimo_total,
            "tempo_espera": time.time() - inicio,
            "erro": f"Timeout após {timeout}s",
        }

    except Exception as e:
        return {
            "sucesso": False,
            "total_modificacoes": 0,
            "tempo_espera": 0,
            "erro": str(e),
        }


def verificar_versao(versao_id: str) -> dict:
    """
    Verifica o estado de processamento de uma versão.

    Args:
        versao_id: ID da versão

    Returns:
        dict com:
            - sucesso: bool (True se tem modificações)
            - status: str
            - total_modificacoes: int
            - erro: str | None
    """
    print(f"\n🔍 Verificando versão {versao_id}...")

    try:
        repo = DirectusRepository(
            base_url=config.DIRECTUS_BASE_URL, token=config.DIRECTUS_TOKEN
        )

        verificacao = repo.verificar_modificacoes_versao(versao_id)

        if verificacao["erro"]:
            return {
                "sucesso": False,
                "status": "error",
                "total_modificacoes": 0,
                "erro": verificacao["erro"],
            }

        return {
            "sucesso": verificacao["sucesso"],
            "status": verificacao["status_versao"],
            "total_modificacoes": verificacao["total_modificacoes"],
            "erro": None,
        }

    except Exception as e:
        return {
            "sucesso": False,
            "status": "error",
            "total_modificacoes": 0,
            "erro": str(e),
        }


def reprocessar_e_comparar(versao_id: str, use_ast: bool = True) -> dict:
    """
    Reprocessa uma versão e compara com estado anterior.

    Args:
        versao_id: ID da versão
        use_ast: Se deve usar AST

    Returns:
        dict com:
            - sucesso: bool (True se substituiu corretamente)
            - total_antes: int
            - total_depois: int
            - substituiu: bool
            - erro: str | None
    """
    print(f"\n🔄 Reprocessando versão {versao_id}...")

    try:
        repo = DirectusRepository(
            base_url=config.DIRECTUS_BASE_URL, token=config.DIRECTUS_TOKEN
        )

        # Estado antes
        antes = repo.verificar_modificacoes_versao(versao_id)

        if antes["erro"]:
            return {
                "sucesso": False,
                "total_antes": 0,
                "total_depois": 0,
                "substituiu": False,
                "erro": f"Erro ao verificar estado anterior: {antes['erro']}",
            }

        total_antes = antes["total_modificacoes"]
        print(f"   📊 Total modificações antes: {total_antes}")

        # Reprocessar
        resultado = processar_versao(versao_id, use_ast)

        if not resultado["sucesso"]:
            return {
                "sucesso": False,
                "total_antes": total_antes,
                "total_depois": 0,
                "substituiu": False,
                "erro": resultado["erro"],
            }

        total_depois = resultado["total_modificacoes"]
        print(f"   📊 Total modificações depois: {total_depois}")

        substituiu = total_depois == total_antes

        if substituiu:
            print("   ✅ Reprocessamento SUBSTITUIU modificações (correto)")
        else:
            print(
                f"   ❌ Reprocessamento {'ACUMULOU' if total_depois > total_antes else 'REMOVEU'} modificações"
            )

        return {
            "sucesso": substituiu,
            "total_antes": total_antes,
            "total_depois": total_depois,
            "substituiu": substituiu,
            "erro": None
            if substituiu
            else "Modificações não foram substituídas corretamente",
        }

    except Exception as e:
        return {
            "sucesso": False,
            "total_antes": 0,
            "total_depois": 0,
            "substituiu": False,
            "erro": str(e),
        }


def exibir_resumo(versao_id: str) -> dict:
    """
    Exibe resumo detalhado do processamento.

    Args:
        versao_id: ID da versão

    Returns:
        dict com:
            - sucesso: bool
            - resumo: dict (se sucesso)
            - erro: str | None
    """
    print(f"\n📊 Buscando resumo da versão {versao_id}...")

    try:
        repo = DirectusRepository(
            base_url=config.DIRECTUS_BASE_URL, token=config.DIRECTUS_TOKEN
        )

        resumo = repo.get_resumo_processamento_versao(versao_id)

        print("\n" + "=" * 70)
        print(f"RESUMO: {resumo['versao_id']}")
        print("=" * 70)
        print(f"\n📊 Status: {resumo['status']}")
        print(f"📅 Data: {resumo['data_processamento'] or 'N/A'}")
        print(f"📝 Total Modificações: {resumo['total_modificacoes']}")
        print(f"🔗 Com Cláusula: {resumo['modificacoes_com_clausula']}")
        print(f"📈 Taxa Vinculação: {resumo['taxa_vinculacao']}%")

        if resumo["modificacoes_por_categoria"]:
            print("\n📂 Por Categoria:")
            for cat, count in sorted(resumo["modificacoes_por_categoria"].items()):
                print(f"   - {cat}: {count}")

        print("\n" + "=" * 70)

        return {"sucesso": True, "resumo": resumo, "erro": None}

    except Exception as e:
        return {"sucesso": False, "resumo": {}, "erro": str(e)}


def main() -> int:
    """Função principal do CLI."""
    parser = argparse.ArgumentParser(
        description="CLI para processamento e verificação de versões",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "comando",
        choices=["processa", "verifica", "reprocessa", "resumo"],
        help="Comando a executar",
    )

    parser.add_argument("versao_id", help="ID da versão (UUID)")

    parser.add_argument(
        "--use-ast",
        action="store_true",
        default=True,
        help="Usar AST no processamento (padrão: True)",
    )

    parser.add_argument(
        "--no-ast", action="store_true", help="Não usar AST no processamento"
    )

    parser.add_argument(
        "--api-url",
        help="URL base da API (padrão: config.API_BASE_URL ou localhost:5005)",
    )

    args = parser.parse_args()

    use_ast = args.use_ast and not args.no_ast
    versao_id = args.versao_id.strip()

    if not versao_id:
        print("❌ ERRO: versao_id não pode ser vazio")
        return 2

    try:
        if args.comando == "processa":
            resultado = processar_versao(versao_id, use_ast, args.api_url)
            print(f"\n{'✅ SUCESSO' if resultado['sucesso'] else '❌ ERRO'}")
            print(f"Total Modificações: {resultado['total_modificacoes']}")
            if resultado["erro"]:
                print(f"Erro: {resultado['erro']}")
            return 0 if resultado["sucesso"] else 1

        elif args.comando == "verifica":
            resultado = verificar_versao(versao_id)
            print(f"\n{'✅ SUCESSO' if resultado['sucesso'] else '❌ ERRO'}")
            print(f"Status: {resultado['status']}")
            print(f"Total Modificações: {resultado['total_modificacoes']}")
            if resultado["erro"]:
                print(f"Erro: {resultado['erro']}")
            return 0 if resultado["sucesso"] else 1

        elif args.comando == "reprocessa":
            resultado = reprocessar_e_comparar(versao_id, use_ast)
            print(f"\n{'✅ SUCESSO' if resultado['sucesso'] else '❌ ERRO'}")
            print(
                f"Antes: {resultado['total_antes']} | Depois: {resultado['total_depois']}"
            )
            print(f"Substituiu: {'Sim' if resultado['substituiu'] else 'Não'}")
            if resultado["erro"]:
                print(f"Erro: {resultado['erro']}")
            return 0 if resultado["sucesso"] else 1

        elif args.comando == "resumo":
            resultado = exibir_resumo(versao_id)
            return 0 if resultado["sucesso"] else 1

        else:
            print(f"❌ Comando desconhecido: {args.comando}")
            return 2

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        return 3
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback

        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
