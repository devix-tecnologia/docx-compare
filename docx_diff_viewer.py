import subprocess
import os
import difflib
import sys
import html
import re
from config import OUTPUTS_DIR, LUA_FILTER_PATH

# --- Configuração ---
# LUA_FILTER_PATH já vem do config.py 

# CSS melhorado para estilizar as diferenças
CSS_CONTENT = """
body { 
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; 
    line-height: 1.6; 
    margin: 20px auto; 
    max-width: 1200px; 
    background-color: #f8f9fa; 
    color: #343a40; 
    box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
    padding: 30px; 
    border-radius: 8px; 
}
h1, h2, h3, h4, h5, h6 { 
    color: #212529; 
    margin-top: 1.5em; 
    margin-bottom: 0.5em; 
}
.diff-header { 
    background-color: #e9ecef; 
    padding: 15px 20px; 
    border-bottom: 1px solid #dee2e6; 
    margin: -30px -30px 20px -30px; 
    border-top-left-radius: 8px; 
    border-top-right-radius: 8px; 
    font-size: 1.2em; 
    color: #495057; 
    text-align: center; 
}
.diff-content {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    margin-top: 20px;
}
.added { 
    background-color: #d4edda; 
    color: #155724; 
    font-weight: bold; 
    padding: 8px 12px; 
    border-radius: 4px; 
    text-decoration: none;
    border-left: 4px solid #28a745;
    margin: 8px 0;
    display: block;
}
.removed { 
    background-color: #f8d7da; 
    color: #721c24; 
    text-decoration: line-through; 
    padding: 8px 12px; 
    border-radius: 4px;
    border-left: 4px solid #dc3545;
    margin: 8px 0;
    display: block;
}
.changed-old { 
    background-color: #fff3cd; 
    color: #856404; 
    text-decoration: line-through; 
    padding: 0.1em 0.3em; 
    border-radius: 3px; 
}
.changed-new { 
    background-color: #fff3cd; 
    color: #856404; 
    font-weight: bold; 
    padding: 0.1em 0.3em; 
    border-radius: 3px; 
}
.commented-text-container { 
    border-bottom: 2px dotted #007bff; 
    cursor: help; 
    position: relative; 
    display: inline-block; 
}
.inserted-comment-info { 
    font-family: monospace; 
    font-size: 0.8em; 
    color: #6c757d; 
    margin-left: 0.5em; 
    padding: 0.2em 0.5em; 
    border-left: 3px solid #17a2b8; 
    background-color: #eaf6f9; 
    border-radius: 4px; 
    white-space: normal; 
    display: inline-block; 
}
.inserted-comment-info strong { 
    color: #0056b3; 
    font-weight: bold; 
}
.inserted-comment-info em { 
    font-style: italic; 
    color: #495057; 
}
p { margin-bottom: 1em; }
ul, ol { margin-left: 20px; margin-bottom: 1em; }
table { width: 100%; border-collapse: collapse; margin-bottom: 1em; }
th, td { border: 1px solid #dee2e6; padding: 8px; text-align: left; }
th { background-color: #e9ecef; }
a { color: #007bff; text-decoration: none; }
a:hover { text-decoration: underline; }
.diff-stats {
    background-color: #e3f2fd;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 20px;
    font-size: 0.9em;
}
.diff-stats .added-count { color: #2e7d32; }
.diff-stats .removed-count { color: #c62828; }
"""

def clean_html_for_diff(html_content):
    """Remove tags HTML desnecessárias e normaliza o conteúdo para comparação."""
    # Remove quebras de linha desnecessárias
    html_content = re.sub(r'\n\s*\n', '\n', html_content)
    # Remove espaços extras
    html_content = re.sub(r'\s+', ' ', html_content)
    # Remove tags HTML específicas que podem causar ruído na comparação
    html_content = re.sub(r'</?html[^>]*>', '', html_content)
    html_content = re.sub(r'</?head[^>]*>', '', html_content)
    html_content = re.sub(r'</?body[^>]*>', '', html_content)
    html_content = re.sub(r'<meta[^>]*>', '', html_content)
    html_content = re.sub(r'<title[^>]*>.*?</title>', '', html_content)
    
    return html_content.strip()

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

