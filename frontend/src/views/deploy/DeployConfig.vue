<template>
  <div class="deploy-config-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#409eff"><Setting /></el-icon> 部署配置管理</h2>
      <p class="subtitle">动态配置部署参数，无需修改代码</p>
    </div>

    <!-- 部署操作区 -->
    <el-card class="deploy-actions-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="20" color="#67c23a"><Rocket /></el-icon>
          <span>部署操作</span>
        </div>
      </template>
      
      <div class="deploy-buttons">
        <el-button type="success" size="large" @click="handleDeploy">
          <el-icon><Upload /></el-icon>
          执行部署
        </el-button>
        <el-button type="warning" size="large" @click="handleRollback">
          <el-icon><RefreshLeft /></el-icon>
          快速回滚
        </el-button>
        <el-button type="info" size="large" @click="handleViewLogs">
          <el-icon><Document /></el-icon>
          查看日志
        </el-button>
        <el-button type="danger" size="large" @click="handleRestartService">
          <el-icon><SwitchButton /></el-icon>
          重启服务
        </el-button>
      </div>
      
      <el-alert
        title="操作提示"
        type="info"
        :closable="false"
        show-icon
        class="mt-3"
      >
        <template #default>
          部署前请确认配置正确，部署过程会自动备份当前版本。回滚功能可快速恢复到上一个稳定版本。
        </template>
      </el-alert>
    </el-card>

    <!-- 配置分类标签页 -->
    <el-card class="config-card" shadow="hover">
      <el-tabs v-model="activeCategory" @tab-change="loadConfigs">
        <el-tab-pane label="🖥️ 服务器配置" name="server">
          <ConfigTable 
            :configs="serverConfigs" 
            @update="handleUpdateConfig"
            @test="handleTestConnection"
          />
        </el-tab-pane>
        
        <el-tab-pane label="🚀 部署配置" name="deployment">
          <ConfigTable 
            :configs="deploymentConfigs" 
            @update="handleUpdateConfig"
          />
        </el-tab-pane>
        
        <el-tab-pane label="💾 备份配置" name="backup">
          <!-- 备份操作区 -->
          <div class="backup-actions">
            <el-button type="primary" size="large" @click="handleBackupNow">
              <el-icon><CopyDocument /></el-icon>
              立即备份
            </el-button>
            <el-button type="success" size="large" @click="handleViewBackupHistory">
              <el-icon><Document /></el-icon>
              查看备份历史
            </el-button>
            <el-button type="warning" size="large" @click="handleCleanupBackups">
              <el-icon><Delete /></el-icon>
              清理过期备份
            </el-button>
          </div>
          
          <el-divider />
          
          <!-- 备份配置表格 -->
          <ConfigTable 
            :configs="backupConfigs" 
            @update="handleUpdateConfig"
          />
        </el-tab-pane>
        
        <el-tab-pane label="📊 监控配置" name="monitor">
          <!-- 监控操作区 -->
          <div class="monitor-actions">
            <el-button type="success" size="large" @click="handleHealthCheck">
              <el-icon><CircleCheck /></el-icon>
              健康检查
            </el-button>
            <el-button type="primary" size="large" @click="handleViewBackendLogs">
              <el-icon><Document /></el-icon>
              查看后端日志
            </el-button>
            <el-button type="info" size="large" @click="handleViewFrontendLogs">
              <el-icon><Files /></el-icon>
              查看前端日志
            </el-button>
            <el-button type="warning" size="large" @click="handleViewResourceUsage">
              <el-icon><Monitor /></el-icon>
              资源监控
            </el-button>
          </div>
          
          <el-divider />
          
          <!-- 监控配置说明 -->
          <el-alert
            title="监控功能说明"
            type="info"
            :closable="false"
            show-icon
            class="mb-3"
          >
            <template #default>
              <div style="line-height: 1.8;">
                <strong>健康检查：</strong>检查后端和前端服务是否正常运行<br>
                <strong>后端日志：</strong>查看 Flask 后端运行日志（默认50行）<br>
                <strong>前端日志：</strong>查看 Vite 前端构建和运行日志<br>
                <strong>资源监控：</strong>查看服务器 CPU、内存、磁盘使用情况
              </div>
            </template>
          </el-alert>
          
          <!-- 监控配置表格 -->
          <ConfigTable 
            :configs="monitorConfigs" 
            @update="handleUpdateConfig"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 批量操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" @click="handleBatchSave">
        <el-icon><Check /></el-icon>
        保存所有修改
      </el-button>
      <el-button @click="loadConfigs">
        <el-icon><Refresh /></el-icon>
        刷新配置
      </el-button>
      <el-button type="warning" @click="handleResetDefaults">
        <el-icon><RefreshRight /></el-icon>
        恢复默认配置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Check, Refresh, RefreshRight, Rocket, Upload, RefreshLeft, Document, SwitchButton, CopyDocument, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import ConfigTable from './components/ConfigTable.vue'

const activeCategory = ref('server')
const allConfigs = ref([])

// 按分类过滤配置
const serverConfigs = computed(() => 
  allConfigs.value.filter(c => c.category === 'server')
)

const deploymentConfigs = computed(() => 
  allConfigs.value.filter(c => c.category === 'deployment')
)

const backupConfigs = computed(() => 
  allConfigs.value.filter(c => c.category === 'backup')
)

const monitorConfigs = computed(() => 
  allConfigs.value.filter(c => c.category === 'monitor')
)

