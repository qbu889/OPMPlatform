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
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['opmvue.nokiafz.asia'],
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/spreadsheet': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/register': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/forgot-password': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/word-to-md': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/markdown-upload': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/fpa-generator': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/word-to-excel': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/chatbot': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/schedule-config': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/schedule': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/kafka-generator': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/clean-event-page': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/sql-formatter': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
    },
  },
})
