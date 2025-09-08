#!/usr/bin/env python3
"""
Exemplo demonstrando o uso do módulo docx_utils.

Este script mostra como utilizar as funcionalidades centralizadas
do módulo docx_utils para comparar documentos DOCX.
"""

import os
from datetime import datetime

from src.docx_compare.core.docx_utils import (
    analyze_differences,
    compare_docx_files,
    convert_docx_to_html_content,
    convert_docx_to_text,
    generate_diff_lines,
    get_css_styles,
    html_to_text,
)


def exemplo_basico():
    """Demonstra uso básico do módulo docx_utils."""
    print("🔄 Exemplo básico do módulo docx_utils")

    # Testar conversão de DOCX para texto
    if os.path.exists("documentos/doc-rafael-original.docx"):
        print("\n📄 Convertendo DOCX para texto...")
        texto = convert_docx_to_text("documentos/doc-rafael-original.docx")
        print(f"✅ Texto extraído: {len(texto)} caracteres")
        print(f"Primeiras 100 chars: {texto[:100]}...")

        # Testar conversão para HTML
        print("\n🌐 Convertendo DOCX para HTML...")
        html = convert_docx_to_html_content("documentos/doc-rafael-original.docx")
        print(f"✅ HTML gerado: {len(html)} caracteres")

        # Testar conversão HTML para texto
        print("\n🔧 Convertendo HTML para texto...")
        texto_limpo = html_to_text(html, preserve_structure=True)
        print(f"✅ Texto limpo: {len(texto_limpo)} caracteres")

        # Testar análise de diferenças
        if os.path.exists("documentos/doc-rafael-alterado.docx"):
            print("\n🔍 Analisando diferenças...")
            texto_modificado = convert_docx_to_text(
                "documentos/doc-rafael-alterado.docx"
            )
            stats = analyze_differences(texto, texto_modificado)
            print(
                f"✅ Estatísticas: {stats['total_additions']} adições, {stats['total_deletions']} remoções"
            )

    else:
        print("❌ Arquivo de exemplo não encontrado")


def exemplo_estilos_css():
    """Demonstra diferentes estilos CSS disponíveis."""
    print("\n🎨 Exemplos de estilos CSS:")

    estilos = ["default", "minimal", "modern"]

    for estilo in estilos:
        css = get_css_styles(estilo)
        print(f"✅ Estilo '{estilo}': {len(css)} caracteres")


def exemplo_comparacao_completa():
    """Demonstra comparação completa entre dois documentos."""
    print("\n📊 Comparação completa de documentos:")

    original = "documentos/doc-rafael-original.docx"
    modificado = "documentos/doc-rafael-alterado.docx"

    if os.path.exists(original) and os.path.exists(modificado):
        print(f"🔄 Comparando {original} vs {modificado}")

        # Usar função de comparação
        original_text, modified_text, statistics = compare_docx_files(
            original, modificado
        )

        print("✅ Análise concluída:")
        print(f"   📈 Adições: {statistics['total_additions']}")
        print(f"   📉 Remoções: {statistics['total_deletions']}")
        print(f"   🔄 Modificações: {statistics['total_modifications']}")

        # Gerar linhas de diff
        diff_lines = generate_diff_lines(original_text, modified_text)
        print(f"   📋 Linhas de diff: {len(diff_lines)}")

        # Mostrar algumas modificações
        if statistics["modifications"]:
            print("\n🔍 Primeiras modificações:")
            for i, mod in enumerate(statistics["modifications"][:3]):
                print(f"   {i + 1}. '{mod['original']}' → '{mod['modified']}'")

    else:
        print("❌ Arquivos de exemplo não encontrados")


def gerar_relatorio_html():
    """Gera um relatório HTML demonstrativo."""
    print("\n📄 Gerando relatório HTML demonstrativo...")

    css = get_css_styles("modern")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Exemplo docx_utils</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">Demonstração do Módulo docx_utils</h1>
                <p class="subtitle">Funcionalidades centralizadas para comparação de documentos</p>
            </div>

            <div class="statistics">
                <div class="stat-card">
                    <span class="stat-number">8</span>
                    <span class="stat-label">Funções Principais</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">3</span>
                    <span class="stat-label">Estilos CSS</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">100%</span>
                    <span class="stat-label">Compatibilidade</span>
                </div>
            </div>

            <div class="comparison-section">
                <h2 class="section-title">Funcionalidades Disponíveis</h2>
                <div class="modifications-list">
                    <div class="modification-item">
                        <strong>convert_docx_to_text()</strong>
                        <div class="modification-new">Converte documentos DOCX para texto puro</div>
                    </div>
                    <div class="modification-item">
                        <strong>convert_docx_to_html_content()</strong>
                        <div class="modification-new">Converte documentos DOCX para HTML com filtros</div>
                    </div>
                    <div class="modification-item">
                        <strong>html_to_text()</strong>
                        <div class="modification-new">Extrai texto limpo de conteúdo HTML</div>
                    </div>
                    <div class="modification-item">
                        <strong>analyze_differences()</strong>
                        <div class="modification-new">Analisa diferenças e gera estatísticas</div>
                    </div>
                    <div class="modification-item">
                        <strong>get_css_styles()</strong>
                        <div class="modification-new">Fornece estilos CSS para relatórios</div>
                    </div>
                </div>
            </div>

            <div class="timestamp">
                Relatório gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
            </div>
        </div>
    </body>
    </html>
    """

    output_path = "results/exemplo_docx_utils.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Relatório gerado em: {output_path}")
    return output_path


if __name__ == "__main__":
    print("🚀 Demonstração do módulo docx_utils")
    print("=" * 50)

    try:
        exemplo_basico()
        exemplo_estilos_css()
        exemplo_comparacao_completa()
        relatorio = gerar_relatorio_html()

        print("\n🎉 Demonstração concluída com sucesso!")
        print(f"📁 Relatório disponível em: {relatorio}")

    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        import traceback

        traceback.print_exc()
