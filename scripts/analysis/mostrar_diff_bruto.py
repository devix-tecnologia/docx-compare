#!/usr/bin/env python3
"""
Script para mostrar o formato diff bruto gerado pelo difflib
"""

import difflib


def mostrar_diff_bruto():
    """Mostra o formato diff bruto que é usado internamente"""

    print("🔍 Mostrando formato DIFF bruto...")
    print("=" * 80)

    # Textos de exemplo
    original_text = """CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: Empresa ABC
CONTRATADA: Empresa XYZ

PREÂMBULO
Este contrato estabelece as condições gerais...

DEFINIÇÕES
Para fins deste contrato, consideram-se:

CLÁUSULA 1ª - OBJETO
O objeto deste contrato é...

CLÁUSULA 1.1 - ESPECIFICAÇÕES
As especificações técnicas...

CLÁUSULA 1.2 - PRAZO
O prazo de execução..."""

    tagged_text = """CONTRATO DE PRESTAÇÃO DE SERVIÇOS

CONTRATANTE: {{contratante}}
CONTRATADA: {{contratada}}

{{preambulo}}
Este contrato estabelece as {{condicoes_gerais}}...

{{definicoes}}
Para fins deste contrato, consideram-se:

CLÁUSULA {{1}} - OBJETO
O objeto deste contrato é...

CLÁUSULA {{1.1}} - ESPECIFICAÇÕES
As especificações técnicas...

CLÁUSULA {{1.2}} - PRAZO
O prazo de execução..."""

    print("📄 TEXTO ORIGINAL:")
    for i, linha in enumerate(original_text.split("\n"), 1):
        print(f"{i:2d}: {linha}")

    print("\n" + "=" * 80)
    print("🏷️ TEXTO COM TAGS:")
    for i, linha in enumerate(tagged_text.split("\n"), 1):
        print(f"{i:2d}: {linha}")

    print("\n" + "=" * 80)
    print("🔍 DIFF BRUTO (unified_diff):")
    print("-" * 80)

    # Gerar diff exatamente como o código faz
    original_lines = original_text.split("\n")
    modified_lines = tagged_text.split("\n")

    diff = list(
        difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile="Original",
            tofile="Modificado",
            lineterm="",
        )
    )

    # Mostrar cada linha do diff com numeração
    for i, linha_diff in enumerate(diff):
        print(f"{i:2d}: {repr(linha_diff)}")

    print("\n" + "=" * 80)
    print("🔍 DIFF FORMATADO PARA LEITURA:")
    print("-" * 80)

    for linha_diff in diff:
        if linha_diff.startswith("@@"):
            print(f"📍 {linha_diff}")
        elif linha_diff.startswith("---"):
            print(f"📄 ARQUIVO ORIGINAL: {linha_diff}")
        elif linha_diff.startswith("+++"):
            print(f"🏷️  ARQUIVO MODIFICADO: {linha_diff}")
        elif linha_diff.startswith("-"):
            print(f"❌ REMOVIDO: {linha_diff}")
        elif linha_diff.startswith("+"):
            print(f"✅ ADICIONADO: {linha_diff}")
        else:
            print(f"➡️  CONTEXTO: {linha_diff}")

    print("\n" + "=" * 80)
    print("🔍 PROCESSAMENTO DAS LINHAS DO DIFF:")
    print("-" * 80)

    i = 0
    modification_count = 1

    while i < len(diff):
        line = diff[i]

        print(f"\n📍 Processando linha {i}: {repr(line)}")

        if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            print("   🔸 Cabeçalho do diff - ignorado")
            i += 1
            continue
        elif line.startswith("-"):
            original_content = line[1:].strip()
            if original_content:
                print(f"   🔸 Conteúdo removido: '{original_content}'")
                if i + 1 < len(diff) and diff[i + 1].startswith("+"):
                    modified_content = diff[i + 1][1:].strip()
                    print(f"   🔸 Próxima linha é adição: '{modified_content}'")
                    print(
                        f"   ➡️  MODIFICAÇÃO #{modification_count}: '{original_content}' → '{modified_content}'"
                    )
                    i += 2
                else:
                    print(
                        f"   ➡️  REMOÇÃO #{modification_count}: '{original_content}' (sem substituto)"
                    )
                    i += 1
                modification_count += 1
            else:
                i += 1
        elif line.startswith("+"):
            added_content = line[1:].strip()
            if added_content:
                print(f"   🔸 Conteúdo adicionado: '{added_content}'")
                print(f"   ➡️  ADIÇÃO #{modification_count}: '{added_content}'")
                modification_count += 1
            i += 1
        else:
            print("   🔸 Linha de contexto - ignorada")
            i += 1


if __name__ == "__main__":
    mostrar_diff_bruto()
