"""
Utilitários comuns para processamento de documentos DOCX e comparação.

Este módulo contém funcionalidades compartilhadas entre api_server.py e docx_diff_viewer.py:
- Conversão de DOCX para HTML/texto
- Processamento e limpeza de HTML
- Estilos CSS para relatórios de comparação
- Análise de diferenças entre documentos
"""

import difflib
import html
import os
import re
import subprocess


def sanitize_html_for_csp(html_content: str) -> str:
    """
    Sanitiza HTML para compatibilidade com Content Security Policy (CSP).

    Move estilos inline para um bloco <style> no cabeçalho, mantendo a aparência
    visual mas removendo violações de CSP.

    Args:
        html_content: Conteúdo HTML original

    Returns:
        HTML sanitizado compatível com CSP
    """
    # Primeiro, garantir que não há nenhum estilo inline
    # Regex mais agressiva para encontrar todos os tipos de estilos inline
    style_patterns = [
        r'style\s*=\s*["\'][^"\']*["\']',  # style="..." ou style='...'
        r'style\s*=\s*[^"\'\s>][^\s>]*',  # style=valor sem aspas
    ]

    sanitized_content = html_content

    # Remover todos os estilos inline encontrados
    for pattern in style_patterns:
        sanitized_content = re.sub(pattern, "", sanitized_content, flags=re.IGNORECASE)

    # Remover atributos que podem causar problemas de CSP
    unsafe_attributes = [
        r'onclick\s*=\s*["\'][^"\']*["\']',
        r'onload\s*=\s*["\'][^"\']*["\']',
        r'onerror\s*=\s*["\'][^"\']*["\']',
        r'onmouseover\s*=\s*["\'][^"\']*["\']',
        r'href\s*=\s*["\']javascript:[^"\']*["\']',
    ]

    for pattern in unsafe_attributes:
        sanitized_content = re.sub(pattern, "", sanitized_content, flags=re.IGNORECASE)

    # Adicionar meta tags de CSP para melhor compatibilidade
    csp_meta = """<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'none';">"""

    # Inserir meta CSP no cabeçalho
    if "<head>" in sanitized_content:
        sanitized_content = sanitized_content.replace("<head>", f"<head>\n{csp_meta}")
    elif "<meta charset=" in sanitized_content:
        # Se não há <head> mas há charset, inserir após charset
        sanitized_content = re.sub(
            r"(<meta charset=[^>]*>)", f"\\1\n{csp_meta}", sanitized_content
        )

    return sanitized_content


# CSS padrão para relatórios de comparação
DEFAULT_CSS = """
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
.diff-stats {
    background-color: #e3f2fd;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 20px;
    font-size: 0.9em;
}
.diff-stats .added-count { color: #2e7d32; }
.diff-stats .removed-count { color: #c62828; }
.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.header {
    border-bottom: 3px solid #007acc;
    padding-bottom: 20px;
    margin-bottom: 30px;
}
.title {
    color: #007acc;
    font-size: 28px;
    font-weight: bold;
    margin: 0;
}
.subtitle {
    color: #666;
    font-size: 16px;
    margin: 5px 0 0 0;
}
.statistics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 30px 0;
}
.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}
.stat-number {
    font-size: 2em;
    font-weight: bold;
    display: block;
}
.stat-label {
    font-size: 0.9em;
    opacity: 0.9;
}
.comparison-section {
    margin: 30px 0;
}
.section-title {
    color: #333;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #eee;
}
.diff-container {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    max-height: 400px;
    overflow-y: auto;
}
.diff-line {
    margin: 2px 0;
    padding: 2px 5px;
    border-radius: 3px;
}
.diff-added {
    background-color: #d4edda;
    color: #155724;
    border-left: 4px solid #28a745;
}
.diff-removed {
    background-color: #f8d7da;
    color: #721c24;
    border-left: 4px solid #dc3545;
}
.diff-context {
    color: #6c757d;
}
.modifications-list {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    overflow: hidden;
}
.modification-item {
    padding: 15px;
    border-bottom: 1px solid #eee;
}
.modification-item:last-child {
    border-bottom: none;
}
.modification-original {
    background: #fff3cd;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 5px 0;
    border-left: 4px solid #ffc107;
}
.modification-new {
    background: #d1ecf1;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 5px 0;
    border-left: 4px solid #17a2b8;
}
.timestamp {
    color: #6c757d;
    font-size: 14px;
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}
p { margin-bottom: 1em; }
ul, ol { margin-left: 20px; margin-bottom: 1em; }
table { width: 100%; border-collapse: collapse; margin-bottom: 1em; }
th, td { border: 1px solid #dee2e6; padding: 8px; text-align: left; }
th { background-color: #e9ecef; }
a { color: #007bff; text-decoration: none; }
a:hover { text-decoration: underline; }
"""