def extract_body_content(html_file):
    """Extrai apenas o conteúdo do body do HTML."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrai o conteúdo entre as tags body
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    if body_match:
        return body_match.group(1).strip()
    return content

def html_to_text(html_content):
    """Converte HTML para texto limpo, preservando estrutura básica."""
    import re
    
    # Remove comentários HTML
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Converte tags de formatação para texto simples
    html_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\1', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<b[^>]*>(.*?)</b>', r'\1', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<em[^>]*>(.*?)</em>', r'\1', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<i[^>]*>(.*?)</i>', r'\1', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<u[^>]*>(.*?)</u>', r'\1', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<mark[^>]*>(.*?)</mark>', r'\1', html_content, flags=re.DOTALL)
    
    # Converte listas para texto simples
    html_content = re.sub(r'<ol[^>]*>', '\n', html_content)
    html_content = re.sub(r'</ol>', '\n', html_content)
    html_content = re.sub(r'<ul[^>]*>', '\n', html_content)
    html_content = re.sub(r'</ul>', '\n', html_content)
    html_content = re.sub(r'<li[^>]*>', '• ', html_content)
    html_content = re.sub(r'</li>', '\n', html_content)
    
    # Converte blockquotes
    html_content = re.sub(r'<blockquote[^>]*>', '\n    ', html_content)
    html_content = re.sub(r'</blockquote>', '\n', html_content)
    
    # Converte quebras de linha e parágrafos
    html_content = re.sub(r'<br[^>]*/?>', '\n', html_content)
    html_content = re.sub(r'</p>', '\n\n', html_content)
    html_content = re.sub(r'<p[^>]*>', '', html_content)
    
    # Remove todas as outras tags HTML restantes
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Decodifica entidades HTML
    html_content = html_content.replace('&lt;', '<')
    html_content = html_content.replace('&gt;', '>')
    html_content = html_content.replace('&amp;', '&')
    html_content = html_content.replace('&quot;', '"')
    html_content = html_content.replace('&apos;', "'")
    html_content = html_content.replace('&nbsp;', ' ')
    html_content = html_content.replace('&mdash;', '—')
    html_content = html_content.replace('&ndash;', '–')
    
    # Limpa espaços e quebras de linha excessivos
    html_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', html_content)
    html_content = re.sub(r'[ \t]+', ' ', html_content)
    html_content = re.sub(r' +\n', '\n', html_content)
    html_content = re.sub(r'\n +', '\n', html_content)
    
    return html_content.strip()


def generate_diff_html(original_docx, modified_docx, output_html):
    temp_original_html = "original_temp.html"
    temp_modified_html = "modified_temp.html"
    
    try:
        # 1. Converter ambos os DOCX para HTML
        convert_docx_to_html(original_docx, temp_original_html, LUA_FILTER_PATH)
        convert_docx_to_html(modified_docx, temp_modified_html, LUA_FILTER_PATH)

        # 2. Extrair apenas o conteúdo do body
        original_content = extract_body_content(temp_original_html)
        modified_content = extract_body_content(temp_modified_html)

        # 3. Converter HTML para texto limpo
        original_text = html_to_text(original_content)
        modified_text = html_to_text(modified_content)

        # 4. Dividir em parágrafos para melhor comparação
        original_paragraphs = [p.strip() for p in original_text.split('\n\n') if p.strip()]
        modified_paragraphs = [p.strip() for p in modified_text.split('\n\n') if p.strip()]

        # 5. Usar difflib para comparar os parágrafos
        d = difflib.unified_diff(
            original_paragraphs, 
            modified_paragraphs, 
            fromfile='Original', 
            tofile='Modificado', 
            lineterm=''
        )
        
        # Converter para lista para poder contar
        diff_lines = list(d)
        
        # Contar adições e remoções
        added_count = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed_count = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))

        # 6. Gerar HTML final
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n')
            f.write('<html lang="pt-br">\n')
            f.write('<head>\n')
            f.write('<meta charset="utf-8">\n')
            f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
            f.write('<title>Comparação de Documentos</title>\n')
            f.write(f'<style>{CSS_CONTENT}</style>\n')
            f.write('</head>\n')
            f.write('<body>\n')
            f.write('<div class="diff-header">\n')
            f.write('<h1>Comparação de Documentos</h1>\n')
            f.write(f'<p><strong>Original:</strong> {os.path.basename(original_docx)} | ')
            f.write(f'<strong>Modificado:</strong> {os.path.basename(modified_docx)}</p>\n')
            f.write('</div>\n')
            
            f.write('<div class="diff-stats">\n')
            f.write(f'<strong>Estatísticas:</strong> ')
            f.write(f'<span class="added-count">+{added_count} adições</span> | ')
            f.write(f'<span class="removed-count">-{removed_count} remoções</span>\n')
            f.write('</div>\n')
            
            f.write('<div class="diff-content">\n')
            
            # Regenerar o diff para exibição
            d = difflib.unified_diff(
                original_paragraphs, 
                modified_paragraphs, 
                fromfile='Original', 
                tofile='Modificado', 
                lineterm=''
            )
            
            for line in d:
                if line.startswith('@@') or line.startswith('---') or line.startswith('+++'):
                    continue
                elif line.startswith('+'):
                    content = html.escape(line[1:])
                    f.write(f'<p class="added">{content}</p>\n')
                elif line.startswith('-'):
                    content = html.escape(line[1:])
                    f.write(f'<p class="removed">{content}</p>\n')
                elif line.startswith(' '):
                    content = html.escape(line[1:])
                    f.write(f'<p>{content}</p>\n')
            
            f.write('</div>\n')
            f.write('</body>\n')
            f.write('</html>\n')
            
        print(f"Diff HTML gerado em: {output_html}")

    finally:
        # Limpar arquivos temporários
        for temp_file in [temp_original_html, temp_modified_html]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Uso: python docx_diff_viewer.py <original.docx> <modificado.docx> [saida.html]")
        print("Se saida.html não for especificado, será criado em outputs/resultado.html")
        sys.exit(1)

    original_doc = sys.argv[1]
    modified_doc = sys.argv[2]
    
    # Se output não foi especificado, usar pasta outputs com nome padrão
    if len(sys.argv) == 3:
        output_html_file = os.path.join(OUTPUTS_DIR, "resultado.html")
    else:
        output_html_file = sys.argv[3]
        # Se o caminho não é absoluto e não contém pasta, colocar em outputs
        if not os.path.isabs(output_html_file) and os.path.dirname(output_html_file) == "":
            output_html_file = os.path.join(OUTPUTS_DIR, output_html_file)

    if not os.path.exists(LUA_FILTER_PATH):
        print(f"ERRO: Filtro Lua não encontrado em '{LUA_FILTER_PATH}'. Verifique o caminho.")
        sys.exit(1)

    generate_diff_html(original_doc, modified_doc, output_html_file)