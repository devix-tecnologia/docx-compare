
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
  
  return textoComDestaque.replace(/\n/g, '<br>')
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
