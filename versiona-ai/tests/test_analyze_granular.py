"""
Teste rápido da função analyze_differences_granular
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from docx_utils import analyze_differences_granular


def test_detecta_alteracao_simples():
    """Testa detecção de alteração simples (30 dias → 15 dias)"""
    original = "O prazo será de 30 dias corridos."
    modificado = "O prazo será de 15 dias corridos."

    resultado = analyze_differences_granular(original, modificado)

    modificacoes = resultado["modificacoes"]
    estatisticas = resultado["estatisticas"]

    print(f"\n✅ Total modificações: {estatisticas['total_modificacoes']}")
    print(f"   Por tipo: {estatisticas['por_tipo']}")

    # Deve detectar pelo menos 1 modificação
    assert len(modificacoes) > 0, "Deveria detectar pelo menos 1 modificação"

    # Pelo menos uma deve ser ALTERACAO
    tipos = [mod["tipo"] for mod in modificacoes]
    assert "ALTERACAO" in tipos, (
        f"Deveria ter ALTERACAO, mas tem: {estatisticas['por_tipo']}"
    )

    print("\n📋 Modificações detectadas:")
    for i, mod in enumerate(modificacoes, 1):
        print(
            f"{i}. {mod['tipo']}: {mod['conteudo'].get('original', '')} → {mod['conteudo'].get('novo', '')}"
        )

    print("\n✅ Teste passou!")


def test_detecta_multiplas_alteracoes():
    """Testa detecção de múltiplas alterações no mesmo parágrafo"""
    original = "A CONTRATADA prestará serviços conforme QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO."
    modificado = "A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO e nas ordens de serviço emitidas pela CONTRATANTE."

    resultado = analyze_differences_granular(original, modificado)

    modificacoes = resultado["modificacoes"]
    estatisticas = resultado["estatisticas"]

    print(f"\n✅ Total modificações: {estatisticas['total_modificacoes']}")
    print(f"   Por tipo: {estatisticas['por_tipo']}")

    # Deve detectar alterações/inserções
    assert len(modificacoes) >= 1, "Deveria detectar modificações"

    print("\n📋 Modificações detectadas:")
    for i, mod in enumerate(modificacoes, 1):
        orig = mod["conteudo"].get("original", "")[:50]
        novo = mod["conteudo"].get("novo", "")[:50]
        print(f"{i}. {mod['tipo']}: '{orig}...' → '{novo}...'")

    print("\n✅ Teste passou!")


def test_detecta_insercao_no_meio():
    """Testa detecção de inserção no meio do texto"""
    original = "Este contrato estabelece as condições gerais."
    modificado = (
        "Este contrato estabelece as condições gerais e específicas de prestação."
    )

    resultado = analyze_differences_granular(original, modificado)

    modificacoes = resultado["modificacoes"]
    estatisticas = resultado["estatisticas"]

    print(f"\n✅ Total modificações: {estatisticas['total_modificacoes']}")
    print(f"   Por tipo: {estatisticas['por_tipo']}")

    # Deve detectar pelo menos 1 inserção
    assert estatisticas["por_tipo"].get("INSERCAO", 0) >= 1, "Deveria detectar INSERCAO"

    print("\n📋 Modificações detectadas:")
    for i, mod in enumerate(modificacoes, 1):
        print(f"{i}. {mod['tipo']}: {mod['conteudo']}")

    print("\n✅ Teste passou!")


if __name__ == "__main__":
    test_detecta_alteracao_simples()
    test_detecta_multiplas_alteracoes()
    test_detecta_insercao_no_meio()

    print("\n" + "=" * 80)
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("=" * 80)
