#!/usr/bin/env python3
"""
Exemplo de integração do sistema de comparação com visualizador web
Gera dados estruturados que podem ser consumidos por um frontend Vue 3
"""

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from docx_compare.core.implementacoes_mock import FactoryImplementacoesMock
from docx_compare.core.pipeline_funcional import (
    ContextoProcessamento,
    PrioridadeProcessamento,
    executar_pipeline_completo,
)
from docx_compare.core.teste_implementacoes_mock import criar_modelo_teste


def converter_para_diff_web(resultados_pipeline: list[Any]) -> dict[str, Any]:
    """
    Converte resultados do pipeline para formato consumível pelo frontend Vue 3.

    Args:
        resultados_pipeline: Resultados do executar_pipeline_completo

    Returns:
        Dicionário estruturado para visualização web
    """
    dados_diff = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_documentos": len(resultados_pipeline),
            "versao_sistema": "1.0.0",
        },
        "documentos": [],
    }

    for i, resultado in enumerate(resultados_pipeline):
        documento_diff = {
            "id": f"doc_{i + 1}",
            "estatisticas": {
                "total_modificacoes": len(resultado.modificacoes),
                "total_blocos": len(resultado.blocos_agrupados),
                "tempo_processamento": resultado.tempo_processamento,
            },
            "modificacoes": [],
            "blocos": [],
            "conteudo_comparacao": {
                "original": "",  # Será preenchido com o texto original
                "modificado": "",  # Será preenchido com o texto modificado
                "diff_highlights": [],  # Posições para destacar no frontend
            },
        }

        # Processar modificações individuais
        for mod in resultado.modificacoes:
            modificacao_data = {
                "id": mod.id,
                "tipo": mod.tipo.value,
                "posicao": {
                    "linha": mod.posicao_original.linha,
                    "coluna": mod.posicao_original.coluna,
                    "offset": mod.posicao_original.offset,
                },
                "conteudo": {
                    "original": mod.conteudo_original,
                    "novo": mod.conteudo_novo,
                },
                "confianca": mod.confianca,
                "tags_relacionadas": list(mod.tags_relacionadas),
                "css_class": f"diff-{mod.tipo.value}",  # Para estilização CSS
                "destaque_cor": determinar_cor_modificacao(
                    mod.tipo.value, mod.confianca
                ),
            }
            documento_diff["modificacoes"].append(modificacao_data)

            # Adicionar highlight para o frontend
            highlight = {
                "inicio": mod.posicao_original.offset,
                "fim": mod.posicao_original.offset + len(mod.conteudo_original),
                "tipo": mod.tipo.value,
                "confianca": mod.confianca,
                "texto_original": mod.conteudo_original,
                "texto_novo": mod.conteudo_novo,
            }
            documento_diff["conteudo_comparacao"]["diff_highlights"].append(highlight)

        # Processar blocos agrupados
        for j, bloco in enumerate(resultado.blocos_agrupados):
            bloco_data = {
                "id": f"bloco_{j + 1}",
                "tipo_predominante": bloco.tipo_predominante.value,
                "relevancia": bloco.relevancia,
                "modificacoes_ids": [mod.id for mod in bloco.modificacoes],
                "resumo": f"{len(bloco.modificacoes)} modificações do tipo {bloco.tipo_predominante.value}",
                "css_class": f"bloco-{bloco.tipo_predominante.value}",
            }
            documento_diff["blocos"].append(bloco_data)

        dados_diff["documentos"].append(documento_diff)

    return dados_diff


def determinar_cor_modificacao(tipo: str, confianca: float) -> str:
    """
    Determina a cor de destaque baseada no tipo e confiança da modificação.

    Args:
        tipo: Tipo da modificação (alteracao, insercao, remocao)
        confianca: Nível de confiança (0.0 a 1.0)

    Returns:
        Código de cor CSS
    """
    if confianca >= 0.9:
        intensidade = "strong"
    elif confianca >= 0.7:
        intensidade = "medium"
    else:
        intensidade = "weak"

    cores = {
        "alteracao": {
            "strong": "#ff6b6b",  # Vermelho forte
            "medium": "#ff8e8e",  # Vermelho médio
            "weak": "#ffb3b3",  # Vermelho fraco
        },
        "insercao": {
            "strong": "#51cf66",  # Verde forte
            "medium": "#8ce99a",  # Verde médio
            "weak": "#b2f2bb",  # Verde fraco
        },
        "remocao": {
            "strong": "#ff8787",  # Laranja forte
            "medium": "#ffa8a8",  # Laranja médio
            "weak": "#ffc9c9",  # Laranja fraco
        },
    }

    return cores.get(tipo, {}).get(intensidade, "#e9ecef")


