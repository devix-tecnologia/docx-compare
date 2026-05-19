#!/usr/bin/env python3
"""
Cria versão de teste no Directus E2E usando modelo existente.

O Directus E2E já tem o modelo 48b43d38 com 294 tags e 556 cláusulas.
Este script cria uma versão de teste vinculada a esse modelo.

Uso:
    python criar_versao_teste.py
"""

import subprocess
import uuid

# IDs conhecidos do E2E
MODELO_ID = "48b43d38-76b4-47a2-93a4-4216ad57defc"
VERSAO_ID = "2573b998-63d0-4471-ad85-db6f860c3721"  # Mesmo ID dos testes


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


def criar_versao():
    """Cria versão de teste"""
    try:
        print("🔍 Verificando se versão já existe...")
        result = executar_sql(f"SELECT id FROM versao WHERE id = '{VERSAO_ID}';")
        if result:
            print(f"   ✓ Versão {VERSAO_ID[:8]} já existe")
            return VERSAO_ID

        print("📋 Buscando detalhes do modelo...")
        result = executar_sql(
            f"SELECT id, nome FROM modelo_contrato WHERE id = '{MODELO_ID}';"
        )
        if not result:
            print(f"   ❌ Modelo {MODELO_ID[:8]} não encontrado")
            return None

        print("   ✓ Modelo encontrado")

        print("📝 Verificando se contrato existe...")
        result = executar_sql(
            f"SELECT id FROM contrato WHERE modelo_id = '{MODELO_ID}' LIMIT 1;"
        )

        if not result:
            print("   Criando contrato...")
            contrato_id = str(uuid.uuid4())
            executar_sql(
                f"""
                INSERT INTO contrato (id, modelo_id, nome, descricao, status, date_created)
                VALUES ('{contrato_id}', '{MODELO_ID}', 'Contrato Teste E2E',
                        'Contrato de teste com modelo 48b43d38 (294 tags, 556 cláusulas)',
                        'published', NOW());
                """
            )
        else:
            contrato_id = result.split()[0]

        print(f"   ✓ Contrato: {contrato_id[:8]}")

        print("💾 Criando versão...")
        executar_sql(
            f"""
            INSERT INTO versao (
                id,
                contrato_id,
                numero_versao,
                status,
                tipo_processamento,
                date_created
            ) VALUES ('{VERSAO_ID}', '{contrato_id}', '1.0', 'processada', 'ast', NOW());
            """
        )

        print("✏️  Criando modificações de exemplo...")

        # Buscar algumas tags para vincular modificações
        tags_result = executar_sql(
            f"""
            SELECT id, tag_nome, posicao_inicio_texto, posicao_fim_texto
            FROM modelo_contrato_tag
            WHERE modelo_contrato = '{MODELO_ID}'
            AND posicao_inicio_texto IS NOT NULL
            ORDER BY posicao_inicio_texto
            LIMIT 5;
            """
        )

        if tags_result:
            for line in tags_result.split("\n"):
                if not line.strip():
                    continue

                parts = line.split("|")
                if len(parts) < 3:
                    continue

                tag_id = parts[0].strip()
                pos_inicio = parts[2].strip() if len(parts) > 2 else "0"
                pos_fim = (
                    parts[3].strip() if len(parts) > 3 else str(int(pos_inicio) + 100)
                )

                # Buscar cláusula vinculada à tag
                clausula_result = executar_sql(
                    f"SELECT id FROM clausula WHERE tag = '{tag_id}' LIMIT 1;"
                )
                clausula_id = (
                    clausula_result.split()[0] if clausula_result.strip() else "NULL"
                )
                clausula_value = f"'{clausula_id}'" if clausula_id != "NULL" else "NULL"

                mod_id = str(uuid.uuid4())
                executar_sql(
                    f"""
                    INSERT INTO modificacao (
                        id,
                        versao_id,
                        categoria,
                        posicao_inicio,
                        posicao_fim,
                        clausula_id,
                        conteudo_json,
                        date_created
                    ) VALUES (
                        '{mod_id}',
                        '{VERSAO_ID}',
                        'INSERCAO',
                        {pos_inicio},
                        {pos_fim},
                        {clausula_value},
                        '{{"novo": "Texto modificado de exemplo"}}',
                        NOW()
                    );
                    """
                )

        print("\n✅ Versão criada com sucesso!")
        print(f"   ID: {VERSAO_ID}")
        print(f"   Contrato: {contrato_id[:8]}")
        print(f"   Modelo: {MODELO_ID[:8]}")
        print("\n🧪 Teste com: http://localhost:8011/api/process")
        print(f'   POST {{"versao_id": "{VERSAO_ID}"}}')

        return VERSAO_ID

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    print("=" * 60)
    print("📦 CRIAR VERSÃO DE TESTE NO DIRECTUS E2E")
    print("=" * 60)
    print(f"Modelo: {MODELO_ID[:8]} (294 tags, 556 cláusulas)")
    print(f"Versão: {VERSAO_ID}")
    print("=" * 60)
    print()

    criar_versao()


if __name__ == "__main__":
    main()
