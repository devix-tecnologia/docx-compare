#!/usr/bin/env python3
"""
Utilidades para análise de texto e diferenças
Módulo comum para evitar duplicação de código entre os arquivos do projeto
"""

import difflib
import re


def html_to_text(html_content):
    """Converte HTML para texto limpo"""
    html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
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
    html_content = re.sub(
        r"<li[^>]*><p[^>]*>(.*?)</p></li>", r"• \1", html_content, flags=re.DOTALL
    )
    html_content = re.sub(
        r"<li[^>]*>(.*?)</li>", r"• \1", html_content, flags=re.DOTALL
    )
    html_content = re.sub(r"<ol[^>]*>|</ol>", "", html_content)
    html_content = re.sub(r"<ul[^>]*>|</ul>", "", html_content)
    html_content = re.sub(r"<blockquote[^>]*>|</blockquote>", "", html_content)
    html_content = re.sub(r"<p[^>]*>|</p>", "\n", html_content)
    html_content = re.sub(r"<br[^>]*/?>", "\n", html_content)
    html_content = re.sub(r"<[^>]+>", "", html_content)
    html_content = re.sub(r"&nbsp;", " ", html_content)
    html_content = re.sub(r"&amp;", "&", html_content)
    html_content = re.sub(r"&lt;", "<", html_content)
    html_content = re.sub(r"&gt;", ">", html_content)
    html_content = re.sub(r"&quot;", '"', html_content)
    html_content = re.sub(r"\n\s*\n", "\n", html_content)
    return html_content.strip()


def analyze_differences_detailed(original_text, modified_text):
    """Analisa as diferenças e retorna modificações detalhadas"""
    original_lines = original_text.split("\n")
    modified_lines = modified_text.split("\n")

    diff = list(
        difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile="Original",
            tofile="Modificado",
            lineterm="",
        )
    )

    modifications = []
    modification_count = 1

    i = 0
    while i < len(diff):
        line = diff[i]

        if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            i += 1
            continue
        elif line.startswith("-"):
            # Linha removida
            original_content = line[1:].strip()
            if original_content:  # Ignorar linhas vazias
                # Calcular posição no texto original
                linha_aprox = _calculate_line_position(original_text, original_content)
                pos_inicio = _calculate_text_position(original_text, original_content)
                pos_fim = pos_inicio + len(original_content)

                # Verificar se a próxima linha é uma adição (modificação)
                if i + 1 < len(diff) and diff[i + 1].startswith("+"):
                    modified_content = diff[i + 1][1:].strip()
                    modifications.append(
                        {
                            "categoria": "modificacao",
                            "conteudo": original_content,
                            "alteracao": modified_content,
                            "sort": modification_count,
                            "caminho_inicio": f"modificacao_{modification_count}_linha_{linha_aprox}_pos_{pos_inicio}",
                            "caminho_fim": f"modificacao_{modification_count}_linha_{linha_aprox}_pos_{pos_fim}",
                            "posicao_inicio": pos_inicio,
                            "posicao_fim": pos_fim,
                        }
                    )
                    i += 2  # Pular a próxima linha pois já processamos
                else:
                    # Apenas remoção
                    modifications.append(
                        {
                            "categoria": "remocao",
                            "conteudo": original_content,
                            "alteracao": "",
                            "sort": modification_count,
                            "caminho_inicio": f"modificacao_{modification_count}_linha_{linha_aprox}_pos_{pos_inicio}",
                            "caminho_fim": f"modificacao_{modification_count}_linha_{linha_aprox}_pos_{pos_fim}",
                            "posicao_inicio": pos_inicio,
                            "posicao_fim": pos_fim,
                        }
                    )
                    i += 1
                modification_count += 1
        elif line.startswith("+"):
            # Linha adicionada (que não foi processada como modificação)
            added_content = line[1:].strip()
            if added_content:  # Ignorar linhas vazias
                # Para adições, calcular posição no texto modificado
                linha_aprox = _calculate_line_position(modified_text, added_content)
                pos_inicio = _calculate_text_position(modified_text, added_content)
                pos_fim = pos_inicio + len(added_content)

                modifications.append(
                    {
                        "categoria": "adicao",
                        "conteudo": "",
                        "alteracao": added_content,
                        "sort": modification_count,
                        "caminho_inicio": f"modificacao_{modification_count}_linha_{linha_aprox}_pos_{pos_inicio}",
                        "caminho_fim": f"modificacao_{modification_count}_linha_{linha_aprox}_pos_{pos_fim}",
                        "posicao_inicio": pos_inicio,
                        "posicao_fim": pos_fim,
                    }
                )
                modification_count += 1
            i += 1
        else:
            i += 1

    return modifications


def _calculate_line_position(text: str, content: str) -> int:
    """Calcula a linha aproximada onde o conteúdo aparece no texto"""
    try:
        pos = text.find(content)
        if pos != -1:
            return text[:pos].count("\n") + 1
    except Exception:
        pass
    return 1


def _calculate_text_position(text: str, content: str) -> int:
    """Calcula a posição do caractere no texto"""
    try:
        pos = text.find(content)
        return pos if pos != -1 else 0
    except Exception:
        return 0


def analyze_differences_for_directus(original_text, modified_text):
    """
    Versão compatível com API simples - retorna análise de diferenças
    para compatibilidade com código existente
    """
    return analyze_differences_detailed(original_text, modified_text)


def analyze_differences(original_text: str, modified_text: str) -> dict:
    """
    Versão compatível com docx_utils - retorna análise em formato dict
    para compatibilidade com código existente
    """
    modifications = analyze_differences_detailed(original_text, modified_text)

    # Contar tipos de modificações
    adicoes = sum(1 for mod in modifications if mod["categoria"] == "adicao")
    remocoes = sum(1 for mod in modifications if mod["categoria"] == "remocao")
    modificacoes = sum(1 for mod in modifications if mod["categoria"] == "modificacao")

    # Converter para formato esperado pelo docx_diff_viewer
    modifications_for_viewer = []
    for mod in modifications:
        mod_dict = {
            "original": mod["conteudo"],
            "modified": mod["alteracao"],
            "caminho_inicio": mod["caminho_inicio"],
            "caminho_fim": mod["caminho_fim"],
            "posicao_inicio": mod["posicao_inicio"],
            "posicao_fim": mod["posicao_fim"],
            "categoria": mod["categoria"],
            "sort": mod["sort"],
        }
        modifications_for_viewer.append(mod_dict)

    return {
        "total_modifications": len(modifications),
        "total_additions": adicoes,
        "total_deletions": remocoes,
        "total_changes": modificacoes,
        "additions": adicoes,
        "deletions": remocoes,
        "modifications": modifications_for_viewer,
        "details": modifications,
    }
