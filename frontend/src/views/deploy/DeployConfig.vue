<template>
  <div class="deploy-config-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#667eea"><Upload /></el-icon> 部署管理中心</h2>
      <p class="subtitle">可视化部署、备份恢复、实时监控</p>
    </div>

    <!-- 部署状态卡片 -->
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Monitor /></el-icon> 部署状态</span>
          <el-tag :type="deployStatus.is_deploying ? 'warning' : 'success'">
            {{ deployStatus.is_deploying ? '部署中' : '空闲' }}
          </el-tag>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="status-item">
            <div class="label">当前步骤</div>
            <div class="value">{{ deployStatus.current_step || '无' }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <div class="label">进度</div>
            <el-progress :percentage="deployStatus.progress" />
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <div class="label">上次部署</div>
            <div class="value">{{ deployStatus.last_deploy_time || '从未' }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="status-item">
            <div class="label">状态</div>
            <el-tag :type="getStatusType(deployStatus.last_deploy_status)">
              {{ getStatusText(deployStatus.last_deploy_status) }}
            </el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 操作按钮区域 -->
    <el-card class="actions-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Operation /></el-icon> 部署操作</span>
          <el-button size="small" @click="showConfigDialog">
            <el-icon><Setting /></el-icon>
            基础配置
          </el-button>
        </div>
      </template>
      
      <div class="action-buttons">
        <el-button 
          type="primary" 
          size="large"
          @click="showDeployDialog('fast')"
          :disabled="deployStatus.is_deploying"
        >
          <el-icon><Cpu /></el-icon>
          快速部署
        </el-button>
        
        <el-button 
          type="success" 
          size="large"
          @click="showDeployDialog('full')"
          :disabled="deployStatus.is_deploying"
        >
          <el-icon><Refresh /></el-icon>
          完整部署
        </el-button>
        
        <el-button 
          type="warning" 
          size="large"
          @click="createBackup"
          :disabled="deployStatus.is_deploying"
        >
          <el-icon><FolderAdd /></el-icon>
          创建备份
        </el-button>
        
        <el-button 
          type="info" 
          size="large"
          @click="restartService"
          :disabled="deployStatus.is_deploying"
        >
          <el-icon><SwitchButton /></el-icon>
          重启服务
        </el-button>
        
        <el-button 
          type="danger" 
          size="large"
          @click="showRestoreDialog"
          :disabled="deployStatus.is_deploying"
        >
          <el-icon><Download /></el-icon>
          恢复备份
        </el-button>
      </div>
    </el-card>

    <!-- 实时日志区域 -->
    <el-card class="logs-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Document /></el-icon> 实时部署日志</span>
          <div>
            <el-button size="small" @click="clearLogs">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
            <el-button size="small" @click="scrollToBottom">
              <el-icon><Bottom /></el-icon>
              滚动到底部
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="logs-container" ref="logsContainer">
        <div 
          v-for="(log, index) in logs" 
          :key="index"
          class="log-entry"
          :class="`log-${log.level}`"
        >
          <span class="log-time">[{{ log.timestamp }}]</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        <div v-if="logs.length === 0" class="empty-logs">
          暂无日志
        </div>
      </div>
    </el-card>

    <!-- 服务器日志查看 -->
    <el-card class="server-logs-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><View /></el-icon> 服务器日志</span>
          <div class="log-controls">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="toggleAutoRefresh"
            />
            <el-select 
              v-model="refreshInterval" 
              size="small" 
              style="width: 120px"
              :disabled="!autoRefresh"
              @change="updateRefreshInterval"
            >
              <el-option label="每 5 秒" :value="5000" />
              <el-option label="每 10 秒" :value="10000" />
              <el-option label="每 30 秒" :value="30000" />
              <el-option label="每 1 分钟" :value="60000" />
              <el-option label="每 5 分钟" :value="300000" />
            </el-select>
            <el-select v-model="serverLogType" size="small" style="width: 150px" @change="loadServerLogs">
              <el-option label="后端日志" value="backend" />
              <el-option label="Nginx访问" value="nginx" />
              <el-option label="Nginx错误" value="error" />
            </el-select>
            <el-button size="small" @click="loadServerLogs">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="server-logs-content">
        <pre>{{ serverLogs }}</pre>
      </div>
    </el-card>

    <!-- 备份列表 -->
    <el-card class="backups-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Folder /></el-icon> 备份版本</span>
          <el-button size="small" @click="loadBackups">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="backups" stripe max-height="400">
        <el-table-column prop="display_name" label="备份名称" min-width="200" />
        <el-table-column prop="date" label="备份时间" width="180" />
        <el-table-column prop="size" label="大小" width="120" />
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary"
              @click="restoreBackup(row.filename)"
            >
              恢复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      title="部署基础配置"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="deployConfig" label-width="120px">
        <el-divider content-position="left">服务器信息</el-divider>
        
        <el-form-item label="远程用户">
          <el-input v-model="deployConfig.remote_user" placeholder="root" />
        </el-form-item>
        
        <el-form-item label="远程主机">
          <el-input v-model="deployConfig.remote_host" placeholder="8.146.228.47" />
        </el-form-item>
        
        <el-form-item label="远程路径">
          <el-input v-model="deployConfig.remote_path" placeholder="/project/wordToWord" />
        </el-form-item>
        
        <el-form-item label="备份目录">
          <el-input v-model="deployConfig.backup_dir" placeholder="/project/backups" />
        </el-form-item>
        
        <el-divider content-position="left">端口配置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="本地端口">
              <el-input-number v-model="deployConfig.local_port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Nginx端口">
              <el-input-number v-model="deployConfig.nginx_port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">高级配置</el-divider>
        
        <el-form-item label="Git分支">
          <el-input v-model="deployConfig.git_branch" placeholder="q/dev" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="SSH超时(秒)">
              <el-input-number v-model="deployConfig.ssh_timeout" :min="10" :max="300" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部署超时(秒)">
              <el-input-number v-model="deployConfig.deploy_timeout" :min="60" :max="600" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :loading="savingConfig">
          保存配置
        </el-button>
      </template>
    </el-dialog>

    <!-- 部署确认对话框 -->
    <el-dialog
      v-model="deployDialogVisible"
      :title="deployDialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        :title="deployDialogMessage"
        type="warning"
        :closable="false"
        class="mb-3"
      />
      
      <template #footer>
        <el-button @click="deployDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmDeploy" :loading="deploying">
          确认部署
        </el-button>
      </template>
    </el-dialog>

    <!-- 恢复确认对话框 -->
    <el-dialog
      v-model="restoreDialogVisible"
      title="选择备份版本"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-table 
        :data="backups" 
        stripe 
        max-height="400"
        highlight-current-row
        @current-change="handleBackupSelect"
      >
        <el-table-column prop="display_name" label="备份名称" min-width="200" />
        <el-table-column prop="date" label="备份时间" width="180" />
        <el-table-column prop="size" label="大小" width="120" />
      </el-table>
      
      <template #footer>
        <el-button @click="restoreDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmRestore"
          :disabled="!selectedBackup"
          :loading="restoring"
        >
          确认恢复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, Monitor, Operation, Cpu, Refresh, FolderAdd,
  SwitchButton, Download, Document, Delete, Bottom,
  View, Folder, Setting
} from '@element-plus/icons-vue'

// 配置
const configDialogVisible = ref(false)
const savingConfig = ref(false)
const deployConfig = reactive({
  remote_user: 'root',
  remote_host: '8.146.228.47',
  remote_path: '/project/wordToWord',
  backup_dir: '/project/backups',
  local_port: 5004,
  nginx_port: 5173,
  git_branch: 'q/dev',
  ssh_timeout: 60,
  deploy_timeout: 120
})

// 部署状态
const deployStatus = reactive({
  is_deploying: false,
  current_step: '',
  progress: 0,
  last_deploy_time: null,
  last_deploy_status: null
})

// 日志
const logs = ref([])
const logsContainer = ref(null)
let eventSource = null

// 服务器日志
const serverLogs = ref('')
const serverLogType = ref('backend')
const autoRefresh = ref(false)
const refreshInterval = ref(10000) // 默认 10 秒
let autoRefreshTimer = null

// 备份列表
const backups = ref([])

// 对话框
const deployDialogVisible = ref(false)
const deployDialogTitle = ref('')
const deployDialogMessage = ref('')
const deployType = ref('fast')
const deploying = ref(false)

const restoreDialogVisible = ref(false)
const selectedBackup = ref(null)
const restoring = ref(false)

// 加载部署配置
const loadDeployConfig = async () => {
  try {
    const response = await fetch('/deploy-config/config')
    const result = await response.json()
    if (result.success) {
      Object.assign(deployConfig, result.data)
    }
  } catch (error) {
    console.error('加载部署配置失败:', error)
  }
}

// 显示配置对话框
const showConfigDialog = () => {
  configDialogVisible.value = true
}

// 保存配置
const saveConfig = async () => {
  savingConfig.value = true
  try {
    const response = await fetch('/deploy-config/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(deployConfig)
    })
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success('配置保存成功')
      configDialogVisible.value = false
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingConfig.value = false
  }
}

