#!/usr/bin/env python3
"""
Script para verificar como os caminhos das tags estão sendo gerados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processador_modelo_contrato import extract_tags_from_differences

def test_caminhos_tags():
    """Testa se os caminhos das tags estão sendo gerados corretamente"""
    
    print("🧪 Testando geração de caminhos das tags...")
    
    # Simulando dados de modificações
    test_modifications = [
        {
            'categoria': 'modificacao',
            'conteudo': 'Este é o texto original sem tags',
            'alteracao': 'Este é o texto com {{preambulo}} modificado',
            'sort': 0
        },
        {
            'categoria': 'adicao', 
            'conteudo': '',
            'alteracao': 'Nova seção com {{1}} e {{1.1}} adicionadas',
            'sort': 1
        },
        {
            'categoria': 'modificacao',
            'conteudo': 'Texto antigo',
            'alteracao': 'Novo texto com {{condicoes_gerais}} e {{2}}',
            'sort': 2
        }
    ]
    
    # Extrair tags
    tags_encontradas = extract_tags_from_differences(test_modifications)
    
    print("\n📋 Resumo das tags encontradas:")
    for tag in tags_encontradas:
        print(f"  • Tag: '{tag['nome']}'")
        print(f"    - Caminho início: {tag['caminho_tag_inicio']}")
        print(f"    - Caminho fim: {tag['caminho_tag_fim']}")
        print(f"    - Linha aproximada: {tag['linha_aproximada']}")
        print(f"    - Posições: {tag['posicao_inicio']} → {tag['posicao_fim']}")
        print(f"    - Contexto: {tag['contexto'][:50]}...")
        print()
    
    return tags_encontradas

if __name__ == "__main__":
    tags = test_caminhos_tags()
    print(f"✅ Teste concluído! {len(tags)} tags processadas.")
