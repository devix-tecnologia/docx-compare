import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import globals from 'globals'

export default [
  // Ignorar arquivos
  {
    ignores: ['dist/**', 'node_modules/**', '.vite/**', 'coverage/**'],
  },

  // Configuração base para JavaScript
  {
    files: ['**/*.js', '**/*.ts'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2022,
      },
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      ...js.configs.recommended.rules,
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    },
  },

  // Configuração para arquivos Vue
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
      globals: {
        ...globals.browser,
      },
    },
    plugins: {
      vue,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...vue.configs.essential.rules,
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off', // Permitido para exibição de diffs HTML
    },
  },
]
