#!/usr/bin/env python3
"""
Teste do SDK do Directus
"""

import os
import unittest
from unittest.mock import Mock, patch

from dotenv import load_dotenv


class TestDirectusSDK(unittest.TestCase):
    """Testes para o SDK do Directus."""

    def setUp(self):
        """Configuração dos testes."""
        load_dotenv()
        self.base_url = (
            os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
            .replace("/admin/", "")
            .rstrip("/")
        )
        self.token = os.getenv("DIRECTUS_TOKEN", "test-token")

    def test_directus_configuration(self):
        """Testa se as configurações do Directus estão corretas."""
        self.assertIsNotNone(self.base_url)
        self.assertTrue(self.base_url.startswith("http"))
        self.assertIsNotNone(self.token)

    @patch("directus_sdk_py.DirectusClient")
    def test_directus_client_creation(self, mock_directus_client):
        """Testa a criação do cliente Directus."""
        # Mock do cliente
        mock_client = Mock()
        mock_directus_client.return_value = mock_client

        try:
            from directus_sdk_py import DirectusClient

            client = DirectusClient(url=self.base_url, token=self.token)
            self.assertIsNotNone(client)
        except ImportError:
            self.skipTest("directus_sdk_py não está instalado")

    @patch("directus_sdk_py.DirectusClient")
    def test_directus_get_items(self, mock_directus_client):
        """Testa a busca de itens no Directus."""
        # Mock do cliente e resposta
        mock_client = Mock()
        mock_client.get_items.return_value = [
            {"id": "123", "status": "processar"},
            {"id": "456", "status": "processado"},
        ]
        mock_directus_client.return_value = mock_client

        try:
            from directus_sdk_py import DirectusClient

            client = DirectusClient(url=self.base_url, token=self.token)

            # Teste buscar todos os itens
            versoes_all = client.get_items("versao")
            self.assertIsInstance(versoes_all, list)
            self.assertEqual(len(versoes_all), 2)

            # Teste buscar com filtro
            versoes_filtradas = client.get_items(
                "versao", {"filter": {"status": "processar"}}
            )
            self.assertIsInstance(versoes_filtradas, list)

        except ImportError:
            self.skipTest("directus_sdk_py não está instalado")

    def test_environment_variables(self):
        """Testa se as variáveis de ambiente estão configuradas."""
        # Testa se pelo menos temos URLs válidas
        self.assertTrue(
            self.base_url.startswith("http://") or self.base_url.startswith("https://")
        )
        # Token deve ter pelo menos alguns caracteres
        self.assertGreater(len(self.token), 5)


if __name__ == "__main__":
    unittest.main()
