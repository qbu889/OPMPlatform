import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页 - OPM 系统' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: { title: '用户登录', hidden: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
    meta: { title: '用户注册', hidden: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/auth/ForgotPassword.vue'),
    meta: { title: '忘记密码', hidden: true }
  },
  // 文档模块
  {
    path: '/word-to-md',
    name: 'WordToMd',
    component: () => import('../views/document/WordToMd.vue'),
    meta: { title: 'Word 转 Markdown', hidden: true }
  },
  {
    path: '/markdown-upload',
    name: 'MarkdownUpload',
    component: () => import('../views/document/MarkdownUpload.vue'),
    meta: { title: 'Markdown 转 Word', hidden: true }
  },
  {
    path: '/word-to-excel',
    name: 'WordToExcel',
    component: () => import('../views/document/WordToExcel.vue'),
    meta: { title: 'Word 转 Excel', hidden: true }
  },
  {
    path: '/fpa-generator',
    name: 'FpaGenerator',
    component: () => import('../views/document/FpaGenerator.vue'),
    meta: { title: 'FPA 预估表', hidden: true }
  },
  // 智能系统
  {
    path: '/spreadsheet',
    name: 'SpreadsheetList',
    component: () => import('../views/spreadsheet/SpreadsheetList.vue'),
    meta: { title: '在线表格', hidden: true }
  },
  {
    path: '/spreadsheet/:id',
    name: 'SpreadsheetDetail',
    component: () => import('../views/spreadsheet/SpreadsheetDetail.vue'),
    meta: { title: '在线表格', hidden: true }
  },
  {
    path: '/chatbot',
    name: 'Chatbot',
    component: () => import('../views/chat/Chatbot.vue'),
    meta: { title: '智能客服', hidden: true }
  },
  {
    path: '/schedule-config',
    name: 'ScheduleConfig',
    component: () => import('../views/schedule/ScheduleConfig.vue'),
    meta: { title: '排班配置', hidden: true }
  },
  // 高效工具
  {
    path: '/clean-event-page',
    name: 'CleanEventPage',
    component: () => import('../views/tools/CleanEventPage.vue'),
    meta: { title: '事件数据清洗', hidden: true }
  },
  {
    path: '/sql-formatter',
    name: 'SqlFormatter',
    component: () => import('../views/tools/SqlFormatter.vue'),
    meta: { title: 'SQL 格式化', hidden: true }
  },
  {
    path: '/kafka-generator',
    name: 'KafkaGenerator',
    component: () => import('../views/tools/KafkaGenerator.vue'),
    meta: { title: 'Kafka 消息生成', hidden: true }
  },
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/Error.vue'),
    meta: { title: '页面不存在' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  const title = to.meta.title || 'OPM 系统'
  document.title = title

  next()
})

export default router
