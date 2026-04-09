import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/spreadsheet': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/register': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/word-to-md': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/markdown-upload': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/fpa-generator': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/word-to-excel': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/chatbot': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/schedule-config': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/kafka-generator': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/clean-event-page': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
