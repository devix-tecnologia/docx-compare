#!/usr/bin/env python3
"""
Teste simples da estrutura versiona-ai
Valida que a organização de pastas está funcionando
"""

import os
from pathlib import Path


def verificar_estrutura():
    """Verifica se a estrutura da pasta versiona-ai está correta"""
    base_path = Path(__file__).parent

    print("🔍 Verificando estrutura da pasta versiona-ai...")
    print(f"📂 Base: {base_path}")
    print()

    # Estrutura esperada
    estrutura_esperada = {
        "README.md": "📄 Documentação principal",
        "INVERSAO_DEPENDENCIA_DIRECTUS.md": "📄 Documentação técnica",
        "__init__.py": "🐍 Módulo Python principal",
        "core/__init__.py": "🐍 Módulo core",
        "core/pipeline_funcional.py": "⚙️ Pipeline principal",
        "core/implementacoes_mock.py": "🎭 Implementações mock",
        "core/implementacoes_directus.py": "🏢 Implementações Directus",
        "core/exemplo_directus.py": "📘 Exemplo Directus",
        "core/exemplo_real_vs_mock.py": "📘 Exemplo comparativo",
        "tests/__init__.py": "🐍 Módulo de testes",
        "tests/teste_implementacoes_mock.py": "🧪 Testes mock",
        "tests/teste_implementacoes_directus.py": "🧪 Testes Directus",
        "tests/pipeline_funcional_teste.py": "🧪 Testes pipeline",
        "exemplos/__init__.py": "🐍 Módulo de exemplos",
        "exemplos/pipeline_funcional_exemplo.py": "📚 Exemplo básico",
        "web/__init__.py": "🐍 Módulo web",
        "web/html_diff_generator.py": "🌐 Gerador HTML",
        "web/visualizador_diff_exemplo.py": "🌐 Visualizador Vue",
        "web/DiffVisualizer.vue": "🎨 Componente Vue 3",
        "web/exemplo_diff.html": "🎨 Resultado HTML",
        "web/diff_data_exemplo.json": "📊 Dados exemplo",
    }

    # Verificar cada arquivo/pasta
    arquivos_encontrados = 0
    arquivos_faltando = []

    for caminho_relativo, descricao in estrutura_esperada.items():
        caminho_completo = base_path / caminho_relativo

        if caminho_completo.exists():
            tamanho = ""
            if caminho_completo.is_file():
                size_bytes = caminho_completo.stat().st_size
                if size_bytes > 1024:
                    tamanho = f" ({size_bytes // 1024}KB)"
                else:
                    tamanho = f" ({size_bytes}B)"

            print(f"✅ {descricao} - {caminho_relativo}{tamanho}")
            arquivos_encontrados += 1
        else:
            print(f"❌ {descricao} - {caminho_relativo} (FALTANDO)")
            arquivos_faltando.append(caminho_relativo)

    print()
    print("📊 Resumo:")
    print(f"   ✅ Encontrados: {arquivos_encontrados}/{len(estrutura_esperada)}")
    print(f"   ❌ Faltando: {len(arquivos_faltando)}")

    if arquivos_faltando:
        print(f"   📋 Arquivos faltando: {', '.join(arquivos_faltando)}")

    # Calcular tamanho total
    tamanho_total = 0
    for root, _dirs, files in os.walk(base_path):
        for file in files:
            tamanho_total += os.path.getsize(os.path.join(root, file))

    print(f"   💾 Tamanho total: {tamanho_total // 1024}KB")

    if len(arquivos_faltando) == 0:
        print("\n🎉 ✅ Estrutura versiona-ai COMPLETA e ORGANIZADA!")
        print("🚀 Sistema pronto para uso!")
    else:
        print(
            f"\n⚠️ Estrutura incompleta - {len(arquivos_faltando)} arquivo(s) faltando"
        )

    return len(arquivos_faltando) == 0


if __name__ == "__main__":
    print("🌟 Validador da Estrutura Versiona AI")
    print("=" * 50)

    sucesso = verificar_estrutura()

    if sucesso:
        print("\n🎯 Próximos passos:")
        print("1. Execute testes: python tests/teste_*.py")
        print("2. Veja exemplos: python exemplos/pipeline_*.py")
        print("3. Gere HTML: python web/html_diff_generator.py")
        print("4. Leia docs: README.md")

    exit(0 if sucesso else 1)
