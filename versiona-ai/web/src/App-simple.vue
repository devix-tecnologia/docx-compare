<template>
  <div id="app">
    <h1>🚀 Versiona AI - Teste</h1>
    <p>Se você conseguir ver isso, o Vue está funcionando!</p>
    <button @click="testarAPI">Testar API</button>
    <div v-if="apiResponse">
      <h3>Resposta da API:</h3>
      <pre>{{ apiResponse }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      apiResponse: null
    }
  },
  async mounted() {
    console.log('Vue App montado com sucesso!')
    this.testarAPI()
  },
  methods: {
    async testarAPI() {
      try {
        console.log('Testando API...')
        const response = await fetch('/api/health')
        console.log('Response status:', response.status)
        if (response.ok) {
          const data = await response.json()
          this.apiResponse = data
          console.log('API funcionando:', data)
        } else {
          this.apiResponse = { error: 'API não responde' }
        }
      } catch (error) {
        console.error('Erro na API:', error)
        this.apiResponse = { error: error.message }
      }
    }
  }
}
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  border: 2px solid #ccc;
  border-radius: 10px;
}

button {
  background: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin: 10px 0;
}

button:hover {
  background: #45a049;
}

pre {
  background: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}
</style>
