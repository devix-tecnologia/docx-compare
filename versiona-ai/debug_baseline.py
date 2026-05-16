"""Debug do algoritmo baseline para entender por que falhou."""

import json
from difflib import SequenceMatcher

# Carregar dados
with open('versao_c2b1dfa0_raw.json') as f:
    data = json.load(f)

# Extrair tags
tags = data['contrato']['modelo_contrato']['tags']
print("=" * 80)
print("TAGS DO MODELO")
print("=" * 80)
for i, tag in enumerate(tags, 1):
    print(f"\n{i}. Tag: {tag['tag_nome']}")
    print(f"   Posição: {tag['posicao_inicio_texto']}-{tag['posicao_fim_texto']}")
    print(f"   Texto: {tag['conteudo'][:100]}...")

# Extrair texto completo do .docx
from repositorio import DirectusRepository
import docx
import os

DIRECTUS_URL = "http://localhost:8065"
DIRECTUS_TOKEN = "pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP"

arquivo_id = data['contrato']['modelo_contrato'].get('arquivo_original')
repo = DirectusRepository(DIRECTUS_URL, DIRECTUS_TOKEN)
arquivo_path = repo.download_file(arquivo_id)
doc = docx.Document(arquivo_path)
texto_completo = "\n".join([p.text for p in doc.paragraphs])
os.remove(arquivo_path)

print("\n" + "=" * 80)
print("TEXTO COMPLETO (.docx)")
print("=" * 80)
print(f"Total: {len(texto_completo)} caracteres")
print(f"Preview: {texto_completo[:200]}...")

# Extrair modificações
modificacoes = data['modificacoes']
print("\n" + "=" * 80)
print("MODIFICAÇÕES")
print("=" * 80)
for i, mod in enumerate(modificacoes, 1):
    print(f"\n{i}. {mod['categoria']}: {mod['alteracao'][:80]}...")
    
    # Testar busca simples
    pos = texto_completo.find(mod['alteracao'])
    print(f"   Busca simples (str.find): {pos}")
    
    if pos != -1:
        print(f"   ✅ Encontrado na posição {pos}-{pos + len(mod['alteracao'])}")
        
        # Verificar overlap com tags
        mod_inicio = pos
        mod_fim = pos + len(mod['alteracao'])
        
        for tag in tags:
            tag_inicio = tag['posicao_inicio_texto']
            tag_fim = tag['posicao_fim_texto']
            
            # Calcular overlap
            overlap_inicio = max(mod_inicio, tag_inicio)
            overlap_fim = min(mod_fim, tag_fim)
            overlap_length = max(0, overlap_fim - overlap_inicio)
            
            if overlap_length > 0:
                mod_length = mod_fim - mod_inicio
                overlap_ratio = overlap_length / mod_length
                print(f"   📍 Overlap com '{tag['tag_nome']}': {overlap_ratio:.2%}")
                
                if overlap_ratio > 0.5:
                    print(f"      ✅ VINCULARIA por overlap!")
    else:
        print(f"   ❌ NÃO encontrado no texto")
        
        # Tentar fuzzy matching com tags
        print(f"   🔍 Tentando fuzzy matching...")
        for tag in tags:
            tag_texto = tag['conteudo']
            
            # Substring check
            if mod['alteracao'] in tag_texto:
                print(f"      ✅ É substring de '{tag['tag_nome']}'")
            else:
                # Fuzzy matching
                similarity = SequenceMatcher(None, mod['alteracao'], tag_texto).ratio()
                if similarity >= 0.85:
                    print(f"      ✅ Fuzzy match {similarity:.2%} com '{tag['tag_nome']}'")
                elif similarity >= 0.5:
                    print(f"      ⚠️  Fuzzy match {similarity:.2%} com '{tag['tag_nome']}' (abaixo threshold)")

print("\n" + "=" * 80)
print("ANÁLISE FINAL")
print("=" * 80)
print("O baseline precisa:")
print("1. Calcular posições das modificações (str.find no texto)")
print("2. Vincular por fuzzy matching (threshold 85%) ou overlap (>50%)")
print("Se str.find retorna -1, não há vinculação possível.")
