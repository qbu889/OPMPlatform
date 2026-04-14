<template>
  <el-header class="header">
    <div class="header-content">
      <div class="logo" @click="goHome">
        <img src="/nokia-06.png" alt="NOKIA" class="logo-icon" />
        <span class="logo-text">OPM 系统</span>
      </div>

      <el-menu mode="horizontal" :ellipsis="false">
        <router-link to="/" custom v-slot="{ navigate, href }">
          <el-menu-item @click="navigate" :index="'/'">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
        </router-link>

        <el-sub-menu index="document">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>文档</span>
          </template>
          <router-link to="/word-to-md" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/word-to-md">
                <el-icon><Document /></el-icon>
                <span>Word 转 Markdown</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/markdown-upload" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/markdown-upload">
                <el-icon><Files /></el-icon>
                <span>Markdown 转 Word</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/word-to-excel" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/word-to-excel">
                <el-icon><DataBoard /></el-icon>
                <span>Word 转 Excel</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/fpa-generator" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/fpa-generator">
                <el-icon><DataAnalysis /></el-icon>
                <span>FPA 预估表生成</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/excel-to-cosmic" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/excel-to-cosmic">
                <el-icon><Document /></el-icon>
                <span>表格转 COSMIC</span>
              </el-menu-item>
            </a>
          </router-link>
        </el-sub-menu>

        <el-sub-menu index="smart">
          <template #title>
            <el-icon><Platform /></el-icon>
            <span>智能系统</span>
          </template>
          <router-link to="/spreadsheet" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/spreadsheet">
                <el-icon><Grid /></el-icon>
                <span>在线表格</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/chatbot" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/chatbot">
                <el-icon><ChatDotRound /></el-icon>
                <span>智能客服</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/schedule-config" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/schedule-config">
                <el-icon><Calendar /></el-icon>
                <span>排班配置管理</span>
              </el-menu-item>
            </a>
          </router-link>
        </el-sub-menu>

        <el-sub-menu index="tools">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>高效工具</span>
          </template>
          <router-link to="/clean-event-page" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/clean-event-page">
                <el-icon><Edit /></el-icon>
                <span>事件数据清洗</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/es-to-excel" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/es-to-excel">
                <el-icon><Download /></el-icon>
                <span>ES 查询结果转 Excel</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/sql-formatter" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/sql-formatter">
                <el-icon><DataBoard /></el-icon>
                <span>SQL ID 格式化</span>
              </el-menu-item>
            </a>
          </router-link>
          <router-link to="/kafka-generator" custom v-slot="{ navigate, href }">
            <a :href="href" class="menu-link" @click="navigate">
              <el-menu-item index="/kafka-generator">
                <el-icon><Operation /></el-icon>
                <span>Kafka 消息生成</span>
              </el-menu-item>
            </a>
          </router-link>
        </el-sub-menu>
      </el-menu>

      <div class="user-menu">
        <template v-if="userStore.isLoggedIn">
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              <span>{{ userStore.username }}</span>
              <span v-if="userStore.isAdmin" class="admin-badge">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="showChangePasswordModal = true">
                  <el-icon><Key /></el-icon>
                  <span>修改密码</span>
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.isAdmin">
                  <el-icon><Setting /></el-icon>
                  <span>系统设置</span>
                </el-dropdown-item>
                <el-divider />
                <el-dropdown-item @click="handleLogout">
                  <el-icon><ArrowLeft /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button size="small" @click="goTo('/login')">
            <el-icon><Avatar /></el-icon>
            <span>登录</span>
          </el-button>
          <el-button size="small" type="primary" @click="goTo('/register')">
            <el-icon><UserFilled /></el-icon>
            <span>注册</span>
          </el-button>
        </template>
      </div>
    </div>
  </el-header>

  <!-- Change Password Modal -->
  <el-dialog v-model="showChangePasswordModal" title="修改密码" width="400px">
    <el-form :model="passwordForm" ref="passwordFormRef">
      <el-form-item label="当前密码">
        <el-input v-model="passwordForm.oldPassword" type="password" />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="passwordForm.newPassword" type="password" />
        <div class="el-form-item__content">
          <el-text type="info" size="small">至少 8 位，包含字母和数字</el-text>
        </div>
      </el-form-item>
      <el-form-item label="确认新密码">
        <el-input v-model="passwordForm.confirmPassword" type="password" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showChangePasswordModal = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSavePassword">
        保存更改
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  Document,
  Platform,
  OfficeBuilding,
  Files,
  DataBoard,
  DataAnalysis,
  Grid,
  ChatDotRound,
  Calendar,
  UserFilled,
  Avatar,
  Key,
  Setting,
  Download,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { changePassword, logout } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const showChangePasswordModal = ref(false)
const passwordFormRef = ref(null)
const saving = ref(false)

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const goHome = () => {
  router.push('/')
}

const goTo = (path) => {
  router.push(path)
}



const handleMenuSelect = (index) => {
  const pathMap = {
    home: '/',
    'word-to-md': '/word-to-md',
    'markdown-upload': '/markdown-upload',
    'word-to-excel': '/word-to-excel',
    'fpa-generator': '/fpa-generator',
    spreadsheet: '/spreadsheet',
    chatbot: '/chatbot',
    'schedule-config': '/schedule-config',
    'clean-event-page': '/clean-event-page',
    'sql-formatter': '/sql-formatter',
    'kafka-generator': '/kafka-generator',
  }

  if (pathMap[index]) {
    router.push(pathMap[index])
  }
}

