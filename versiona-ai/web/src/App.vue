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

          <!-- Status da Conexão -->
          <div class="connection-status">
            <span v-if="isConnectedToAPI" class="status connected"> 🟢 API Conectada </span>
            <span v-else class="status offline"> 🔴 Modo Offline </span>

            <!-- Controle de Modo (Mock vs Real) -->
            <div v-if="isConnectedToAPI" class="mode-control">
              <label class="mode-toggle">
                <input type="checkbox" v-model="useMockData" />
                <span class="toggle-slider"></span>
                <span class="toggle-label">{{ useMockData ? '🔧 Dados Mock' : '📊 Dados Reais' }}</span>
              </label>
            </div>

            <button
              v-if="isConnectedToAPI && !loading"
              @click="processarNovoDocumento"
              class="process-btn"
            >
              🔄 {{ useMockData ? 'Processar Mock' : 'Processar Real' }}
            </button>
            <span v-if="loading" class="loading-indicator"> ⏳ Carregando... </span>
          </div>

          <div class="stats">
            <span class="stat">📊 {{ stats.total_modificacoes }} modificações</span>
            <span class="stat">⏱️ {{ stats.tempo_processamento.toFixed(3) }}s</span>
            <span class="stat">🎯 {{ stats.total_blocos }} blocos</span>
          </div>

          <!-- Abas de Navegação -->
          <div class="tabs">
            <button
              class="tab"
              :class="{ active: activeTab === 'lista' }"
              @click="activeTab = 'lista'"
            >
              📋 Lista de Modificações
            </button>
            <button
              class="tab"
              :class="{ active: activeTab === 'lado-a-lado' }"
              @click="activeTab = 'lado-a-lado'"
            >
              🔍 Comparação Lado a Lado
            </button>
            <button
              class="tab"
              :class="{ active: activeTab === 'vue-diff' }"
              @click="activeTab = 'vue-diff'"
            >
              ⚡ Vue-Diff Avançado
            </button>
          </div>
        </div>

        <div class="diff-content">
          <!-- Vista Lista -->
          <div v-if="activeTab === 'lista'" class="modifications-list">
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

          <!-- Vista Lado a Lado -->
          <div v-else-if="activeTab === 'lado-a-lado'">
            <DiffVisualizerSideBySide :dados="sampleData" />
          </div>

          <!-- Vista Vue-Diff -->
          <div v-else-if="activeTab === 'vue-diff'">
            <VueDiffViewer :dados="sampleData" />
          </div>
        </div>

        <!-- Legenda apenas para a vista lista -->
        <div v-if="activeTab === 'lista'" class="diff-legend">
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
  import DiffVisualizerSideBySide from './DiffVisualizerSideBySide.vue'
