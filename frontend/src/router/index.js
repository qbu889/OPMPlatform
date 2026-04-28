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
  {
    path: '/excel-to-cosmic',
    name: 'ExcelToCosmic',
    component: () => import('../views/document/ExcelToCosmic.vue'),
    meta: { title: 'Excel 转 COSMIC', hidden: true }
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
  // 钉钉推送模块
  {
    path: '/dingtalk-push',
    name: 'DingTalkPushList',
    component: () => import('../views/dingtalk-push/DingTalkPushList.vue'),
    meta: { title: '钉钉推送管理', hidden: true }
  },
  {
    path: '/dingtalk-push/config/new',
    name: 'DingTalkPushConfigNew',
    component: () => import('../views/dingtalk-push/DingTalkPushConfig.vue'),
    meta: { title: '新建推送任务', hidden: true }
  },
  {
    path: '/dingtalk-push/config/:id',
    name: 'DingTalkPushConfigEdit',
    component: () => import('../views/dingtalk-push/DingTalkPushConfig.vue'),
    meta: { title: '编辑推送任务', hidden: true }
  },
  {
    path: '/dingtalk-push/preview/:id?',
    name: 'DingTalkPushPreview',
    component: () => import('../views/dingtalk-push/DingTalkPushPreview.vue'),
    meta: { title: '消息预览', hidden: true }
  },
  {
    path: '/dingtalk-push/history',
    name: 'DingTalkPushHistory',
    component: () => import('../views/dingtalk-push/DingTalkPushHistory.vue'),
    meta: { title: '推送历史', hidden: true }
  },
  // 高效工具
  {
    path: '/clean-event-page',
    name: 'CleanEventPage',
    component: () => import('../views/tools/CleanEventPage.vue'),
    meta: { title: '事件数据清洗（旧）', hidden: true }
  },
  {
    path: '/clean-event',
    name: 'CleanEvent',
    component: () => import('../views/document/CleanEvent.vue'),
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
  {
    path: '/kafka-field-meta',
    name: 'KafkaFieldMetaManager',
    component: () => import('../views/kafka/KafkaFieldMetaManager.vue'),
    meta: { title: 'Kafka 字段映射管理', hidden: true }
  },
  {
    path: '/es-to-excel',
    name: 'EsToExcel',
    component: () => import('../views/tools/EsToExcel.vue'),
    meta: { title: 'ES 查询结果转 Excel', hidden: true }
  },
  {
    path: '/es-field-mapping',
    name: 'EsFieldMapping',
    component: () => import('../views/tools/EsFieldMapping.vue'),
    meta: { title: 'ES 字段映射配置', hidden: true }
  },
  {
    path: '/adjustment-calculator',
    name: 'AdjustmentCalculator',
    component: () => import('../views/tools/AdjustmentCalculator.vue'),
    meta: { title: '调整因子计算器', hidden: true }
  },
  {
    path: '/adjustment-factor',
    name: 'AdjustmentFactor',
    component: () => import('../views/tools/AdjustmentFactor.vue'),
    meta: { title: '调整因子管理', hidden: true }
  },
  {
    path: '/watermark-remover',
    name: 'WatermarkRemover',
    component: () => import('../views/tools/WatermarkRemover.vue'),
    meta: { title: '图片水印清除', hidden: true }
  },
  {
    path: '/sql-generator',
    name: 'SqlGenerator',
    component: () => import('../views/tools/SqlGenerator.vue'),
    meta: { title: 'SQL 智能生成器', hidden: true }
  },
  // 文档模块
  {
    path: '/fpa-category-rules',
    name: 'FpaCategoryRules',
    component: () => import('../views/document/FpaCategoryRules.vue'),
    meta: { title: 'FPA 类别规则管理' }
  },
  // 智能客服
  {
    path: '/category-management',
    name: 'CategoryManagement',
    component: () => import('../views/chat/CategoryManagement.vue'),
    meta: { title: '专业领域管理', hidden: true }
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
