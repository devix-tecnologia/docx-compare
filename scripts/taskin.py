#!/usr/bin/env python3
"""Wrapper para executar pnpx taskin através do uv."""
import subprocess
import sys


def main():
    """Execute pnpx taskin com os argumentos fornecidos."""
    try:
        result = subprocess.run(
            ["pnpx", "taskin"] + sys.argv[1:],
            check=False
        )
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ Erro: pnpm não encontrado. Instale com: npm install -g pnpm")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