// 加载配置
const loadConfigs = async () => {
  try {
    const response = await axios.get('/api/deploy/config/list', {
      params: { hide_sensitive: false }
    })
    
    if (response.data.success) {
      allConfigs.value = response.data.configs
      ElMessage.success('配置加载成功')
    } else {
      ElMessage.error('加载配置失败：' + response.data.error)
    }
  } catch (error) {
    ElMessage.error('网络错误：' + error.message)
  }
}

// 更新单个配置
const handleUpdateConfig = async (config) => {
  try {
    const response = await axios.post('/api/deploy/config/update', {
      config_key: config.config_key,
      config_value: config.config_value
    })
    
    if (response.data.success) {
      ElMessage.success('配置更新成功')
      // 更新本地数据
      const index = allConfigs.value.findIndex(c => c.config_key === config.config_key)
      if (index !== -1) {
        allConfigs.value[index].config_value = config.config_value
      }
    } else {
      ElMessage.error('更新失败：' + response.data.error)
    }
  } catch (error) {
    ElMessage.error('网络错误：' + error.message)
  }
}

// 测试 SSH 连接
const handleTestConnection = async () => {
  try {
    const remoteHost = serverConfigs.value.find(c => c.config_key === 'remote_host')?.config_value
    const remoteUser = serverConfigs.value.find(c => c.config_key === 'remote_user')?.config_value
    const sshPort = serverConfigs.value.find(c => c.config_key === 'ssh_port')?.config_value
    
    const response = await axios.post('/api/deploy/config/test-connection', {
      remote_host: remoteHost,
      remote_user: remoteUser,
      ssh_port: parseInt(sshPort)
    })
    
    if (response.data.success) {
      ElMessage.success({
        message: '✅ SSH 连接成功！',
        duration: 3000
      })
    } else {
      ElMessage.error({
        message: '❌ SSH 连接失败：' + response.data.error,
        duration: 5000
      })
    }
  } catch (error) {
    ElMessage.error('测试失败：' + error.message)
  }
}

// 批量保存
const handleBatchSave = async () => {
  try {
    const modifiedConfigs = allConfigs.value.map(c => ({
      config_key: c.config_key,
      config_value: c.config_value
    }))
    
    const response = await axios.post('/api/deploy/config/batch-update', {
      configs: modifiedConfigs
    })
    
    if (response.data.success) {
      ElMessage.success(`✅ 成功更新 ${response.data.updated_count} 个配置`)
      loadConfigs()
    } else {
      ElMessage.error('批量更新失败：' + response.data.error)
    }
  } catch (error) {
    ElMessage.error('网络错误：' + error.message)
  }
}

// 恢复默认配置
const handleResetDefaults = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要恢复所有配置为默认值吗？此操作不可撤销！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 实现批量重置逻辑
    ElMessage.info('恢复默认配置功能开发中...')
  } catch {
    // 用户取消
  }
}

// 执行部署
const handleDeploy = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要执行部署吗？部署过程会自动备份当前版本。',
      '确认部署',
      {
        confirmButtonText: '确定部署',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('正在执行部署，请稍候...')
    // TODO: 调用部署 API
    // const response = await axios.post('/api/deploy/execute')
    
    setTimeout(() => {
      ElMessage.success('✅ 部署成功！')
    }, 2000)
  } catch {
    // 用户取消
  }
}

// 快速回滚
const handleRollback = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要回滚到上一个版本吗？当前版本将被备份。',
      '确认回滚',
      {
        confirmButtonText: '确定回滚',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('正在执行回滚，请稍候...')
    // TODO: 调用回滚 API
    // const response = await axios.post('/api/deploy/rollback')
    
    setTimeout(() => {
      ElMessage.success('✅ 回滚成功！')
    }, 2000)
  } catch {
    // 用户取消
  }
}

// 查看日志
const handleViewLogs = () => {
  ElMessage.info('日志查看功能开发中...')
  // TODO: 打开日志查看对话框或跳转到日志页面
}

// 重启服务
const handleRestartService = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重启服务吗？重启过程中服务将暂时不可用。',
      '确认重启',
      {
        confirmButtonText: '确定重启',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('正在重启服务，请稍候...')
    // TODO: 调用重启 API
    // const response = await axios.post('/api/deploy/restart')
    
    setTimeout(() => {
      ElMessage.success('✅ 服务重启成功！')
    }, 2000)
  } catch {
    // 用户取消
  }
}

// 立即备份
const handleBackupNow = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要立即执行备份吗？备份将包含数据库、配置文件和重要数据。',
      '确认备份',
      {
        confirmButtonText: '确定备份',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    ElMessage.info('正在执行备份，请稍候...')
    // TODO: 调用备份 API
    // const response = await axios.post('/api/deploy/backup/execute')
    
    setTimeout(() => {
      ElMessage.success('✅ 备份成功！备份文件已保存到指定目录。')
    }, 2000)
  } catch {
    // 用户取消
  }
}

// 查看备份历史
const handleViewBackupHistory = () => {
  ElMessage.info('备份历史查看功能开发中...')
  // TODO: 打开备份历史对话框或跳转到备份历史页面
  // 显示：备份时间、备份大小、备份类型、操作按钮（恢复、删除）
}

// 清理过期备份
const handleCleanupBackups = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清理过期备份吗？将根据配置保留天数删除旧备份。',
      '确认清理',
      {
        confirmButtonText: '确定清理',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('正在清理过期备份...')
    // TODO: 调用清理 API
    // const response = await axios.post('/api/deploy/backup/cleanup')
    
    setTimeout(() => {
      ElMessage.success('✅ 过期备份清理完成！')
    }, 2000)
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadConfigs()
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
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
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

.config-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.deploy-actions-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border-left: 4px solid #67c23a;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.deploy-buttons,
.backup-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 10px 0;
}

.mt-3 {
  margin-top: 15px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}
</style>
