<template>
  <div class="app-container">
    <header v-if="!headless" class="app-header">
      <h1>🚀 Versiona AI</h1>
      <p>Visualizador de Diferenças em Documentos</p>
    </header>

    <main class="app-main">
      <div class="diff-visualizer">
        <div v-if="!headless" class="diff-header">
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
                <span class="toggle-label">{{
                  useMockData ? '🔧 Dados Mock' : '📊 Dados Reais'
                }}</span>
              </label>
            </div>

            <button v-if="isConnectedToAPI && !loading" @click="listarVersoes" class="versions-btn">
              📋 {{ showVersionsList ? 'Ocultar Versões' : 'Listar Versões' }}
            </button>
            <button
              v-if="isConnectedToAPI && !loading"
              @click="processarNovoDocumento"
              class="process-btn"
            >
              🔄 {{ useMockData ? 'Processar Mock' : 'Processar Real' }}
            </button>
            <span v-if="loading" class="loading-indicator"> ⏳ Carregando... </span>
          </div>

          <!-- Estatísticas - Apenas quando há versão processada -->
          <div v-if="hasProcessedVersion" class="stats">
            <span class="stat">📊 {{ stats.total_modificacoes }} modificações</span>
            <span class="stat">⏱️ {{ stats.tempo_processamento.toFixed(3) }}s</span>
            <span class="stat">🎯 {{ stats.total_blocos }} blocos</span>
          </div>

          <!-- Lista de Versões Disponíveis -->
          <div v-if="showVersionsList" class="versions-section">
            <h3>📋 Versões Disponíveis</h3>
            <div v-if="loadingVersions" class="loading-versions">⏳ Carregando versões...</div>
            <div v-else-if="availableVersions.length > 0" class="versions-list">
              <div
                v-for="version in availableVersions"
                :key="version.id"
                class="version-item"
                @click="processarVersaoEspecifica(version.id)"
              >
                <div class="version-header">
                  <span class="version-id"
                    >🆔 {{ version.versao || version.id.substring(0, 8) }}</span
                  >
                  <span class="version-status" :class="version.status">{{ version.status }}</span>
                </div>
                <div class="version-details">
                  <p><strong>Origem:</strong> {{ version.origem }}</p>
                  <p>
                    <strong>Data:</strong>
                    {{ new Date(version.date_created).toLocaleDateString('pt-BR') }}
                  </p>
                  <p v-if="version.observacao">
                    <strong>Observação:</strong> {{ version.observacao.substring(0, 100) }}...
                  </p>
                </div>
                <button class="version-process-btn">🔄 Processar Esta Versão</button>
              </div>
            </div>
            <div v-else class="no-versions">
              ℹ️ Nenhuma versão encontrada no modo {{ useMockData ? 'mock' : 'real' }}
            </div>
          </div>

          <!-- Abas de Navegação - Apenas quando há versão processada -->
          <div v-if="hasProcessedVersion" class="tabs">
            <button
              class="tab"
              :class="{ active: activeTab === 'lista' }"
              @click="setActiveTab('lista')"
            >
              📋 Lista de Modificações
            </button>
            <button
              class="tab"
              :class="{ active: activeTab === 'blocos' }"
              @click="setActiveTab('blocos')"
            >
              🎯 Blocos Agrupados
            </button>
            <button
              class="tab"
              :class="{ active: activeTab === 'lado-a-lado' }"
              @click="setActiveTab('lado-a-lado')"
            >
              🔍 Comparação Lado a Lado
            </button>
            <button
              class="tab"
              :class="{ active: activeTab === 'vue-diff' }"
              @click="setActiveTab('vue-diff')"
            >
              ⚡ Vue-Diff Avançado
            </button>
          </div>
        </div>
        <!-- fim diff-header -->

        <!-- Estado Inicial - Nenhuma Versão Processada -->
        <div v-if="!hasProcessedVersion" class="initial-state">
          <div class="welcome-message">
            <h3>👋 Bem-vindo ao Versiona AI</h3>
            <p>Para começar, você pode:</p>
            <ul>
              <li>📋 <strong>Listar Versões</strong> - Ver todas as versões disponíveis</li>
              <li>🔄 <strong>Processar</strong> - Processar uma versão automaticamente</li>
              <li>🎯 <strong>Escolher Específica</strong> - Selecionar uma versão da lista</li>
            </ul>
            <div class="quick-actions">
              <button @click="listarVersoes" class="quick-action-btn">
                📋 Ver Versões Disponíveis
              </button>
              <button @click="processarNovoDocumento" class="quick-action-btn primary">
                🚀 Processar Primeira Versão
              </button>
            </div>
          </div>
        </div>

        <!-- Conteúdo das Diferenças - Apenas quando há versão processada -->
        <div v-else class="diff-content">
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

          <!-- Vista Blocos Agrupados -->
          <div v-else-if="activeTab === 'blocos'" class="blocks-view">
            <div
              v-if="blocosComModificacoes && blocosComModificacoes.length > 0"
              class="blocks-container"
            >
              <div class="blocks-header">
                <h3>🎯 Agrupamento Posicional</h3>
                <p>
                  Modificações organizadas por blocos baseado na análise de tags e proximidade
                  posicional
                </p>
              </div>

              <div
                v-for="(bloco, index) in blocosComModificacoes"
                :key="bloco.id || index"
                class="block-item"
              >
                <div class="block-header">
                  <div class="block-title">
                    <h4>
                      📋 Bloco {{ index + 1 }}:
                      {{
                        bloco.clausula
                          ? `${bloco.clausula.numero || ''} ${bloco.clausula.nome || ''}`.trim()
                          : 'Sem cláusula vinculada'
                      }}
                    </h4>
                    <span class="block-type" :class="bloco.tipo">{{
                      bloco.tipo || 'indefinido'
                    }}</span>
                  </div>
                  <div class="block-position">
                    📍 Posição: {{ bloco.posicao_inicio || 'N/A' }} -
                    {{ bloco.posicao_fim || 'N/A' }}
                    <span class="modifications-count"
                      >{{ bloco.total_modificacoes || 0 }} modificações</span
                    >
                  </div>
                </div>

                <div class="block-content">
                  <div class="block-preview" v-if="bloco.conteudo_estimado">
                    <strong>Conteúdo:</strong>
                    <span class="content-preview">{{ bloco.conteudo_estimado }}</span>
                  </div>

                  <!-- Modificações relacionadas a este bloco -->
                  <div class="block-modifications">
                    <div
                      v-if="bloco.modificacoes && bloco.modificacoes.length > 0"
                      class="modifications-list"
                    >
                      <h5>🔧 Modificações neste bloco ({{ bloco.modificacoes.length }}):</h5>
                      <div
                        v-for="modificacao in bloco.modificacoes"
                        :key="modificacao.id"
                        class="modification-summary"
                        :class="modificacao.css_class"
                      >
                        <div class="mod-summary-header">
                          <span class="mod-type-small">{{ modificacao.tipo.toUpperCase() }}</span>
                          <span class="mod-confidence-small"
                            >{{ (modificacao.confianca * 100).toFixed(1) }}%</span
                          >
                        </div>
                        <div class="mod-summary-content">
                          <div class="mod-content-comparison">
                            <div v-if="modificacao.conteudo.original" class="mod-original">
                              <label class="mod-label">Original:</label>
                              <span class="mod-text">"{{ modificacao.conteudo.original }}"</span>
                            </div>
                            <div v-if="modificacao.conteudo.novo" class="mod-new">
                              <label class="mod-label">Novo:</label>
                              <span class="mod-text">"{{ modificacao.conteudo.novo }}"</span>
                            </div>
                          </div>
                        </div>
                        <div
                          class="mod-summary-position"
                          v-if="modificacao.caminho && modificacao.caminho.inicio"
                        >
                          📍 {{ modificacao.caminho.inicio }}
                        </div>
                      </div>
                    </div>
                    <div v-else class="no-modifications">
                      <small
                        >ℹ️ Nenhuma modificação identificada neste bloco baseado na análise
                        atual</small
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="no-blocks">
              <div class="no-blocks-message">
                <h3>🔍 Nenhum Bloco Detalhado Encontrado</h3>
                <p>
                  Esta versão foi processada usando método fallback. Os blocos detalhados serão
                  disponibilizados quando:
                </p>
                <ul>
                  <li>📍 As tags tiverem informações de posição no banco de dados</li>
                  <li>🏷️ O sistema conseguir extrair tags das diferenças entre documentos</li>
                  <li>📊 O agrupamento posicional identificar seções estruturadas</li>
                </ul>
                <p><strong>Total de blocos identificados:</strong> {{ stats.total_blocos }}</p>
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

        <!-- Legenda apenas para a vista lista e quando há versão processada -->
        <div v-if="hasProcessedVersion && activeTab === 'lista'" class="diff-legend">
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

    <footer v-if="!headless" class="app-footer">
      <p>Desenvolvido com ❤️ e Vue 3 • Versiona AI © 2025</p>
    </footer>
  </div>
