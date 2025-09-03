import argparse
import difflib
import html
import os
import sys

from config import LUA_FILTER_PATH, OUTPUTS_DIR
from docx_utils import (
    analyze_differences,
    convert_docx_to_html,
    extract_body_content,
    get_css_styles,
    html_to_text,
)


def generate_diff_html(original_docx, modified_docx, output_html, dry_run=False):
    """
    Gera comparação HTML entre dois documentos DOCX.

    Args:
        original_docx: Caminho para o documento original
        modified_docx: Caminho para o documento modificado
        output_html: Caminho para o arquivo HTML de saída
        dry_run: Se True, apenas analisa sem gerar arquivo
    """
    temp_original_html = "original_temp.html"
    temp_modified_html = "modified_temp.html"

    try:
        print(
            f"🔍 Analisando: {os.path.basename(original_docx)} vs {os.path.basename(modified_docx)}"
        )

        # 1. Converter ambos os DOCX para HTML
        convert_docx_to_html(original_docx, temp_original_html, LUA_FILTER_PATH)
        convert_docx_to_html(modified_docx, temp_modified_html, LUA_FILTER_PATH)

        # 2. Extrair apenas o conteúdo do body
        original_content = extract_body_content(temp_original_html)
        modified_content = extract_body_content(temp_modified_html)

        # 3. Converter HTML para texto limpo
        original_text = html_to_text(original_content)
        modified_text = html_to_text(modified_content)

        # 4. Analisar diferenças
        stats = analyze_differences(original_text, modified_text)

        # Mostrar estatísticas
        print("📊 Resultados da análise:")
        print(f"   📈 Adições: {stats['total_additions']}")
        print(f"   📉 Remoções: {stats['total_deletions']}")
        print(f"   🔄 Modificações: {stats['total_modifications']}")

        if stats["modifications"]:
            print("   📝 Exemplos de modificações:")
            for i, mod in enumerate(stats["modifications"][:3]):
                print(
                    f"      {i + 1}. '{mod['original'][:50]}...' → '{mod['modified'][:50]}...'"
                )

        # Se for dry-run, parar aqui
        if dry_run:
            print("🔍 Modo dry-run: análise concluída, nenhum arquivo gerado")
            return stats

        # 5. Dividir em parágrafos para melhor comparação
        original_paragraphs = [
            p.strip() for p in original_text.split("\n\n") if p.strip()
        ]
        modified_paragraphs = [
            p.strip() for p in modified_text.split("\n\n") if p.strip()
        ]

        # 6. Usar difflib para comparar os parágrafos
        d = difflib.unified_diff(
            original_paragraphs,
            modified_paragraphs,
            fromfile="Original",
            tofile="Modificado",
            lineterm="",
        )

        # Converter para lista para poder contar
        diff_lines = list(d)

        # Contar adições e remoções (para compatibilidade)
        added_count = sum(
            1
            for line in diff_lines
            if line.startswith("+") and not line.startswith("+++")
        )
        removed_count = sum(
            1
            for line in diff_lines
            if line.startswith("-") and not line.startswith("---")
        )

        # 7. Gerar HTML final
        with open(output_html, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n")
            f.write('<html lang="pt-br">\n')
            f.write("<head>\n")
            f.write('<meta charset="utf-8">\n')
            f.write(
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            )
            f.write("<title>Comparação de Documentos</title>\n")
            f.write(f"<style>{get_css_styles()}</style>\n")
            f.write("</head>\n")
            f.write("<body>\n")
            f.write('<div class="diff-header">\n')
            f.write("<h1>Comparação de Documentos</h1>\n")
            f.write(
                f"<p><strong>Original:</strong> {os.path.basename(original_docx)} | "
            )
            f.write(
                f"<strong>Modificado:</strong> {os.path.basename(modified_docx)}</p>\n"
            )
            f.write("</div>\n")

            f.write('<div class="diff-stats">\n')
            f.write("<strong>Estatísticas:</strong> ")
            f.write(
                f'<span class="added-count">+{stats["total_additions"]} adições</span> | '
            )
            f.write(
                f'<span class="removed-count">-{stats["total_deletions"]} remoções</span>\n'
            )
            f.write("</div>\n")

            f.write('<div class="diff-content">\n')

            # Regenerar o diff para exibição
            d = difflib.unified_diff(
                original_paragraphs,
                modified_paragraphs,
                fromfile="Original",
                tofile="Modificado",
                lineterm="",
            )

            for line in d:
                if (
                    line.startswith("@@")
                    or line.startswith("---")
                    or line.startswith("+++")
                ):
                    continue
                elif line.startswith("+"):
                    content = html.escape(line[1:])
                    f.write(f'<p class="added">{content}</p>\n')
                elif line.startswith("-"):
                    content = html.escape(line[1:])
                    f.write(f'<p class="removed">{content}</p>\n')
                elif line.startswith(" "):
                    content = html.escape(line[1:])
                    f.write(f"<p>{content}</p>\n")

            f.write("</div>\n")
            f.write("</body>\n")
            f.write("</html>\n")

        print(f"✅ Diff HTML gerado em: {output_html}")
        return stats

    finally:
        # Limpar arquivos temporários
        for temp_file in [temp_original_html, temp_modified_html]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


def main():
    """Função principal do CLI com suporte a argumentos."""
    parser = argparse.ArgumentParser(
        description="Compara dois documentos DOCX e gera um relatório HTML das diferenças",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python docx_diff_viewer.py original.docx modificado.docx
  python docx_diff_viewer.py original.docx modificado.docx saida.html
  python docx_diff_viewer.py original.docx modificado.docx --dry-run
  python docx_diff_viewer.py original.docx modificado.docx --dry-run --verbose
        """,
    )

    parser.add_argument("original", help="Caminho para o documento DOCX original")

    parser.add_argument("modified", help="Caminho para o documento DOCX modificado")

    parser.add_argument(
        "output",
        nargs="?",
        help="Caminho para o arquivo HTML de saída (padrão: outputs/resultado.html)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa apenas a análise sem gerar arquivo HTML",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Exibe informações detalhadas durante a execução",
    )

    parser.add_argument(
        "--style",
        choices=["default", "minimal", "modern"],
        default="default",
        help="Estilo CSS para o relatório HTML (padrão: default)",
    )

    args = parser.parse_args()

    # Validar arquivos de entrada
    for file_path, name in [(args.original, "original"), (args.modified, "modificado")]:
        if not os.path.exists(file_path):
            print(f"❌ ERRO: Arquivo {name} não encontrado: {file_path}")
            sys.exit(1)
        if not file_path.lower().endswith(".docx"):
            print(f"⚠️  AVISO: Arquivo {name} não possui extensão .docx: {file_path}")

    # Definir arquivo de saída
    if args.dry_run:
        output_html_file = None
    elif args.output:
        output_html_file = args.output
        # Se o caminho não é absoluto e não contém pasta, colocar em outputs
        if (
            not os.path.isabs(output_html_file)
            and os.path.dirname(output_html_file) == ""
        ):
            output_html_file = os.path.join(OUTPUTS_DIR, output_html_file)
    else:
        output_html_file = os.path.join(OUTPUTS_DIR, "resultado.html")

    # Verificar filtro Lua
    if not os.path.exists(LUA_FILTER_PATH):
        print(
            f"❌ ERRO: Filtro Lua não encontrado em '{LUA_FILTER_PATH}'. Verifique o caminho."
        )
        sys.exit(1)

    # Executar comparação
    try:
        if args.verbose:
            print("🔧 Configurações:")
            print(f"   📁 Original: {args.original}")
            print(f"   📁 Modificado: {args.modified}")
            if not args.dry_run:
                print(f"   📄 Saída: {output_html_file}")
                print(f"   🎨 Estilo: {args.style}")
            print(
                f"   🔍 Modo: {'Análise apenas (dry-run)' if args.dry_run else 'Gerar HTML'}"
            )
            print(f"   🔧 Filtro Lua: {LUA_FILTER_PATH}")
            print()

        # Configurar estilo CSS se não for dry-run
        if not args.dry_run:
            # Temporariamente modificar get_css_styles para usar o estilo escolhido
            import docx_utils

            original_get_css = docx_utils.get_css_styles
            docx_utils.get_css_styles = lambda style_type="default": original_get_css(
                args.style
            )

        stats = generate_diff_html(
            args.original, args.modified, output_html_file, dry_run=args.dry_run
        )

        if args.verbose and stats:
            print("\n📊 Detalhes da análise:")
            print(
                f"   🔢 Total de modificações encontradas: {len(stats.get('modifications', []))}"
            )
            if stats.get("modifications"):
                print("   📝 Mostrando até 10 modificações:")
                for i, mod in enumerate(stats["modifications"][:10]):
                    print(f"      {i + 1:2d}. '{mod['original'][:40]}...'")
                    print(f"          → '{mod['modified'][:40]}...'")

        print("\n✅ Comparação concluída com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante a comparação: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
