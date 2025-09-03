#!/usr/bin/env python3
"""
Script de teste para a API simples
"""

import requests

# Configuração
API_BASE_URL = "http://localhost:5002"


def test_health():
    """Testa o endpoint de saúde"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro no teste de saúde: {e}")
        return False


def test_compare():
    """Testa o endpoint de comparação com UUIDs de exemplo"""
    try:
        # UUIDs reais do Directus
        data = {
            "original_file_id": "9512120c-93b9-4503-93cc-3c0cb492e664",
            "modified_file_id": "1CjYes_ficb6NFphrLziseNXCACiyQRF",
        }

        response = requests.post(
            f"{API_BASE_URL}/compare",
            json=data,
            headers={"Content-Type": "application/json"},
        )

        print(f"Compare Status: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"🎉 Sucesso! Resultado em: {result['result_url']}")
                return True

        return False

    except Exception as e:
        print(f"Erro no teste de comparação: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testando API Simples de Comparação de Documentos")
    print("=" * 50)

    print("1. Testando Health...")
    if test_health():
        print("✅ Health OK")
    else:
        print("❌ Health falhou")
        exit(1)

    print("\n2. Testando Compare...")
    print("ℹ️  NOTA: Este teste falhará se os UUIDs não existirem no Directus")
    if test_compare():
        print("✅ Compare OK")
    else:
        print("❌ Compare falhou (esperado se UUIDs não existirem)")

    print("\n📝 Para testar com UUIDs reais:")
    print("1. Configure DIRECTUS_BASE_URL e DIRECTUS_TOKEN no .env")
    print("2. Substitua os UUIDs no teste acima pelos UUIDs reais dos seus arquivos")
    print("3. Execute novamente o teste")
