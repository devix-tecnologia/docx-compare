#!/usr/bin/env python3
"""
Vincula modificações às cláusulas no Directus E2E usando algoritmo de vinculação.

Atualiza o banco de dados PostgreSQL diretamente para vincular modificações
às cláusulas baseado em posições e conteúdo.

Uso:
    python vincular_modificacoes.py --versao 2573b998-63d0-4471-ad85-db6f860c3721
"""

import argparse
import subprocess
import sys

VERSAO_ID = "2573b998-63d0-4471-ad85-db6f860c3721"


def executar_sql(query: str) -> str:
    """Executa SQL no PostgreSQL via docker exec"""
    cmd = [
        "docker",
        "exec",
        "e2e-ui-postgres",
        "psql",
        "-U",
        "directus",
        "-d",
        "directus",
        "-t",
        "-c",
        query,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Erro SQL: {result.stderr}")
    return result.stdout.strip()


def vincular_modificacoes():
    """Vincula modificações às cláusulas baseado em posições"""

    print("=" * 60)
    print("🔗 VINCULAÇÃO DE MODIFICAÇÕES ÀS CLÁUSULAS")
    print("=" * 60)
    print(f"Versão: {VERSAO_ID[:8]}")
    print("=" * 60)
    print()

    # 1. Buscar informações da versão
    print("📋 1. Buscando informações da versão...")
    versao_info = executar_sql(f"""
        SELECT
            v.id::text,
            c.modelo_contrato::text as modelo_id,
            (SELECT COUNT(*) FROM modificacao WHERE versao = v.id) as total_mods
        FROM versao v
        LEFT JOIN contrato c ON v.contrato = c.id
        WHERE v.id = '{VERSAO_ID}';
    """)

    if not versao_info.strip():
        print("   ❌ Versão não encontrada")
        return False

    parts = versao_info.split("|")
    modelo_id = parts[1].strip()
    total_mods = parts[2].strip()

    print("   ✓ Versão encontrada")
    print(f"   - Modelo: {modelo_id[:8]}")
    print(f"   - Modificações: {total_mods}")
    print()

    # 2. Vincular modificações baseado em posições
    print("🔗 2. Vinculando modificações às cláusulas...")
    print("   Estratégia: matching por posição + conteúdo")
    print()

    # Buscar modificações e tentar vincular
    modificacoes = executar_sql(f"""
        SELECT
            m.id::text,
            m.posicao_inicio,
            m.posicao_fim,
            m.categoria
        FROM modificacao m
        WHERE m.versao = '{VERSAO_ID}'
        ORDER BY m.posicao_inicio;
    """)

    if not modificacoes.strip():
        print("   ⚠️  Nenhuma modificação encontrada")
        return False

    vinculadas = 0
    nao_vinculadas = 0

    for line in modificacoes.split("\n"):
        if not line.strip():
            continue

        parts = line.split("|")
        if len(parts) < 4:
            continue

        mod_id = parts[0].strip()
        pos_inicio = parts[1].strip()
        _pos_fim = parts[2].strip()
        categoria = parts[3].strip()

        if not pos_inicio or pos_inicio == "":
            print(f"   ⚠️  Mod {mod_id[:8]} sem posição - pulando")
            nao_vinculadas += 1
            continue

        # Buscar cláusula que contenha essa posição
        clausula_result = executar_sql(f"""
            SELECT
                c.id::text,
                c.numero,
                c.nome
            FROM clausula c
            JOIN modelo_contrato_tag t ON c.tag = t.id
            WHERE t.modelo_contrato = '{modelo_id}'
            AND t.posicao_inicio_texto <= {pos_inicio}
            AND t.posicao_fim_texto >= {pos_inicio}
            ORDER BY (t.posicao_fim_texto - t.posicao_inicio_texto)
            LIMIT 1;
        """)

        if not clausula_result.strip():
            print(f"   ⚠️  Mod {mod_id[:8]} ({categoria}) sem cláusula compatível")
            nao_vinculadas += 1
            continue

        clausula_parts = clausula_result.split("|")
        clausula_id = clausula_parts[0].strip()
        clausula_numero = clausula_parts[1].strip() if len(clausula_parts) > 1 else "?"

        # Atualizar modificação com a cláusula
        try:
            executar_sql(f"""
                UPDATE modificacao
                SET clausula = '{clausula_id}'
                WHERE id = '{mod_id}';
            """)
            print(f"   ✅ Mod {mod_id[:8]} ({categoria}) → Cláusula {clausula_numero}")
            vinculadas += 1
        except Exception as e:
            print(f"   ❌ Erro ao vincular {mod_id[:8]}: {e}")
            nao_vinculadas += 1

    print()
    print("=" * 60)
    print("📊 RESULTADO DA VINCULAÇÃO")
    print("=" * 60)
    print(f"✅ Vinculadas: {vinculadas}")
    print(f"⚠️  Não vinculadas: {nao_vinculadas}")

    if vinculadas > 0:
        taxa = (vinculadas / (vinculadas + nao_vinculadas)) * 100
        print(f"📈 Taxa de sucesso: {taxa:.1f}%")

    print()

    return vinculadas > 0


def verificar_vinculacoes():
    """Verifica se as vinculações têm objetivo e referencias"""
    print()
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DAS VINCULAÇÕES")
    print("=" * 60)
    print()

    result = executar_sql(f"""
        SELECT
            m.id::text,
            c.numero,
            c.nome,
            CASE
                WHEN c.objetivo IS NULL OR LENGTH(TRIM(c.objetivo)) = 0
                THEN '✗'
                ELSE '✓'
            END as tem_objetivo,
            CASE
                WHEN EXISTS (
                    SELECT 1 FROM referencia r WHERE r.clausula = c.id
                )
                THEN '✓'
                ELSE '✗'
            END as tem_referencias
        FROM modificacao m
        JOIN clausula c ON m.clausula = c.id
        WHERE m.versao = '{VERSAO_ID}'
        ORDER BY m.date_created;
    """)

    if not result.strip():
        print("⚠️  Nenhuma modificação vinculada encontrada")
        return

    print("Modificação | Cláusula | Objetivo | Referências")
    print("-" * 60)

    for line in result.split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 5:
            mod_id = parts[0].strip()[:8]
            numero = parts[1].strip()
            tem_obj = parts[3].strip()
            tem_ref = parts[4].strip()
            print(f"{mod_id} | {numero:10s} | {tem_obj:8s} | {tem_ref}")

    print()


def main():
    global VERSAO_ID

    parser = argparse.ArgumentParser(
        description="Vincula modificações às cláusulas no Directus E2E"
    )
    parser.add_argument(
        "--versao",
        default=VERSAO_ID,
        help=f"ID da versão (padrão: {VERSAO_ID})",
    )

    args = parser.parse_args()
    VERSAO_ID = args.versao

    try:
        if vincular_modificacoes():
            verificar_vinculacoes()
            print("✅ Processo concluído com sucesso!")
            print()
            print("🧪 Teste a API:")
            print("   curl -X POST http://localhost:8011/api/process \\")
            print('     -H "Content-Type: application/json" \\')
            print(f'     -d \'{{"versao_id":"{VERSAO_ID}"}}\'')
            print()
        else:
            print("❌ Nenhuma modificação foi vinculada")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