def clean_html_for_diff(html_content: str) -> str:
    """Remove tags HTML desnecessárias e normaliza o conteúdo para comparação."""
    # Remove quebras de linha desnecessárias
    html_content = re.sub(r"\n\s*\n", "\n", html_content)
    # Remove espaços extras
    html_content = re.sub(r"\s+", " ", html_content)
    # Remove tags HTML específicas que podem causar ruído na comparação
    html_content = re.sub(r"</?html[^>]*>", "", html_content)
    html_content = re.sub(r"</?head[^>]*>", "", html_content)
    html_content = re.sub(r"</?body[^>]*>", "", html_content)
    html_content = re.sub(r"<meta[^>]*>", "", html_content)
    html_content = re.sub(r"<title[^>]*>.*?</title>", "", html_content)

    return html_content.strip()


def convert_docx_to_html(
    docx_path: str, output_html_path: str, lua_filter_path: str | None = None
) -> None:
    """Converte um DOCX para HTML usando Pandoc com filtro Lua opcional."""

    cmd = [
        "pandoc",
        docx_path,
        "--to=html",
        "--track-changes=all",
        f"-o{output_html_path}",
    ]

    if lua_filter_path and os.path.exists(lua_filter_path):
        cmd.insert(-1, f"--lua-filter={lua_filter_path}")

    print(f"Executando: {' '.join(cmd)}")
    print(f"📁 Tamanho do arquivo: {os.path.getsize(docx_path)} bytes")

    try:
        import time

        start_time = time.time()
        print(f"⏰ Iniciando pandoc às {time.strftime('%H:%M:%S')}")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )  # Reduzir para 30 segundos
        end_time = time.time()
        print(f"✅ Pandoc concluído em {end_time - start_time:.2f} segundos")
        if result.returncode != 0:
            print(f"Erro ao converter {docx_path}:")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            raise RuntimeError(f"Erro no Pandoc para {docx_path}: {result.stderr}")

        # Remove estilos inline do arquivo gerado para compatibilidade com CSP
        if os.path.exists(output_html_path):
            with open(output_html_path, encoding="utf-8") as f:
                content = f.read()

            content = remove_inline_styles(content)

            with open(output_html_path, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"Convertido {docx_path} para {output_html_path}")

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Timeout na conversão do arquivo {docx_path}")
    except Exception as e:
        raise RuntimeError(f"Erro na conversão: {e}")


def convert_docx_to_text(docx_path: str) -> str:
    """Converte um DOCX para texto usando Pandoc."""

    try:
        cmd = ["pandoc", docx_path, "-t", "plain"]
        print(f"Executando: {' '.join(cmd)}")
        print(f"📁 Tamanho do arquivo: {os.path.getsize(docx_path)} bytes")
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", timeout=120
        )  # Aumentar para 2 minutos
        if result.returncode != 0:
            raise Exception(f"Erro ao converter {docx_path}: {result.stderr}")
        return result.stdout

    except subprocess.TimeoutExpired:
        raise Exception(f"Timeout na conversão do arquivo {docx_path}")
    except Exception as e:
        raise Exception(f"Erro na conversão: {e}")


def remove_inline_styles(html_content: str) -> str:
    """
    Remove estilos inline do HTML para compatibilidade com Content Security Policy (CSP).

    Args:
        html_content: Conteúdo HTML que pode conter atributos style=""

    Returns:
        HTML limpo sem estilos inline
    """
    # Remove todos os atributos style=""
    html_content = re.sub(
        r'\s+style\s*=\s*["\'][^"\']*["\']', "", html_content, flags=re.IGNORECASE
    )

    # Remove estilos CSS inline das tags <style> que podem ter sido gerados pelo Pandoc
    # Mas mantém nossos estilos CSS customizados
    html_content = re.sub(
        r"<style[^>]*>.*?</style>", "", html_content, flags=re.DOTALL | re.IGNORECASE
    )

    return html_content


