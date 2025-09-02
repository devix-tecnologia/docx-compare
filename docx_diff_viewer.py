import subprocess
import os
import difflib
import sys # <-- ADICIONE ESTA LINHA

# --- Configuração ---
LUA_FILTER_PATH = "comments_html_filter_direct.lua" 

# CSS para estilizar as diferenças - agora embutido no script novamente
CSS_CONTENT = """
body { font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; margin: 20px auto; max-width: 900px; background-color: #f8f9fa; color: #343a40; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 30px; border-radius: 8px; }
h1, h2, h3, h4, h5, h6 { color: #212529; margin-top: 1.5em; margin-bottom: 0.5em; }
.diff-header { background-color: #e9ecef; padding: 15px 20px; border-bottom: 1px solid #dee2e6; margin: -30px -30px 20px -30px; border-top-left-radius: 8px; border-top-right-radius: 8px; font-size: 1.2em; color: #495057; text-align: center; }
.added { background-color: #d4edda; color: #155724; font-weight: bold; padding: 0.1em 0.3em; border-radius: 3px; text-decoration: none; }
.removed { background-color: #f8d7da; color: #721c24; text-decoration: line-through; padding: 0.1em 0.3em; border-radius: 3px; }
.changed-old { background-color: #fff3cd; color: #856404; text-decoration: line-through; padding: 0.1em 0.3em; border-radius: 3px; }
.changed-new { background-color: #fff3cd; color: #856404; font-weight: bold; padding: 0.1em 0.3em; border-radius: 3px; }
.commented-text-container { border-bottom: 2px dotted #007bff; cursor: help; position: relative; display: inline-block; }
.inserted-comment-info { font-family: monospace; font-size: 0.8em; color: #6c757d; margin-left: 0.5em; padding: 0.2em 0.5em; border-left: 3px solid #17a2b8; background-color: #eaf6f9; border-radius: 4px; white-space: normal; display: inline-block; }
.inserted-comment-info strong { color: #0056b3; font-weight: bold; }
.inserted-comment-info em { font-style: italic; color: #495057; }
p { margin-bottom: 1em; }
ul, ol { margin-left: 20px; margin-bottom: 1em; }
table { width: 100%; border-collapse: collapse; margin-bottom: 1em; }
th, td { border: 1px solid #dee2e6; padding: 8px; text-align: left; }
th { background-color: #e9ecef; }
a { color: #007bff; text-decoration: none; }
a:hover { text-decoration: underline; }
pre { white-space: pre-wrap; word-wrap: break-word; } /* Adiciona pre para o diff */
"""

def convert_docx_to_html(docx_path, output_html_path, lua_filter_path):
    """Converte um DOCX para HTML usando Pandoc com o filtro Lua."""
    cmd = [
        "pandoc",
        docx_path,
        "--to=html",
        "--track-changes=all",
        f"--lua-filter={lua_filter_path}",
        f"-o{output_html_path}"
    ]
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao converter {docx_path}:")
        print(result.stderr)
        raise RuntimeError(f"Erro no Pandoc para {docx_path}")
    print(f"Convertido {docx_path} para {output_html_path}")


def generate_diff_html(original_docx, modified_docx, output_html):
    temp_original_html = "original_temp.html"
    temp_modified_html = "modified_temp.html"
    
    try:
        # 1. Converter ambos os DOCX para HTML (com o filtro Lua para comentários)
        convert_docx_to_html(original_docx, temp_original_html, LUA_FILTER_PATH)
        convert_docx_to_html(modified_docx, temp_modified_html, LUA_FILTER_PATH)

        with open(temp_original_html, 'r', encoding='utf-8') as f:
            html_orig_lines = f.readlines()
        with open(temp_modified_html, 'r', encoding='utf-8') as f:
            html_mod_lines = f.readlines()

        # 2. Usar difflib para comparar as linhas HTML
        d = difflib.Differ()
        diff_result = list(d.compare(html_orig_lines, html_mod_lines))

        # 3. Gerar o HTML final com as diferenças visuais
        html_output_lines = ['<!DOCTYPE html>', '<html>', '<head>', '<meta charset="utf-8">', '<title>Document Diff</title>']
        html_output_lines.append(f'<style>{CSS_CONTENT}</style>')
        html_output_lines.append('</head>')
        html_output_lines.append('<body>')
        html_output_lines.append('<div class="diff-header"><h1>Diferenças do Documento</h1></div>')
        html_output_lines.append('<pre>')

        for line in diff_result:
            if line.startswith('  '): # Linha inalterada
                html_output_lines.append(line[2:])
            elif line.startswith('+ '): # Linha adicionada
                html_output_lines.append(f'<span class="added">{line[2:].rstrip()}</span>\n')
            elif line.startswith('- '): # Linha removida
                html_output_lines.append(f'<span class="removed">{line[2:].rstrip()}</span>\n')
            elif line.startswith('? '):
                pass # Ignorar linhas de info do difflib para um diff mais limpo

        html_output_lines.append('</pre>')
        html_output_lines.append('</body>')
        html_output_lines.append('</html>')

        with open(output_html, 'w', encoding='utf-8') as f:
            f.writelines(html_output_lines)
            
        print(f"Diff HTML gerado em: {output_html}")

    finally:
        # Limpar arquivos temporários
        for temp_file in [temp_original_html, temp_modified_html]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Uso: python docx_diff_viewer.py <original.docx> <modificado.docx> <saida.html>")
        sys.exit(1)

    original_doc = sys.argv[1]
    modified_doc = sys.argv[2]
    output_html_file = sys.argv[3]

    if not os.path.exists(LUA_FILTER_PATH):
        print(f"ERRO: Filtro Lua não encontrado em '{LUA_FILTER_PATH}'. Verifique o caminho.")
        sys.exit(1)

    generate_diff_html(original_doc, modified_doc, output_html_file)