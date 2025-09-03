#!/usr/bin/env python3
"""
Testes para funcionalidade dry-run da API e processador
"""

import subprocess
import unittest


class TestDryRunAPI(unittest.TestCase):
    """Testa funcionalidade dry-run para API e processador"""

    def test_api_dry_run_help(self):
        """Testa se o --help da API inclui a opção --dry-run"""
        result = subprocess.run(
            ["python", "api_simple.py", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/sidarta/repositorios/docx-compare",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("sem modificar registros no Directus", result.stdout)

    def test_processador_dry_run_help(self):
        """Testa se o --help do processador inclui a opção --dry-run"""
        result = subprocess.run(
            ["python", "processador_automatico.py", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/sidarta/repositorios/docx-compare",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("sem modificar registros no Directus", result.stdout)

    def test_makefile_dry_commands(self):
        """Testa se o Makefile contém os novos comandos dry-run"""
        with open("/Users/sidarta/repositorios/docx-compare/Makefile") as f:
            makefile_content = f.read()

        self.assertIn("run-api-dry:", makefile_content)
        self.assertIn("run-processor-dry:", makefile_content)
        self.assertIn("--dry-run", makefile_content)

    def test_dry_run_command_line_parsing(self):
        """Testa se os argumentos da linha de comando estão sendo processados corretamente"""
        # Testar argparse básico sem executar o servidor
        result = subprocess.run(
            [
                "python",
                "-c",
                """
import sys
sys.path.append('/Users/sidarta/repositorios/docx-compare')
from api_simple import create_arg_parser
parser = create_arg_parser()
args = parser.parse_args(['--dry-run', '--host', 'test-host', '--port', '9999'])
print(f'dry_run: {args.dry_run}')
print(f'host: {args.host}')
print(f'port: {args.port}')
""",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("dry_run: True", result.stdout)
        self.assertIn("host: test-host", result.stdout)
        self.assertIn("port: 9999", result.stdout)

    def test_dry_run_function_signatures(self):
        """Testa se as funções têm o parâmetro dry_run"""
        # Verificar se as funções foram modificadas corretamente
        with open("/Users/sidarta/repositorios/docx-compare/api_simple.py") as f:
            api_content = f.read()

        self.assertIn(
            "def update_versao_status(versao_id, result_url, total_modifications, dry_run=False)",
            api_content,
        )
        self.assertIn(
            "def save_modifications_to_directus(versao_id, modifications, dry_run=False)",
            api_content,
        )
        self.assertIn('dry_run = data.get("dry_run", False)', api_content)

        with open(
            "/Users/sidarta/repositorios/docx-compare/processador_automatico.py"
        ) as f:
            proc_content = f.read()

        self.assertIn("def processar_versao(versao_data, dry_run=False)", proc_content)
        self.assertIn("def loop_processador(dry_run=False)", proc_content)
        self.assertIn("dry_run=False,", proc_content)


class TestMakefileDryCommands(unittest.TestCase):
    """Testa comandos dry-run do Makefile"""

    def test_makefile_help_shows_dry_commands(self):
        """Testa se o help do Makefile mostra os novos comandos"""
        result = subprocess.run(
            ["make", "help"],
            capture_output=True,
            text=True,
            cwd="/Users/sidarta/repositorios/docx-compare",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("run-api-dry", result.stdout)
        self.assertIn("run-processor-dry", result.stdout)
        self.assertIn("modo dry-run", result.stdout)

    def test_validate_dry_run_output_in_code(self):
        """Testa se as mensagens de dry-run estão presentes no código"""
        with open("/Users/sidarta/repositorios/docx-compare/api_simple.py") as f:
            api_content = f.read()

        # Verificar se as mensagens de dry-run estão presentes
        self.assertIn("🏃‍♂️ DRY-RUN:", api_content)
        self.assertIn("Não executando atualização no Directus", api_content)
        self.assertIn("Não salvando modificações no Directus", api_content)

        with open(
            "/Users/sidarta/repositorios/docx-compare/processador_automatico.py"
        ) as f:
            proc_content = f.read()

        self.assertIn("🏃‍♂️ DRY-RUN:", proc_content)
        self.assertIn("Analisando versão", proc_content)
        self.assertIn("sem alterações", proc_content)


if __name__ == "__main__":
    print("🧪 Testando funcionalidade dry-run para API e processador...")
    unittest.main(verbosity=2)