const handleLogout = async () => {
  await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    type: 'warning',
  })

  try {
    await logout()
    userStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    console.error('退出登录错误:', error)
    ElMessage.error('退出登录失败')
  }
}

const handleSavePassword = async () => {
  if (!passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    ElMessage.error('请填写完整信息')
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  if (passwordForm.value.newPassword.length < 8) {
    ElMessage.error('新密码至少 8 位')
    return
  }

  saving.value = true
  try {
    const result = await changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword,
      passwordForm.value.confirmPassword
    )

    if (result.success) {
      ElMessage.success('密码修改成功')
      showChangePasswordModal.value = false
      passwordForm.value.oldPassword = ''
      passwordForm.value.newPassword = ''
      passwordForm.value.confirmPassword = ''
    } else {
      ElMessage.error(result.message || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.15);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 48px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Dark mode header */
@media (prefers-color-scheme: dark) {
  .header {
    background: rgba(29, 29, 31, 0.72);
  }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 48px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 32px;
  transition: opacity 0.2s ease;
}

.logo:hover {
  opacity: 0.7;
}

.logo-icon {
  height: 20px;
  margin-right: 10px;
}

.logo-text {
  color: #1d1d1f;
  font-weight: 600;
  font-size: 14px;
  letter-spacing: -0.01em;
}

.el-menu {
  background: transparent;
  border: none;
  flex: 1;
  height: 48px;
}

.el-menu-item,
.el-sub-menu__title {
  color: #1d1d1f;
  height: 48px;
  line-height: 48px;
  font-size: 13px;
  font-weight: 400;
  padding: 0 16px;
  transition: color 0.2s ease;
}

.el-menu-item:hover,
.el-sub-menu__title:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #0071e3;
}

.el-menu-item.is-active {
  color: var(--apple-text);
  font-weight: 500;
}

/* 子菜单样式 - Apple 风格 */
.el-menu--popup {
  background-color: rgba(251, 251, 253, 0.95) !important;
  backdrop-filter: saturate(180%) blur(20px);
  border-color: var(--apple-border) !important;
  border-radius: 12px;
  padding: 8px 0;
}

@media (prefers-color-scheme: dark) {
  .el-menu--popup {
    background-color: rgba(30, 30, 30, 0.95) !important;
  }
}

.el-menu--popup .el-menu-item {
  color: #1d1d1f !important;
  background-color: transparent !important;
  height: 36px;
  line-height: 36px;
  font-size: 13px;
  border-radius: 6px;
  margin: 2px 8px;
  padding: 0 12px;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

.el-menu--popup .el-menu-item:hover {
  background: rgba(0, 113, 227, 0.1) !important;
  color: #0071e3 !important;
  border: none !important;
  box-shadow: none !important;
}

.el-menu--popup .el-menu-item.is-active {
  color: var(--apple-blue) !important;
  font-weight: 500;
}

/* 子菜单箭头颜色 */
.el-sub-menu__icon-arrow {
  color: var(--apple-text-secondary);
}

.user-menu {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: var(--apple-text);
  padding: 6px 12px;
  border-radius: 980px;
  transition: all 0.2s ease;
  font-size: 13px;
}

.user-info:hover {
  background: var(--apple-bg-secondary);
}

.user-info .el-icon {
  margin-right: 6px;
  font-size: 16px;
}

.user-info span:first-child {
  margin-right: 6px;
}

.admin-badge {
  background: #ff3b30;
  color: white;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 980px;
  font-weight: 500;
}

.el-button {
  color: #1d1d1f !important;
  border-radius: 980px !important;
  font-size: 13px !important;
  height: 32px !important;
  padding: 0 16px !important;
  font-weight: 500 !important;
}

.el-button:hover {
  background: rgba(0, 0, 0, 0.05) !important;
  border-color: transparent !important;
}

.el-button span,
.el-button .el-icon {
  color: #1d1d1f !important;
}

.el-button--primary {
  background-color: #0071e3 !important;
  border-color: #0071e3 !important;
}

.el-button--primary span,
.el-button--primary .el-icon {
  color: white !important;
}

.el-button--primary:hover {
  background-color: #0077ed !important;
  border-color: #0077ed !important;
}

/* Menu link wrapper for native right-click support */
.menu-link {
  text-decoration: none;
  color: inherit;
  display: block;
  pointer-events: none;
}

.menu-link .el-menu-item {
  pointer-events: auto;
}

.menu-link:hover {
  text-decoration: none;
  color: #1d1d1f;
}

.menu-link:hover .el-menu-item {
  color: #1d1d1f !important;
}

/* Deep selectors to override Element Plus */
:deep(.el-button.el-button--primary) {
  background-color: #0071e3 !important;
  border-color: #0071e3 !important;
  color: white !important;
}

:deep(.el-button.el-button--primary span),
:deep(.el-button.el-button--primary .el-icon) {
  color: white !important;
}

:deep(.el-button.el-button--primary:hover) {
  background-color: #0077ed !important;
  border-color: #0077ed !important;
}
</style>
