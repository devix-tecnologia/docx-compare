#!/usr/bin/env python3
"""
Script para gerar prompt de teste A/B: IA vs Sistema Estruturado

Busca os mesmos dados que o sistema processou e gera um prompt
para o Claude analisar, permitindo comparação dos resultados.
"""

import json
import os
import sys
from pathlib import Path

import docx
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN")


def buscar_modelo_contrato(modelo_id: str) -> dict:
    """Busca dados do modelo de contrato no Directus."""
    url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato/{modelo_id}"
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

    params = {"fields": "*,arquivo_com_tags.*,arquivo_original.*,tags.*"}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    return response.json()["data"]


def buscar_contrato(contrato_id: str) -> dict:
    """Busca dados do contrato no Directus."""
    url = f"{DIRECTUS_BASE_URL}/items/contrato/{contrato_id}"
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

    params = {"fields": "*,versoes.*"}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    return response.json()["data"]


def buscar_versao(versao_id: str) -> dict:
    """Busca versão específica do contrato."""
    url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

    params = {"fields": "*,arquivo.*,modificacoes.*"}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    return response.json()["data"]


def buscar_versoes_modelo(modelo_id: str) -> list:
    """Busca versões do modelo de contrato."""
    url = f"{DIRECTUS_BASE_URL}/items/versao"
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

    params = {
        "filter": json.dumps(
            {
                "contrato": {"modelo_contrato": {"_eq": modelo_id}},
                "status": {"_in": ["concluido", "em_processamento"]},
            }
        ),
        "fields": "*,arquivo.*,contrato.*,modificacoes.*",
        "limit": 5,
        "sort": "-date_created",
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    return response.json()["data"]


def baixar_arquivo(arquivo_id: str, destino: Path) -> Path:
    """Baixa arquivo do Directus."""
    url = f"{DIRECTUS_BASE_URL}/assets/{arquivo_id}"
    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(response.content)

    return destino


def extrair_texto_docx(caminho: Path) -> str:
    """Extrai texto de um arquivo DOCX."""
    doc = docx.Document(caminho)

    paragrafos = []
    for i, para in enumerate(doc.paragraphs):
        texto = para.text.strip()
        if texto:
            paragrafos.append(f"[P{i:03d}] {texto}")

    return "\n".join(paragrafos)


def gerar_prompt(contrato_id: str, output_dir: Path) -> Path:
    """Gera prompt completo para teste A/B."""

    print(f"🔍 Buscando contrato {contrato_id}...")
    contrato = buscar_contrato(contrato_id)

    print(
        f"📄 Contrato: {contrato.get('titulo', 'Sem título')} (#{contrato.get('numero')})"
    )

    # Buscar modelo de contrato vinculado
    modelo_id = contrato.get("modelo_contrato")
    if not modelo_id:
        raise ValueError("Contrato não possui modelo vinculado")

    print(f"🔍 Buscando modelo de contrato {modelo_id}...")
    modelo = buscar_modelo_contrato(modelo_id)
    print(f"📄 Modelo: {modelo.get('nome', 'Sem nome')}")

    # Baixar arquivo do modelo (usar arquivo_com_tags se disponível, senão original)
    arquivo_obj = modelo.get("arquivo_com_tags") or modelo.get("arquivo_original")
    if not arquivo_obj:
        raise ValueError("Modelo não possui arquivo vinculado")

    # Extrair ID do arquivo (pode ser string ou objeto)
    arquivo_id = arquivo_obj["id"] if isinstance(arquivo_obj, dict) else arquivo_obj

    temp_dir = output_dir / "temp"
    modelo_path = baixar_arquivo(arquivo_id, temp_dir / f"modelo_{modelo_id}.docx")
    print(f"✅ Modelo baixado: {modelo_path}")

    # Extrair texto do modelo
    texto_modelo = extrair_texto_docx(modelo_path)

    # Buscar tags/cláusulas completas (já expandidas pelo fields=*,tags.*)
    print("🔍 Processando tags...")
    tags_objs = modelo.get("tags", [])
    tags_formatadas = []

    # Buscar cláusulas do modelo para vincular às tags
    clausulas_ids = modelo.get("clausulas", [])
    clausulas_map = {}
    if clausulas_ids:
        print(f"🔍 Buscando {len(clausulas_ids)} cláusulas...")
        for clausula_id in clausulas_ids:
            try:
                url = f"{DIRECTUS_BASE_URL}/items/clausula/{clausula_id}"
                headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    clausula_data = response.json()["data"]
                    clausulas_map[clausula_id] = clausula_data.get("nome", "Sem nome")
            except Exception as e:
                print(f"⚠️  Erro ao buscar cláusula {clausula_id}: {e}")

    for tag in tags_objs:
        # Tags já vêm expandidas como objetos
        if isinstance(tag, dict):
            # Buscar nomes das cláusulas vinculadas
            clausulas_vinculadas = []
            for clausula_id in tag.get("clausulas", []):
                if clausula_id in clausulas_map:
                    clausulas_vinculadas.append(
                        {"id": clausula_id, "nome": clausulas_map[clausula_id]}
                    )

            tags_formatadas.append(
                {
                    "id": tag.get("id"),
                    "tag_nome": tag.get("tag_nome", "Sem nome"),
                    "posicao_inicio": tag.get("posicao_inicio_texto"),
                    "posicao_fim": tag.get("posicao_fim_texto"),
                    "conteudo_preview": tag.get("conteudo", "")[:100] + "..."
                    if tag.get("conteudo")
                    else "",
                    "clausulas": clausulas_vinculadas,
                }
            )

    print(f"🏷️  Tags encontradas: {len(tags_formatadas)}")

    # Buscar versão do contrato
    versoes_objs = contrato.get("versoes", [])
    if not versoes_objs:
        raise ValueError("Contrato não possui versões")

    # Extrair ID da primeira versão (pode ser string ou objeto)
    versao_obj = versoes_objs[0]
    versao_id = versao_obj["id"] if isinstance(versao_obj, dict) else versao_obj

    print(f"\n🔍 Buscando versão {versao_id}...")
    versao = buscar_versao(versao_id)

    print(f"📝 Versão selecionada: {versao_id}")
    print(f"   Status: {versao.get('status')}")
    print(f"   Modificações: {len(versao.get('modificacoes', []))}")

    # Baixar arquivo da versão
    arquivo_versao_obj = versao.get("arquivo")
    if not arquivo_versao_obj:
        raise ValueError("Versão não possui arquivo vinculado")

    # Extrair ID do arquivo (pode ser string ou objeto)
    arquivo_versao_id = (
        arquivo_versao_obj["id"]
        if isinstance(arquivo_versao_obj, dict)
        else arquivo_versao_obj
    )

    versao_path = baixar_arquivo(
        arquivo_versao_id, temp_dir / f"versao_{versao_id}.docx"
    )
    print(f"✅ Versão baixada: {versao_path}")

    # Extrair texto da versão
    texto_versao = extrair_texto_docx(versao_path)

    # Buscar modificações geradas pelo sistema
    modificacoes_ids = versao.get("modificacoes", [])
    modificacoes_sistema = []

    if modificacoes_ids:
        print(f"\n🔍 Buscando detalhes de {len(modificacoes_ids)} modificações...")
        for mod_id in modificacoes_ids:
            # Se modificacoes já são objetos, usar direto; se são IDs, buscar
            if isinstance(mod_id, dict):
                modificacoes_sistema.append(mod_id)
            else:
                try:
                    url = f"{DIRECTUS_BASE_URL}/items/modificacao/{mod_id}"
                    headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        modificacoes_sistema.append(response.json()["data"])
                except Exception as e:
                    print(f"⚠️  Erro ao buscar modificação {mod_id}: {e}")

    # Preparar resumo das modificações para o prompt
    mods_resumo = []
    for mod in modificacoes_sistema:
        mods_resumo.append(
            {
                "id": mod.get("id"),
                "tipo": mod.get("tipo"),
                "posicao_inicio": mod.get("posicao_inicio"),
                "posicao_fim": mod.get("posicao_fim"),
                "tem_conteudo": bool(mod.get("conteudo")),
                "tem_original": bool(mod.get("conteudo_original")),
            }
        )

    # Gerar prompt
    prompt = f"""# Teste A/B: Análise de Contrato com IA vs Sistema Estruturado

## Contexto

Você é um sistema de análise jurídica que identifica modificações entre versões de contratos. Sua tarefa é comparar dois documentos e gerar uma lista estruturada de modificações, vinculando-as às cláusulas do modelo de contrato.

**IMPORTANTE**: O sistema estruturado já processou estes documentos e encontrou **{len(modificacoes_sistema)} modificações**. Sua análise será comparada com este resultado.

## Sua Tarefa

Analise as diferenças entre o documento do MODELO (template) e o documento da VERSÃO (modificado) e gere uma lista de modificações com a seguinte estrutura JSON:

```json
{{
  "modificacoes": [
    {{
      "id": "mod-001",
      "tipo": "adicao|remocao|alteracao",
      "conteudo_original": "texto do modelo que foi alterado/removido (null se adição)",
      "conteudo": "texto na versão (null se remoção)",
      "posicao_aprox": 150,
      "clausula_relacionada_id": "uuid ou null",
      "clausula_relacionada_nome": "nome da cláusula ou null",
      "contexto": "explicação da mudança",
      "nivel_impacto": "baixo|medio|alto",
      "confianca": "0-100%"
    }}
  ],
  "resumo": {{
    "total_adicoes": 0,
    "total_remocoes": 0,
    "total_alteracoes": 0,
    "clausulas_afetadas": [],
    "analise_qualitativa": "2-3 parágrafos sobre mudanças mais significativas"
  }}
}}
```

## Critérios de Qualidade

1. **Precisão**: Identifique TODAS as diferenças relevantes entre os textos
2. **Vinculação**: Use as posições das tags para associar modificações às cláusulas corretas
3. **Contexto**: Explique o significado jurídico/contratual de cada mudança
4. **Agrupamento**: Modificações próximas na mesma cláusula podem ser agrupadas
5. **Impacto**: Avalie se a mudança é cosmética (baixo), significativa (medio) ou crítica (alto)

## Regras Específicas

- Ignore diferenças de formatação pura (negrito, itálico, fonte)
- Ignore espaçamentos e quebras de linha se não mudarem o sentido
- Priorize mudanças em: valores monetários, datas, prazos, obrigações, responsabilidades
- Uma substituição de texto é uma "alteracao", não uma remoção + adição
- Compare os textos parágrafo por parágrafo usando os marcadores [P000], [P001], etc.

---

## DADOS DE ENTRADA

### 1. Modelo de Contrato - Informações

**ID do Modelo**: `{modelo_id}`
**Nome**: {modelo.get("nome", "N/A")}
**Arquivo**: {arquivo_obj.get("filename_download", "N/A") if isinstance(arquivo_obj, dict) else "N/A"}

### 2. Tags/Cláusulas do Modelo

```json
{json.dumps(tags_formatadas, indent=2, ensure_ascii=False)}
```

### 3. Documento do MODELO (Template Base)

```text
{texto_modelo}
```

### 4. Documento da VERSÃO (Com Modificações)

**ID da Versão**: `{versao_id}`
**Status**: {versao.get("status")}
**Origem**: {versao.get("origem")}

```text
{texto_versao}
```

---

## RESULTADO DO SISTEMA ESTRUTURADO (Para Comparação)

O sistema estruturado identificou **{len(modificacoes_sistema)} modificações**.

Resumo das modificações do sistema:
```json
{json.dumps(mods_resumo, indent=2, ensure_ascii=False)}
```

---

## INSTRUÇÕES FINAIS

1. Analise cuidadosamente os dois documentos
2. Identifique TODAS as diferenças
3. Para cada diferença, determine qual cláusula (tag) ela pertence usando as posições
4. Gere o JSON completo conforme o schema acima
5. Adicione a análise qualitativa no campo `resumo.analise_qualitativa`

**Comece sua análise agora!**
"""

    # Salvar prompt
    prompt_path = output_dir / f"prompt_teste_ab_{contrato_id[:8]}_{versao_id[:8]}.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    print(f"\n✅ Prompt salvo em: {prompt_path}")

    # Salvar dados estruturados separadamente para facilitar comparação
    dados_path = output_dir / f"dados_sistema_{contrato_id[:8]}_{versao_id[:8]}.json"
    dados_sistema = {
        "contrato_id": contrato_id,
        "contrato_titulo": contrato.get("titulo"),
        "modelo_id": modelo_id,
        "modelo_nome": modelo.get("nome"),
        "versao_id": versao_id,
        "versao_status": versao.get("status"),
        "total_modificacoes_sistema": len(modificacoes_sistema),
        "modificacoes_sistema": modificacoes_sistema,
        "tags": tags_formatadas,
        "arquivos": {
            "modelo": str(modelo_path.relative_to(output_dir)),
            "versao": str(versao_path.relative_to(output_dir)),
        },
    }
    dados_path.write_text(
        json.dumps(dados_sistema, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"✅ Dados do sistema salvos em: {dados_path}")

    return prompt_path


def main():
    if not DIRECTUS_TOKEN:
        print("❌ DIRECTUS_TOKEN não configurado no .env")
        sys.exit(1)

    # Contrato a ser analisado
    contrato_id = "77b8555b-e40d-4ece-8c8a-88367b36a625"

    # Diretório de saída
    output_dir = Path(__file__).parent / "teste_ab_output"
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("🧪 GERADOR DE PROMPT PARA TESTE A/B")
    print("=" * 80)
    print()

    try:
        prompt_path = gerar_prompt(contrato_id, output_dir)

        if prompt_path:
            print("\n" + "=" * 80)
            print("✅ PROMPT GERADO COM SUCESSO!")
            print("=" * 80)
            print(f"\n📄 Arquivo: {prompt_path}")
            print(f"📂 Diretório: {output_dir}")
            print("\n📋 Próximos passos:")
            print("   1. Abra o arquivo .md gerado")
            print("   2. Copie o conteúdo")
            print("   3. Cole em uma conversa com o Claude")
            print("   4. Compare o resultado com os dados em dados_sistema_*.json")
            print()

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