</template>

<script>
  import DiffVisualizerSideBySide from './DiffVisualizerSideBySide.vue';
import VueDiffViewer from './VueDiffViewer.vue';

  export default {
    name: 'App',
    components: {
      DiffVisualizerSideBySide,
      VueDiffViewer,
    },
    data() {
      return {
        titulo: 'Versiona AI - Visualizador de Diferenças',
        activeTab: 'lista', // 'lista', 'lado-a-lado', ou 'vue-diff'
        loading: false,
        isConnectedToAPI: false,
        useMockData: false, // Controla se deve usar dados mock ou reais
        showVersionsList: false, // Controla se mostra a lista de versões
        availableVersions: [], // Lista de versões disponíveis
        loadingVersions: false, // Controla loading da busca de versões
        hasProcessedVersion: false, // Controla se há uma versão processada
        headless: false, // Controla se deve ocultar os cabeçalhos
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
        // Se os dados vêm direto da API (estrutura nova)
        if (this.sampleData.modificacoes && this.sampleData.total_blocos !== undefined) {
          return {
            total_modificacoes: this.sampleData.modificacoes?.length || 0,
            tempo_processamento: this.sampleData.tempo_processamento || 0,
            total_blocos: this.sampleData.total_blocos || 0,
          }
        }

        // Estrutura antiga (dados mock)
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
        // Se os dados vêm direto da API (estrutura nova)
        if (this.sampleData.modificacoes) {
          return this.sampleData.modificacoes || []
        }

        // Estrutura antiga (dados mock)
        const doc = this.sampleData.documentos?.[0] || {}
        return doc.modificacoes || []
      },
      blocosDetalhados() {
        // Se os dados vêm direto da API (estrutura nova)
        if (this.sampleData.blocos_detalhados) {
          return this.sampleData.blocos_detalhados || []
        }

        // Estrutura antiga (dados mock)
        const doc = this.sampleData.documentos?.[0] || {}
        return doc.blocos_detalhados || []
      },
      blocosComModificacoes() {
        const blocos = this.blocosDetalhados

        if (!blocos.length) {
          return blocos
        }

        // Se os blocos já vêm com modificações do backend, usar direto
        // Isso acontece quando os dados vêm do Directus
        if (blocos.some(b => b.modificacoes && b.modificacoes.length > 0)) {
          return blocos
        }

        // Caso contrário, tentar mapear modificações (modo legacy/mock)
        const modificacoes = this.modificacoes

        if (!modificacoes.length) {
          return blocos
        }

        return blocos.map(bloco => {
          // Mapear modificações que estão dentro da faixa de posição do bloco
          const modificacoesDoBloco = modificacoes.filter(mod => {
            // Se a modificação tem posição e está dentro da faixa do bloco
            if (mod.posicao && bloco.posicao_inicio && bloco.posicao_fim) {
              // Converter posição de linha/coluna para posição aproximada no texto
              const posicaoAprox = (mod.posicao.linha - 1) * 50 + mod.posicao.coluna
              const dentroDoBloco =
                posicaoAprox >= bloco.posicao_inicio && posicaoAprox <= bloco.posicao_fim
              return dentroDoBloco
            }

            // Se não há posição exata, usar tags relacionadas
            if (mod.tags_relacionadas && mod.tags_relacionadas.length > 0) {
              const temTagRelacionada = mod.tags_relacionadas.some(
                tag =>
                  tag.toLowerCase().includes(bloco.nome.toLowerCase()) ||
                  bloco.nome.toLowerCase().includes(tag.toLowerCase())
              )
              return temTagRelacionada
            }

            return false
          })

          return {
            ...bloco,
            modificacoes: modificacoesDoBloco,
            total_modificacoes: modificacoesDoBloco.length,
          }
        })
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
      // Carregar tab da query string antes de qualquer outra coisa
      this.loadTabFromQueryString()

      // Verificar se há diff_id na URL
      const urlParams = new URLSearchParams(window.location.search)
      const diffId = urlParams.get('diff_id')
      const mockParam = urlParams.get('mock')
      const headlessParam = urlParams.get('headless')

      // Definir modo headless baseado no parâmetro da URL
      if (headlessParam !== null) {
        this.headless = headlessParam === 'true'
        console.log(`🖥️ Modo headless: ${this.headless}`)
      }

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

      // Métodos para controlar tab via query string
      setActiveTab(tabName) {
        console.log(`🔄 Mudando para tab: ${tabName}`)
        this.activeTab = tabName
        this.updateQueryString()
      },

      updateQueryString() {
        const url = new URL(window.location)
        url.searchParams.set('mode', this.activeTab)

        // Preservar outros parâmetros existentes
        window.history.pushState({}, '', url)
        console.log(`🌐 Query string atualizada: mode=${this.activeTab}`)
      },
      loadTabFromQueryString() {
        const urlParams = new URLSearchParams(window.location.search)
        const mode = urlParams.get('mode')

        // Validar se o mode é válido
        const validTabs = ['lista', 'blocos', 'lado-a-lado', 'vue-diff']
        if (mode && validTabs.includes(mode)) {
          this.activeTab = mode
          console.log(`📋 Tab carregada da URL: ${mode}`)
        } else {
          console.log(`📋 Usando tab padrão: ${this.activeTab}`)
        }
      },

      async listarVersoes() {
        if (!this.isConnectedToAPI) {
          alert('API não está conectada. Verifique se o servidor está rodando')
          return
        }

        this.showVersionsList = !this.showVersionsList

        if (this.showVersionsList && this.availableVersions.length === 0) {
          await this.buscarVersoes()
        }
      },

      async buscarVersoes(retryCount = 0) {
        this.loadingVersions = true
        try {
          const versoesUrl = this.useMockData ? '/api/versoes?mock=true' : '/api/versoes?mock=false'
          console.log(`🔍 Buscando versões (tentativa ${retryCount + 1}): ${versoesUrl}`)

          const response = await fetch(versoesUrl)
          if (!response.ok) {
            throw new Error('Erro ao buscar versões disponíveis')
          }

          const data = await response.json()
          this.availableVersions = data.versoes || []
          console.log(`📋 ${this.availableVersions.length} versões encontradas`)

          // Se não encontrou versões e ainda há tentativas disponíveis, tentar novamente
          if (this.availableVersions.length === 0 && retryCount < 2) {
            console.log(`⏳ Nenhuma versão encontrada, tentando novamente em 1 segundo...`)
            await new Promise(resolve => setTimeout(resolve, 1000))
            return this.buscarVersoes(retryCount + 1)
          }
        } catch (error) {
          console.error('❌ Erro ao buscar versões:', error)

          // Se ainda há tentativas disponíveis, tentar novamente
          if (retryCount < 2) {
            console.log(
              `⏳ Erro na tentativa ${retryCount + 1}, tentando novamente em 1 segundo...`
            )
            await new Promise(resolve => setTimeout(resolve, 1000))
            return this.buscarVersoes(retryCount + 1)
          } else {
            // Última tentativa falhou
            alert('Erro ao buscar versões: ' + error.message)
            this.availableVersions = []
          }
        } finally {
          this.loadingVersions = false
        }
      },

      async processarVersaoEspecifica(versaoId) {
        if (!this.isConnectedToAPI) {
          alert('API não está conectada')
          return
        }

        this.loading = true
        try {
          console.log(`🔄 Processando versão específica: ${versaoId}`)

          const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              versao_id: versaoId,
              mock: this.useMockData,
            }),
          })

          if (response.ok) {
            const resultado = await response.json()
            console.log('✅ Versão processada com sucesso:', resultado)

            if (resultado.id) {
              // Extrair modificações reais do diff HTML
              const resultadoExtracao = this.extrairModificacoesDoDiff(resultado.diff_html)

              const diffData = {
                documentos: [
                  {
                    nome: `Versão ${resultado.versao_id}`,
                    conteudo_comparacao: {
                      original: resultado.original,
                      modificado: resultado.modified,
                    },
                    estatisticas: {
                      total_modificacoes: resultadoExtracao.total_modificacoes,
                      tempo_processamento: 0.015,
                      total_blocos: resultado.total_blocos || resultadoExtracao.total_blocos,
                    },
                    modificacoes: resultadoExtracao.modificacoes,
                    blocos_detalhados: resultado.blocos_detalhados || [],
                  },
                ],
              }

              this.sampleData = diffData
              this.titulo = `Versão ${versaoId.substring(0, 8)} - Processada`

              // Marcar como versão processada
              this.hasProcessedVersion = true

              // Atualizar estatísticas baseado nos dados reais
              this.stats = {
                total_modificacoes: resultadoExtracao.total_modificacoes,
                tempo_processamento: 0.015,
                total_blocos: resultadoExtracao.total_blocos,
              }

              // Extrair modificações para exibição na lista
              this.modificacoes = resultadoExtracao.modificacoes

              // Ocultar lista de versões após processar
              this.showVersionsList = false

              // Atualizar URL com diff_id se disponível
              const newUrl = `${window.location.pathname}?diff_id=${resultado.id}&mock=${this.useMockData}`
              window.history.pushState({}, '', newUrl)
            } else {
              throw new Error('Dados incompletos recebidos da API')
            }
          } else {
            throw new Error('Erro ao processar versão')
          }
        } catch (error) {
          console.error('❌ Erro ao processar versão:', error)
          alert('Erro ao processar versão: ' + error.message)
        } finally {
          this.loading = false
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
            this.hasProcessedVersion = true
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

          let versoesData = null
          let lastError = null
          const maxRetries = 3

          // Tentar buscar versões com retry automático
          for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
              console.log(`📡 Tentativa ${attempt}/${maxRetries} de buscar versões`)

              const versoesResponse = await fetch(versoesUrl)
              if (!versoesResponse.ok) {
                throw new Error(`HTTP ${versoesResponse.status}: ${versoesResponse.statusText}`)
              }

              versoesData = await versoesResponse.json()

              // Verificar se encontrou versões
              if (versoesData.versoes && versoesData.versoes.length > 0) {
                console.log(
                  `✅ Versões encontradas na tentativa ${attempt}: ${versoesData.versoes.length} registros`
                )
                break
              } else {
                console.warn(`⚠️ Tentativa ${attempt}: Nenhuma versão encontrada`)
                if (attempt < maxRetries) {
                  console.log(`⏱️ Aguardando 1 segundo antes da próxima tentativa...`)
                  await new Promise(resolve => setTimeout(resolve, 1000))
                }
              }
            } catch (error) {
              lastError = error
              console.error(`❌ Erro na tentativa ${attempt}:`, error.message)

              if (attempt < maxRetries) {
                console.log(`⏱️ Aguardando 1 segundo antes da próxima tentativa...`)
                await new Promise(resolve => setTimeout(resolve, 1000))
              }
            }
          }

          // Verificar se conseguiu buscar versões
          if (!versoesData || !versoesData.versoes || versoesData.versoes.length === 0) {
            const modoTexto = this.useMockData ? 'mock' : 'Directus'
            const errorMsg = lastError ? `: ${lastError.message}` : ''
            alert(
              `Nenhuma versão encontrada para processar no modo ${modoTexto} após ${maxRetries} tentativas${errorMsg}`
            )
            this.loading = false
            return
          }

          // Usar a primeira versão disponível
          const versaoId = versoesData.versoes[0].id
          console.log(
            `🔄 Processando versão ID: ${versaoId} (modo: ${this.useMockData ? 'mock' : 'real'})`
          )

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
            if (resultado.diff_id || resultado.id) {
              // A API retorna dados completos (diff_id é o campo correto, id é legacy)
              const diffId = resultado.diff_id || resultado.id
              console.log('📋 Dados completos da API:', resultado)

              // Se a API retorna modificações já formatadas, usar direto
              if (resultado.modificacoes && resultado.modificacoes.length > 0) {
                console.log('✅ Usando modificações da API')
                this.sampleData = {
                  modificacoes: resultado.modificacoes,
                  total_blocos: resultado.total_blocos || 0,
                  blocos_detalhados: resultado.blocos_detalhados || [],
                  metodo: resultado.metodo || 'AST_PANDOC',
                  metricas: resultado.metricas || {},
                }
                this.hasProcessedVersion = true
                this.modificacoes = resultado.modificacoes

                // Atualizar URL com diff_id
                const newUrl = new URL(window.location)
                newUrl.searchParams.set('diff_id', diffId)
                window.history.pushState({}, '', newUrl)

                const modoTexto = this.useMockData ? 'Mock' : 'Directus'
                this.titulo = `Diff ${diffId} - Processado via ${modoTexto}`
                console.log('✅ Documento processado:', resultado)
                return
              }

              // Fallback: extrair modificações do diff HTML (modo legacy)
              const resultadoExtracao = this.extrairModificacoesDoDiff(resultado.diff_html)

              const diffData = {
                documentos: [
                  {
                    nome: `Versão ${resultado.versao_id}`,
                    conteudo_comparacao: {
                      original: resultado.original,
                      modificado: resultado.modified,
                    },
                    estatisticas: {
                      total_modificacoes: resultadoExtracao.total_modificacoes,
                      tempo_processamento: 0.015,
                      total_blocos: resultado.total_blocos || resultadoExtracao.total_blocos,
                    },
                    modificacoes: resultadoExtracao.modificacoes,
                    blocos_detalhados: resultado.blocos_detalhados || [],
                  },
                ],
              }

              this.sampleData = diffData
              const modoTexto = this.useMockData ? 'Mock' : 'Directus'
              this.titulo = `Versão ${resultado.versao_id} - Processado via ${modoTexto}`
              console.log('✅ Documento processado:', resultado)

              // Marcar como versão processada
              this.hasProcessedVersion = true

              // Atualizar estatísticas baseado nos dados reais
              this.stats = {
                total_modificacoes: resultadoExtracao.total_modificacoes,
                tempo_processamento: 0.015,
                total_blocos: resultadoExtracao.total_blocos,
              }

              // Extrair modificações para exibição na lista
              this.modificacoes = resultadoExtracao.modificacoes

              // Atualizar URL com diff_id
              const newUrl = new URL(window.location)
              newUrl.searchParams.set('diff_id', diffId)
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

        // Contar blocos (cláusulas/seções) identificados
        const clauseHeaders = doc.querySelectorAll('.clause-header')
        console.log('📋 Blocos (cláusulas) encontrados:', clauseHeaders.length)

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

        // Retornar objeto com modificações e estatísticas
        return {
          modificacoes,
          total_blocos: clauseHeaders.length || 1, // Mínimo 1 bloco
          total_modificacoes: modificacoes.length,
        }
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

  .versions-btn {
    background: rgba(255, 255, 255, 0.9);
    color: #059669;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.3s ease;
    margin-right: 0.5rem;
  }

  .versions-btn:hover {
    background: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .versions-section {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .versions-section h3 {
    margin: 0 0 1rem 0;
    color: white;
    font-size: 1.2rem;
  }

  .loading-versions {
    text-align: center;
    color: rgba(255, 255, 255, 0.7);
    padding: 2rem;
    font-style: italic;
  }

  .versions-list {
    display: grid;
    gap: 1rem;
    max-height: 400px;
    overflow-y: auto;
  }

  .version-item {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid rgba(0, 0, 0, 0.1);
  }

  .version-item:hover {
    background: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .version-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .version-id {
    font-weight: 600;
    color: #4f46e5;
  }

  .version-status {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .version-status.fechada {
    background: #dcfdf7;
    color: #059669;
  }

  .version-status.em_processamento {
    background: #fef3c7;
    color: #d97706;
  }

  .version-status.aberta {
    background: #dbeafe;
    color: #2563eb;
  }

  .version-details {
    margin: 0.5rem 0;
    font-size: 0.9rem;
  }

  .version-details p {
    margin: 0.25rem 0;
    color: #6b7280;
  }

  .version-process-btn {
    background: #4f46e5;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.5rem;
    width: 100%;
    transition: all 0.2s ease;
  }

  .version-process-btn:hover {
    background: #4338ca;
    transform: translateY(-1px);
  }

  .no-versions {
    text-align: center;
    color: rgba(255, 255, 255, 0.7);
    padding: 2rem;
    font-style: italic;
  }

  .initial-state {
    background: white;
    border-radius: 12px;
    padding: 3rem;
    margin: 2rem 0;
    text-align: center;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }

  .welcome-message h3 {
    color: #1f2937;
    font-size: 1.8rem;
    margin-bottom: 1rem;
  }

  .welcome-message p {
    color: #4b5563;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
  }

  .welcome-message ul {
    text-align: left;
    max-width: 400px;
    margin: 0 auto 2rem auto;
    color: #374151;
  }

  .welcome-message li {
    margin: 0.5rem 0;
    font-size: 1rem;
  }

  .quick-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .quick-action-btn {
    background: rgba(255, 255, 255, 0.9);
    color: #4f46e5;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    min-width: 200px;
  }

  .quick-action-btn:hover {
    background: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  }

  .quick-action-btn.primary {
    background: #4f46e5;
    color: white;
  }

  .quick-action-btn.primary:hover {
    background: #4338ca;
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

  .mode-toggle input[type='checkbox'] {
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

  .mode-toggle input[type='checkbox']:checked + .toggle-slider {
    background: #fbbf24;
    border-color: #f59e0b;
  }

  .mode-toggle input[type='checkbox']:checked + .toggle-slider::before {
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

  /* Estilos para a vista de blocos */
  .blocks-view {
    padding: 1rem;
  }

  .blocks-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .blocks-header {
    text-align: center;
    margin-bottom: 2rem;
    border-bottom: 2px solid #f1f3f4;
    padding-bottom: 1rem;
  }

  .blocks-header h3 {
    color: #1f2937;
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
  }

  .blocks-header p {
    color: #6b7280;
    margin: 0;
    font-size: 0.95rem;
  }

  .block-item {
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    overflow: hidden;
    transition: all 0.3s ease;
  }

  .block-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  .block-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 1.5rem;
  }

  .block-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .block-title h4 {
    margin: 0;
    font-size: 1.1rem;
  }

  .block-type {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    text-transform: uppercase;
    font-weight: 600;
  }

  .block-type.existente {
    background: rgba(34, 197, 94, 0.2);
  }

  .block-type.extraida {
    background: rgba(251, 191, 36, 0.2);
  }

  .block-position {
    font-size: 0.9rem;
    opacity: 0.9;
  }

  .block-content {
    padding: 1.5rem;
  }

  .block-preview {
    margin-bottom: 1rem;
  }

  .content-preview {
    display: block;
    background: #f1f3f4;
    padding: 1rem;
    border-radius: 6px;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9rem;
    color: #374151;
    margin-top: 0.5rem;
    border-left: 4px solid #667eea;
  }

  .block-modifications {
    background: #e3f2fd;
    padding: 1rem;
    border-radius: 6px;
    border-left: 4px solid #2196f3;
  }

  .block-modifications small {
    color: #1565c0;
    font-style: italic;
  }

  .no-blocks {
    text-align: center;
    padding: 3rem 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .no-blocks-message h3 {
    color: #1f2937;
    margin-bottom: 1rem;
  }

  .no-blocks-message p {
    color: #6b7280;
    margin-bottom: 1rem;
    line-height: 1.6;
  }

  .no-blocks-message ul {
    text-align: left;
    max-width: 500px;
    margin: 1rem auto;
    color: #374151;
  }

  .no-blocks-message li {
    margin-bottom: 0.5rem;
  }

  /* Estilos para modificações nos blocos */
  .modifications-count {
    background: #e3f2fd;
    color: #1976d2;
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: 1rem;
  }

  .modifications-list {
    margin-top: 1rem;
  }

  .modifications-list h5 {
    color: #1f2937;
    margin: 0 0 1rem 0;
    font-size: 1rem;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .modification-summary {
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 0.8rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
  }

  .modification-summary:hover {
    background: #f1f3f4;
    border-color: #d1d5db;
  }

  .modification-summary.diff-alteracao {
    border-left: 4px solid #ff6b6b;
  }

  .modification-summary.diff-insercao {
    border-left: 4px solid #51cf66;
  }

  .modification-summary.diff-remocao {
    border-left: 4px solid #ffd43b;
  }

  .mod-summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .mod-type-small {
    background: #6b7280;
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .mod-confidence-small {
    background: #10b981;
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
  }

  .mod-summary-content {
    margin: 0.5rem 0;
  }

  .mod-content-comparison {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .mod-original,
  .mod-new {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .mod-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .mod-original .mod-label {
    color: #dc2626;
  }

  .mod-new .mod-label {
    color: #16a34a;
  }

  .mod-text {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.85rem;
    line-height: 1.4;
    padding: 0.4rem 0.6rem;
    border-radius: 4px;
    word-wrap: break-word;
  }

  .mod-original .mod-text {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
  }

  .mod-new .mod-text {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
  }

  .mod-summary-text {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.85rem;
    color: #374151;
    line-height: 1.4;
  }

  .mod-summary-position {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.5rem;
  }

  .no-modifications {
    text-align: center;
    padding: 1.5rem;
    background: #f9fafb;
    border-radius: 6px;
    border: 1px dashed #d1d5db;
  }

  .no-modifications small {
    color: #6b7280;
    font-style: italic;
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

    .blocks-view {
      padding: 0.5rem;
    }

    .block-title {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .modifications-count {
      margin-left: 0;
      margin-top: 0.5rem;
    }

    .mod-summary-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.3rem;
    }
  }
</style>
