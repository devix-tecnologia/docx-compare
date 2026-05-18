#!/usr/bin/env python3
"""
Script para processar versão REAL do Directus com algoritmos otimizados.

Baixa dados da versão 2573b998-63d0-4471-ad85-db6f860c3721 (produção)
e testa com fuzzy, regex e híbrido.

Uso:
    python processar_caso_real.py
    python processar_caso_real.py --algoritmo fuzzy
    python processar_caso_real.py --algoritmo hibrido --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Adicionar diretório atual e tests/ ao path
sys.path.insert(0, str(Path(__file__).parent))
tests_dir = Path(__file__).parent / "tests"
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from algoritmos.fuzzy.algoritmo import AlgoritmoFuzzyAvancado
from algoritmos.hibrido.algoritmo import AlgoritmoHibrido
from algoritmos.producao.algoritmo import AlgoritmoProducao
from algoritmos.regex.algoritmo import AlgoritmoRegex
from repositorio import DirectusRepository

# Configuração
DIRECTUS_LOCAL_URL = (
    "http://localhost:8065"  # Porta do Directus no docker-compose.ui-test.yml
)
DIRECTUS_TOKEN = "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"  # Token de leitura
VERSAO_ID = "2573b998-63d0-4471-ad85-db6f860c3721"

ALGORITMOS = {
    "producao": AlgoritmoProducao,
    "fuzzy": AlgoritmoFuzzyAvancado,
    "regex": AlgoritmoRegex,
    "hibrido": AlgoritmoHibrido,
}


def baixar_versao_directus(versao_id: str) -> dict[str, Any]:
    """
    Baixa dados de uma versão do Directus usando o Repositorio.

    Args:
        versao_id: UUID da versão

    Returns:
        Dict com dados da versão expandida
    """
    print(f"📡 Buscando versão {versao_id[:8]}... no Directus...")

    repo = DirectusRepository(base_url=DIRECTUS_LOCAL_URL, token=DIRECTUS_TOKEN)

    try:
        # Usar get_versao com fields customizados para expandir TUDO
        fields = [
            "*",  # Todos os campos da versão
            "modificacoes.*",  # Expandir cada modificação
            "modificacoes.clausula.*",  # Cláusula vinculada (ground truth)
            "contrato.*",  # Dados do contrato
            "contrato.modelo_contrato.*",  # Modelo com arquivos
            "contrato.modelo_contrato.tags.*",  # Tags do modelo (TODAS, não só 100)
            "contrato.modelo_contrato.tags.clausulas.*",  # Cláusulas das tags
        ]

        # IMPORTANTE: _limit: -1 em TODOS os relacionamentos para não truncar
        # Sintaxe Directus: deep usa path completo com colchetes aninhados
        deep = {
            "modificacoes": {"_limit": -1},
            "contrato": {
                "modelo_contrato": {
                    "_limit": -1,
                    "tags": {"_limit": -1},
                }
            },
        }

        versao = repo.get_versao(versao_id, fields=fields, deep=deep)

        if versao and versao.get("id"):
            print("✅ Versão encontrada!")

            # Contar dados
            mods = versao.get("modificacoes", [])
            contrato = versao.get("contrato", {})
            modelo = contrato.get("modelo_contrato", {}) if contrato else {}
            tags = modelo.get("tags", []) if modelo else []

            # Salvar dados brutos para debug
            import json

            with open(f"versao_{versao_id[:8]}_raw.json", "w", encoding="utf-8") as f:
                json.dump(versao, f, indent=2, ensure_ascii=False, default=str)
            print(f"   💾 Dados brutos salvos: versao_{versao_id[:8]}_raw.json")

            print(
                f"   - Modificações: {len(mods) if isinstance(mods, list) else 'N/A'}"
            )
            print(
                f"   - Tags do modelo: {len(tags) if isinstance(tags, list) else 'N/A'}"
            )

            return versao
        else:
            raise Exception(f"❌ Versão {versao_id} não encontrada")

    except Exception as e:
        print(f"⚠️  Erro ao buscar versão: {e}")
        raise


def extrair_dados_para_algoritmo(versao: dict[str, Any]) -> dict[str, Any]:
    """
    Extrai dados da versão no formato esperado pelos algoritmos.

    Args:
        versao: Dados brutos do Directus (estrutura: versao.contrato.modelo_contrato.tags)

    Returns:
        Dict com modificacoes, tags e texto_completo
    """
    # Navegar estrutura: versao -> contrato -> modelo_contrato
    contrato = versao.get("contrato", {})
    if not contrato:
        raise Exception("❌ Versão sem contrato vinculado")

    modelo = contrato.get("modelo_contrato", {})
    if not modelo:
        raise Exception("❌ Contrato sem modelo vinculado")

    # Extrair tags do modelo
    tags_raw = modelo.get("tags", [])
    tags = []
    for tag in tags_raw:
        # Tags do modelo têm campos: id, tag_nome, posicao_inicio_texto, posicao_fim_texto, conteudo
        tags.append(
            {
                "id": tag.get("id"),
                "titulo": tag.get("tag_nome")
                or tag.get("titulo")
                or f"Tag {tag.get('id')}",
                "texto": tag.get("conteudo")
                or tag.get("texto_tag")
                or tag.get("texto", ""),
                "posicao_inicio": tag.get("posicao_inicio_texto"),
                "posicao_fim": tag.get("posicao_fim_texto"),
            }
        )

    # Extrair modificações da versão
    modificacoes_raw = versao.get("modificacoes", [])
    modificacoes = []

    for mod in modificacoes_raw:
        # Se modificacoes são apenas IDs (não expandidos), pular
        if isinstance(mod, str):
            continue

        # Estrutura: {id, tipo/categoria, alteracao (texto), conteudo_json, posicao_inicio, posicao_fim, clausula}
        tipo = mod.get("categoria") or mod.get("tipo", "ALTERACAO")

        # O conteúdo pode estar em diferentes campos dependendo da versão
        texto_mod = ""
        if mod.get("alteracao"):
            # Campo usado nas versões processadas mais recentes
            texto_mod = mod.get("alteracao", "")
        elif mod.get("conteudo_json"):
            # Campo JSON usado em versões antigas
            conteudo_json = mod.get("conteudo_json", {})
            if tipo == "INSERCAO":
                texto_mod = conteudo_json.get("novo", "")
            elif tipo == "REMOCAO":
                texto_mod = conteudo_json.get("original", "")
            elif tipo == "ALTERACAO":
                texto_mod = conteudo_json.get("novo", "")

        # Pular REMOCAO sem conteúdo válido (ex: "--")
        if tipo == "REMOCAO" and (not texto_mod or texto_mod == "--"):
            continue

        # Montar conteúdo no formato esperado pelos algoritmos
        conteudo = {}
        if tipo == "INSERCAO":
            conteudo["novo"] = texto_mod
        elif tipo == "REMOCAO":
            conteudo["original"] = texto_mod
        elif tipo == "ALTERACAO":
            # Para ALTERACAO, o campo 'alteracao' pode conter o novo valor
            # TODO: Precisaríamos do original também para fazer diff correto
            conteudo["novo"] = texto_mod
            conteudo["original"] = ""  # Não temos o original nessa estrutura

        modificacoes.append(
            {
                "id": mod.get("id"),
                "tipo": tipo,
                "conteudo": conteudo,
                "posicao_inicio": mod.get("posicao_inicio"),
                "posicao_fim": mod.get("posicao_fim"),
                "clausula_vinculada_esperada": mod.get(
                    "clausula"
                ),  # Ground truth do Directus
            }
        )

    # Texto completo: tentar múltiplas fontes
    texto_completo = ""

    # 1. Campo direto do modelo
    if modelo.get("texto_completo"):
        texto_completo = modelo["texto_completo"]
        print(f"   ✅ Texto do modelo: {len(texto_completo)} caracteres")
    # 2. Arquivo original do modelo (se tiver)
    elif modelo.get("arquivo_original"):
        arquivo_id = modelo["arquivo_original"]
        print(f"   📄 Baixando arquivo original: {arquivo_id}...")

        # Criar repo para baixar arquivo
        repo = DirectusRepository(base_url=DIRECTUS_LOCAL_URL, token=DIRECTUS_TOKEN)

        try:
            # Baixar arquivo .docx
            arquivo_path = repo.download_file(arquivo_id)

            # Extrair texto do .docx
            import docx

            doc = docx.Document(arquivo_path)
            texto_completo = "\n".join([p.text for p in doc.paragraphs])

            print(f"   ✅ Texto extraído do .docx: {len(texto_completo)} caracteres")

            # Limpar arquivo temporário
            import os

            os.remove(arquivo_path)

        except Exception as e:
            print(f"   ⚠️  Erro ao baixar/extrair arquivo: {e}")
            # 3. Concatenar texto das tags como fallback
            if tags:
                texto_completo = " ".join(t.get("texto", "") for t in tags_raw)
                print(f"   ⚠️  Usando concatenação de {len(tags)} tags como texto")
    # 3. Concatenar texto das tags como último recurso
    elif tags:
        texto_completo = " ".join(t.get("texto", "") for t in tags_raw)
        print(f"   ⚠️  Usando concatenação de {len(tags)} tags como texto")

    return {
        "versao_id": versao.get("id"),
        "modificacoes": modificacoes,
        "tags": tags,
        "texto_completo": texto_completo,
    }


def processar_com_algoritmo(
    algoritmo_classe, dados: dict[str, Any], verbose: bool = False
) -> dict[str, Any]:
    """
    Processa versão com algoritmo específico.

    Args:
        algoritmo_classe: Classe do algoritmo (ex: AlgoritmoFuzzyAvancado)
        dados: Dados extraídos do Directus
        verbose: Imprimir detalhes

    Returns:
        Dict com estatísticas de vinculação
    """
    algoritmo = algoritmo_classe()
    modificacoes = dados["modificacoes"]
    tags = dados["tags"]
    texto = dados["texto_completo"]

    print(f"\n🔬 Processando com {algoritmo.nome}...")
    print(f"   - {len(modificacoes)} modificações")
    print(f"   - {len(tags)} cláusulas")
    print(f"   - {len(texto)} caracteres de texto")

    # Vincular
    resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)

    # Calcular estatísticas
    vinculadas = sum(1 for r in resultado if r.get("tag_vinculada"))
    nao_vinculadas = len(resultado) - vinculadas
    taxa_vinculacao = (vinculadas / len(resultado) * 100) if resultado else 0

    print("\n📊 Resultados:")
    print(f"   - Vinculadas: {vinculadas}/{len(resultado)} ({taxa_vinculacao:.1f}%)")
    print(f"   - Não vinculadas: {nao_vinculadas}")

    # Detalhes por modificação
    if verbose:
        print("\n📋 Detalhamento:")
        for i, mod in enumerate(resultado, 1):
            tag_id = mod.get("tag_vinculada")
            if isinstance(tag_id, dict):
                tag_id = tag_id.get("id")

            status = "✅" if tag_id else "❌"
            tipo = mod.get("tipo", "?")

            print(f"   {status} Mod {i} ({tipo}): ", end="")
            if tag_id:
                tag = next((t for t in tags if t["id"] == tag_id), None)
                titulo = tag.get("titulo", "?") if tag else "?"
                print(f"→ {titulo[:50]}")
            else:
                print("não vinculada")

    # Estatísticas do híbrido
    if hasattr(algoritmo, "obter_estatisticas"):
        stats = algoritmo.obter_estatisticas()
        print("\n🎯 Estratégias usadas:")
        for estrategia, dados_est in stats.items():
            if dados_est["count"] > 0:
                print(
                    f"   - {estrategia}: {dados_est['count']} ({dados_est['percentage']:.1f}%)"
                )

    return {
        "algoritmo": algoritmo.nome,
        "total_modificacoes": len(resultado),
        "vinculadas": vinculadas,
        "nao_vinculadas": nao_vinculadas,
        "taxa_vinculacao": taxa_vinculacao,
        "resultado": resultado,
    }


def comparar_algoritmos(dados: dict[str, Any], algoritmos_nomes: list = None):
    """
    Compara múltiplos algoritmos no caso real.

    Args:
        dados: Dados extraídos do Directus
        algoritmos_nomes: Lista de algoritmos para testar (None = todos)
    """
    if not algoritmos_nomes:
        algoritmos_nomes = ["producao", "fuzzy", "regex", "hibrido"]

    print("\n" + "=" * 80)
    print("📊 COMPARAÇÃO DE ALGORITMOS - CASO REAL")
    print("=" * 80)

    resultados = []
    for nome in algoritmos_nomes:
        if nome not in ALGORITMOS:
            print(
                f"⚠️  Algoritmo '{nome}' não encontrado. Disponíveis: {', '.join(ALGORITMOS.keys())}"
            )
            continue

        classe = ALGORITMOS[nome]
        resultado = processar_com_algoritmo(classe, dados, verbose=False)
        resultados.append(resultado)

    # Ranking
    print("\n" + "=" * 80)
    print("🏆 RANKING FINAL:")
    print("=" * 80)

    resultados_ordenados = sorted(
        resultados, key=lambda r: r["taxa_vinculacao"], reverse=True
    )

    medalhas = ["🥇", "🥈", "🥉"]
    for i, res in enumerate(resultados_ordenados):
        medalha = medalhas[i] if i < 3 else "  "
        print(
            f"{medalha} {i + 1}. {res['algoritmo']}: {res['taxa_vinculacao']:.1f}% "
            f"({res['vinculadas']}/{res['total_modificacoes']} vinculadas)"
        )

    print("=" * 80)


def main():
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Processa versão real do Directus com algoritmos otimizados"
    )
    parser.add_argument(
        "--algoritmo",
        "-a",
        choices=list(ALGORITMOS.keys()) + ["todos"],
        default="todos",
        help="Algoritmo a usar (default: comparar todos)",
    )
    parser.add_argument(
        "--versao", "-v", default=VERSAO_ID, help=f"ID da versão (default: {VERSAO_ID})"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Imprimir detalhes de cada modificação"
    )
    parser.add_argument("--salvar", help="Salvar resultado em arquivo JSON")

    args = parser.parse_args()

    try:
        # 1. Baixar dados
        versao = baixar_versao_directus(args.versao)

        # 2. Extrair dados
        dados = extrair_dados_para_algoritmo(versao)

        # 3. Processar
        if args.algoritmo == "todos":
            comparar_algoritmos(dados)
        else:
            classe = ALGORITMOS[args.algoritmo]
            resultado = processar_com_algoritmo(classe, dados, verbose=args.verbose)

            # 4. Salvar se solicitado
            if args.salvar:
                with open(args.salvar, "w", encoding="utf-8") as f:
                    json.dump(resultado, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Resultado salvo em: {args.salvar}")

        print("\n✅ Processamento concluído!")

    except Exception as e:
        print(f"\n❌ Erro: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
