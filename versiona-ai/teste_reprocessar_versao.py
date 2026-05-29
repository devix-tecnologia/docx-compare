#!/usr/bin/env python3
"""
Script para reprocessar uma versão específica e validar análise granular.
Testa a implementação da Task-016 localmente.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar diretamente as classes necessárias
from directus_server import DirectusAPI

# Carregar variáveis de ambiente
load_dotenv()

VERSAO_ID = "8d8e89a8-ba89-4e0e-846c-43e7ad058309"
CONTRATO_ID = "86035523-977b-42cf-adda-6fd364170aa9"


def main():
    print("=" * 80)
    print("🧪 TESTE: Reprocessamento com Análise Granular (Task-016)")
    print("=" * 80)
    print()

    # Inicializar API do Directus
    api = DirectusAPI()

    print(f"📄 Versão: {VERSAO_ID}")
    print(f"📝 Contrato: {CONTRATO_ID}")
    print()

    # Processar versão
    print("🔄 Processando versão com análise granular...")
    print()

    inicio = datetime.now()

    try:
        # Processar com AST (melhor método) e análise granular automática
        resultado = api.process_versao(VERSAO_ID, mock=False, use_ast=True)

        tempo_decorrido = (datetime.now() - inicio).total_seconds()

        if not resultado:
            print("❌ Erro: process_versao retornou None")
            return 1

        print(f"\n✅ Processamento concluído em {tempo_decorrido:.2f}s")
        print()

        # Analisar modificações detectadas
        modificacoes = resultado.get("modificacoes", [])
        total = len(modificacoes)

        print("=" * 80)
        print("📊 RESULTADOS")
        print("=" * 80)
        print()

        # Contar por categoria
        por_categoria = {}
        for mod in modificacoes:
            cat = mod.get("categoria", "DESCONHECIDO")
            por_categoria[cat] = por_categoria.get(cat, 0) + 1

        print(f"Total de modificações: {total}")
        print()
        print("Por categoria:")
        for cat, count in sorted(por_categoria.items()):
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {cat}: {count} ({pct:.1f}%)")

        print()

        # Comparar com baseline e IA
        print("=" * 80)
        print("📈 COMPARAÇÃO")
        print("=" * 80)
        print()

        baseline_total = 10
        baseline_insercao = 10
        baseline_alteracao = 0

        ia_total = 44
        ia_alteracao = 34
        ia_insercao = 10

        print("BASELINE (antes da Task-016):")
        print(f"  Total: {baseline_total}")
        print(f"  INSERCAO: {baseline_insercao} (100%)")
        print(f"  ALTERACAO: {baseline_alteracao} (0%)")
        print()

        print("IA (ground truth):")
        print(f"  Total: {ia_total}")
        print(f"  INSERCAO: {ia_insercao} ({ia_insercao / ia_total * 100:.1f}%)")
        print(f"  ALTERACAO: {ia_alteracao} ({ia_alteracao / ia_total * 100:.1f}%)")
        print()

        print("SISTEMA ATUAL:")
        print(f"  Total: {total}")
        for cat, count in sorted(por_categoria.items()):
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {cat}: {count} ({pct:.1f}%)")

        print()

        # Verificar meta
        alteracoes_atuais = por_categoria.get("ALTERACAO", 0)
        pct_alteracoes = (alteracoes_atuais / total * 100) if total > 0 else 0

        print("=" * 80)
        print("✅ VALIDAÇÃO DA META")
        print("=" * 80)
        print()

        meta_total_min = 40
        meta_alteracao_pct_min = 60

        print(f"Meta 1: Total ≥ {meta_total_min} modificações")
        if total >= meta_total_min:
            print(f"  ✅ PASSOU: {total} ≥ {meta_total_min}")
        else:
            print(f"  ❌ FALHOU: {total} < {meta_total_min}")

        print()

        print(f"Meta 2: ALTERACAO ≥ {meta_alteracao_pct_min}%")
        if pct_alteracoes >= meta_alteracao_pct_min:
            print(f"  ✅ PASSOU: {pct_alteracoes:.1f}% ≥ {meta_alteracao_pct_min}%")
        else:
            print(f"  ❌ FALHOU: {pct_alteracoes:.1f}% < {meta_alteracao_pct_min}%")

        print()

        # Salvar resultado para comparação
        output_dir = Path(__file__).parent / "teste_ab_output"
        output_dir.mkdir(exist_ok=True)

        resultado_file = (
            output_dir / f"resultado_sistema_reprocessado_{VERSAO_ID[:8]}.json"
        )

        resultado_para_salvar = {
            "versao_id": VERSAO_ID,
            "contrato_id": CONTRATO_ID,
            "timestamp": datetime.now().isoformat(),
            "tempo_processamento": tempo_decorrido,
            "total_modificacoes": total,
            "por_categoria": por_categoria,
            "modificacoes": modificacoes,
            "metodo": "sistema_estruturado_com_analise_granular",
            "validacao": {
                "meta_total_min": meta_total_min,
                "meta_alteracao_pct_min": meta_alteracao_pct_min,
                "passou_meta_total": total >= meta_total_min,
                "passou_meta_alteracao": pct_alteracoes >= meta_alteracao_pct_min,
            },
        }

        with open(resultado_file, "w", encoding="utf-8") as f:
            json.dump(resultado_para_salvar, f, indent=2, ensure_ascii=False)

        print(f"💾 Resultado salvo em: {resultado_file}")
        print()

        return 0

    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
