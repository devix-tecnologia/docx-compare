<template>
  <div class="app-container">
    <header class="app-header">
      <h1>🚀 Versiona AI</h1>
      <p>Visualizador de Diferenças em Documentos</p>
    </header>

    <main class="app-main">
      <div class="diff-visualizer">
        <div class="diff-header">
          <h2>{{ titulo }}</h2>
          <div class="stats">
            <span class="stat">📊 {{ stats.total_modificacoes }} modificações</span>
            <span class="stat">⏱️ {{ stats.tempo_processamento.toFixed(3) }}s</span>
            <span class="stat">🎯 {{ stats.total_blocos }} blocos</span>
          </div>
        </div>

        <div class="diff-content">
          <div class="modifications-list">
            <div
              v-for="modificacao in modificacoes"
              :key="modificacao.id"
              class="modification-item"
              :class="modificacao.css_class"
              @click="onModificacaoClick(modificacao)"
            >
              <div class="mod-header">
                <span class="mod-type">{{ modificacao.tipo.toUpperCase() }}</span>
                <span class="mod-confidence">{{ (modificacao.confianca * 100).toFixed(1) }}%</span>
              </div>

              <div class="mod-content">
                <div class="mod-original" v-if="modificacao.conteudo.original">
                  <strong>Original:</strong> "{{ modificacao.conteudo.original }}"
                </div>
                <div class="mod-new"><strong>Novo:</strong> "{{ modificacao.conteudo.novo }}"</div>
              </div>

              <div class="mod-position">
                📍 Linha {{ modificacao.posicao.linha }}, Coluna {{ modificacao.posicao.coluna }}
              </div>

              <div
                class="mod-tags"
                v-if="modificacao.tags_relacionadas && modificacao.tags_relacionadas.length > 0"
              >
                <span v-for="tag in modificacao.tags_relacionadas" :key="tag" class="tag">
                  🏷️ {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="diff-legend">
          <div class="legend-item alteracao">
            <span class="legend-color"></span>
            <span>Alteração</span>
          </div>
          <div class="legend-item insercao">
            <span class="legend-color"></span>
            <span>Inserção</span>
          </div>
          <div class="legend-item remocao">
            <span class="legend-color"></span>
            <span>Remoção</span>
          </div>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <p>Desenvolvido com ❤️ e Vue 3 • Versiona AI © 2025</p>
    </footer>
  </div>
</template>

<script>
  export default {
    name: 'App',
    data() {
      return {
        titulo: 'Demonstração - Contrato v1.0 vs v2.0',
        sampleData: {
          metadata: {
            timestamp: new Date().toISOString(),
            total_documentos: 1,
            versao_sistema: '1.0.0',
          },
          documentos: [
            {
              id: 'demo_doc',
              estatisticas: {
                total_modificacoes: 3,
                total_blocos: 1,
                tempo_processamento: 0.015,
              },
              modificacoes: [
                {
                  id: 'mod_1',
                  tipo: 'alteracao',
                  posicao: { linha: 1, coluna: 25, offset: 25 },
                  conteudo: { original: '{{valor}}', novo: '{{preco}}' },
                  confianca: 0.95,
                  tags_relacionadas: ['valor', 'preco'],
                  css_class: 'diff-alteracao',
                  destaque_cor: '#ff6b6b',
                },
                {
                  id: 'mod_2',
                  tipo: 'alteracao',
                  posicao: { linha: 3, coluna: 15, offset: 65 },
                  conteudo: { original: 'dias úteis', novo: 'dias corridos' },
                  confianca: 0.9,
                  tags_relacionadas: [],
                  css_class: 'diff-alteracao',
                  destaque_cor: '#ff6b6b',
                },
                {
                  id: 'mod_3',
                  tipo: 'insercao',
                  posicao: { linha: 2, coluna: 50, offset: 75 },
                  conteudo: { original: '', novo: ' alterado' },
                  confianca: 0.85,
                  tags_relacionadas: [],
                  css_class: 'diff-insercao',
                  destaque_cor: '#51cf66',
                },
              ],
            },
          ],
        },
      }
    },
    computed: {
      stats() {
        const doc = this.sampleData.documentos?.[0] || {}
        return (
          doc.estatisticas || {
            total_modificacoes: 0,
            tempo_processamento: 0,
            total_blocos: 0,
          }
        )
      },
      modificacoes() {
        const doc = this.sampleData.documentos?.[0] || {}
        return doc.modificacoes || []
      },
    },
    methods: {
      onModificacaoClick(modificacao) {
        console.log('🔍 Modificação clicada:', modificacao)
        alert(
          `Modificação: ${modificacao.tipo}\nConfiança: ${(modificacao.confianca * 100).toFixed(1)}%\nDetalhes: ${modificacao.conteudo.original} → ${modificacao.conteudo.novo}`
        )
      },
    },
  }
</script>

<style scoped>
  .app-container {
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    min-height: 90vh;
    display: flex;
    flex-direction: column;
  }

  .app-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    padding: 2rem;
  }

  .app-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
  }

  .app-header p {
    margin: 0.5rem 0 0 0;
    font-size: 1.2rem;
    opacity: 0.9;
  }

  .app-main {
    flex: 1;
    padding: 0;
  }

  .app-footer {
    background: #f8f9fa;
    text-align: center;
    padding: 1rem;
    color: #6c757d;
    font-size: 0.9rem;
  }

  /* Estilos do DiffVisualizer integrado */
  .diff-visualizer {
    background: white;
    width: 100%;
  }

  .diff-header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 1.5rem;
    text-align: center;
  }

  .diff-header h2 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
    font-weight: 600;
  }

  .stats {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
  }

  .stat {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    backdrop-filter: blur(10px);
  }

  .diff-content {
    padding: 1.5rem;
  }

  .modifications-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .modification-item {
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .modification-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .modification-item.diff-alteracao {
    border-left: 4px solid #ff6b6b;
    background: linear-gradient(90deg, #fff5f5 0%, white 100%);
  }

  .modification-item.diff-insercao {
    border-left: 4px solid #51cf66;
    background: linear-gradient(90deg, #f0fff4 0%, white 100%);
  }

  .modification-item.diff-remocao {
    border-left: 4px solid #ffd43b;
    background: linear-gradient(90deg, #fffbf0 0%, white 100%);
  }

  .mod-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .mod-type {
    background: #4f46e5;
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .mod-confidence {
    background: #10b981;
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .mod-content {
    margin: 0.5rem 0;
  }

  .mod-original,
  .mod-new {
    margin: 0.3rem 0;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9rem;
  }

  .mod-original {
    color: #dc3545;
  }

  .mod-new {
    color: #198754;
  }

  .mod-position {
    font-size: 0.8rem;
    color: #6b7280;
    margin: 0.5rem 0;
  }

  .mod-tags {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .tag {
    background: #f3f4f6;
    color: #374151;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    border: 1px solid #d1d5db;
  }

  .diff-legend {
    background: #f8f9fa;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: center;
    gap: 2rem;
    border-top: 1px solid #e5e7eb;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
  }

  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 3px;
  }

  .legend-item.alteracao .legend-color {
    background: #ff6b6b;
  }

  .legend-item.insercao .legend-color {
    background: #51cf66;
  }

  .legend-item.remocao .legend-color {
    background: #ffd43b;
  }

  @media (max-width: 768px) {
    .stats {
      flex-direction: column;
      gap: 0.5rem;
    }

    .diff-legend {
      flex-direction: column;
      gap: 0.5rem;
    }

    .modification-item {
      padding: 0.8rem;
    }

    .app-header h1 {
      font-size: 2rem;
    }
  }
</style>