def gerar_exemplo_diff_web():
    """
    Gera um exemplo completo de dados para visualização web.
    """
    print("🌐 Gerando dados para visualizador diff web...")

    # Configurar factory mock
    factory = FactoryImplementacoesMock()
    processador, analisador, comparador, agrupador = factory.criar_todos()

    # Criar arquivos temporários com conteúdo exemplo
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_original.txt", delete=False
    ) as f1:
        conteudo_original = """
        CONTRATO DE PRESTAÇÃO DE SERVIÇOS

        Entre {{contratante}} e {{contratada}}, fica estabelecido:

        1. OBJETO: Prestação de serviços de {{tipo_servico}}
        2. VALOR: R$ {{valor}} reais
        3. PRAZO: {{prazo}} dias úteis
        4. PAGAMENTO: Em {{forma_pagamento}}

        Documento original gerado em {{data_geracao}}.
        """
        f1.write(conteudo_original)
        caminho_original = Path(f1.name)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_modificado.txt", delete=False
    ) as f2:
        conteudo_modificado = """
        CONTRATO DE PRESTAÇÃO DE SERVIÇOS ALTERADO

        Entre {{contratante}} e {{contratada}}, fica estabelecido:

        1. OBJETO: Prestação de serviços de {{tipo_servico}}
        2. VALOR: R$ {{preco}} reais
        3. PRAZO: {{prazo}} dias corridos
        4. PAGAMENTO: Em {{forma_pagamento}}
        5. REAJUSTE: Aplicável conforme índice {{indice_reajuste}}

        Documento modificado gerado em {{data_geracao}}.
        """
        f2.write(conteudo_modificado)
        caminho_modificado = Path(f2.name)

    try:
        modelos = [criar_modelo_teste()]
        contexto = ContextoProcessamento(
            prioridade=PrioridadeProcessamento.NORMAL,
            timeout_segundos=30,
            modo_paralelo=False,
            filtros_ativos=set(),
            configuracoes={},
        )

        # Executar pipeline
        resultados = executar_pipeline_completo(
            documentos_originais=[caminho_original],
            documentos_modificados=[caminho_modificado],
            _modelos=modelos,
            _contexto=contexto,
            processador=processador,
            analisador=analisador,
            comparador=comparador,
            agrupador=agrupador,
        )

        # Converter para formato web
        dados_diff = converter_para_diff_web(resultados)

        # Adicionar conteúdo completo dos documentos
        dados_diff["documentos"][0]["conteudo_comparacao"]["original"] = (
            conteudo_original.strip()
        )
        dados_diff["documentos"][0]["conteudo_comparacao"]["modificado"] = (
            conteudo_modificado.strip()
        )

        # Salvar JSON para o frontend
        output_path = Path(__file__).parent / "diff_data_exemplo.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dados_diff, f, indent=2, ensure_ascii=False)

        print(f"✅ Dados salvos em: {output_path}")
        print(
            f"📊 {dados_diff['metadata']['total_documentos']} documento(s) processado(s)"
        )
        print(
            f"🔍 {len(dados_diff['documentos'][0]['modificacoes'])} modificação(ões) encontrada(s)"
        )

        # Mostrar exemplo da estrutura
        print("\n📋 Exemplo da estrutura JSON gerada:")
        exemplo = {
            "metadata": dados_diff["metadata"],
            "documentos[0]": {
                "estatisticas": dados_diff["documentos"][0]["estatisticas"],
                "modificacoes[0]": dados_diff["documentos"][0]["modificacoes"][0]
                if dados_diff["documentos"][0]["modificacoes"]
                else None,
            },
        }
        print(json.dumps(exemplo, indent=2, ensure_ascii=False))

        return dados_diff

    finally:
        # Limpar arquivos temporários
        caminho_original.unlink()
        caminho_modificado.unlink()


