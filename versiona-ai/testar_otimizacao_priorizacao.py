#!/usr/bin/env python3
"""
Teste da otimização: INSERCAO + REMOCAO → ALTERACAO
"""

from directus_server import SemanticGroupingConfig, _group_modifications_semantically


def test_insercao_remocao_vira_alteracao():
    """Testa se grupo com INSERCAO + REMOCAO vira ALTERACAO."""
    
    mods = [
        {
            "tipo": "REMOCAO",
            "conteudo": {"original": "texto antigo removido"},
            "posicao": {"linha": 10},
            "clausula_original": "1.1",
        },
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "texto novo inserido"},
            "posicao": {"linha": 11},
            "clausula_modificada": "1.1",
        },
    ]
    
    config = SemanticGroupingConfig(
        max_distance=1000,  # Agrupar tudo
        min_modification_size=1,
        require_same_clause=True,
        require_same_type=False,  # Permitir tipos diferentes
    )
    
    result = _group_modifications_semantically(mods, config)
    
    print(f"\n{'='*60}")
    print("TESTE: INSERCAO + REMOCAO → ALTERACAO")
    print(f"{'='*60}")
    print(f"Antes: 2 modificações")
    print(f"  - 1 REMOCAO")
    print(f"  - 1 INSERCAO")
    print(f"\nDepois: {len(result)} modificação(ões)")
    if result:
        print(f"  - Tipo: {result[0].get('tipo')}")
        print(f"  - Agrupadas: {result[0].get('modificacoes_agrupadas', 0)}")
    
    assert len(result) == 1, f"Esperava 1 modificação, got {len(result)}"
    assert result[0].get("tipo") == "ALTERACAO", f"Esperava ALTERACAO, got {result[0].get('tipo')}"
    assert result[0].get("modificacoes_agrupadas") == 2
    
    print(f"\n✅ PASSOU: Grupo INSERCAO+REMOCAO virou ALTERACAO!\n")


def test_apenas_insercao_continua_insercao():
    """Testa se grupo com apenas INSERCAO continua INSERCAO."""
    
    mods = [
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "texto novo 1"},
            "posicao": {"linha": 10},
            "clausula_modificada": "1.1",
        },
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "texto novo 2"},
            "posicao": {"linha": 11},
            "clausula_modificada": "1.1",
        },
    ]
    
    config = SemanticGroupingConfig(
        max_distance=1000,
        min_modification_size=1,
        require_same_clause=True,
        require_same_type=False,
    )
    
    result = _group_modifications_semantically(mods, config)
    
    print(f"\n{'='*60}")
    print("TESTE: Apenas INSERCAO → continua INSERCAO")
    print(f"{'='*60}")
    print(f"Antes: 2 INSERCAOes")
    print(f"Depois: {len(result)} modificação, tipo: {result[0].get('tipo') if result else 'N/A'}")
    
    assert len(result) == 1
    assert result[0].get("tipo") == "INSERCAO"
    
    print(f"✅ PASSOU: Grupo puro de INSERCAO continua INSERCAO!\n")


def test_alteracao_com_outros_continua_alteracao():
    """Testa se grupo com ALTERACAO + outros continua ALTERACAO."""
    
    mods = [
        {
            "tipo": "ALTERACAO",
            "conteudo": {"original": "antigo", "novo": "novo"},
            "posicao": {"linha": 10},
            "clausula_original": "1.1",
            "clausula_modificada": "1.1",
        },
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "texto novo"},
            "posicao": {"linha": 11},
            "clausula_modificada": "1.1",
        },
        {
            "tipo": "REMOCAO",
            "conteudo": {"original": "texto removido"},
            "posicao": {"linha": 12},
            "clausula_original": "1.1",
        },
    ]
    
    config = SemanticGroupingConfig(
        max_distance=1000,
        min_modification_size=1,
        require_same_clause=True,
        require_same_type=False,
    )
    
    result = _group_modifications_semantically(mods, config)
    
    print(f"\n{'='*60}")
    print("TESTE: ALTERACAO + INSERCAO + REMOCAO → ALTERACAO")
    print(f"{'='*60}")
    print(f"Antes: 3 modificações (1 ALTERACAO, 1 INSERCAO, 1 REMOCAO)")
    print(f"Depois: {len(result)} modificação, tipo: {result[0].get('tipo') if result else 'N/A'}")
    
    assert len(result) == 1
    assert result[0].get("tipo") == "ALTERACAO"
    
    print(f"✅ PASSOU: Grupo com ALTERACAO continua ALTERACAO!\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTES DE OTIMIZAÇÃO DA PRIORIZAÇÃO DE TIPOS")
    print("="*60)
    
    try:
        test_insercao_remocao_vira_alteracao()
        test_apenas_insercao_continua_insercao()
        test_alteracao_com_outros_continua_alteracao()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*60)
        print("\nOtimização validada: Grupos mistos INSERCAO+REMOCAO")
        print("agora são classificados como ALTERACAO (troca de conteúdo)")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}\n")
        exit(1)
