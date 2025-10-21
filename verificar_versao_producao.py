#!/usr/bin/env python3
"""
Script para verificar uma versão no Directus usando o repositório.
Verifica se as modificações foram registradas corretamente.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório versiona-ai ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "versiona-ai"))

from repositorio import DirectusRepository
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN")

def main():
    versao_id = "73b215cb-8f94-4b07-9d23-b8d72a8a2d3f"
    
    print("=" * 80)
    print("🔍 VERIFICANDO VERSÃO EM PRODUÇÃO")
    print("=" * 80)
    print(f"Versão ID: {versao_id}")
    print(f"Directus: {DIRECTUS_BASE_URL}")
    print()
    
    # Criar repositório
    repo = DirectusRepository(DIRECTUS_BASE_URL, DIRECTUS_TOKEN)
    
    # Testar conexão
    print("📡 Testando conexão com Directus...")
    result = repo.test_connection()
    if not result['success']:
        print(f"❌ Falha na conexão: {result['message']}")
        return 1
    
    print(f"✅ Conectado (status {result['status_code']})")
    print()
    
    # Buscar versão completa para view
    print("📥 Buscando versão completa...")
    versao_data = repo.get_versao_completa_para_view(versao_id)
    
    if not versao_data:
        print(f"❌ Versão {versao_id} não encontrada!")
        return 1
    
    print(f"✅ Versão encontrada!")
    print()
    
    # Exibir informações da versão
    print("📊 INFORMAÇÕES DA VERSÃO:")
    print("-" * 80)
    print(f"  ID: {versao_data.get('id')}")
    print(f"  Status: {versao_data.get('status')}")
    print(f"  Data criação: {versao_data.get('date_created')}")
    print(f"  Data atualização: {versao_data.get('date_updated')}")
    print(f"  Data processamento: {versao_data.get('data_hora_processamento', 'N/A')}")
    print()
    
    # Verificar modificações
    modificacoes = versao_data.get('modificacoes', [])
    print(f"📝 MODIFICAÇÕES: {len(modificacoes)} encontradas")
    print("-" * 80)
    
    if not modificacoes:
        print("  ⚠️  Nenhuma modificação registrada!")
        print("  💡 A versão pode não ter sido processada ainda.")
    else:
        # Estatísticas das modificações
        categorias = {}
        com_clausula = 0
        
        for mod in modificacoes:
            categoria = mod.get('categoria', 'unknown')
            categorias[categoria] = categorias.get(categoria, 0) + 1
            
            if mod.get('clausula'):
                com_clausula += 1
        
        print(f"\n  ✅ Total: {len(modificacoes)} modificações")
        print(f"  📋 Com cláusula: {com_clausula} ({com_clausula/len(modificacoes)*100:.1f}%)")
        print(f"\n  📊 Por categoria:")
        for cat, count in sorted(categorias.items()):
            print(f"     - {cat}: {count}")
        
        # Mostrar primeiras 3 modificações
        print(f"\n  📄 Primeiras 3 modificações:")
        for i, mod in enumerate(modificacoes[:3], 1):
            clausula_info = "N/A"
            if mod.get('clausula'):
                clausula = mod['clausula']
                if isinstance(clausula, dict):
                    clausula_info = f"{clausula.get('numero')} - {clausula.get('nome')}"
                else:
                    clausula_info = str(clausula)
            
            print(f"\n     Modificação {i}:")
            print(f"       ID: {mod.get('id')}")
            print(f"       Categoria: {mod.get('categoria')}")
            print(f"       Cláusula: {clausula_info}")
            print(f"       Posição: {mod.get('posicao_inicio')} - {mod.get('posicao_fim')}")
    
    print()
    print("=" * 80)
    print("✅ VERIFICAÇÃO CONCLUÍDA")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
