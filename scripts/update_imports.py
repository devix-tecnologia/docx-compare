#!/usr/bin/env python3
"""
Script para atualizar imports após reorganização do projeto.
"""

from pathlib import Path


def update_imports_in_file(file_path: Path) -> bool:
    """Atualiza os imports em um arquivo Python."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Mapear imports antigos para novos
        import_mappings = {
            "from src.docx_compare.core.docx_utils import": "from src.docx_compare.core.docx_utils import",
            "from src.docx_compare.core import docx_utils": "from src.docx_compare.core from src.docx_compare.core import docx_utils",
            "from src.docx_compare.utils.directus_utils import": "from src.docx_compare.utils.directus_utils import",
            "from src.docx_compare.utils import directus_utils": "from src.docx_compare.utils from src.docx_compare.utils import directus_utils",
            "from src.docx_compare.utils.text_analysis_utils import": "from src.docx_compare.utils.text_analysis_utils import",
            "from src.docx_compare.utils import text_analysis_utils": "from src.docx_compare.utils from src.docx_compare.utils import text_analysis_utils",
            "from src.docx_compare.core.docx_diff_viewer import": "from src.docx_compare.core.docx_diff_viewer import",
            "from src.docx_compare.core import docx_diff_viewer": "from src.docx_compare.core from src.docx_compare.core import docx_diff_viewer",
            "from src.docx_compare.processors.processador_automatico import": "from src.docx_compare.processors.processador_automatico import",
            "from src.docx_compare.processors import processador_automatico": "from src.docx_compare.processors from src.docx_compare.processors import processador_automatico",
        }

        # Aplicar mapeamentos
        for old_import, new_import in import_mappings.items():
            content = content.replace(old_import, new_import)

        # Atualizar caminhos de arquivos de configuração
        path_mappings = {
            "config/comments_html_filter_direct.lua": "config/config/comments_html_filter_direct.lua",
            '"config/comments_html_filter_direct.lua"': '"config/config/comments_html_filter_direct.lua"',
            "'config/comments_html_filter_direct.lua'": "'config/config/comments_html_filter_direct.lua'",
        }

        for old_path, new_path in path_mappings.items():
            content = content.replace(old_path, new_path)

        # Salvar apenas se houve mudanças
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Atualizado: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False


def main():
    """Executa a atualização de imports em todos os arquivos Python relevantes."""
    base_dir = Path(__file__).parent.parent
    updated_files = 0

    # Diretórios para processar
    directories = [
        base_dir / "src",
        base_dir / "tests",
        base_dir / "scripts",
        base_dir / "config",
    ]

    print("🔄 Atualizando imports após reorganização...")

    for directory in directories:
        if directory.exists():
            for file_path in directory.rglob("*.py"):
                if update_imports_in_file(file_path):
                    updated_files += 1

    print(f"\n✅ Concluído! {updated_files} arquivos atualizados.")


if __name__ == "__main__":
    main()
