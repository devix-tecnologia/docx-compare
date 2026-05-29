#!/usr/bin/env python3
"""
Orquestrador de Teste A/B: Sistema Estruturado vs IA Pura

Este script coordena três subagentes:
1. Subagente Sistema: Processa contrato via Docker (sistema estruturado)
2. Subagente IA: Processa contrato via IA pura
3. Subagente Comparador: Compara resultados e gera análise

Fluxo:
- Contrato → Modelo de Contrato → Versões
- Cada versão é processada pelos dois métodos
- Comparação gera métricas de precisão, recall, tempo, qualidade
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from docx import Document
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN")


class SubagenteSetup:
    """Prepara dados para processamento."""

    def __init__(self, contrato_id: str):
        self.contrato_id = contrato_id
        self.headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

    def buscar_contrato(self) -> dict:
        """Busca dados do contrato."""
        url = f"{DIRECTUS_BASE_URL}/items/contrato/{self.contrato_id}"
        params = {
            "fields": "*,versoes.*",
            "deep[versoes][_limit]": "-1",
        }
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()["data"]

    def buscar_modelo(self, modelo_id: str) -> dict:
        """Busca modelo de contrato com tags."""
        url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato/{modelo_id}"
        params = {
            "fields": "*,tags.*,clausulas.*",
            "deep[tags][_limit]": "-1",
            "deep[clausulas][_limit]": "-1",
        }
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()["data"]

    def buscar_versao(self, versao_id: str) -> dict:
        """Busca versão específica."""
        url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
        params = {
            "fields": "*,arquivo.*,modificacoes.*",
            "deep[modificacoes][_limit]": "-1",
        }
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()["data"]

    def preparar_contexto(self) -> dict[str, Any]:
        """Prepara todo o contexto necessário."""
        print(f"📦 Preparando contexto para contrato {self.contrato_id}...")

        # Buscar contrato
        contrato = self.buscar_contrato()
        print(f"   ✓ Contrato: {contrato.get('titulo')} (#{contrato.get('numero')})")

        # Buscar modelo
        modelo_id = contrato.get("modelo_contrato")
        modelo = self.buscar_modelo(modelo_id)
        print(f"   ✓ Modelo: {modelo.get('nome')} ({len(modelo.get('tags', []))} tags)")

        # Buscar versões
        versoes_ids = contrato.get("versoes", [])
        versoes = []
        for versao_obj in versoes_ids:
            versao_id = versao_obj["id"] if isinstance(versao_obj, dict) else versao_obj
            versao = self.buscar_versao(versao_id)
            versoes.append(versao)
            print(
                f"   ✓ Versão: {versao_id} ({versao.get('status')}, {len(versao.get('modificacoes', []))} mods)"
            )

        return {
            "contrato": contrato,
            "modelo": modelo,
            "versoes": versoes,
            "timestamp": datetime.now().isoformat(),
        }


class SubagenteSistema:
    """Processa contrato usando sistema estruturado (Docker)."""

    def __init__(self, contexto: dict):
        self.contexto = contexto

    def processar(self) -> dict[str, Any]:
        """
        Processa contrato via API do sistema Docker.

        Returns:
            Resultado com modificações detectadas, tempo, métricas
        """
        print("\n🔧 SUBAGENTE SISTEMA: Processando via Docker...")

        contrato_id = self.contexto["contrato"]["id"]
        modelo_id = self.contexto["modelo"]["id"]

        inicio = datetime.now()

        try:
            # Chamar API do sistema (assumindo que está rodando)
            # Aqui você pode usar a API local ou fazer chamadas diretas ao Directus
            # para pegar os resultados já processados

            versoes_resultados = []
            for versao in self.contexto["versoes"]:
                versao_id = versao["id"]
                modificacoes_ids = versao.get("modificacoes", [])

                # Buscar detalhes das modificações
                modificacoes = []
                for mod_id in modificacoes_ids:
                    if isinstance(mod_id, dict):
                        modificacoes.append(mod_id)
                    else:
                        # Buscar modificação do Directus
                        try:
                            url = f"{DIRECTUS_BASE_URL}/items/modificacao/{mod_id}"
                            headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
                            response = requests.get(url, headers=headers, timeout=30)
                            if response.status_code == 200:
                                modificacoes.append(response.json()["data"])
                        except Exception as e:
                            print(f"      ⚠️ Erro ao buscar modificação {mod_id}: {e}")

                versoes_resultados.append(
                    {
                        "versao_id": versao_id,
                        "status": versao.get("status"),
                        "modificacoes": modificacoes,
                        "total": len(modificacoes),
                    }
                )

                print(f"   ✓ Versão {versao_id[:8]}: {len(modificacoes)} modificações")

            tempo_decorrido = (datetime.now() - inicio).total_seconds()

            resultado = {
                "metodo": "sistema_estruturado",
                "contrato_id": contrato_id,
                "modelo_id": modelo_id,
                "versoes": versoes_resultados,
                "total_modificacoes": sum(v["total"] for v in versoes_resultados),
                "tempo_segundos": tempo_decorrido,
                "sucesso": True,
                "timestamp": datetime.now().isoformat(),
            }

            print(
                f"   ✅ Sistema: {resultado['total_modificacoes']} modificações em {tempo_decorrido:.2f}s"
            )
            return resultado

        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return {
                "metodo": "sistema_estruturado",
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }


class SubagenteIA:
    """Processa contrato usando IA pura."""

    def __init__(self, contexto: dict, output_dir: Path):
        self.contexto = contexto
        self.output_dir = output_dir
        self.temp_dir = output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)

    def baixar_arquivo(self, arquivo_id: str, destino: Path) -> Path:
        """Baixa arquivo do Directus."""
        url = f"{DIRECTUS_BASE_URL}/assets/{arquivo_id}"
        headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}

        destino.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()

        with open(destino, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return destino

    def extrair_texto_docx(self, docx_path: Path) -> str:
        """Extrai texto do DOCX com marcadores de parágrafo."""
        doc = Document(docx_path)
        paragrafos = []

        for i, para in enumerate(doc.paragraphs):
            texto = para.text.strip()
            if texto:
                paragrafos.append(f"[P{i:03d}] {texto}")

        return "\n".join(paragrafos)

    def gerar_prompt(self, versao: dict) -> tuple[str, Path, Path]:
        """Gera prompt completo para IA analisar uma versão."""
        modelo = self.contexto["modelo"]
        contrato = self.contexto["contrato"]

        # Decidir qual documento usar como baseline (anterior)
        versao_anterior_id = versao.get("versao_anterior")

        if versao_anterior_id:
            # Se há versão anterior, usar documento dessa versão
            print(
                f"      ℹ️  Usando versão anterior como baseline: {versao_anterior_id[:8]}..."
            )
            url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_anterior_id}"
            headers = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
            params = {"fields": "*,arquivo.*"}
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            versao_anterior = response.json()["data"]

            arquivo_baseline_obj = versao_anterior.get("arquivo")
            baseline_label = f"VERSÃO ANTERIOR ({versao_anterior_id[:8]})"
        else:
            # Se não há versão anterior, usar arquivo_original do modelo (documento sem tags)
            print("      ℹ️  Usando arquivo original do modelo como baseline")
            arquivo_baseline_obj = modelo.get("arquivo_original")
            baseline_label = "DOCUMENTO ORIGINAL (sem tags)"

        arquivo_baseline_id = (
            arquivo_baseline_obj["id"]
            if isinstance(arquivo_baseline_obj, dict)
            else arquivo_baseline_obj
        )

        baseline_path = self.baixar_arquivo(
            arquivo_baseline_id, self.temp_dir / f"baseline_{versao['id']}.docx"
        )

        # Baixar arquivo da versão atual
        arquivo_versao_obj = versao.get("arquivo")
        arquivo_versao_id = (
            arquivo_versao_obj["id"]
            if isinstance(arquivo_versao_obj, dict)
            else arquivo_versao_obj
        )

        versao_path = self.baixar_arquivo(
            arquivo_versao_id, self.temp_dir / f"versao_{versao['id']}.docx"
        )

        # Extrair textos
        texto_baseline = self.extrair_texto_docx(baseline_path)
        texto_versao = self.extrair_texto_docx(versao_path)

        # Extrair informações das tags
        tags_info = []
        for tag in modelo.get("tags", []):
            if isinstance(tag, dict):
                tags_info.append(
                    {
                        "id": tag.get("id"),
                        "nome": tag.get("tag_nome"),
                        "posicao_inicio": tag.get("posicao_inicio_texto"),
                        "posicao_fim": tag.get("posicao_fim_texto"),
                        "preview": tag.get("conteudo", "")[:80] + "..."
                        if tag.get("conteudo")
                        else "",
                    }
                )

        prompt = f"""# Teste A/B: Análise de Contrato com IA Pura

