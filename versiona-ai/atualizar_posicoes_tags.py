#!/usr/bin/env python3
"""
Atualiza posições das tags de modelo_contrato para usar coordenadas do texto limpo
(sem marcações {{TAG-X}})

Este script corrige o bug onde as tags tinham posições calculadas no texto COM marcações,
mas o diff é feito no texto SEM marcações.
"""
import os
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from processador_tags_modelo import ProcessadorTagsModelo


def atualizar_posicoes_modelo(modelo_id: str, directus_url: str, directus_token: str):
    """
    Atualiza posições das tags de um modelo_contrato.
    
    Args:
        modelo_id: ID do modelo de contrato
        directus_url: URL base do Directus
        directus_token: Token de autenticação
    """
    base_url = directus_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {directus_token}",
        "Content-Type": "application/json",
    }
    
    print("="  * 80)
    print("🔄 ATUALIZAR POSIÇÕES DAS TAGS")
    print("=" * 80)
    print(f"Modelo: {modelo_id}")
    print(f"Directus: {directus_url}")
    print("=" * 80)
    
    # 1. Buscar modelo com arquivo_com_tags
    print("\n📥 Buscando modelo...")
    url = f"{base_url}/items/modelo_contrato/{modelo_id}"
    params = {"fields": "id,nome,arquivo_com_tags"}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    
    if response.status_code != 200:
        raise ValueError(f"Erro ao buscar modelo: HTTP {response.status_code}")
    
    modelo_data = response.json()["data"]
    arquivo_tagged_id = modelo_data.get("arquivo_com_tags")
    
    if not arquivo_tagged_id:
        raise ValueError("Modelo não tem arquivo_com_tags")
    
    print(f"✅ Modelo encontrado: {modelo_data.get('nome')}")
    print(f"📁 Arquivo com tags: {arquivo_tagged_id}")
    
    # 2. Baixar e processar arquivo_com_tags
    print("\n📥 Baixando arquivo_com_tags...")
    processador = ProcessadorTagsModelo(directus_url, directus_token)
    texto_tagged = processador._baixar_e_extrair_texto(arquivo_tagged_id)
    print(f"📊 Texto com tags: {len(texto_tagged)} caracteres")
    
    # 3. Remover marcações e criar mapa de posições
    print("\n🔄 Removendo marcações...")
    texto_limpo, mapa_posicoes = processador._remover_marcacoes_e_mapear(texto_tagged)
    print(f"📊 Texto limpo: {len(texto_limpo)} caracteres")
    print(f"🗺️  Mapa de {len(mapa_posicoes)} posições criado")
    
    # 4. Extrair conteúdo e posições no texto limpo
    print("\n🏷️  Extraindo conteúdo das tags...")
    conteudo_tags = processador._extrair_conteudo_entre_tags(
        texto_com_tags=texto_tagged,
        texto_limpo=texto_limpo,
        mapa_posicoes=mapa_posicoes
    )
    print(f"✅ {len(conteudo_tags)} tags processadas")
    
    # 5. Buscar tags existentes no banco
    print("\n📥 Buscando tags do banco...")
    tags_url = f"{base_url}/items/modelo_contrato_tag"
    params = {
        "filter[modelo_contrato][_eq]": modelo_id,
        "fields": "id,tag_nome,posicao_inicio_texto,posicao_fim_texto",
        "limit": -1
    }
    response = requests.get(tags_url, headers=headers, params=params, timeout=30)
    
    if response.status_code != 200:
        raise ValueError(f"Erro ao buscar tags: HTTP {response.status_code}")
    
    tags_banco = response.json()["data"]
    print(f"✅ {len(tags_banco)} tags encontradas no banco")
    
    # 6. Atualizar cada tag individualmente
    print("\n🔄 Atualizando posições das tags...")
    atualizadas = 0
    nao_encontradas = 0
    erros = 0
    
    for tag in tags_banco:
        tag_id = tag["id"]
        tag_nome = tag["tag_nome"]
        pos_antiga_inicio = tag.get("posicao_inicio_texto")
        pos_antiga_fim = tag.get("posicao_fim_texto")
        
        # Buscar nova posição no conteudo_tags
        if tag_nome not in conteudo_tags:
            nao_encontradas += 1
            print(f"  ⚠️  Tag {tag_nome} não encontrada no processamento")
            continue
        
        nova_pos = conteudo_tags[tag_nome]
        pos_nova_inicio = nova_pos["posicao_inicial_texto"]
        pos_nova_fim = nova_pos["posicao_final_texto"]
        
        # Verificar se mudou
        if pos_antiga_inicio == pos_nova_inicio and pos_antiga_fim == pos_nova_fim:
            # Posição já está correta
            continue
        
        # Atualizar tag
        update_url = f"{base_url}/items/modelo_contrato_tag/{tag_id}"
        update_data = {
            "posicao_inicio_texto": pos_nova_inicio,
            "posicao_fim_texto": pos_nova_fim
        }
        
        response = requests.patch(
            update_url,
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            atualizadas += 1
            delta_inicio = pos_nova_inicio - (pos_antiga_inicio or 0)
            delta_fim = pos_nova_fim - (pos_antiga_fim or 0)
            if atualizadas <= 5:  # Log apenas primeiras 5
                print(f"  ✅ Tag {tag_nome}: {pos_antiga_inicio}→{pos_nova_inicio} ({delta_inicio:+d}), {pos_antiga_fim}→{pos_nova_fim} ({delta_fim:+d})")
        else:
            erros += 1
            if erros <= 3:  # Log apenas primeiros 3 erros
                print(f"  ❌ Erro ao atualizar tag {tag_nome}: HTTP {response.status_code}")
    
    # Relatório final
    print("\n" + "=" * 80)
    print("✅ ATUALIZAÇÃO CONCLUÍDA")
    print("=" * 80)
    print(f"Tags atualizadas: {atualizadas}")
    print(f"Tags não encontradas: {nao_encontradas}")
    print(f"Erros: {erros}")
    print(f"Total processado: {len(tags_banco)}")
    
    return {
        "atualizadas": atualizadas,
        "nao_encontradas": nao_encontradas,
        "erros": erros,
        "total": len(tags_banco)
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Atualizar posições das tags para usar texto limpo"
    )
    parser.add_argument(
        "--modelo-id",
        required=True,
        help="ID do modelo de contrato"
    )
    parser.add_argument(
        "--directus-url",
        default="http://localhost:8065",
        help="URL base do Directus (default: http://localhost:8065)"
    )
    parser.add_argument(
        "--directus-token",
        default="pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP",
        help="Token de autenticação do Directus"
    )
    
    args = parser.parse_args()
    
    try:
        resultado = atualizar_posicoes_modelo(
            modelo_id=args.modelo_id,
            directus_url=args.directus_url,
            directus_token=args.directus_token
        )
        
        if resultado["erros"] > 0:
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
