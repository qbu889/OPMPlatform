<template>
  <div class="config-table">
    <el-table :data="configs" stripe style="width: 100%">
      <el-table-column prop="config_key" label="配置项" width="200">
        <template #default="{ row }">
          <strong>{{ row.config_key }}</strong>
        </template>
      </el-table-column>
      
      <el-table-column prop="description" label="说明" min-width="200">
        <template #default="{ row }">
          <span class="description">{{ row.description }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="当前值" min-width="250">
        <template #default="{ row }">
          <!-- 敏感信息隐藏显示 -->
          <el-input
            v-if="row.is_sensitive"
            v-model="row.config_value"
            type="password"
            show-password
            size="small"
            placeholder="请输入配置值"
          />
          
          <!-- 布尔类型 -->
          <el-switch
            v-else-if="row.config_type === 'boolean'"
            v-model="row.config_value"
            active-value="true"
            inactive-value="false"
            active-text="启用"
            inactive-text="禁用"
          />
          
          <!-- 数字类型 -->
          <el-input-number
            v-else-if="row.config_type === 'number'"
            v-model="row.config_value"
            :min="0"
            :max="99999"
            size="small"
            controls-position="right"
            style="width: 100%"
          />
          
          <!-- 字符串类型 -->
          <el-input
            v-else
            v-model="row.config_value"
            size="small"
            placeholder="请输入配置值"
          />
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button 
            type="primary" 
            size="small" 
            @click="handleUpdate(row)"
          >
            保存
          </el-button>
          
          <el-button 
            v-if="row.config_key === 'remote_host'"
            type="success" 
            size="small" 
            @click="handleTestConnection"
          >
            测试
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div v-if="configs.length === 0" class="empty-tip">
      <el-empty description="暂无配置数据" />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  configs: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['update', 'test'])

const handleUpdate = (row) => {
  emit('update', row)
}

const handleTestConnection = () => {
  emit('test')
}
</script>

<style scoped>
.config-table {
  padding: 10px;
}

.description {
  color: #666;
  font-size: 13px;
}

.empty-tip {
  padding: 40px 0;
  text-align: center;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-table__cell) {
  padding: 8px 0;
}
</style>