import VueDiffViewer from './VueDiffViewer.vue'

  export default {
    name: 'App',
    components: {
      DiffVisualizerSideBySide,
      VueDiffViewer,
    },
    data() {
      return {
        titulo: 'Demonstração - Contrato v1.0 vs v2.0',
        activeTab: 'lista', // 'lista', 'lado-a-lado', ou 'vue-diff'
        loading: false,
        isConnectedToAPI: false,
        useMockData: false, // Controla se deve usar dados mock ou reais
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
              conteudo_comparacao: {
                original: `Contrato de Prestação de Serviços

O presente contrato estabelece que o prazo para entrega será de 30 dias úteis a partir da assinatura, com {{valor}} especificado no anexo I.

As condições de pagamento seguem o cronograma estabelecido no documento principal.`,
                modificado: `Contrato de Prestação de Serviços

O presente contrato estabelece que o prazo para entrega alterado será de 30 dias corridos a partir da assinatura, com {{preco}} especificado no anexo I.

As condições de pagamento seguem o cronograma estabelecido no documento principal.`,
                diff_highlights: [
                  {
                    tipo: 'alteracao',
                    inicio: 95,
                    fim: 103,
                    texto_original: '{{valor}}',
                    texto_novo: '{{preco}}',
                    confianca: 0.95,
                  },
                  {
                    tipo: 'alteracao',
                    inicio: 70,
                    fim: 80,
                    texto_original: 'dias úteis',
                    texto_novo: 'dias corridos',
                    confianca: 0.9,
                  },
                  {
                    tipo: 'insercao',
                    inicio: 65,
                    fim: 65,
                    texto_original: '',
                    texto_novo: ' alterado',
                    confianca: 0.85,
                  },
                ],
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
    watch: {
      // Observar mudanças no modo mock e atualizar URL
      useMockData(newValue) {
        const url = new URL(window.location)
        url.searchParams.set('mock', newValue.toString())
        window.history.pushState({}, '', url)
        console.log(`🔄 Modo alterado para: ${newValue ? 'Mock' : 'Real'}`)
      },
    },
    mounted() {
      // Verificar se há diff_id na URL
      const urlParams = new URLSearchParams(window.location.search)
      const diffId = urlParams.get('diff_id')
      const mockParam = urlParams.get('mock')

      // Definir modo mock baseado no parâmetro da URL
      if (mockParam !== null) {
        this.useMockData = mockParam === 'true'
      }

      if (diffId) {
        this.carregarDiffDoAPI(diffId)
      } else {
        this.verificarConexaoAPI()
        // Se mock=false, carregar dados reais automaticamente
        if (mockParam === 'false') {
          setTimeout(() => {
            this.processarVersoes()
          }, 1000) // Aguardar um segundo para conexão API
        }
      }
    },
    methods: {
      async verificarConexaoAPI() {
        console.log('🔍 Tentando conectar à API...')
        try {
          const response = await fetch('/health')
          console.log('📡 Resposta da API:', response.status, response.ok)
          if (response.ok) {
            const data = await response.json()
            console.log('📊 Dados da API:', data)
            this.isConnectedToAPI = true
            this.titulo = 'Versiona AI - Conectado ao API'
            console.log('✅ API conectada')
          } else {
            console.log('❌ API retornou erro:', response.status)
            this.isConnectedToAPI = false
          }
        } catch (error) {
          console.log('ℹ️ Modo offline - usando dados de demonstração', error)
          this.isConnectedToAPI = false
        }
      },

      async carregarDiffDoAPI(diffId) {
        this.loading = true
        try {
          const response = await fetch(`/api/data/${diffId}`)
          if (response.ok) {
            const data = await response.json()
            this.sampleData = data
            this.titulo = `Diff ${diffId} - Carregado do API`
            this.isConnectedToAPI = true
            console.log('✅ Diff carregado do API:', data)
          } else {
            throw new Error('Diff não encontrado')
          }
        } catch (error) {
          console.error('❌ Erro ao carregar diff:', error)
          console.info(
            `Erro ao carregar diff do API: ${error.message}. Usando dados de demonstração.`
          )
        } finally {
          this.loading = false
        }
      },

      async processarNovoDocumento() {
        if (!this.isConnectedToAPI) {
          alert('API não está conectada. Verifique se o servidor está rodando')
          return
        }

        this.loading = true
        try {
          // Primeiro, buscar versões disponíveis para processar
          const versoesUrl = this.useMockData ? '/api/versoes?mock=true' : '/api/versoes?mock=false'
          console.log(`🔍 Buscando versões: ${versoesUrl}`)

          const versoesResponse = await fetch(versoesUrl)
          if (!versoesResponse.ok) {
            throw new Error('Erro ao buscar versões disponíveis')
          }

          const versoesData = await versoesResponse.json()
          if (!versoesData.versoes || versoesData.versoes.length === 0) {
            const modoTexto = this.useMockData ? 'mock' : 'Directus'
            alert(`Nenhuma versão encontrada para processar no modo ${modoTexto}`)
            this.loading = false
            return
          }

          // Usar a primeira versão disponível
          const versaoId = versoesData.versoes[0].id
          console.log(`🔄 Processando versão ID: ${versaoId} (modo: ${this.useMockData ? 'mock' : 'real'})`)

          const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              versao_id: versaoId,
              mock: this.useMockData, // Enviar parâmetro mock baseado no controle
            }),
          })

          if (response.ok) {
            const resultado = await response.json()
            if (resultado.id) {
              // A API retorna dados completos, vamos converter para o formato esperado
              console.log('📋 Dados completos da API:', resultado)

              // Extrair modificações reais do diff HTML
              const modificacoesExtraidas = this.extrairModificacoesDoDiff(resultado.diff_html)

              const diffData = {
                documentos: [
                  {
                    nome: `Versão ${resultado.versao_id}`,
                    conteudo_comparacao: {
                      original: resultado.original,
                      modificado: resultado.modified,
                    },
                    estatisticas: {
                      total_modificacoes: modificacoesExtraidas.length,
                      tempo_processamento: 0.015,
                      total_blocos: 1,
                    },
                    modificacoes: modificacoesExtraidas,
                  },
                ],
              }

              this.sampleData = diffData
              const modoTexto = this.useMockData ? 'Mock' : 'Directus'
              this.titulo = `Versão ${resultado.versao_id} - Processado via ${modoTexto}`
              console.log('✅ Documento processado:', resultado)

              // Atualizar URL com diff_id
              const newUrl = new URL(window.location)
              newUrl.searchParams.set('diff_id', resultado.id)
              window.history.pushState({}, '', newUrl)
            } else {
              console.error('❌ Resposta da API sem ID:', resultado)
              alert('Erro: API não retornou ID válido')
            }
          } else {
            const errorData = await response.json()
            console.error('❌ Erro na API:', errorData)
            alert(`Erro na API: ${errorData.error || 'Erro desconhecido'}`)
          }
        } catch (error) {
          console.error('❌ Erro ao processar documento:', error)
          alert('Erro ao processar documento via API')
        } finally {
          this.loading = false
        }
      },

      extrairModificacoesDoDiff(diffHtml) {
        console.log('🔍 HTML recebido:', diffHtml)

        const modificacoes = []
        let modificacaoId = 1

        // Parse do HTML usando DOMParser
        const parser = new DOMParser()
        const doc = parser.parseFromString(`<div>${diffHtml}</div>`, 'text/html')

        // Buscar elementos de remoção e adição
        const removedElements = doc.querySelectorAll('.diff-removed')
        const addedElements = doc.querySelectorAll('.diff-added')

        console.log('📝 Elementos removidos:', removedElements.length)
        console.log('📝 Elementos adicionados:', addedElements.length)

        // Processar pares de remoção/adição
        const maxElements = Math.max(removedElements.length, addedElements.length)

        for (let i = 0; i < maxElements; i++) {
          const removedEl = removedElements[i]
          const addedEl = addedElements[i]

          const removedText = removedEl ? removedEl.textContent.replace(/^-\s*/, '').trim() : null
          const addedText = addedEl ? addedEl.textContent.replace(/^\+\s*/, '').trim() : null

          if (removedText && addedText) {
            // Alteração
            modificacoes.push({
              id: modificacaoId++,
              tipo: 'ALTERACAO',
              css_class: 'diff-alteracao',
              confianca: 0.95,
              posicao: { linha: i + 1, coluna: 1 },
              conteudo: {
                original: removedText,
                novo: addedText,
              },
              tags_relacionadas: this.extrairPalavrasChave(removedText + ' ' + addedText),
            })
          } else if (addedText) {
            // Inserção
            modificacoes.push({
              id: modificacaoId++,
              tipo: 'INSERCAO',
              css_class: 'diff-insercao',
              confianca: 0.9,
              posicao: { linha: i + 1, coluna: 1 },
              conteudo: {
                novo: addedText,
              },
              tags_relacionadas: this.extrairPalavrasChave(addedText),
            })
          } else if (removedText) {
            // Remoção
            modificacoes.push({
              id: modificacaoId++,
              tipo: 'REMOCAO',
              css_class: 'diff-remocao',
              confianca: 0.85,
              posicao: { linha: i + 1, coluna: 1 },
              conteudo: {
                original: removedText,
              },
              tags_relacionadas: this.extrairPalavrasChave(removedText),
            })
          }
        }

        console.log('✅ Modificações extraídas:', modificacoes)
        return modificacoes
      },

      extrairPalavrasChave(texto) {
        // Extrai palavras-chave relevantes
        const palavras = texto.match(/\w+/g) || []
        return palavras.filter(palavra => palavra.length > 3).slice(0, 2)
      },

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

  /* Status da Conexão */
  .connection-status {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }

  .status {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .status.connected {
    background: rgba(34, 197, 94, 0.2);
    color: #15803d;
  }

  .status.offline {
    background: rgba(239, 68, 68, 0.2);
    color: #dc2626;
  }

  .process-btn {
    background: rgba(255, 255, 255, 0.9);
    color: #4f46e5;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.3s ease;
  }

  .process-btn:hover {
    background: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .loading-indicator {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
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

  /* Controle de Modo (Mock vs Real) */
  .mode-control {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .mode-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    user-select: none;
  }

  .mode-toggle input[type="checkbox"] {
    display: none;
  }

  .toggle-slider {
    position: relative;
    width: 40px;
    height: 20px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 20px;
    transition: all 0.3s ease;
    border: 2px solid rgba(255, 255, 255, 0.4);
  }

  .toggle-slider::before {
    content: '';
    position: absolute;
    width: 14px;
    height: 14px;
    background: white;
    border-radius: 50%;
    top: 1px;
    left: 1px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .mode-toggle input[type="checkbox"]:checked + .toggle-slider {
    background: #fbbf24;
    border-color: #f59e0b;
  }

  .mode-toggle input[type="checkbox"]:checked + .toggle-slider::before {
    transform: translateX(20px);
  }

  .toggle-label {
    color: white;
    font-size: 0.85rem;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.1);
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    backdrop-filter: blur(10px);
  }

  /* Estilos das Abas */
  .tabs {
    display: flex;
    justify-content: center;
    gap: 0.4rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
  }

  .tab {
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.6rem 1.2rem;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.85rem;
    font-weight: 500;
    white-space: nowrap;
    min-width: fit-content;
  }

  .tab:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }

  .tab.active {
    background: white;
    color: #4f46e5;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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
