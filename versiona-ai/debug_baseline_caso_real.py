"""Debug específico para o baseline no caso real c2b1dfa0."""

import sys

sys.path.insert(0, "tests")

import json

from algoritmos.producao.algoritmo import AlgoritmoProducao

# Carregar dados
with open("versao_c2b1dfa0_raw.json") as f:
    data = json.load(f)

# Extrair tags
tags_raw = data["contrato"]["modelo_contrato"]["tags"]
tags = []
for tag in tags_raw:
    tags.append(
        {
            "id": tag.get("id"),
            "titulo": tag.get("tag_nome"),
            "texto": tag.get("conteudo", ""),
            "posicao_inicio": tag.get("posicao_inicio_texto"),
            "posicao_fim": tag.get("posicao_fim_texto"),
        }
    )

# Extrair modificações
modificacoes = []
for mod in data["modificacoes"]:
    texto_mod = mod.get("alteracao", "")
    if texto_mod == "--":
        continue  # Pular REMOCAO

    tipo = mod.get("categoria")
    conteudo = {}
    if tipo == "INSERCAO" or tipo == "ALTERACAO":
        conteudo["novo"] = texto_mod

    modificacoes.append(
        {
            "id": mod["id"],
            "tipo": tipo,
            "conteudo": conteudo,
        }
    )

# Baixar texto
import os

import docx

from repositorio import DirectusRepository

repo = DirectusRepository("http://localhost:8065", "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP")
arquivo_id = data["contrato"]["modelo_contrato"]["arquivo_original"]
arquivo_path = repo.download_file(arquivo_id)
doc = docx.Document(arquivo_path)
texto_completo = "\n".join([p.text for p in doc.paragraphs])
os.remove(arquivo_path)

print("=" * 80)
print("DEBUG: BASELINE NO CASO REAL")
print("=" * 80)
print(f"Modificações: {len(modificacoes)}")
print(f"Tags: {len(tags)}")
print(f"Texto: {len(texto_completo)} chars")
print()

# Processar
alg = AlgoritmoProducao()
print(f"Algoritmo: {alg.nome}")
print(f"Descrição: {alg.descricao}")
print()

# Ver o que acontece com cada modificação
for i, mod in enumerate(modificacoes, 1):
    print(f"\n--- Modificação {i} ({mod['tipo']}) ---")
    texto_busca = mod["conteudo"].get("novo", "")
    print(f"Texto busca: {texto_busca[:60]}...")

    # Tentar calcular posição
    pos = texto_completo.find(texto_busca)
    print(f"str.find(): {pos}")

    if pos == -1:
        print("❌ NÃO encontrado no texto - vai usar fuzzy apenas")

        # Testar fuzzy com cada tag
        threshold = alg._calcular_threshold_dinamico(texto_busca)
        print(f"Threshold: {threshold:.0f}%")

        for tag in tags:
            score = alg._calcular_score_composto(texto_busca, tag["texto"])
            status = "✅" if score >= threshold else "❌"
            print(f"  {status} Tag '{tag['titulo']}': {score:.1f}%")

# Agora processar completo
print("\n" + "=" * 80)
print("PROCESSAMENTO COMPLETO")
print("=" * 80)

resultado = alg.vincular_clausulas(modificacoes, tags, texto_completo)

vinculadas = sum(1 for r in resultado if r.get("tag_vinculada"))
print(
    f"Vinculadas: {vinculadas}/{len(resultado)} ({vinculadas / len(resultado) * 100:.1f}%)"
)

for i, r in enumerate(resultado, 1):
    tag = r.get("tag_vinculada")
    if tag:
        print(f"  ✅ Mod {i} → {tag.get('titulo', '?')}")
    else:
        print(f"  ❌ Mod {i} → não vinculada")
