#!/usr/bin/env python3
"""
Testes de importação de módulos
"""

import os
import sys
import unittest

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports(unittest.TestCase):
    """Testes para verificar se as importações funcionam."""

    def test_python_environment(self):
        """Testa o ambiente Python."""
        self.assertIsNotNone(sys.version)
        self.assertTrue(sys.version.startswith("3."))

    def test_flask_import(self):
        """Testa importação do Flask."""
        try:
            import flask

            # Flask 3.x não tem __version__, usar importlib.metadata
            try:
                import importlib.metadata

                version = importlib.metadata.version("flask")
                self.assertIsNotNone(version)
            except Exception:
                # Fallback: apenas verificar se Flask foi importado
                self.assertIsNotNone(flask)
        except ImportError:
            self.fail("Flask não está disponível")

    def test_requests_import(self):
        """Testa importação do requests."""
        try:
            import requests

            self.assertIsNotNone(requests.__version__)
        except ImportError:
            self.fail("Requests não está disponível")

    def test_dotenv_import(self):
        """Testa importação do python-dotenv."""
        try:
            from dotenv import load_dotenv

            self.assertTrue(callable(load_dotenv))
        except ImportError:
            self.fail("Python-dotenv não está disponível")

    def test_environment_variables(self):
        """Testa variáveis de ambiente básicas."""
        # Carrega .env se existir
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        # Testa algumas variáveis básicas
        flask_port = os.getenv("FLASK_PORT", "5000")
        self.assertIsInstance(flask_port, str)
        self.assertTrue(flask_port.isdigit())

    def test_core_modules_exist(self):
        """Testa se os módulos principais existem."""
        core_modules = [
            "src.docx_compare.core.docx_utils",
            "src.docx_compare.core.docx_diff_viewer",
        ]

        for module_name in core_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Não foi possível importar {module_name}: {e}")


if __name__ == "__main__":
    unittest.main()
