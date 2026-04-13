import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// 后端 API 地址配置
const BACKEND_PORT = 5001
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`

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
    hmr: process.env.NODE_ENV === 'production' ? false : {
      protocol: 'wss',
      host: 'opmvue.nokiafz.asia',
      clientPort: 443,
    },
    proxy: {
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/spreadsheet': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/login': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/register': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/forgot-password': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/word-to-md': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/markdown-upload': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/fpa-generator': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/word-to-excel': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chatbot': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chat': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/schedule-config': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/schedule': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/kafka-generator': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/clean-event-page': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/clean-event': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/sql-formatter': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    },
  },
})