def gerar_componente_vue_exemplo():
    """
    Gera um exemplo de componente Vue 3 para visualizar os diffs.
    """
    componente_vue = """
<template>
  <div class="diff-visualizer">
    <div class="diff-header">
      <h2>Comparação de Documentos</h2>
      <div class="diff-stats">
        <span class="stat">{{ dados.metadata.total_documentos }} documentos</span>
        <span class="stat">{{ totalModificacoes }} modificações</span>
        <span class="stat">{{ tempoProcessamento }}s processamento</span>
      </div>
    </div>

    <div class="diff-content">
      <div class="diff-side original">
        <h3>Original</h3>
        <div
          class="content-viewer"
          v-html="conteudoOriginalComDestaque"
        ></div>
      </div>

      <div class="diff-side modified">
        <h3>Modificado</h3>
        <div
          class="content-viewer"
          v-html="conteudoModificadoComDestaque"
        ></div>
      </div>
    </div>

    <div class="diff-modifications">
      <h3>Modificações Detalhadas</h3>
      <div
        v-for="mod in modificacoes"
        :key="mod.id"
        class="modification-item"
        :class="mod.css_class"
      >
        <div class="mod-header">
          <span class="mod-type">{{ mod.tipo }}</span>
          <span class="mod-confidence">{{ Math.round(mod.confianca * 100) }}%</span>
        </div>
        <div class="mod-content">
          <span class="mod-original">"{{ mod.conteudo.original }}"</span>
          <span class="mod-arrow">→</span>
          <span class="mod-new">"{{ mod.conteudo.novo }}"</span>
        </div>
        <div class="mod-position">
          Linha {{ mod.posicao.linha }}, Coluna {{ mod.posicao.coluna }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

// Props
const props = defineProps({
  dados: {
    type: Object,
    required: true
  }
})

// Computed
const documento = computed(() => props.dados.documentos[0])
const modificacoes = computed(() => documento.value.modificacoes)
const totalModificacoes = computed(() => modificacoes.value.length)
const tempoProcessamento = computed(() =>
  documento.value.estatisticas.tempo_processamento.toFixed(3)
)

const conteudoOriginalComDestaque = computed(() => {
  return aplicarDestaques(
    documento.value.conteudo_comparacao.original,
    documento.value.conteudo_comparacao.diff_highlights,
    'original'
  )
})

const conteudoModificadoComDestaque = computed(() => {
  return aplicarDestaques(
    documento.value.conteudo_comparacao.modificado,
    documento.value.conteudo_comparacao.diff_highlights,
    'modificado'
  )
})

// Methods
function aplicarDestaques(texto, highlights, tipo) {
  let textoComDestaque = texto

  // Ordenar highlights por posição (do final para o início)
  const highlightsSorted = [...highlights].sort((a, b) => b.inicio - a.inicio)

  highlightsSorted.forEach(highlight => {
    const textoDestaque = tipo === 'original'
      ? highlight.texto_original
      : highlight.texto_novo

    const classe = `highlight-${highlight.tipo} confidence-${getConfidenceClass(highlight.confianca)}`
    const elemento = `<span class="${classe}" title="Confiança: ${Math.round(highlight.confianca * 100)}%">${textoDestaque}</span>`

    textoComDestaque = textoComDestaque.substring(0, highlight.inicio) +
                      elemento +
                      textoComDestaque.substring(highlight.fim)
  })

  return textoComDestaque.replace(/\\n/g, '<br>')
}

function getConfidenceClass(confianca) {
  if (confianca >= 0.9) return 'high'
  if (confianca >= 0.7) return 'medium'
  return 'low'
}
</script>

<style scoped>
.diff-visualizer {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.diff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e9ecef;
}

.diff-stats .stat {
  margin-left: 15px;
  padding: 5px 10px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
}

.diff-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.diff-side {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.diff-side h3 {
  margin: 0;
  padding: 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.content-viewer {
  padding: 20px;
  font-family: monospace;
  white-space: pre-wrap;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.highlight-alteracao { background-color: #ffe6e6; }
.highlight-insercao { background-color: #e6ffe6; }
.highlight-remocao { background-color: #fff4e6; }

.confidence-high { border-left: 3px solid #28a745; }
.confidence-medium { border-left: 3px solid #ffc107; }
.confidence-low { border-left: 3px solid #dc3545; }

.modification-item {
  border: 1px solid #dee2e6;
  border-radius: 6px;
  margin-bottom: 10px;
  padding: 15px;
}

.mod-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.mod-type {
  font-weight: bold;
  text-transform: capitalize;
}

.mod-confidence {
  color: #6c757d;
  font-size: 14px;
}

.mod-content {
  margin-bottom: 8px;
  font-family: monospace;
}

.mod-arrow {
  margin: 0 10px;
  color: #6c757d;
}

.mod-original {
  background: #ffe6e6;
  padding: 2px 6px;
  border-radius: 3px;
}

.mod-new {
  background: #e6ffe6;
  padding: 2px 6px;
  border-radius: 3px;
}

.mod-position {
  font-size: 12px;
  color: #6c757d;
}
</style>
"""

    # Salvar componente Vue
    output_path = Path(__file__).parent / "DiffVisualizer.vue"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(componente_vue)

    print(f"✅ Componente Vue 3 salvo em: {output_path}")


if __name__ == "__main__":
    print("🌐 Gerador de Visualizador Diff para Vue 3")
    print("=" * 50)

    # Gerar dados de exemplo
    dados = gerar_exemplo_diff_web()

    print("\n" + "=" * 50)

    # Gerar componente Vue
    gerar_componente_vue_exemplo()

    print("\n🎯 **PRÓXIMOS PASSOS:**")
    print("1. Instalar dependências Vue 3: npm install vue@next")
    print("2. Importar o componente DiffVisualizer.vue")
    print("3. Carregar dados de diff_data_exemplo.json")
    print("4. Personalizar estilos conforme necessário")
    print("\n✨ Visualizador pronto para uso!")