## Sua Missão

Você é um sistema de análise jurídica especializado. Sua tarefa é identificar **TODAS as modificações** entre o documento ANTERIOR e o documento VERSÃO ATUAL.

## Contexto do Teste

- **Contrato**: {self.contexto["contrato"].get("titulo")} (#{self.contexto["contrato"].get("numero")})
- **Modelo**: {modelo.get("nome")} ({len(tags_info)} tags/cláusulas mapeadas)
- **Baseline**: {baseline_label}
- **Versão Atual**: {versao.get("id")[:8]}... (Status: {versao.get("status")})

**IMPORTANTE**: Um sistema estruturado já processou estes documentos. Seu resultado será comparado para avaliar precisão, recall e qualidade da análise por IA pura.

---

## Tags/Cláusulas do Modelo (para referência)

As seguintes tags/cláusulas estão mapeadas no modelo de contrato. Use-as para vincular modificações às cláusulas correspondentes:

{json.dumps(tags_info, indent=2, ensure_ascii=False)}

---

## DOCUMENTO ANTERIOR ({baseline_label})

```text
{texto_baseline}
```

---

## DOCUMENTO VERSÃO ATUAL (Modificado)

```text
{texto_versao}
```

---

## Sua Tarefa

Compare os dois documentos acima e gere um JSON com **TODAS as modificações** encontradas.

### Estrutura do JSON de Resposta

```json
{{
  "versao_id": "{versao.get("id")}",
  "modificacoes": [
    {{
      "id_sequencial": 1,
      "tipo": "adicao|remocao|alteracao",
      "conteudo_original": "texto exato do documento anterior (null se adição)",
      "conteudo": "texto exato na versão atual (null se remoção)",
      "posicao_inicio": 150,
      "posicao_fim": 250,
      "paragrafo_inicio": "P042",
      "paragrafo_fim": "P045",
      "tag_relacionada_id": "uuid ou null",
      "tag_relacionada_nome": "nome da tag/cláusula ou null",
      "contexto": "explicação clara da mudança",
      "nivel_impacto": "baixo|medio|alto",
      "confianca": 85
    }}
  ],
  "resumo": {{
    "total_modificacoes": 10,
    "total_adicoes": 3,
    "total_remocoes": 2,
    "total_alteracoes": 5,
    "tags_afetadas": ["1.1", "2.3"],
    "tempo_analise_estimado": "2 minutos",
    "observacoes": "Principais mudanças concentradas em valores e prazos"
  }},
  "metadata": {{
    "metodo": "ia_pura",
    "modelo_usado": "GitHub Copilot / Claude",
    "timestamp": "{datetime.now().isoformat()}"
  }}
}}
```

### Critérios Importantes

1. **Precisão**: Identifique TODAS as diferenças de conteúdo
2. **Vinculação**: Use as posições das tags para associar modificações
3. **Tipo correto**:
   - `adicao`: texto que existe na versão atual mas não no documento anterior
   - `remocao`: texto que existe no documento anterior mas não na versão atual
   - `alteracao`: texto que mudou (substituição)
4. **Impacto**:
   - `baixo`: formatação, pontuação, correções ortográficas
   - `medio`: mudanças de valores, datas não críticas
   - `alto`: mudanças em obrigações, responsabilidades, valores críticos
5. **Ignore**: Diferenças de formatação pura (negrito, itálico, fonte) e tags de marcação (como {{{{1}}}}, {{{{/1}}}}, etc.)
6. **Posições**: Use os marcadores [P000], [P001], etc para identificar parágrafos

### Instruções Finais

- Compare parágrafo por parágrafo usando os marcadores [PXXX]
- Use as posições das tags para vincular modificações às cláusulas
- **IGNORE completamente tags de marcação** como {{{{tag}}}}, {{{{/tag}}}} - elas são apenas metadados estruturais
- Seja completo: não omita modificações pequenas de **conteúdo real**
- Retorne APENAS o JSON, sem texto adicional antes ou depois
- JSON deve ser válido e parseável

**COMECE SUA ANÁLISE AGORA!**
"""

        return prompt, baseline_path, versao_path

    def processar(self) -> dict[str, Any]:
        """
        Processa contrato usando IA pura (via GitHub Copilot manual).

        Returns:
            Resultado com modificações detectadas pela IA
        """
        print("\n🤖 SUBAGENTE IA: Gerando prompt para análise manual...")

        inicio = datetime.now()

        try:
            versoes_resultados = []
            prompts_gerados = []

            for versao in self.contexto["versoes"]:
                print(f"   📝 Gerando prompt para versão {versao['id'][:8]}...")

                # Gerar prompt completo com documentos
                prompt, baseline_path, versao_path = self.gerar_prompt(versao)

                # Salvar prompt em arquivo
                versao_id_short = versao["id"][:8]
                prompt_path = self.output_dir / f"prompt_ia_{versao_id_short}.md"
                prompt_path.write_text(prompt, encoding="utf-8")

                print(f"      ✅ Prompt salvo: {prompt_path.name}")
                print(f"      📄 Baseline: {baseline_path.name}")
                print(f"      📄 Versão: {versao_path.name}")
                print(f"      📄 Versão: {versao_path.name}")

                prompts_gerados.append(
                    {
                        "versao_id": versao["id"],
                        "prompt_path": str(prompt_path),
                        "resultado_esperado": f"resultado_ia_{versao_id_short}.json",
                    }
                )

            tempo_decorrido = (datetime.now() - inicio).total_seconds()

            # Instruções para o usuário
            print("\n" + "=" * 70)
            print("📋 INSTRUÇÕES PARA ANÁLISE COM IA")
            print("=" * 70)
            print("\n1. Abra uma NOVA CONVERSA no GitHub Copilot")
            for item in prompts_gerados:
                versao_id_short = item["versao_id"][:8]
                print(f"\n2. Copie o conteúdo de: {Path(item['prompt_path']).name}")
                print("3. Cole na conversa e aguarde a resposta JSON")
                print("4. Copie o JSON da resposta")
                print(f"5. Salve em: {self.output_dir}/{item['resultado_esperado']}")

            print("\n6. Após salvar TODOS os arquivos, execute:")
            print("   python teste_ab_orquestrador.py --comparar")
            print("\n" + "=" * 70)

            resultado = {
                "metodo": "ia_pura",
                "contrato_id": self.contexto["contrato"]["id"],
                "modelo_id": self.contexto["modelo"]["id"],
                "prompts_gerados": prompts_gerados,
                "aguardando_usuario": True,
                "tempo_geracao_segundos": tempo_decorrido,
                "sucesso": True,
                "timestamp": datetime.now().isoformat(),
                "instrucoes": "Prompts salvos. Usuário deve processar manualmente e salvar resultados.",
            }

            print(f"\n   ✅ Prompts gerados em {tempo_decorrido:.2f}s")
            return resultado

        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback

            traceback.print_exc()
            return {
                "metodo": "ia_pura",
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }


class SubagenteComparador:
    """Compara resultados do Sistema vs IA."""

    def __init__(self, resultado_sistema: dict, resultado_ia: dict, contexto: dict):
        self.resultado_sistema = resultado_sistema
        self.resultado_ia = resultado_ia
        self.contexto = contexto

    def comparar(self) -> dict[str, Any]:
        """
        Compara resultados dos dois métodos.

        Returns:
            Análise comparativa com métricas
        """
        print("\n📊 SUBAGENTE COMPARADOR: Analisando resultados...")

        comparacao = {
            "timestamp": datetime.now().isoformat(),
            "contrato_id": self.contexto["contrato"]["id"],
            "metodo_a": {
                "nome": "Sistema Estruturado",
                "total_modificacoes": self.resultado_sistema.get(
                    "total_modificacoes", 0
                ),
                "tempo_segundos": self.resultado_sistema.get("tempo_segundos", 0),
                "sucesso": self.resultado_sistema.get("sucesso", False),
            },
            "metodo_b": {
                "nome": "IA Pura",
                "total_modificacoes": self.resultado_ia.get("total_modificacoes", 0),
                "tempo_segundos": self.resultado_ia.get("tempo_segundos", 0),
                "sucesso": self.resultado_ia.get("sucesso", False),
            },
            "metricas": {},
            "analise_qualitativa": [],
        }

        # Comparar totais
        total_sistema = comparacao["metodo_a"]["total_modificacoes"]
        total_ia = comparacao["metodo_b"]["total_modificacoes"]

        if total_sistema > 0 or total_ia > 0:
            diferenca = abs(total_sistema - total_ia)
            diferenca_percentual = (
                (diferenca / max(total_sistema, total_ia) * 100)
                if max(total_sistema, total_ia) > 0
                else 0
            )

            comparacao["metricas"] = {
                "diferenca_absoluta": diferenca,
                "diferenca_percentual": round(diferenca_percentual, 2),
                "concordancia": round(100 - diferenca_percentual, 2),
            }

            print("   📈 Métricas:")
            print(f"      Sistema: {total_sistema} modificações")
            print(f"      IA: {total_ia} modificações")
            print(f"      Diferença: {diferenca} ({diferenca_percentual:.1f}%)")
            print(f"      Concordância: {comparacao['metricas']['concordancia']:.1f}%")

        # Análise qualitativa
        if self.resultado_ia.get("observacao"):
            comparacao["analise_qualitativa"].append(
                {
                    "aspecto": "Limitação IA",
                    "observacao": self.resultado_ia["observacao"],
                }
            )

        # Análise de tempo
        tempo_sistema = comparacao["metodo_a"]["tempo_segundos"]
        tempo_ia = comparacao["metodo_b"]["tempo_segundos"]
        if tempo_sistema > 0 and tempo_ia > 0:
            comparacao["analise_qualitativa"].append(
                {
                    "aspecto": "Performance",
                    "observacao": f"Sistema: {tempo_sistema:.2f}s vs IA: {tempo_ia:.2f}s",
                }
            )

        print("   ✅ Comparação concluída")
        return comparacao


def comparar_resultados(output_dir: Path, contrato_id: str = None):
    """Compara resultados após usuário processar com IA."""
    print("=" * 80)
    print("🔄 COMPARANDO RESULTADOS SISTEMA vs IA")
    print("=" * 80)
    print()

    # Encontrar estado intermediário
    if contrato_id:
        # Buscar por contrato_id específico
        estados = []
        for estado_file in output_dir.glob("estado_intermediario_*.json"):
            with open(estado_file, encoding="utf-8") as f:
                estado_data = json.load(f)
                if estado_data.get("contrato_id") == contrato_id:
                    estados.append(estado_file)

        if not estados:
            print(f"❌ Nenhum estado encontrado para contrato {contrato_id}")
            sys.exit(1)

        # Usar o mais recente deste contrato
        estado_path = sorted(estados, reverse=True)[0]
        print(
            f"📂 Carregando estado: {estado_path.name} (contrato: {contrato_id[:8]}...)"
        )
    else:
        # Buscar o mais recente de qualquer contrato
        estados = sorted(output_dir.glob("estado_intermediario_*.json"), reverse=True)
        if not estados:
            print(
                "❌ Nenhum estado intermediário encontrado. Execute o script primeiro."
            )
            sys.exit(1)

        estado_path = estados[0]
        print(f"📂 Carregando estado: {estado_path.name}")

    with open(estado_path, encoding="utf-8") as f:
        estado = json.load(f)

    resultado_sistema = estado["resultado_sistema"]
    prompts_info = estado["resultado_ia"]["prompts_gerados"]

    # Carregar resultados da IA
    print("\n📥 Carregando resultados da IA...")
    versoes_ia = []
    total_modificacoes_ia = 0

    for prompt_info in prompts_info:
        resultado_path = output_dir / prompt_info["resultado_esperado"]

        if not resultado_path.exists():
            print(f"   ⚠️  Não encontrado: {resultado_path.name}")
            print("      Por favor, complete a análise manual primeiro.")
            continue

        print(f"   ✓ Carregando: {resultado_path.name}")
        with open(resultado_path, encoding="utf-8") as f:
            resultado_versao = json.load(f)
            versoes_ia.append(resultado_versao)
            total_modificacoes_ia += resultado_versao.get("resumo", {}).get(
                "total_modificacoes", 0
            )

    if not versoes_ia:
        print("\n❌ Nenhum resultado da IA encontrado. Complete a análise primeiro.")
        sys.exit(1)

    resultado_ia = {
        "metodo": "ia_pura",
        "versoes": versoes_ia,
        "total_modificacoes": total_modificacoes_ia,
        "sucesso": True,
    }

    # Comparar
    contexto = {"contrato": {"id": estado["contrato_id"]}, **estado.get("contexto", {})}

    comparador = SubagenteComparador(resultado_sistema, resultado_ia, contexto)
    comparacao = comparador.comparar()

    # Salvar resultado final
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    resultado_final = {
        "teste_ab": {
            "contrato_id": estado["contrato_id"],
            "timestamp": timestamp,
            "contexto": estado.get("contexto", {}),
            "resultado_sistema": resultado_sistema,
            "resultado_ia": resultado_ia,
            "comparacao": comparacao,
        }
    }

    resultado_path = output_dir / f"teste_ab_completo_{timestamp}.json"
    resultado_path.write_text(
        json.dumps(resultado_final, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\n" + "=" * 80)
    print("✅ COMPARAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print(f"\n📄 Resultado salvo em: {resultado_path}")
    print("\n📊 Resumo Final:")
    print(
        f"   • Sistema: {resultado_sistema.get('total_modificacoes', 0)} modificações"
    )
    print(f"   • IA: {resultado_ia.get('total_modificacoes', 0)} modificações")
    if comparacao.get("metricas"):
        print(
            f"   • Diferença: {comparacao['metricas']['diferenca_absoluta']} modificações"
        )
        print(f"   • Concordância: {comparacao['metricas']['concordancia']:.1f}%")
    print()


def main():
    """Função principal do orquestrador."""
    if not DIRECTUS_TOKEN:
        print("❌ DIRECTUS_TOKEN não configurado no .env")
        sys.exit(1)

    # Verificar modo de operação
    if len(sys.argv) > 1 and sys.argv[1] == "--comparar":
        # Modo comparação: usuário já processou com IA
        output_dir = Path(__file__).parent / "teste_ab_output"

        # Verificar se foi passado contrato_id como segundo argumento
        contrato_id = sys.argv[2] if len(sys.argv) > 2 else None
        comparar_resultados(output_dir, contrato_id)
        return

    # Contrato para teste A/B (pode ser passado como argumento)
    if len(sys.argv) > 1 and sys.argv[1] != "--comparar":
        contrato_id = sys.argv[1]
    else:
        contrato_id = "77b8555b-e40d-4ece-8c8a-88367b36a625"  # default

    # Diretório de saída
    output_dir = Path(__file__).parent / "teste_ab_output"
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("🧪 TESTE A/B: SISTEMA ESTRUTURADO vs IA PURA")
    print("=" * 80)
    print()

    try:
        # 1. Setup: Preparar contexto
        setup = SubagenteSetup(contrato_id)
        contexto = setup.preparar_contexto()

        # 2. Subagente Sistema: Processar via Docker
        subagente_sistema = SubagenteSistema(contexto)
        resultado_sistema = subagente_sistema.processar()

        # 3. Subagente IA: Gerar prompts para análise manual
        subagente_ia = SubagenteIA(contexto, output_dir)
        resultado_ia = subagente_ia.processar()

        # Salvar estado intermediário (sem comparação ainda)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        estado_path = output_dir / f"estado_intermediario_{timestamp}.json"
        estado = {
            "contrato_id": contrato_id,
            "timestamp": timestamp,
            "contexto": {
                "contrato_titulo": contexto["contrato"].get("titulo"),
                "modelo_nome": contexto["modelo"].get("nome"),
                "total_versoes": len(contexto["versoes"]),
                "total_tags_modelo": len(contexto["modelo"].get("tags", [])),
            },
            "resultado_sistema": resultado_sistema,
            "resultado_ia": resultado_ia,
        }

        estado_path.write_text(
            json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print("\n" + "=" * 80)
        print("✅ PREPARAÇÃO CONCLUÍDA - AGUARDANDO ANÁLISE MANUAL")
        print("=" * 80)
        print(f"\n📄 Estado salvo em: {estado_path}")
        print("\n📊 Resumo:")
        print(
            f"   • Sistema: {resultado_sistema.get('total_modificacoes', 0)} modificações"
        )
        print("   • IA: Aguardando análise manual")
        print("\n📝 Siga as instruções acima para completar o teste A/B")
        print()

    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
