import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// 后端 API 地址配置
const isProd = process.env.NODE_ENV === 'production'
// 开发环境: 5002, 生产环境: 5004 (可通过 BACKEND_PORT 环境变量覆盖)
const BACKEND_PORT = process.env.BACKEND_PORT || (isProd ? 5004 : 5002)
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
    port: isProd ? 5173 : 5200,
    allowedHosts: ['opmvue.nokiafz.asia'],
    // 强制禁用 HMR 缓存
    hmr: {
      overlay: true,
    },
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
      // Kafka Generator API 接口（注意：不包括 /kafka-generator 页面路由）
      '/kafka-generator/field-meta': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/kafka-generator/field-cache': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/kafka-generator/field-order': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/kafka-generator/field-options': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/kafka-generator/generate': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/kafka-generator/history': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // Clean Event API 接口（已由 /api 规则代理，无需单独配置）
      // FPA Generator API 接口
      '/fpa-generator/api': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/fpa-generator/download': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/fpa-generator/task': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // FPA Rules (Category Rules)
      '/fpa-rules': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // Adjustment Factor
      '/adjustment': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/adjustment-calc': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // Chatbot API 接口(不包括 /chatbot 页面路由)
      '/chatbot/upload_progress': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chatbot/chat': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chatbot/upload_document': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chatbot/knowledge': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chatbot/session': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chatbot/feedback': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // Excel2Word
      '/excel2word': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // Word to Excel API 接口(不包括 /word-to-excel 页面路由)
      '/word-to-excel/api': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // Schedule Config API 接口(不包括 /schedule-config 页面路由)
      '/schedule-config/api': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // Markdown Upload API 接口（不包括 /markdown-upload 页面路由）
      '/markdown-upload/upload': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/markdown-upload/convert': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/markdown-upload/download': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      // SQL Formatter API 接口
      '/swagger': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    },
  },
})
