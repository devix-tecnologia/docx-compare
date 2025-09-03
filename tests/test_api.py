import requests
import json
import time

# Configuração
API_BASE_URL = "http://localhost:5000"

def test_health():
    """Testa o endpoint de saúde."""
    print("🔍 Testando endpoint de saúde...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()

def test_config():
    """Testa o endpoint de configuração."""
    print("🔍 Testando endpoint de configuração...")
    try:
        response = requests.get(f"{API_BASE_URL}/config")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()

def test_compare(original_file_id, modified_file_id):
    """Testa o endpoint de comparação."""
    print("🔍 Testando endpoint de comparação...")
    
    payload = {
        "original_file_id": original_file_id,
        "modified_file_id": modified_file_id
    }
    
    print(f"Enviando payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/compare",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Tempo de processamento: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Comparação realizada com sucesso!")
            print(f"🔗 URL do resultado: {result['result_url']}")
            print(f"📊 Estatísticas:")
            print(f"   - Adições: {result['statistics']['total_additions']}")
            print(f"   - Remoções: {result['statistics']['total_deletions']}")
            print(f"   - Modificações: {result['statistics']['total_modifications']}")
            print(f"📄 Arquivo original: {result['original_file']['filename']} ({result['original_file']['size_bytes']} bytes)")
            print(f"📄 Arquivo modificado: {result['modified_file']['filename']} ({result['modified_file']['size_bytes']} bytes)")
        else:
            print("❌ Erro na comparação:")
            print(f"Response: {response.text}")
        print()
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()

def test_invalid_payload():
    """Testa com payload inválido."""
    print("🔍 Testando payload inválido...")
    
    try:
        # Teste sem IDs
        response = requests.post(f"{API_BASE_URL}/compare", json={})
        print(f"Status (sem IDs): {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Teste com UUID inválido
        response = requests.post(f"{API_BASE_URL}/compare", json={
            "original_file_id": "invalid-uuid",
            "modified_file_id": "another-invalid-uuid"
        })
        print(f"Status (UUID inválido): {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"❌ Erro: {e}")
        print()

if __name__ == "__main__":
    print("🧪 Executando testes da API do Comparador de Documentos")
    print("=" * 60)
    
    # Testes básicos
    test_health()
    test_config()
    test_invalid_payload()
    
    # Teste de comparação (substitua pelos IDs reais dos seus arquivos no Directus)
    print("⚠️  Para testar a comparação, substitua os IDs abaixo pelos IDs reais dos arquivos no Directus")
    print("    Exemplo de uso:")
    print("    test_compare('550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440001')")
    print()
    
    # Descomente as linhas abaixo e substitua pelos IDs reais para testar
    # test_compare(
    #     "original-file-uuid-here", 
    #     "modified-file-uuid-here"
    # )
