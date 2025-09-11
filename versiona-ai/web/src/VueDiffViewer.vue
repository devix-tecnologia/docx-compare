<template>
  <div class="vue-diff-viewer">
    <div class="diff-header">
      <h2>Comparação com Vue-Diff</h2>
      <div class="diff-stats">
        <span class="stat">📄 Diff Avançado</span>
        <span class="stat">🔍 Detecção Automática</span>
        <span class="stat">⚡ Vue-powered</span>
      </div>
    </div>

    <div class="diff-container">
      <div v-html="diffHtml" class="diff-content"></div>
    </div>

    <div class="diff-info">
      <h3>Informações do Diff</h3>
      <div class="info-grid">
        <div class="info-item">
          <strong>Linhas Originais:</strong> {{ linhasOriginais }}
        </div>
        <div class="info-item">
          <strong>Linhas Modificadas:</strong> {{ linhasModificadas }}
        </div>
        <div class="info-item">
          <strong>Diferenças:</strong> {{ totalDiferencas }}
        </div>
        <div class="info-item">
          <strong>Similaridade:</strong> {{ porcentagemSimilaridade }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'

  // Props
  const props = defineProps({
    dados: {
      type: Object,
      required: true,
    },
  })

  // Computed
  const documento = computed(() => props.dados.documentos[0])
  
  const conteudoOriginal = computed(() => {
    return documento.value.conteudo_comparacao?.original || `Contrato de Prestação de Serviços

O presente contrato estabelece que o prazo para entrega será de 30 dias úteis a partir da assinatura, com {{valor}} especificado no anexo I.

As condições de pagamento seguem o cronograma estabelecido no documento principal.

Cláusula 1: Objeto do contrato
Cláusula 2: Prazo de execução  
Cláusula 3: Valor e forma de pagamento`
  })

  const conteudoModificado = computed(() => {
    return documento.value.conteudo_comparacao?.modificado || `Contrato de Prestação de Serviços

O presente contrato estabelece que o prazo para entrega alterado será de 30 dias corridos a partir da assinatura, com {{preco}} especificado no anexo I.

As condições de pagamento seguem o cronograma estabelecido no documento principal.

Cláusula 1: Objeto do contrato revisado
Cláusula 2: Prazo de execução estendido
Cláusula 3: Valor e forma de pagamento atualizada
Cláusula 4: Nova cláusula de garantias`
  })

  const diffHtml = computed(() => {
    try {
      // Simular um diff básico sem dependências externas
      const original = conteudoOriginal.value.split('\n')
      const modified = conteudoModificado.value.split('\n')
      
      let diffOutput = '<div class="simple-diff">'
      
      const maxLines = Math.max(original.length, modified.length)
      
      for (let i = 0; i < maxLines; i++) {
        const origLine = original[i] || ''
        const modLine = modified[i] || ''
        
        if (origLine === modLine) {
          diffOutput += `<div class="diff-line unchanged">
            <span class="line-number">${i + 1}</span>
            <span class="line-content">${origLine}</span>
          </div>`
        } else {
          if (origLine) {
            diffOutput += `<div class="diff-line removed">
              <span class="line-number">-</span>
              <span class="line-content">${origLine}</span>
            </div>`
          }
          if (modLine) {
            diffOutput += `<div class="diff-line added">
              <span class="line-number">+</span>
              <span class="line-content">${modLine}</span>
            </div>`
          }
        }
      }
      
      diffOutput += '</div>'
      return diffOutput
    } catch (error) {
      console.error('Erro ao gerar diff:', error)
      return '<div class="error">Erro ao gerar diff</div>'
    }
  })

  const linhasOriginais = computed(() => conteudoOriginal.value.split('\n').length)
  const linhasModificadas = computed(() => conteudoModificado.value.split('\n').length)
  
  const totalDiferencas = computed(() => {
    return documento.value.modificacoes?.length || 3
  })

  const porcentagemSimilaridade = computed(() => {
    const original = conteudoOriginal.value
    const modificado = conteudoModificado.value
    const maxLength = Math.max(original.length, modificado.length)
    const similarity = 1 - (Math.abs(original.length - modificado.length) / maxLength)
    return Math.round(similarity * 100)
  })
</script>

<style scoped>
  .vue-diff-viewer {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .diff-header {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    padding: 1.5rem;
    text-align: center;
  }

  .diff-header h2 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
    font-weight: 600;
  }

  .diff-stats {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
  }

  .stat {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    backdrop-filter: blur(10px);
  }

  .diff-container {
    padding: 1.5rem;
    background: #f8fafc;
  }

  .diff-content {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    background: white;
  }

  /* Estilos para diff simples */
  :deep(.simple-diff) {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.5;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
  }

  :deep(.diff-line) {
    display: flex;
    align-items: flex-start;
    padding: 0;
    margin: 0;
    border-bottom: 1px solid #f1f5f9;
  }

  :deep(.diff-line:last-child) {
    border-bottom: none;
  }

  :deep(.line-number) {
    background: #f8fafc;
    color: #64748b;
    padding: 0.5rem 0.75rem;
    border-right: 1px solid #e2e8f0;
    font-size: 0.75rem;
    text-align: right;
    min-width: 50px;
    user-select: none;
    font-weight: 500;
  }

  :deep(.line-content) {
    padding: 0.5rem 0.75rem;
    flex: 1;
    white-space: pre-wrap;
    word-break: break-word;
  }

  :deep(.diff-line.unchanged) {
    background: white;
  }

  :deep(.diff-line.removed) {
    background: #fef2f2;
    color: #dc2626;
  }

  :deep(.diff-line.removed .line-number) {
    background: #fecaca;
    color: #dc2626;
    font-weight: 600;
  }

  :deep(.diff-line.added) {
    background: #f0fdf4;
    color: #166534;
  }

  :deep(.diff-line.added .line-number) {
    background: #bbf7d0;
    color: #166534;
    font-weight: 600;
  }

  :deep(.error) {
    background: #fef2f2;
    color: #dc2626;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    font-weight: 500;
  }

  .diff-info {
    padding: 1.5rem;
    background: #f1f5f9;
    border-top: 1px solid #e2e8f0;
  }

  .diff-info h3 {
    margin: 0 0 1rem 0;
    color: #1e293b;
    font-size: 1.2rem;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .info-item {
    background: white;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    font-size: 0.9rem;
  }

  .info-item strong {
    color: #374151;
  }

  /* Estilos para o vue-diff */
  :deep(.d2h-wrapper) {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  :deep(.d2h-file-header) {
    background: #374151 !important;
    color: white !important;
    padding: 0.75rem 1rem;
    font-weight: 600;
  }

  :deep(.d2h-code-side-line) {
    padding: 0.5rem 0.75rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.4;
  }

  :deep(.d2h-ins) {
    background: #dcfce7 !important;
    border-color: #16a34a !important;
  }

  :deep(.d2h-del) {
    background: #fef2f2 !important;
    border-color: #dc2626 !important;
  }

  :deep(.d2h-code-line-ctn) {
    border: none !important;
  }

  :deep(.d2h-code-side-linenumber) {
    background: #f8fafc !important;
    color: #64748b !important;
    padding: 0.5rem 0.75rem;
    border-right: 1px solid #e2e8f0 !important;
    font-size: 0.8rem;
  }
</style>
