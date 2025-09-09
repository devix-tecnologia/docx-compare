#!/usr/bin/env python3
"""
Script wrapper para docx_diff_viewer.py
Mantém compatibilidade com testes e scripts antigos.
"""

import os
import sys

# Adicionar o diretório src ao path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importar e executar o módulo principal
if __name__ == "__main__":
    from docx_compare.core.docx_diff_viewer import main
    main()