def convert_docx_to_html_content(
    docx_path: str, lua_filter_path: str | None = None
) -> str:
    """Converte um DOCX para HTML e retorna o conteúdo como string."""
    cmd = ["pandoc", docx_path, "-t", "html", "--standalone"]

    if lua_filter_path and os.path.exists(lua_filter_path):
        cmd.extend(["--lua-filter", lua_filter_path])

    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    if result.returncode != 0:
        raise Exception(f"Erro ao converter {docx_path}: {result.stderr}")

    # Remove estilos inline para compatibilidade com CSP
    html_content = result.stdout
    html_content = remove_inline_styles(html_content)

    return html_content


def extract_body_content(html_content: str) -> str:
    """Extrai apenas o conteúdo do body do HTML."""
    # Se é um arquivo, lê o conteúdo
    if os.path.exists(html_content):
        with open(html_content, encoding="utf-8") as f:
            content = f.read()
    else:
        content = html_content

    # Extrai o conteúdo entre as tags body
    body_match = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL)
    if body_match:
        return body_match.group(1).strip()
    return content


def html_to_text(html_content: str, preserve_structure: bool = True) -> str:
    """
    Converte HTML para texto limpo.

    Args:
        html_content: Conteúdo HTML para converter
        preserve_structure: Se True, preserva estrutura básica (listas, parágrafos)
                           Se False, remove todas as tags e retorna texto simples
    """
    if preserve_structure:
        return _html_to_text_with_structure(html_content)
    else:
        return _html_to_text_simple(html_content)


