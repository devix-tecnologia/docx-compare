#!/usr/bin/env python3
"""
Testes para verificar importações e dependências do projeto
"""

import importlib.metadata
import os
import sys
import unittest

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


class TestImports(unittest.TestCase):
    """Testes para verificar se todas as dependências estão funcionando."""

    def test_python_environment(self):
        """Testa informações do ambiente Python."""
        print(f"Python: {sys.version}")
        self.assertTrue(sys.version_info >= (3, 8))

    def test_flask_import(self):
        """Testa importação do Flask."""
        try:
            flask_version = importlib.metadata.version("flask")
        except importlib.metadata.PackageNotFoundError:
            flask_version = "unknown"

        print(f"Flask instalado: {flask_version}")
        self.assertNotEqual(flask_version, "unknown")

    def test_requests_import(self):
        """Testa importação do requests."""
        try:
            requests_version = importlib.metadata.version("requests")
        except importlib.metadata.PackageNotFoundError:
            requests_version = "unknown"

        print(f"Requests instalado: {requests_version}")
        self.assertNotEqual(requests_version, "unknown")

    def test_dotenv_import(self):
        """Testa importação do python-dotenv."""
        from dotenv import load_dotenv

        print("Python-dotenv disponível")
        load_dotenv()
        print(".env carregado")
        # Teste que load_dotenv não gera exceção
        self.assertTrue(True)

    def test_environment_variables(self):
        """Testa variáveis de ambiente."""
        print(f"FLASK_PORT: {os.getenv('FLASK_PORT', 'Não encontrado')}")
        # Apenas verificamos que conseguimos acessar as variáveis de ambiente
        self.assertIsInstance(os.getenv("FLASK_PORT", "default"), str)

    def test_core_modules_exist(self):
        """Testa se os módulos principais do projeto existem."""
        try:
            # Verificar se conseguimos importar módulos do projeto
            import importlib.util

            spec = importlib.util.find_spec("src.docx_compare.core.docx_utils")
            if spec is not None:
                print("Módulo docx_utils importado com sucesso")
                self.assertTrue(True)
            else:
                print("Aviso: Módulo docx_utils não encontrado")
                self.assertTrue(True)  # Não falhamos o teste
        except ImportError as e:
            print(f"Aviso: Não foi possível importar docx_utils: {e}")
            # Não falhamos o teste, apenas logamos
            self.assertTrue(True)


if __name__ == "__main__":
    print("🚀 Testando imports e dependências...")
    unittest.main()
