#!/usr/bin/env python3
"""
Script para corrigir dados da coleção modelo_contrato_clausula
Copia valores do campo 'numero' para o campo 'nome' quando nome estiver vazio
"""

import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DIRECTUS_BASE_URL = (
    os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
    .replace("/admin/", "")
    .rstrip("/")
)
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "your-directus-token")

# Headers para requisições HTTP
DIRECTUS_HEADERS = {
    "Authorization": f"Bearer {DIRECTUS_TOKEN}",
    "Content-Type": "application/json",
}

def testar_conexao_e_descobrir_colecoes():
    """
    Testa conexão e descobre as coleções disponíveis
    """
    try:
        print("🧪 Testando conectividade e descobrindo coleções...")
        
        # Testar com algumas variações do nome da coleção
        possiveis_nomes = [
            "modelo_contrato_clausula",
            "modelo_contrato-clausula", 
            "clausula",
            "clausulas"
        ]
        
        for nome in possiveis_nomes:
            print(f"   Testando coleção '{nome}'...")
            
            response = requests.get(
                f"{DIRECTUS_BASE_URL}/items/{nome}",
                params={"limit": 1},
                headers=DIRECTUS_HEADERS
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Coleção '{nome}' encontrada!")
                return nome
            elif response.status_code == 403:
                print(f"   ⚠️ Coleção '{nome}' sem permissão")
            else:
                print(f"   ❌ Coleção '{nome}' não encontrada")
        
        return None
        
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return None

def buscar_clausulas_sem_nome(nome_colecao):
    """
    Busca cláusulas que têm número mas não têm nome preenchido
    """
    try:
        print(f"🔍 Buscando cláusulas sem nome preenchido na coleção '{nome_colecao}'...")
        
        # Buscar todas as cláusulas
        response = requests.get(
            f"{DIRECTUS_BASE_URL}/items/{nome_colecao}",
            params={
                "limit": 1000,  # Ajustar se necessário
                "fields": "id,numero,nome"
            },
            headers=DIRECTUS_HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            clausulas = data.get('data', [])
            
            print(f"✅ Encontradas {len(clausulas)} cláusulas no total")
            
            # Filtrar cláusulas que precisam de correção
            clausulas_para_corrigir = []
            for clausula in clausulas:
                numero = str(clausula.get('numero', '') or '').strip()
                nome = str(clausula.get('nome', '') or '').strip()
                
                # Se tem número mas não tem nome, ou se nome está vazio
                if numero and (not nome or nome == ''):
                    clausulas_para_corrigir.append(clausula)
            
            print(f"🎯 Encontradas {len(clausulas_para_corrigir)} cláusulas para corrigir")
            return clausulas_para_corrigir
            
        else:
            print(f"❌ Erro ao buscar cláusulas: {response.status_code}")
            if response.status_code == 403:
                print("   Problema de permissão - verifique as permissões do token")
            return []
            
    except Exception as e:
        print(f"❌ Erro ao buscar cláusulas: {e}")
        return []

def corrigir_clausula(clausula_id, numero, nome_colecao):
    """
    Atualiza o campo nome de uma cláusula com o valor do número
    """
    try:
        response = requests.patch(
            f"{DIRECTUS_BASE_URL}/items/{nome_colecao}/{clausula_id}",
            json={"nome": numero},
            headers=DIRECTUS_HEADERS
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Erro ao atualizar cláusula {clausula_id}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar cláusula {clausula_id}: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🔧 Iniciando correção de dados da coleção modelo_contrato_clausula")
    print(f"🔗 Conectando em: {DIRECTUS_BASE_URL}")
    print(f"🔑 Token: {DIRECTUS_TOKEN[:10]}...")
    print("=" * 60)
    
    # Primeiro, descobrir o nome correto da coleção
    nome_colecao = testar_conexao_e_descobrir_colecoes()
    
    if not nome_colecao:
        print("❌ Não foi possível encontrar uma coleção de cláusulas acessível")
        return
    
    # Buscar cláusulas para corrigir
    clausulas_para_corrigir = buscar_clausulas_sem_nome(nome_colecao)
    
    if not clausulas_para_corrigir:
        print("ℹ️ Nenhuma cláusula encontrada para correção")
        return
    
    print("\n📋 Cláusulas que serão corrigidas:")
    print("=" * 60)
    for clausula in clausulas_para_corrigir[:10]:  # Mostrar apenas primeiras 10
        print(f"ID: {clausula['id']} | Número: '{clausula.get('numero', 'N/A')}' | Nome atual: '{clausula.get('nome', 'vazio')}'")
    
    if len(clausulas_para_corrigir) > 10:
        print(f"... e mais {len(clausulas_para_corrigir) - 10} cláusulas")
    
    # Confirmar execução
    print("\n⚠️  ATENÇÃO: Este script irá modificar dados no banco de dados!")
    confirmacao = input("Digite 'CONFIRMAR' para prosseguir ou qualquer outra coisa para cancelar: ")
    
    if confirmacao != 'CONFIRMAR':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Processar correções
    print(f"\n🚀 Iniciando correção de {len(clausulas_para_corrigir)} cláusulas...")
    print("=" * 60)
    
    sucesso = 0
    erro = 0
    
    for i, clausula in enumerate(clausulas_para_corrigir, 1):
        clausula_id = clausula['id']
        numero = clausula.get('numero', '')
        
        print(f"[{i:3d}/{len(clausulas_para_corrigir)}] Corrigindo cláusula {clausula_id}...")
        print(f"         Copiando '{numero}' para campo nome")
        
        if corrigir_clausula(clausula_id, numero, nome_colecao):
            print(f"         ✅ Sucesso!")
            sucesso += 1
        else:
            print(f"         ❌ Falhou!")
            erro += 1
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO DA CORREÇÃO:")
    print(f"   ✅ Sucessos: {sucesso}")
    print(f"   ❌ Erros: {erro}")
    print(f"   📈 Total processado: {sucesso + erro}")
    
    if erro == 0:
        print("🎉 Correção concluída com sucesso!")
    else:
        print("⚠️ Correção concluída com alguns erros")

if __name__ == "__main__":
    main()
