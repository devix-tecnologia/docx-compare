#!/usr/bin/env python3
"""
Testes para o módulo docx_utils.

Testa todas as funcionalidades centralizadas do módulo docx_utils
para garantir compatibilidade e funcionamento correto.
"""

import os
import sys
import unittest

# Adicionar o diretório pai ao path para importar docx_utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docx_utils import (
    analyze_differences,
    clean_html_for_diff,
    compare_docx_files,
    convert_docx_to_html_content,
    convert_docx_to_text,
    extract_body_content,
    generate_diff_lines,
    get_css_styles,
    html_to_text,
)


class TestDocxUtils(unittest.TestCase):
    """Testes para funcionalidades do módulo docx_utils."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.html_sample = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Título Principal</h1>
            <p>Este é um parágrafo com <strong>texto em negrito</strong>.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <blockquote>Esta é uma citação</blockquote>
        </body>
        </html>
        """

        self.text_sample_1 = "Linha 1\nLinha 2\nLinha 3"
        self.text_sample_2 = "Linha 1\nLinha 2 modificada\nLinha 3\nLinha 4"

    def test_clean_html_for_diff(self):
        """Testa limpeza de HTML para comparação."""
        html = (
            "<html><head><title>Test</title></head><body><p>Content</p></body></html>"
        )
        cleaned = clean_html_for_diff(html)

        self.assertNotIn("<html>", cleaned)
        self.assertNotIn("<head>", cleaned)
        self.assertNotIn("<title>", cleaned)
        self.assertIn("<p>Content</p>", cleaned)

    def test_extract_body_content(self):
        """Testa extração de conteúdo do body."""
        content = extract_body_content(self.html_sample)

        self.assertIn("Título Principal", content)
        self.assertIn("parágrafo", content)
        self.assertNotIn("<html>", content)
        self.assertNotIn("<head>", content)

    def test_html_to_text_simple(self):
        """Testa conversão simples de HTML para texto."""
        text = html_to_text(self.html_sample, preserve_structure=False)

        self.assertIn("Título Principal", text)
        self.assertIn("texto em negrito", text)
        self.assertNotIn("<h1>", text)
        self.assertNotIn("<strong>", text)

    def test_html_to_text_with_structure(self):
        """Testa conversão de HTML para texto preservando estrutura."""
        text = html_to_text(self.html_sample, preserve_structure=True)

        self.assertIn("Título Principal", text)
        self.assertIn("• Item 1", text)
        self.assertIn("• Item 2", text)
        self.assertNotIn("<li>", text)

    def test_analyze_differences(self):
        """Testa análise de diferenças entre textos."""
        stats = analyze_differences(self.text_sample_1, self.text_sample_2)

        self.assertIn("total_additions", stats)
        self.assertIn("total_deletions", stats)
        self.assertIn("total_modifications", stats)
        self.assertIn("modifications", stats)

        # Deve detectar adições e modificações
        self.assertGreater(stats["total_additions"], 0)
        self.assertGreater(stats["total_modifications"], 0)

    def test_generate_diff_lines(self):
        """Testa geração de linhas de diff."""
        diff_lines = generate_diff_lines(self.text_sample_1, self.text_sample_2)

        self.assertIsInstance(diff_lines, list)
        self.assertGreater(len(diff_lines), 0)

        # Deve conter linhas de diff
        has_addition = any(line.startswith("+") for line in diff_lines)
        has_deletion = any(line.startswith("-") for line in diff_lines)
        self.assertTrue(has_addition or has_deletion)

    def test_get_css_styles(self):
        """Testa obtenção de estilos CSS."""
        # Testa estilo padrão
        css_default = get_css_styles("default")
        self.assertIn("body", css_default)
        self.assertIn(".added", css_default)

        # Testa estilo minimal
        css_minimal = get_css_styles("minimal")
        self.assertIn("body", css_minimal)
        self.assertLess(len(css_minimal), len(css_default))

        # Testa estilo modern
        css_modern = get_css_styles("modern")
        self.assertIn("body", css_modern)
        self.assertIn("gradient", css_modern)

    def test_docx_conversion_with_real_files(self):
        """Testa conversão com arquivos DOCX reais (se disponíveis)."""
        test_file = "documentos/doc-rafael-original.docx"

        if os.path.exists(test_file):
            # Testa conversão para texto
            text = convert_docx_to_text(test_file)
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 0)

            # Testa conversão para HTML
            html = convert_docx_to_html_content(test_file)
            self.assertIsInstance(html, str)
            self.assertGreater(len(html), 0)
            self.assertIn("<html>", html)
        else:
            self.skipTest("Arquivo de teste DOCX não encontrado")

    def test_compare_docx_files_with_real_files(self):
        """Testa comparação completa com arquivos DOCX reais."""
        file1 = "documentos/doc-rafael-original.docx"
        file2 = "documentos/doc-rafael-alterado.docx"

        if os.path.exists(file1) and os.path.exists(file2):
            original_text, modified_text, stats = compare_docx_files(file1, file2)

            self.assertIsInstance(original_text, str)
            self.assertIsInstance(modified_text, str)
            self.assertIsInstance(stats, dict)

            self.assertIn("total_additions", stats)
            self.assertIn("total_deletions", stats)
            self.assertIn("total_modifications", stats)
        else:
            self.skipTest("Arquivos de teste DOCX não encontrados")

    def test_css_injection_safety(self):
        """Testa segurança contra injeção de CSS."""
        # Testa com entrada inválida
        css = get_css_styles("invalid_style")
        self.assertIsInstance(css, str)
        # Deve retornar estilo padrão para entrada inválida
        self.assertIn("body", css)

    def test_html_content_sanitization(self):
        """Testa sanitização de conteúdo HTML."""
        malicious_html = """
        <script>alert('xss')</script>
        <p>Conteúdo legítimo</p>
        <img src="x" onerror="alert('xss')">
        """

        cleaned_text = html_to_text(malicious_html, preserve_structure=False)

        # Não deve conter scripts
        self.assertNotIn("<script>", cleaned_text)
        self.assertNotIn("alert", cleaned_text)
        # Mas deve preservar conteúdo legítimo
        self.assertIn("Conteúdo legítimo", cleaned_text)


def run_performance_test():
    """Executa teste de performance das funções principais."""
    print("\n🚀 Executando testes de performance...")

    import time

    # Teste com arquivos reais se disponíveis
    test_file = "documentos/doc-rafael-original.docx"

    if os.path.exists(test_file):
        # Teste de conversão para texto
        start_time = time.time()
        text = convert_docx_to_text(test_file)
        text_time = time.time() - start_time
        print(f"📄 Conversão para texto: {text_time:.3f}s ({len(text)} chars)")

        # Teste de conversão para HTML
        start_time = time.time()
        html = convert_docx_to_html_content(test_file)
        html_time = time.time() - start_time
        print(f"🌐 Conversão para HTML: {html_time:.3f}s ({len(html)} chars)")

        # Teste de limpeza HTML
        start_time = time.time()
        clean_text = html_to_text(html, preserve_structure=True)
        clean_time = time.time() - start_time
        print(f"🔧 Limpeza HTML: {clean_time:.3f}s ({len(clean_text)} chars)")

    else:
        print("⚠️  Arquivo de teste não encontrado para performance")


if __name__ == "__main__":
    print("🧪 Executando testes do módulo docx_utils")
    print("=" * 50)

    # Executar testes unitários
    unittest.main(verbosity=2, exit=False)

    # Executar teste de performance
    run_performance_test()

    print("\n✅ Testes concluídos!")
