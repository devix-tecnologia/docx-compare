"""
Script para comparar implementação original (texto plano) vs AST.

Executa ambas as implementações no mesmo contrato e compara:
- Número de modificações detectadas
- Tipos (ALTERACAO, REMOCAO, INSERCAO)
- Qualidade das detecções
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.contrato_vigencia_fixture import (
    MODELO_TEXTO_ORIGINAL,
    VERSAO_TEXTO_MODIFICADO,
)


def criar_docx_temporario(texto: str, nome: str) -> str:
    """
    Cria um arquivo DOCX temporário a partir de texto.
    
    Nota: Esta é uma implementação simplificada.
    Em produção, usaríamos python-docx para criar DOCXs reais.
    """
    import subprocess

    # Criar arquivo de texto temporário
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(texto)
        txt_path = f.name

    # Converter para DOCX usando pandoc
    docx_path = txt_path.replace(".txt", f"_{nome}.docx")

    try:
        subprocess.run(
            ["pandoc", txt_path, "-o", docx_path],
            check=True,
            capture_output=True,
        )
        return docx_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar DOCX: {e.stderr.decode()}")
        raise
    finally:
        Path(txt_path).unlink(missing_ok=True)


def comparar_implementacoes():
    """Compara implementação original vs AST."""

    print("=" * 100)
    print("🔬 COMPARAÇÃO: Implementação Original (Texto Plano) vs AST do Pandoc")
    print("=" * 100)

    # Criar DOCXs temporários
    print("\n📝 Criando arquivos DOCX temporários...")
    try:
        original_docx = criar_docx_temporario(MODELO_TEXTO_ORIGINAL, "original")
        modified_docx = criar_docx_temporario(VERSAO_TEXTO_MODIFICADO, "modificado")
        print(f"✅ Original: {original_docx}")
        print(f"✅ Modificado: {modified_docx}")
    except Exception as e:
        print(f"❌ Erro ao criar DOCXs: {e}")
        return

    try:
        # ============================================================
        # TESTE 1: Implementação Original (Texto Plano)
        # ============================================================
        print("\n" + "=" * 100)
        print("📊 TESTE 1: Implementação Original (Texto Plano)")
        print("=" * 100)

        from directus_server import DirectusAPI

        api_original = DirectusAPI()

        # Extrair texto plano
        orig_text = MODELO_TEXTO_ORIGINAL
        mod_text = VERSAO_TEXTO_MODIFICADO

        # Gerar diff
        diff_html_original = api_original._generate_diff_html(orig_text, mod_text)

        # Extrair modificações
        mods_original = api_original._extrair_modificacoes_do_diff(
            diff_html_original, orig_text, mod_text
        )

        # Contar tipos
        tipos_original = {"ALTERACAO": 0, "REMOCAO": 0, "INSERCAO": 0}
        for mod in mods_original:
            tipo = mod.get("tipo", "UNKNOWN")
            tipos_original[tipo] = tipos_original.get(tipo, 0) + 1

        print("\n📈 Resultados Original:")
        print(f"   Total de modificações: {len(mods_original)}")
        print(f"   - ALTERACAO: {tipos_original['ALTERACAO']}")
        print(f"   - REMOCAO: {tipos_original['REMOCAO']}")
        print(f"   - INSERCAO: {tipos_original['INSERCAO']}")

        # ============================================================
        # TESTE 2: Implementação com AST
        # ============================================================
        print("\n" + "=" * 100)
        print("📊 TESTE 2: Implementação com AST do Pandoc")
        print("=" * 100)

        from directus_server_ast import DirectusAPIWithAST

        api_ast = DirectusAPIWithAST()

        # Comparar usando AST
        resultado_ast = api_ast.comparar_documentos_ast(original_docx, modified_docx)

        mods_ast = resultado_ast["modificacoes"]
        metricas_ast = resultado_ast["metricas"]

        print("\n📈 Resultados AST:")
        print(f"   Total de modificações: {metricas_ast['total_modificacoes']}")
        print(f"   - ALTERACAO: {metricas_ast['alteracoes']}")
        print(f"   - REMOCAO: {metricas_ast['remocoes']}")
        print(f"   - INSERCAO: {metricas_ast['insercoes']}")

        # ============================================================
        # COMPARAÇÃO DETALHADA
        # ============================================================
        print("\n" + "=" * 100)
        print("🔍 COMPARAÇÃO DETALHADA")
        print("=" * 100)

        print("\n📊 Diferenças quantitativas:")
        print(f"   Total: Original={len(mods_original)} vs AST={metricas_ast['total_modificacoes']}")
        print(f"   ALTERACAO: Original={tipos_original['ALTERACAO']} vs AST={metricas_ast['alteracoes']}")
        print(f"   REMOCAO: Original={tipos_original['REMOCAO']} vs AST={metricas_ast['remocoes']}")
        print(f"   INSERCAO: Original={tipos_original['INSERCAO']} vs AST={metricas_ast['insercoes']}")

        # Esperado: 7 modificações (1.1 ALTERACAO, 1.2 REMOCAO, 1.4-1.5 ALTERACAO, 2.2-2.3 ALTERACAO, 2.5 INSERCAO)
        esperado = {
            "total": 7,
            "ALTERACAO": 4,  # 1.1, 1.4, 2.2, 2.3
            "REMOCAO": 1,    # 1.2
            "INSERCAO": 1,   # 2.5
        }

        print("\n🎯 Comparação com resultado esperado:")
        print(f"   Esperado: {esperado['total']} modificações")
        print(f"   - ALTERACAO: {esperado['ALTERACAO']}")
        print(f"   - REMOCAO: {esperado['REMOCAO']}")
        print(f"   - INSERCAO: {esperado['INSERCAO']}")

        # Scores
        score_original = calcular_score(tipos_original, len(mods_original), esperado)
        score_ast = calcular_score(
            {
                "ALTERACAO": metricas_ast["alteracoes"],
                "REMOCAO": metricas_ast["remocoes"],
                "INSERCAO": metricas_ast["insercoes"],
            },
            metricas_ast["total_modificacoes"],
            esperado,
        )

        print("\n🏆 SCORES DE PRECISÃO:")
        print(f"   Implementação Original: {score_original:.1%}")
        print(f"   Implementação AST: {score_ast:.1%}")

        if score_ast > score_original:
            print(f"\n✅ VENCEDOR: Implementação AST (+{(score_ast - score_original)*100:.1f}%)")
        elif score_original > score_ast:
            print(f"\n✅ VENCEDOR: Implementação Original (+{(score_original - score_ast)*100:.1f}%)")
        else:
            print("\n🤝 EMPATE: Ambas com mesma precisão")

        # Detalhes das modificações
        print("\n📋 Detalhes das modificações AST:")
        for i, mod in enumerate(mods_ast[:5], 1):  # Mostrar apenas primeiras 5
            print(f"\n   Modificação #{i}:")
            print(f"      Tipo: {mod['tipo']}")
            if mod.get("clausula_original"):
                print(f"      Cláusula Original: {mod['clausula_original']}")
            if mod.get("clausula_modificada"):
                print(f"      Cláusula Modificada: {mod['clausula_modificada']}")
            conteudo = mod.get("conteudo", {})
            if conteudo.get("original"):
                print(f"      Original: {conteudo['original'][:60]}...")
            if conteudo.get("novo"):
                print(f"      Novo: {conteudo['novo'][:60]}...")

    finally:
        # Limpar arquivos temporários
        Path(original_docx).unlink(missing_ok=True)
        Path(modified_docx).unlink(missing_ok=True)
        print("\n🧹 Arquivos temporários removidos")


def calcular_score(tipos: dict, total: int, esperado: dict) -> float:
    """
    Calcula score de precisão comparando com esperado.
    
    Score = (acertos / total_esperado)
    """
    acertos = 0

    # Penalizar diferença no total
    diff_total = abs(total - esperado["total"])
    acertos += max(0, esperado["total"] - diff_total)

    # Penalizar diferença em cada tipo
    for tipo in ["ALTERACAO", "REMOCAO", "INSERCAO"]:
        diff = abs(tipos.get(tipo, 0) - esperado[tipo])
        acertos += max(0, esperado[tipo] - diff) * 0.5  # Peso menor para tipos

    # Normalizar
    max_score = esperado["total"] + sum(esperado.values()) * 0.5
    return acertos / max_score if max_score > 0 else 0.0


if __name__ == "__main__":
    comparar_implementacoes()
