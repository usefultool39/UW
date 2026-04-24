import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const projectRoot = fileURLToPath(new URL('..', import.meta.url))
const charactersRoot = fileURLToPath(new URL('../characters', import.meta.url))

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@characters': charactersRoot
    }
  },
  server: {
    port: 3000,
    host: '127.0.0.1',
    fs: {
      allow: [projectRoot]
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://127.0.0.1:8765',
        changeOrigin: true
      }
    }
  }
})