// 加载部署状态
const loadDeployStatus = async () => {
  try {
    const response = await fetch('/deploy-config/status')
    const result = await response.json()
    if (result.success) {
      Object.assign(deployStatus, result.data)
    }
  } catch (error) {
    console.error('加载部署状态失败:', error)
  }
}

// 连接实时日志流
const connectLogStream = () => {
  eventSource = new EventSource('/deploy-config/logs/stream')
  
  eventSource.onmessage = (event) => {
    const log = JSON.parse(event.data)
    logs.value.push(log)
    
    // 自动滚动到底部
    nextTick(() => {
      if (logsContainer.value) {
        logsContainer.value.scrollTop = logsContainer.value.scrollHeight
      }
    })
  }
  
  eventSource.onerror = (error) => {
    console.error('日志流连接错误:', error)
    eventSource.close()
  }
}

// 加载日志
const loadLogs = async () => {
  try {
    const response = await fetch('/deploy-config/logs')
    const result = await response.json()
    if (result.success) {
      logs.value = result.data.logs
    }
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

// 清空日志
const clearLogs = () => {
  logs.value = []
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

// 切换自动刷新
const toggleAutoRefresh = (enabled) => {
  if (enabled) {
    loadServerLogs() // 立即加载一次
    autoRefreshTimer = setInterval(() => {
      loadServerLogs()
    }, refreshInterval.value)
    ElMessage.success(`已开启自动刷新（每${refreshInterval.value / 1000}秒）`)
  } else {
    if (autoRefreshTimer) {
      clearInterval(autoRefreshTimer)
      autoRefreshTimer = null
    }
    ElMessage.info('已关闭自动刷新')
  }
}

// 更新刷新间隔
const updateRefreshInterval = () => {
  if (autoRefresh.value) {
    // 重新设置定时器
    if (autoRefreshTimer) {
      clearInterval(autoRefreshTimer)
    }
    autoRefreshTimer = setInterval(() => {
      loadServerLogs()
    }, refreshInterval.value)
    ElMessage.success(`刷新间隔已更新为每${refreshInterval.value / 1000}秒`)
  }
}

// 加载服务器日志
const loadServerLogs = async () => {
  try {
    const response = await fetch(`/deploy-config/server-logs?type=${serverLogType.value}&lines=100`)
    const result = await response.json()
    if (result.success) {
      serverLogs.value = result.data.logs
    } else {
      if (!autoRefresh.value) {
        ElMessage.error(result.message)
      }
    }
  } catch (error) {
    console.error('加载服务器日志失败:', error)
    if (!autoRefresh.value) {
      ElMessage.error('加载失败')
    }
  }
}

// 加载备份列表
const loadBackups = async () => {
  try {
    const response = await fetch('/deploy-config/backups')
    const result = await response.json()
    if (result.success) {
      backups.value = result.data.backups
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('加载备份列表失败:', error)
    ElMessage.error('加载失败')
  }
}

// 显示部署对话框
const showDeployDialog = (type) => {
  deployType.value = type
  if (type === 'fast') {
    deployDialogTitle.value = '快速部署'
    deployDialogMessage.value = '将跳过Git操作和前端构建，仅上传变更的Python文件。适合日常小改动。'
  } else {
    deployDialogTitle.value = '完整部署'
    deployDialogMessage.value = '将执行完整的部署流程：Git提交推送、前端构建、后端上传、服务重启。适合重大更新。'
  }
  deployDialogVisible.value = true
}

// 确认部署
const confirmDeploy = async () => {
  deploying.value = true
  try {
    const response = await fetch('/deploy-config/deploy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: deployType.value })
    })
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success('部署任务已启动，请查看实时日志')
      deployDialogVisible.value = false
      
      // 开始轮询状态
      startStatusPolling()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('部署失败:', error)
    ElMessage.error('部署失败')
  } finally {
    deploying.value = false
  }
}

// 创建备份
const createBackup = async () => {
  try {
    await ElMessageBox.confirm('确定要创建当前版本的备份吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await fetch('/deploy-config/backup', {
      method: 'POST'
    })
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success('备份任务已启动')
      // 刷新备份列表
      setTimeout(loadBackups, 5000)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('备份失败:', error)
      ElMessage.error('备份失败')
    }
  }
}

// 重启服务
const restartService = async () => {
  try {
    await ElMessageBox.confirm('确定要重启服务吗？这将导致短暂的服务中断。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await fetch('/deploy-config/restart', {
      method: 'POST'
    })
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success('服务重启成功')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重启失败:', error)
      ElMessage.error('重启失败')
    }
  }
}

