"""
Teste de integração: Comparação AST vs Original usando API Flask

Este script testa ambas as implementações via API Flask e compara resultados.

Uso:
    # Iniciar servidor Flask (em outro terminal)
    uv run python versiona-ai/directus_server.py

    # Executar teste
    uv run python versiona-ai/test_api_ast_vs_original.py
"""

import json

import requests

# Configuração da API
API_URL = "http://localhost:8001/api/process"

# IDs para teste (substitua pelos seus IDs reais)
VERSAO_ID_TESTE = "322e56c0-4b38-4e62-b563-8f29a131889c"


def testar_implementacao_original(versao_id: str) -> dict:
    """Testa implementação original (texto plano)"""
    print("=" * 100)
    print("📊 TESTE 1: Implementação Original (Texto Plano - 51.9% precisão)")
    print("=" * 100)

    payload = {"versao_id": versao_id, "mock": False, "use_ast": False}

    response = requests.post(API_URL, json=payload, timeout=60)

    if response.status_code != 200:
        print(f"❌ Erro: HTTP {response.status_code}")
        print(f"Resposta: {response.text}")
        return {}

    resultado = response.json()

    modificacoes = resultado.get("modificacoes", [])
    metricas = resultado.get("metricas", {})

    print("\n✅ Processamento concluído!")
    print(f"Total de modificações: {len(modificacoes)}")

    # Contar tipos
    tipos = {}
    for mod in modificacoes:
        tipo = mod.get("tipo", "DESCONHECIDO")
        tipos[tipo] = tipos.get(tipo, 0) + 1

    print("\n📊 Distribuição por tipo:")
    for tipo, count in tipos.items():
        print(f"  - {tipo}: {count}")

    if metricas:
        print("\n📈 Métricas:")
        print(f"  {json.dumps(metricas, indent=2)}")

    return resultado


def testar_implementacao_ast(versao_id: str) -> dict:
    """Testa implementação AST (Pandoc - 59.3% precisão)"""
    print("\n" + "=" * 100)
    print("📊 TESTE 2: Implementação AST (Pandoc - 59.3% precisão)")
    print("=" * 100)

    payload = {"versao_id": versao_id, "mock": False, "use_ast": True}

    response = requests.post(API_URL, json=payload, timeout=60)

    if response.status_code != 200:
        print(f"❌ Erro: HTTP {response.status_code}")
        print(f"Resposta: {response.text}")
        return {}

    resultado = response.json()

    modificacoes = resultado.get("modificacoes", [])
    metricas = resultado.get("metricas", {})

    print("\n✅ Processamento AST concluído!")
    print(f"Total de modificações: {len(modificacoes)}")

    # Contar tipos
    tipos = {}
    for mod in modificacoes:
        tipo = mod.get("tipo", "DESCONHECIDO")
        tipos[tipo] = tipos.get(tipo, 0) + 1

    print("\n📊 Distribuição por tipo:")
    for tipo, count in tipos.items():
        print(f"  - {tipo}: {count}")

    if metricas:
        print("\n📈 Métricas:")
        print(f"  {json.dumps(metricas, indent=2)}")

    return resultado


def comparar_resultados(resultado_original: dict, resultado_ast: dict):
    """Compara resultados das duas implementações"""
    print("\n" + "=" * 100)
    print("🔬 COMPARAÇÃO: AST vs Original")
    print("=" * 100)

    mods_original = resultado_original.get("modificacoes", [])
    mods_ast = resultado_ast.get("modificacoes", [])

    print("\nTotal de modificações:")
    print(f"  Original: {len(mods_original)}")
    print(f"  AST: {len(mods_ast)}")
    print(f"  Diferença: {len(mods_ast) - len(mods_original):+d}")

    # Comparar tipos
    tipos_original = {}
    for mod in mods_original:
        tipo = mod.get("tipo", "DESCONHECIDO")
        tipos_original[tipo] = tipos_original.get(tipo, 0) + 1

    tipos_ast = {}
    for mod in mods_ast:
        tipo = mod.get("tipo", "DESCONHECIDO")
        tipos_ast[tipo] = tipos_ast.get(tipo, 0) + 1

    print("\n📊 Comparação por tipo:")
    print(f"{'Tipo':<15} {'Original':<12} {'AST':<12} {'Diferença'}")
    print("-" * 60)

    todos_tipos = set(tipos_original.keys()) | set(tipos_ast.keys())
    for tipo in sorted(todos_tipos):
        count_orig = tipos_original.get(tipo, 0)
        count_ast = tipos_ast.get(tipo, 0)
        diff = count_ast - count_orig
        print(
            f"{tipo:<15} {count_orig:<12} {count_ast:<12} {diff:+d}"
        )

    # Análise de vantagens
    print("\n🎯 Análise:")

    if len(mods_ast) > len(mods_original):
        print(f"  ✅ AST detectou {len(mods_ast) - len(mods_original)} modificações a mais")
    elif len(mods_ast) < len(mods_original):
        print(
            f"  ⚠️ AST detectou {len(mods_original) - len(mods_ast)} modificações a menos"
        )
    else:
        print("  ℹ️ Ambos detectaram o mesmo número de modificações")

    # Verificar detecção de REMOCAO e INSERCAO
    if tipos_ast.get("REMOCAO", 0) > tipos_original.get("REMOCAO", 0):
        print(
            f"  ✅ AST detectou {tipos_ast['REMOCAO']} REMOÇÕES (Original: {tipos_original.get('REMOCAO', 0)})"
        )

    if tipos_ast.get("INSERCAO", 0) > tipos_original.get("INSERCAO", 0):
        print(
            f"  ✅ AST detectou {tipos_ast['INSERCAO']} INSERÇÕES (Original: {tipos_original.get('INSERCAO', 0)})"
        )

    print("\n🏆 Recomendação:")
    if (
        len(mods_ast) > len(mods_original)
        or tipos_ast.get("REMOCAO", 0) > 0
        or tipos_ast.get("INSERCAO", 0) > 0
    ):
        print("  ✅ Use AST (use_ast=true) para melhor precisão e detecção de tipos")
    else:
        print(
            "  ℹ️ Ambas as implementações tiveram desempenho similar neste documento"
        )


def main():
    """Executa teste comparativo completo"""
    print("🚀 TESTE COMPARATIVO: API Flask - AST vs Original")
    print("=" * 100)
    print(f"Versão ID: {VERSAO_ID_TESTE}")
    print(f"API URL: {API_URL}")
    print()

    try:
        # Testar implementação original
        resultado_original = testar_implementacao_original(VERSAO_ID_TESTE)

        # Testar implementação AST
        resultado_ast = testar_implementacao_ast(VERSAO_ID_TESTE)

        # Comparar resultados
        if resultado_original and resultado_ast:
            comparar_resultados(resultado_original, resultado_ast)

        print("\n" + "=" * 100)
        print("✅ TESTE COMPLETO!")
        print("=" * 100)

    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API Flask")
        print("Certifique-se de que o servidor está rodando:")
        print("  uv run python versiona-ai/directus_server.py")
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
