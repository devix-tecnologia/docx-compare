#!/usr/bin/env python3
"""
Testes para a funcionalidade dry-run do docx_diff_viewer.py

Valida que o modo dry-run funciona corretamente sem gerar arquivos.
"""

import os
import subprocess
import sys
import tempfile
import unittest

# Adicionar o diretório src ao path para importar módulos
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, os.path.join(project_root, "src"))


class TestDryRun(unittest.TestCase):
    """Testes para funcionalidade dry-run do CLI."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Caminho para o projeto root
        self.project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        # Arquivos de teste relativos ao projeto root
        self.original_file = os.path.join(
            self.project_root, "documentos", "doc-rafael-original.docx"
        )
        self.modified_file = os.path.join(
            self.project_root, "documentos", "doc-rafael-alterado.docx"
        )

        # Verificar se arquivos de teste existem
        self.files_exist = os.path.exists(self.original_file) and os.path.exists(
            self.modified_file
        )

    def run_cli_command(self, args):
        """Helper para executar comandos do CLI."""
        cmd = [sys.executable, "-m", "docx_compare.core.docx_diff_viewer"] + args
        env = {**os.environ, "PYTHONPATH": os.path.join(self.project_root, "src")}
        return subprocess.run(
            cmd, capture_output=True, text=True, cwd=self.project_root, env=env
        )

    def test_help_option(self):
        """Testa se a opção --help funciona."""
        result = self.run_cli_command(["--help"])

        self.assertEqual(result.returncode, 0)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("--verbose", result.stdout)
        self.assertIn("--style", result.stdout)

    def test_dry_run_basic(self):
        """Testa funcionalidade básica do dry-run."""
        if not self.files_exist:
            self.skipTest("Arquivos de teste DOCX não encontrados")

        # Criar arquivo temporário para verificar que não é criado
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
            temp_output = temp_file.name

        # Remover arquivo temporário
        os.unlink(temp_output)

        # Executar dry-run
        result = self.run_cli_command(
            [
                self.original_file,
                self.modified_file,
                temp_output,
                "--dry-run",
            ]
        )

        # Verificar que comando foi bem-sucedido
        self.assertEqual(result.returncode, 0)

        # Verificar que arquivo não foi criado
        self.assertFalse(os.path.exists(temp_output))

        # Verificar conteúdo da saída
        self.assertIn("🔍 Analisando:", result.stdout)
        self.assertIn("📊 Resultados da análise:", result.stdout)
        self.assertIn("🔍 Modo dry-run:", result.stdout)
        self.assertIn("nenhum arquivo gerado", result.stdout)

    def test_dry_run_verbose(self):
        """Testa dry-run com modo verbose."""
        if not self.files_exist:
            self.skipTest("Arquivos de teste DOCX não encontrados")

        result = self.run_cli_command(
            [
                self.original_file,
                self.modified_file,
                "--dry-run",
                "--verbose",
            ]
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("🔧 Configurações:", result.stdout)
        self.assertIn("📊 Detalhes da análise:", result.stdout)
        self.assertIn("Modo: Análise apenas (dry-run)", result.stdout)

    def test_normal_execution_still_works(self):
        """Testa que execução normal ainda funciona."""
        if not self.files_exist:
            self.skipTest("Arquivos de teste DOCX não encontrados")

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
            temp_output = temp_file.name

        try:
            result = self.run_cli_command(
                [
                    self.original_file,
                    self.modified_file,
                    temp_output,
                ]
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(temp_output))
            self.assertIn("✅ Diff HTML gerado em:", result.stdout)

            # Verificar que arquivo tem conteúdo
            with open(temp_output, encoding="utf-8") as f:
                content = f.read()
                self.assertIn("<html", content)
                self.assertIn("Comparação de Documentos", content)

        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)

    def test_error_handling_missing_file(self):
        """Testa tratamento de erro para arquivo inexistente."""
        result = self.run_cli_command(
            [
                "arquivo_inexistente.docx",
                "outro_inexistente.docx",
                "--dry-run",
            ]
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("❌ ERRO:", result.stdout)
        self.assertIn("não encontrado", result.stdout)

    def test_style_options(self):
        """Testa opções de estilo."""
        if not self.files_exist:
            self.skipTest("Arquivos de teste DOCX não encontrados")

        styles = ["default", "minimal", "modern"]

        for style in styles:
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
                temp_output = temp_file.name

            try:
                result = self.run_cli_command(
                    [
                        self.original_file,
                        self.modified_file,
                        temp_output,
                        "--style",
                        style,
                    ]
                )

                self.assertEqual(result.returncode, 0, f"Estilo {style} falhou")
                self.assertTrue(os.path.exists(temp_output))

            finally:
                if os.path.exists(temp_output):
                    os.unlink(temp_output)

    def test_invalid_style(self):
        """Testa estilo inválido."""
        result = self.run_cli_command(
            [
                "--style",
                "invalid_style",
                "file1.docx",
                "file2.docx",
            ]
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)


def run_cli_tests():
    """Executa testes específicos do CLI."""
    print("🧪 Executando testes do CLI (dry-run)")
    print("=" * 50)

    # Obter caminho do projeto
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Teste rápido da funcionalidade
    test_files = [
        os.path.join(project_root, "documentos", "doc-rafael-original.docx"),
        os.path.join(project_root, "documentos", "doc-rafael-alterado.docx"),
    ]

    if all(os.path.exists(f) for f in test_files):
        print("✅ Arquivos de teste encontrados")

        # Teste dry-run básico
        cmd = [
            sys.executable,
            "-m",
            "docx_compare.core.docx_diff_viewer",
            test_files[0],
            test_files[1],
            "--dry-run",
        ]
        env = {**os.environ, "PYTHONPATH": os.path.join(project_root, "src")}

        print(f"🔄 Executando: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=project_root, env=env
        )

        if result.returncode == 0:
            print("✅ Teste dry-run básico: PASSOU")
        else:
            print("❌ Teste dry-run básico: FALHOU")
            print(f"   Erro: {result.stderr}")

        # Teste com verbose
        cmd_verbose = [
            sys.executable,
            "-m",
            "docx_compare.core.docx_diff_viewer",
            test_files[0],
            test_files[1],
            "--dry-run",
            "--verbose",
        ]
        print(f"🔄 Executando: {' '.join(cmd_verbose)}")
        result_verbose = subprocess.run(
            cmd_verbose, capture_output=True, text=True, cwd=project_root, env=env
        )

        if result_verbose.returncode == 0:
            print("✅ Teste dry-run verbose: PASSOU")
        else:
            print("❌ Teste dry-run verbose: FALHOU")
            print(f"   Erro: {result_verbose.stderr}")

    else:
        print("⚠️  Arquivos de teste não encontrados, pulando testes")


if __name__ == "__main__":
    # Executar testes rápidos
    run_cli_tests()

    print("\n" + "=" * 50)
    print("🧪 Executando suite completa de testes unitários")

    # Executar testes unitários
    unittest.main(verbosity=2)