// 显示恢复对话框
const showRestoreDialog = () => {
  loadBackups()
  restoreDialogVisible.value = true
}

// 选择备份
const handleBackupSelect = (row) => {
  selectedBackup.value = row
}

// 恢复备份
const restoreBackup = (filename) => {
  selectedBackup.value = { filename }
  confirmRestore()
}

// 确认恢复
const confirmRestore = async () => {
  if (!selectedBackup.value) {
    ElMessage.warning('请选择要恢复的备份版本')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要恢复到备份 "${selectedBackup.value.display_name}" 吗？此操作不可逆！`,
      '警告',
      {
        confirmButtonText: '确定恢复',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    restoring.value = true
    const response = await fetch('/deploy-config/deploy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'restore',
        backup_file: selectedBackup.value.filename
      })
    })
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success('恢复任务已启动，请查看实时日志')
      restoreDialogVisible.value = false
      startStatusPolling()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复失败:', error)
      ElMessage.error('恢复失败')
    }
  } finally {
    restoring.value = false
  }
}

// 开始状态轮询
let statusPollingInterval = null
const startStatusPolling = () => {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval)
  }
  
  statusPollingInterval = setInterval(() => {
    loadDeployStatus()
    
    // 如果部署完成，停止轮询
    if (!deployStatus.is_deploying && deployStatus.progress === 100) {
      clearInterval(statusPollingInterval)
    }
  }, 2000)
}

// 获取状态类型
const getStatusType = (status) => {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'danger'
  return 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  if (status === 'success') return '成功'
  if (status === 'failed') return '失败'
  return '未知'
}

// 初始化
onMounted(() => {
  loadDeployStatus()
  loadDeployConfig()
  loadLogs()
  loadBackups()
  loadServerLogs()
  connectLogStream()
})

// 清理
onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
  }
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval)
  }
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
})
</script>

<style scoped>
.deploy-config-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  padding: 30px 20px;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.page-header h2 {
  font-size: 28px;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.status-card,
.actions-card,
.logs-card,
.server-logs-card,
.backups-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.log-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-item {
  text-align: center;
  padding: 15px;
}

.status-item .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.status-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
}

.action-buttons .el-button {
  min-width: 140px;
}

.logs-container {
  height: 400px;
  overflow-y: auto;
  background: #1e1e1e;
  border-radius: 8px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.log-entry {
  margin-bottom: 5px;
  line-height: 1.6;
}

.log-time {
  color: #858585;
  margin-right: 10px;
}

.log-message {
  color: #d4d4d4;
}

.log-info .log-message {
  color: #4fc3f7;
}

.log-success .log-message {
  color: #66bb6a;
}

.log-warning .log-message {
  color: #ffa726;
}

.log-error .log-message {
  color: #ef5350;
}

.empty-logs {
  text-align: center;
  color: #666;
  padding: 50px 0;
}

.server-logs-content {
  height: 300px;
  overflow-y: auto;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.server-logs-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.mb-3 {
  margin-bottom: 15px;
}
</style>
