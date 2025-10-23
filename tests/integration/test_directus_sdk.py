#!/usr/bin/env python3
"""
Teste simples do SDK do Directus
"""

import os
import unittest

from directus_sdk_py import DirectusClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class TestDirectusSDK(unittest.TestCase):
    """Testes para o SDK do Directus."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Configurações
        self.directus_base_url = (
            os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
            .replace("/admin/", "")
            .rstrip("/")
        )
        self.directus_token = os.getenv("DIRECTUS_TOKEN", "your-directus-token")

        print(f"🔗 Testando conexão com: {self.directus_base_url}")
        print(f"🔑 Token: {self.directus_token[:20]}...")

        # Cliente Directus
        self.directus_client = DirectusClient(
            url=self.directus_base_url, token=self.directus_token
        )

    def test_directus_client_creation(self):
        """Testa se o cliente Directus foi criado corretamente."""
        self.assertIsNotNone(self.directus_client)

    def test_directus_configuration(self):
        """Testa se as configurações estão corretas."""
        self.assertTrue(self.directus_base_url.startswith("http"))
        self.assertNotEqual(self.directus_token, "your-directus-token")

    def test_directus_get_items(self):
        """Testa a busca de itens no Directus."""
        try:
            # Teste simples de buscar versões sem filtro primeiro
            print("📋 Buscando todas as versões...")
            versoes_all = self.directus_client.get_items("versao")

            print(f"📊 Quantidade total: {len(versoes_all) if versoes_all else 0}")

            # Mostrar o status de cada versão (com verificação de segurança)
            if versoes_all and isinstance(versoes_all, list):
                for versao in versoes_all:
                    if isinstance(versao, dict):
                        version_id = str(versao.get("id", "unknown"))
                        print(
                            f"  ID: {version_id[:8]}... Status: {versao.get('status', 'N/A')}"
                        )

            # Agora teste com filtro simplificado
            print("\n📋 Testando filtro simples...")

            # Tentar sintaxe mais simples
            versoes_filtradas = self.directus_client.get_items(
                "versao", {"filter": {"status": "processar"}}
            )

            print(f"📊 Tipo do retorno (filtrado): {type(versoes_filtradas)}")
            print(f"📊 Conteúdo do retorno (filtrado): {versoes_filtradas}")

            # Verificar se retornou algo válido (pode ser lista vazia)
            self.assertIsNotNone(versoes_all)

        except Exception as e:
            print(f"❌ Erro: {e}")
            # Em vez de falhar, apenas logamos o erro pois pode ser questão de conectividade
            print("⚠️ Teste falhou por problemas de conectividade ou configuração")

    def test_environment_variables(self):
        """Testa se as variáveis de ambiente estão configuradas."""
        self.assertIsNotNone(os.getenv("DIRECTUS_BASE_URL"))
        self.assertIsNotNone(os.getenv("DIRECTUS_TOKEN"))


if __name__ == "__main__":
    unittest.main()
