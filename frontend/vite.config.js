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
  // 优化构建性能
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'element-plus'],
  },
  build: {
    // 生产环境优化
    target: 'esnext',
    minify: 'esbuild',
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        // 分割代码块
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('vue-router') || id.includes('pinia')) {
              return 'vendor'
            }
            if (id.includes('element-plus')) {
              return 'element-plus'
            }
          }
        },
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['opmvue.nokiafz.asia'],
    // 移除 HMR 的 wss 配置，使用默认 WebSocket
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
