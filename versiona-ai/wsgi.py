#!/usr/bin/env python3
"""
Script de inicialização para produção com Gunicorn
"""

import os
import sys

# Adicionar o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar a aplicação Flask
from directus_server import app

if __name__ == "__main__":
    app.run()
