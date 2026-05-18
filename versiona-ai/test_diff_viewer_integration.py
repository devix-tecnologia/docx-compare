"""
Teste de integração simples para verificar o DiffVisualizer.
Execute: uv run python test_diff_viewer_integration.py
"""

import json

import requests

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def test_diff_viewer():
    """Testa o fluxo completo: processar → visualizar"""

    base_url = "http://localhost:8011"
    versao_id = "2573b998-63d0-4471-ad85-db6f860c3721"

    print(f"{BLUE}🧪 Testando fluxo completo do DiffVisualizer{RESET}\n")

    # 1. Processar versão
    print(f"{BLUE}1️⃣  Processando versão {versao_id}...{RESET}")
    response = requests.post(
        f"{base_url}/api/process",
        json={"versao_id": versao_id},
        timeout=120,  # Aumentado para 2 minutos
    )

    if response.status_code != 200:
        print(f"{RED}❌ Falha no processamento: {response.status_code}{RESET}")
        return False

    data = response.json()
    diff_id = data.get("diff_id")

    if not diff_id:
        print(f"{RED}❌ Nenhum diff_id retornado{RESET}")
        print(json.dumps(data, indent=2))
        return False

    print(f"{GREEN}✅ Processamento OK - diff_id: {diff_id}{RESET}")
    print(f"   Modificações: {data.get('metricas', {}).get('total_modificacoes', 0)}")
    print(f"   Método: {data.get('metodo', 'N/A')}\n")

    # 2. Verificar visualizador HTML
    print(f"{BLUE}2️⃣  Verificando visualizador HTML...{RESET}")
    viewer_url = f"{base_url}/view/{diff_id}"
    response = requests.get(viewer_url, timeout=10)

    if response.status_code != 200:
        print(f"{RED}❌ Visualizador não acessível: {response.status_code}{RESET}")
        return False

    html = response.text
    if "window.VERSAO_ID" in html and diff_id in html:
        print(f"{GREEN}✅ HTML do visualizador OK{RESET}")
        print(f"   URL: {viewer_url}\n")
    else:
        print(f"{RED}❌ HTML inválido - diff_id não encontrado{RESET}")
        return False

    # 3. Verificar API de dados
    print(f"{BLUE}3️⃣  Verificando API de dados...{RESET}")
    api_url = f"{base_url}/api/data/{diff_id}"
    response = requests.get(api_url, timeout=10)

    if response.status_code != 200:
        print(f"{RED}❌ API de dados não acessível: {response.status_code}{RESET}")
        return False

    api_data = response.json()
    mods_count = len(api_data.get("modificacoes", []))
    print(f"{GREEN}✅ API de dados OK{RESET}")
    print(f"   Modificações retornadas: {mods_count}\n")

    # 4. Verificar assets estáticos
    print(f"{BLUE}4️⃣  Verificando assets estáticos...{RESET}")

    # Extrair nome do arquivo JS do HTML
    import re

    js_match = re.search(r'/assets/(index-[^"]+\.js)', html)
    css_match = re.search(r'/assets/(index-[^"]+\.css)', html)

    all_ok = True

    if js_match:
        js_file = js_match.group(1)
        js_url = f"{base_url}/assets/{js_file}"
        response = requests.head(js_url, timeout=5)
        if response.status_code == 200:
            print(f"{GREEN}✅ JavaScript OK: {js_file}{RESET}")
        else:
            print(f"{RED}❌ JavaScript não encontrado: {js_file}{RESET}")
            all_ok = False

    if css_match:
        css_file = css_match.group(1)
        css_url = f"{base_url}/assets/{css_file}"
        response = requests.head(css_url, timeout=5)
        if response.status_code == 200:
            print(f"{GREEN}✅ CSS OK: {css_file}{RESET}")
        else:
            print(f"{RED}❌ CSS não encontrado: {css_file}{RESET}")
            all_ok = False

    if not all_ok:
        return False

    print(f"\n{GREEN}🎉 Todos os testes passaram!{RESET}")
    print(f"\n{BLUE}📋 Para testar com Playwright:{RESET}")
    print(f"   page.goto('{viewer_url}')")
    print("   page.wait_for_selector('#app')")

    return True


if __name__ == "__main__":
    try:
        success = test_diff_viewer()
        exit(0 if success else 1)
    except Exception as e:
        print(f"{RED}❌ Erro: {e}{RESET}")
        import traceback

        traceback.print_exc()
        exit(1)
