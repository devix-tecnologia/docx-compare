#!/usr/bin/env python3
"""
Teste de integração com Directus Real
Demonstra como processar contratos cadastrados no Directus
"""

import requests


def test_directus_integration():
    """Testa integração completa com Directus"""
    base_url = "http://localhost:5002"

    print("🚀 Testando Integração com Directus Real")
    print("=" * 50)

    # 1. Health Check
    print("\n1. 🏥 Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health_data = response.json()
        print(f"✅ Status: {health_data['status']}")
        print(f"🔗 Directus conectado: {health_data['directus_connected']}")
        print(f"🌐 URL Directus: {health_data['directus_url']}")
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return

    # 2. Listar Documentos/Contratos
    print("\n2. 📋 Documentos Disponíveis")
    try:
        response = requests.get(f"{base_url}/api/documents", timeout=10)
        documents = response.json()["documents"]
        print(f"✅ Encontrados {len(documents)} documentos:")
        for i, doc in enumerate(documents[:5]):  # Mostrar apenas os primeiros 5
            print(f"   {i + 1}. ID: {doc['id']} - {doc['title']}")
            print(f"      Coleção: {doc['collection']}")
            print(f"      Atualizado: {doc['updated']}")
    except Exception as e:
        print(f"❌ Erro ao buscar documentos: {e}")
        return

    # 3. Listar Versões para Processar
    print("\n3. 🔄 Versões para Processar")
    try:
        response = requests.get(f"{base_url}/api/versoes", timeout=10)
        versoes = response.json()["versoes"]
        print(f"✅ Encontradas {len(versoes)} versões para processar:")
        for i, versao in enumerate(versoes[:3]):  # Mostrar apenas as primeiras 3
            print(f"   {i + 1}. ID: {versao.get('id', 'N/A')}")
            print(f"      Contrato: {versao.get('contrato_id', 'N/A')}")
            print(f"      Status: {versao.get('status', 'N/A')}")
    except Exception as e:
        print(f"❌ Erro ao buscar versões: {e}")
        versoes = []

    # 4. Processar uma Versão (se disponível)
    if versoes and len(versoes) > 0:
        print("\n4. ⚙️ Processando Versão")
        versao_id = versoes[0].get("id")
        if versao_id:
            try:
                response = requests.post(
                    f"{base_url}/api/process", json={"versao_id": versao_id}, timeout=15
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Versão {versao_id} processada com sucesso!")
                    print(f"🆔 Diff ID: {result['id']}")
                    print(f"🔗 URL de visualização: {result['url']}")
                    print(
                        f"📊 Tamanho do texto original: {len(result['original'])} chars"
                    )
                    print(
                        f"📊 Tamanho do texto modificado: {len(result['modified'])} chars"
                    )

                    # Abrir no browser
                    print(f"\n🌐 Abra no browser: {result['url']}")

                else:
                    print(f"❌ Erro no processamento: {response.status_code}")
            except Exception as e:
                print(f"❌ Erro ao processar versão: {e}")
    else:
        print("\n4. ⚙️ Nenhuma versão disponível para processar")
        print("💡 Para testar o processamento:")
        print("   1. Acesse o Directus: https://contract.devix.co")
        print("   2. Crie/edite uma versão com status 'processar'")
        print("   3. Execute este teste novamente")

    print("\n" + "=" * 50)
    print("🎉 Teste de Integração Concluído!")
    print("\n📋 URLs Úteis:")
    print(f"   🏥 Health: {base_url}/health")
    print(f"   📄 Documentos: {base_url}/api/documents")
    print(f"   🔄 Versões: {base_url}/api/versoes")
    print("   🌐 Frontend Vue: http://localhost:3002")


if __name__ == "__main__":
    test_directus_integration()