def _html_to_text_simple(html_content: str) -> str:
    """Remove todas as tags HTML e retorna apenas o texto."""
    # Remove todas as tags HTML
    text = re.sub(r"<[^>]+>", "", html_content)
    # Decodifica entidades HTML
    text = html.unescape(text)
    # Remove espaços extras
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _html_to_text_with_structure(html_content: str) -> str:
    """Converte HTML para texto limpo, preservando estrutura básica."""
    # Remove comentários HTML
    html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)

    # Converte tags de formatação para texto simples
    html_content = re.sub(
        r"<strong[^>]*>(.*?)</strong>", r"\1", html_content, flags=re.DOTALL
    )
    html_content = re.sub(r"<b[^>]*>(.*?)</b>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(r"<em[^>]*>(.*?)</em>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(r"<i[^>]*>(.*?)</i>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(r"<u[^>]*>(.*?)</u>", r"\1", html_content, flags=re.DOTALL)
    html_content = re.sub(
        r"<mark[^>]*>(.*?)</mark>", r"\1", html_content, flags=re.DOTALL
    )

    # Converte listas para texto simples
    html_content = re.sub(r"<ol[^>]*>", "\n", html_content)
    html_content = re.sub(r"</ol>", "\n", html_content)
    html_content = re.sub(r"<ul[^>]*>", "\n", html_content)
    html_content = re.sub(r"</ul>", "\n", html_content)
    html_content = re.sub(r"<li[^>]*>", "• ", html_content)
    html_content = re.sub(r"</li>", "\n", html_content)

    # Converte blockquotes
    html_content = re.sub(r"<blockquote[^>]*>", "\n    ", html_content)
    html_content = re.sub(r"</blockquote>", "\n", html_content)

    # Converte quebras de linha e parágrafos
    html_content = re.sub(r"<br[^>]*/?>", "\n", html_content)
    html_content = re.sub(r"</p>", "\n\n", html_content)
    html_content = re.sub(r"<p[^>]*>", "", html_content)

    # Remove todas as outras tags HTML restantes
    html_content = re.sub(r"<[^>]+>", "", html_content)

    # Decodifica entidades HTML
    html_content = html_content.replace("&lt;", "<")
    html_content = html_content.replace("&gt;", ">")
    html_content = html_content.replace("&amp;", "&")
    html_content = html_content.replace("&quot;", '"')
    html_content = html_content.replace("&apos;", "'")
    html_content = html_content.replace("&nbsp;", " ")
    html_content = html_content.replace("&mdash;", "—")
    html_content = html_content.replace("&ndash;", "–")

    # Limpa espaços e quebras de linha excessivos
    html_content = re.sub(r"\n\s*\n\s*\n+", "\n\n", html_content)
    html_content = re.sub(r"[ \t]+", " ", html_content)
    html_content = re.sub(r" +\n", "\n", html_content)
    html_content = re.sub(r"\n +", "\n", html_content)

    return html_content.strip()


def analyze_differences(original_text: str, modified_text: str) -> dict:
    """Analisa as diferenças e extrai estatísticas detalhadas."""
    original_lines = original_text.splitlines()
    modified_lines = modified_text.splitlines()

    differ = difflib.unified_diff(original_lines, modified_lines, lineterm="")
    changes = list(differ)

    additions = sum(
        1 for line in changes if line.startswith("+") and not line.startswith("+++")
    )
    deletions = sum(
        1 for line in changes if line.startswith("-") and not line.startswith("---")
    )

    # Encontrar modificações específicas
    modifications = []
    i = 0
    while i < len(changes):
        if changes[i].startswith("-") and not changes[i].startswith("---"):
            original_line = changes[i][1:].strip()
            if (
                i + 1 < len(changes)
                and changes[i + 1].startswith("+")
                and not changes[i + 1].startswith("+++")
            ):
                modified_line = changes[i + 1][1:].strip()
                if original_line and modified_line:
                    modifications.append(
                        {"original": original_line, "modified": modified_line}
                    )
                i += 2
            else:
                i += 1
        else:
            i += 1

    return {
        "total_additions": additions,
        "total_deletions": deletions,
        "total_modifications": len(modifications),
        "modifications": modifications[:10],  # Limitar a 10 exemplos
    }


def generate_diff_lines(
    original_text: str, modified_text: str, context_lines: int = 3
) -> list[str]:
    """Gera linhas de diff entre dois textos."""
    original_lines = original_text.split("\n")
    modified_lines = modified_text.split("\n")

    differ = difflib.unified_diff(
        original_lines, modified_lines, lineterm="", n=context_lines
    )
    return list(differ)


def compare_docx_files(file1_path: str, file2_path: str) -> tuple[str, str, dict]:
    """
    Compara dois arquivos DOCX usando pandoc e retorna o resultado.

    Returns:
        Tuple contendo:
        - original_text: Texto do arquivo original
        - modified_text: Texto do arquivo modificado
        - statistics: Dicionário com estatísticas da comparação
    """
    try:
        # Converter arquivos para texto
        original_text = convert_docx_to_text(file1_path)
        modified_text = convert_docx_to_text(file2_path)

        # Analisar diferenças
        statistics = analyze_differences(original_text, modified_text)

        return original_text, modified_text, statistics

    except Exception as e:
        raise Exception(f"Erro na comparação: {e}")


def get_css_styles(style_type: str = "default") -> str:
    """
    Retorna estilos CSS para relatórios de comparação.

    Args:
        style_type: Tipo de estilo ("default", "minimal", "modern")
    """
    if style_type == "default":
        return DEFAULT_CSS
    elif style_type == "minimal":
        return _get_minimal_css()
    elif style_type == "modern":
        return _get_modern_css()
    else:
        return DEFAULT_CSS


def _get_minimal_css() -> str:
    """CSS minimalista para relatórios."""
    return """
body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
.added { background-color: #d4edda; color: #155724; padding: 4px; }
.removed { background-color: #f8d7da; color: #721c24; text-decoration: line-through; padding: 4px; }
.diff-stats { background-color: #f0f0f0; padding: 10px; margin-bottom: 20px; }
"""


def _get_modern_css() -> str:
    """CSS moderno para relatórios."""
    return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}
.container {
    max-width: 1000px; margin: 0 auto; background: white; border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden;
}
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; padding: 40px; text-align: center;
}
.added {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    color: #155724; padding: 12px; border-radius: 8px; margin: 8px 0;
    border-left: 4px solid #28a745; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.removed {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    color: #721c24; padding: 12px; border-radius: 8px; margin: 8px 0;
    border-left: 4px solid #dc3545; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
"""


# Backwards compatibility - aliases para funções antigas
docx_to_text = convert_docx_to_text
docx_to_html = convert_docx_to_html_content
