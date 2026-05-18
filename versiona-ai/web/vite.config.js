import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/health': {
        target: 'http://localhost:8011',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:8011',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
