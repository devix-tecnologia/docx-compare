#!/usr/bin/env python3
"""
Script CLI para docx_diff_viewer - Ponto de entrada na raiz do projeto
"""

import os
import sys

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    from docx_compare.core.docx_diff_viewer import main

    main()
