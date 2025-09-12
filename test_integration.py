#!/usr/bin/env python3
"""
Teste direto da API para demonstrar funcionamento
"""

import sys

import requests


def test_api():
    """Testa a API completa"""
    # URL base da API
    base_url = "http://localhost:5005"

    print("🧪 Testando API Flask...")

    try:
        # Teste 1: Health check
        print("\n1. Testando health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.json()}")

        # Teste 2: Listar documentos
        print("\n2. Testando listagem de documentos...")
        response = requests.get(f"{base_url}/api/documents", timeout=5)
        documents = response.json()
        print(f"✅ Documentos disponíveis: {documents}")

        # Teste 3: Processar documento
        print("\n3. Testando processamento de documento...")
        doc_id = documents["documents"][0]["id"]
        response = requests.post(
            f"{base_url}/api/process", json={"doc_id": doc_id}, timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Documento processado!")
            print(f"   - ID do diff: {result['id']}")
            print(f"   - URL para visualização: {result['url']}")

            # Teste 4: Obter dados do diff
            print("\n4. Testando obtenção de dados do diff...")
            diff_id = result["id"]
            response = requests.get(f"{base_url}/api/data/{diff_id}", timeout=5)

            if response.status_code == 200:
                diff_data = response.json()
                print("✅ Dados do diff obtidos!")
                print(f"   - Original: {len(diff_data['original'])} chars")
                print(f"   - Modificado: {len(diff_data['modified'])} chars")
                print(f"   - HTML diff: {len(diff_data['diff_html'])} chars")

                return result["url"]
            else:
                print(f"❌ Erro ao obter dados do diff: {response.status_code}")
                return None
        else:
            print(f"❌ Erro no processamento: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Certifique-se de que está rodando.")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None


if __name__ == "__main__":
    # Testar a API
    view_url = test_api()

    if view_url:
        print("\n🎉 Teste completo realizado com sucesso!")
        print(f"🔗 Visualize o resultado em: {view_url}")
        print("🖥️  Frontend disponível em: http://localhost:3002")
        print("⚙️  API disponível em: http://localhost:5005")
    else:
        print("\n❌ Teste falhou. Verifique se a API está rodando.")
        sys.exit(1)
