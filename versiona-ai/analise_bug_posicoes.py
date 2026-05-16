"""
Análise do BUG CRÍTICO: Incompatibilidade de referências de posição.

PROBLEMA FUNDAMENTAL:
- Tags têm posições no TEXTO ORIGINAL (antes das modificações)
- Modificações são calculadas no TEXTO MODIFICADO (após as modificações)
- Baseline usa str.find() no texto modificado e compara com posições das tags
- Resultado: vinculações ERRADAS por overlap falso!

CENÁRIO PROBLEMÁTICO:
1. Texto original: "Cláusula 1. Cláusula 2."
   Tag 1: pos 0-11 (texto original)
   Tag 2: pos 12-23 (texto original)

2. Após INSERCAO "Preâmbulo. " no início:
   Texto modificado: "Preâmbulo. Cláusula 1. Cláusula 2."
   "Preâmbulo." está em pos 0-11 (texto modificado)
   "Cláusula 1." está em pos 12-23 (texto modificado) ← DESLOCADO!

3. Baseline calcula:
   mod_1 "Preâmbulo." = pos 0-11 (texto modificado)
   Compara com tag_1 pos 0-11 (texto ORIGINAL)
   Overlap = 100%! ← FALSO POSITIVO!

SOLUÇÃO:
Opção A: Recalcular posições das tags no texto modificado (complexo)
Opção B: Não usar overlap se posições são do texto original (atual baseline)
Opção C: Usar APENAS fuzzy matching sem posições (mais robusto)
"""

import sys
from pathlib import Path
tests_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_dir))

from algoritmos.producao.algoritmo import AlgoritmoProducao


def test_bug_incompatibilidade_posicoes():
    """
    Demonstra o bug de incompatibilidade entre:
    - Posições das tags (texto original)
    - Posições das modificações (texto modificado)
    """
    alg = AlgoritmoProducao()
    
    # Texto ORIGINAL (usado para posições das tags)
    texto_original = "Cláusula 1. Cláusula 2."
    
    # Texto MODIFICADO (usado pelo baseline para str.find)
    texto_modificado = "Preâmbulo. Cláusula 1. Cláusula 2."
    
    # Tags com posições do TEXTO ORIGINAL
    tags = [
        {
            "id": "tag_1",
            "titulo": "Cláusula 1",
            "texto": "Cláusula 1.",
            "posicao_inicio": 0,   # No texto ORIGINAL
            "posicao_fim": 11,     # No texto ORIGINAL
        },
        {
            "id": "tag_2",
            "titulo": "Cláusula 2",
            "texto": "Cláusula 2.",
            "posicao_inicio": 12,  # No texto ORIGINAL
            "posicao_fim": 23,     # No texto ORIGINAL
        },
    ]
    
    # Modificações
    modificacoes = [
        {
            "id": "mod_1",
            "tipo": "INSERCAO",
            "conteudo": {"novo": "Preâmbulo. "},
        },
    ]
    
    # Baseline usa texto_modificado para str.find()
    resultado = alg.vincular_clausulas(modificacoes, tags, texto_modificado)
    
    print("\n" + "=" * 80)
    print("ANÁLISE DO BUG")
    print("=" * 80)
    
    print(f"\nTexto original:   '{texto_original}'")
    print(f"Texto modificado: '{texto_modificado}'")
    
    print(f"\nTag 1 posições (texto original): {tags[0]['posicao_inicio']}-{tags[0]['posicao_fim']}")
    print(f"Tag 1 no original:   '{texto_original[0:11]}'")
    print(f"Tag 1 no modificado: '{texto_modificado[0:11]}'  ← DIFERENTE!")
    
    print(f"\nModificação calculada em: {resultado[0].get('posicao_inicio')}-{resultado[0].get('posicao_fim')}")
    print(f"Modificação no modificado: '{texto_modificado[0:11]}'")
    
    print(f"\nTag vinculada: {resultado[0].get('tag_vinculada', {}).get('titulo', 'None')}")
    
    if resultado[0].get('tag_vinculada'):
        print("\n❌ BUG CONFIRMADO!")
        print("   'Preâmbulo.' vinculou a 'Cláusula 1' por overlap falso!")
        print("   Posições são de referências diferentes (original vs modificado)")
    else:
        print("\n✅ Bug corrigido! Não vinculou por overlap falso.")
    
    print("=" * 80)


def test_solucao_apenas_fuzzy():
    """
    Solução: Usar APENAS fuzzy matching, ignorar posições.
    
    Mais robusto pois não depende de posições de referências diferentes.
    """
    alg = AlgoritmoProducao()
    
    texto_modificado = "Preâmbulo. Cláusula 1. Cláusula 2."
    
    tags = [
        {
            "id": "tag_1",
            "titulo": "Cláusula 1",
            "texto": "Cláusula 1.",
            "posicao_inicio": 0,
            "posicao_fim": 11,
        },
    ]
    
    modificacoes = [
        {
            "id": "mod_1",
            "tipo": "INSERCAO",
            "conteudo": {"novo": "Preâmbulo. "},
        },
    ]
    
    resultado = alg.vincular_clausulas(modificacoes, tags, texto_modificado)
    
    # Com fuzzy matching puro:
    # "Preâmbulo." vs "Cláusula 1." = ~30% similarity ← Abaixo do threshold
    # Não deve vincular
    
    print("\n" + "=" * 80)
    print("TESTE: Fuzzy matching puro (sem posições)")
    print("=" * 80)
    
    from rapidfuzz import fuzz
    score = fuzz.token_set_ratio("Preâmbulo. ", "Cláusula 1.")
    print(f"\nSimilaridade 'Preâmbulo.' vs 'Cláusula 1.': {score:.1f}%")
    print(f"Threshold: 90% (texto curto)")
    print(f"Vincularia? {score >= 90}")
    
    if not resultado[0].get('tag_vinculada'):
        print("\n✅ Correto! Não vinculou por fuzzy baixo.")
    else:
        print(f"\n❌ Vinculou errado a: {resultado[0]['tag_vinculada']['titulo']}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_bug_incompatibilidade_posicoes()
    test_solucao_apenas_fuzzy()
