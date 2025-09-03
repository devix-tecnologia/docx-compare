#!/usr/bin/env python3
"""
Script simples para testar a API
"""

import sys
import os
# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🚀 Testando API...")

try:
    print(f"Python: {sys.version}")
    
    import flask
    print(f"Flask instalado: {flask.__version__}")
    
    import requests
    print(f"Requests instalado: {requests.__version__}")
    
    from dotenv import load_dotenv
    print("Python-dotenv disponível")
    
    load_dotenv()
    print(".env carregado")
    
    print(f"FLASK_PORT: {os.getenv('FLASK_PORT', 'Não encontrado')}")
    
    # Agora importar o módulo da API
    print("Importando api_server...")
    import api_server
    print("api_server importado com sucesso!")
    
    print("✅ Todas as dependências estão funcionando!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
