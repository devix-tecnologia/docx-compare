#!/usr/bin/env python3
"""
Teste isolado da função convert_docx_to_html
"""

import os
import sys

sys.path.append("/Users/sidarta/repositorios/docx-compare")

from src.docx_compare.core.docx_utils import convert_docx_to_html


def test_conversion():
    # Arquivo que sabemos que existe e é válido
    input_file = "/var/folders/db/k04l5r0n09j8dphykj0wtpfr0000gn/T/tmp0vp524hj"
    output_file = "/tmp/test_conversion_python.html"
    filter_path = "/Users/sidarta/repositorios/docx-compare/config/comments_html_filter_direct.lua"

    print("🔍 Testando conversão:")
    print(f"  Input: {input_file}")
    print(f"  Output: {output_file}")
    print(f"  Filter: {filter_path}")

    try:
        print("🚀 Iniciando conversão...")
        convert_docx_to_html(input_file, output_file, filter_path)
        print("✅ Conversão concluída!")

        # Verificar resultado
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"📄 Arquivo gerado: {size} bytes")
        else:
            print("❌ Arquivo não foi gerado")

    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_conversion()
