<template>
  <div class="schedule-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon :size="36"><Calendar /></el-icon>
        排班配置管理系统
      </h2>
      <p class="subtitle">智能排班管理与配置工具</p>
    </div>

    <!-- 主卡片 -->
    <el-card class="main-card" shadow="hover">
      <el-tabs v-model="activeTab">
        <!-- 人员配置标签页 -->
        <el-tab-pane label="人员配置" name="staff">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="mb-3" shadow="hover">
                <template #header>
                  <div class="flex justify-between items-center">
                    <span><el-icon><UserFilled /></el-icon> 核心人员配置</span>
                    <el-button size="small" @click="toggleCoreEdit">
                      {{ isCoreEditing ? '完成' : '编辑' }}
                    </el-button>
                  </div>
                </template>
                <el-form-item label="核心人员">
                  <el-input 
                    v-model="staffConfig.coreStaff" 
                    placeholder="输入核心人员姓名"
                    :disabled="!isCoreEditing"
                  />
                </el-form-item>
              </el-card>

              <el-card class="mt-3" shadow="hover">
                <template #header>
                  <div class="flex justify-between items-center">
                    <span><el-icon><User /></el-icon> 测试人员配置</span>
                    <el-button size="small" @click="toggleTestEdit">
                      {{ isTestEditing ? '完成' : '编辑' }}
                    </el-button>
                  </div>
                </template>
                <div v-for="(staff, index) in staffConfig.testStaffs" :key="index" class="mb-2">
                  <el-input-group>
                    <el-input 
                      v-model="staffConfig.testStaffs[index]" 
                      placeholder="输入测试人员姓名"
                      :disabled="!isTestEditing"
                    />
                    <el-button 
                      v-if="isTestEditing"
                      type="danger" 
                      @click="removeTestStaff(index)"
                    >
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </el-input-group>
                </div>
                <el-button 
                  v-if="isTestEditing"
                  type="success" 
                  size="small" 
                  @click="addTestStaff"
                  class="mt-2"
                >
                  <el-icon><Plus /></el-icon> 添加测试人员
                </el-button>
              </el-card>
            </el-col>

            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <span><el-icon><InfoFilled /></el-icon> 配置说明</span>
                </template>
                <el-alert type="info" :closable="false" class="mb-3">
                  <ul style="margin: 0; padding-left: 20px;">
                    <li>核心人员通常为主班人员</li>
                    <li>测试人员参与轮班和辅助工作</li>
                    <li>至少需要一名核心人员和一名测试人员</li>
                    <li>修改配置后记得保存</li>
                  </ul>
                </el-alert>
                <div class="button-group">
                  <el-button type="primary" block @click="saveStaffConfig">
                    <el-icon><Check /></el-icon> 保存人员配置
                  </el-button>
                  <el-button type="success" block @click="loadStaffConfig">
                    <el-icon><Refresh /></el-icon> 加载当前配置
                  </el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 请假配置标签页 -->
        <el-tab-pane label="请假配置" name="leave">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover">
                <template #header>
                  <span><el-icon><CirclePlus /></el-icon> 添加请假记录</span>
                </template>
                <el-form :model="leaveForm" label-width="100px">
                  <el-form-item label="请假人员" required>
                    <el-select v-model="leaveForm.staffName" placeholder="请选择人员" class="w-full">
                      <el-option 
                        v-for="staff in allStaffList" 
                        :key="staff" 
                        :label="staff" 
                        :value="staff"
                      />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="开始日期" required>
                    <el-date-picker 
                      v-model="leaveForm.startDate" 
                      type="date" 
                      placeholder="选择开始日期"
                      class="w-full"
                    />
                  </el-form-item>
                  <el-form-item label="结束日期" required>
                    <el-date-picker 
                      v-model="leaveForm.endDate" 
                      type="date" 
                      placeholder="选择结束日期"
                      class="w-full"
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-checkbox v-model="leaveForm.isFullDay">全天请假</el-checkbox>
                  </el-form-item>
                  <template v-if="!leaveForm.isFullDay">
                    <el-form-item label="开始时间">
                      <el-time-picker 
                        v-model="leaveForm.startTime" 
                        format="HH:mm"
                        value-format="HH:mm"
                        placeholder="选择开始时间"
                        class="w-full"
                      />
                    </el-form-item>
                    <el-form-item label="结束时间">
                      <el-time-picker 
                        v-model="leaveForm.endTime" 
                        format="HH:mm"
                        value-format="HH:mm"
                        placeholder="选择结束时间"
                        class="w-full"
                      />
                    </el-form-item>
                  </template>
                  <el-form-item label="请假原因">
                    <el-input 
                      v-model="leaveForm.reason" 
                      type="textarea" 
                      :rows="2"
                      placeholder="选填"
                    />
                  </el-form-item>
                  <el-button type="primary" @click="submitLeaveRecord" class="w-full">
                    <el-icon><CirclePlus /></el-icon> 添加请假
                  </el-button>
                </el-form>
              </el-card>
            </el-col>

            <el-col :span="16">
              <el-card shadow="hover">
                <template #header>
                  <div class="flex justify-between items-center">
                    <span><el-icon><List /></el-icon> 请假记录查询</span>
                    <div>
                      <el-date-picker 
                        v-model="leaveQuery.startDate" 
                        type="date" 
                        placeholder="开始日期"
                        size="small"
                      />
                      <span class="mx-2">至</span>
                      <el-date-picker 
                        v-model="leaveQuery.endDate" 
                        type="date" 
                        placeholder="结束日期"
                        size="small"
                      />
                      <el-button type="primary" size="small" @click="searchLeaveRecords" class="ml-2">
                        <el-icon><Search /></el-icon> 查询
                      </el-button>
                    </div>
                  </div>
                </template>
                <div v-if="leaveRecords.length === 0" class="text-center text-gray-500 py-4">
                  暂无请假记录
                </div>
                <div v-else class="space-y-2">
                  <div 
                    v-for="record in leaveRecords" 
                    :key="record.id"
                    class="record-item"
                  >
                    <div class="flex justify-between items-start">
                      <div>
                        <strong>{{ record.staff_name }}</strong>
                        <el-tag 
                          :type="record.staff_type === 'CORE' ? 'danger' : 'primary'" 
                          size="small" 
                          class="ml-2"
                        >
                          {{ record.staff_type === 'CORE' ? '核心' : '测试' }}
                        </el-tag>
                        <div class="text-sm text-gray-500 mt-1">
                          {{ formatDate(record.leave_date) }}
                        </div>
                        <div class="text-sm">
                          时段: {{ record.is_full_day ? '全天' : `${record.start_time || '00:00'} - ${record.end_time || '23:59'}` }}
                        </div>
                        <div v-if="record.reason" class="text-sm text-gray-600 mt-1">
                          原因: {{ record.reason }}
                        </div>
                      </div>
                      <el-button 
                        type="danger" 
                        size="small" 
                        text
                        @click="deleteLeaveRecord(record.id)"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 生成排班标签页 -->
        <el-tab-pane label="生成排班" name="generate">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <span><el-icon><Setting /></el-icon> 排班生成设置</span>
                </template>
                <el-form label-width="100px">
                  <el-form-item label="开始日期" required>
                    <el-date-picker 
                      v-model="generateForm.startDate" 
                      type="date" 
                      placeholder="选择开始日期"
                      class="w-full"
                    />
                  </el-form-item>
                  <el-form-item label="结束日期" required>
                    <el-date-picker 
                      v-model="generateForm.endDate" 
                      type="date" 
                      placeholder="选择结束日期"
                      class="w-full"
                    />
                  </el-form-item>
                  <el-alert type="warning" :closable="false" class="mb-3">
                    注意：生成排班会根据当前人员配置和请假记录自动生成排班表
                  </el-alert>
                  <el-button type="success" @click="generateSchedule" class="w-full">
                    <el-icon><Setting /></el-icon> 生成排班表
                  </el-button>
                </el-form>
              </el-card>
            </el-col>

            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <span><el-icon><InfoFilled /></el-icon> 生成说明</span>
                </template>
                <el-alert type="info" :closable="false" class="mb-3">
                  <h6 class="font-bold mb-2">排班生成规则：</h6>
                  <ul style="margin: 0; padding-left: 20px;">
                    <li>根据设定的时段自动分配人员</li>
                    <li>考虑请假记录，自动调整排班</li>
                    <li>节假日早班避开前一日同时段人员</li>
                    <li>轮换机制确保公平分配</li>
                  </ul>
                </el-alert>
                <el-card shadow="never">
                  <template #header>
                    <span class="text-sm font-bold"><el-icon><Clock /></el-icon> 时段配置</span>
                  </template>
                  <div class="text-sm">
                    <p class="font-semibold mb-1">日常时段：</p>
                    <ul class="list-disc pl-5 mb-3">
                      <li>8:00～9:00</li>
                      <li>9:00～12:00</li>
                      <li>13:30～18:00</li>
                      <li>18:00～21:00</li>
                    </ul>
                    <p class="font-semibold mb-1">节假日时段：</p>
                    <ul class="list-disc pl-5">
                      <li>8:00～12:00</li>
                      <li>13:30～17:30</li>
                      <li>17:30～21:30</li>
                    </ul>
                  </div>
                </el-card>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 排班查询标签页 -->
        <el-tab-pane label="排班查询" name="query">
          <el-card shadow="hover">
            <template #header>
              <div class="flex justify-between items-center">
                <span><el-icon><Search /></el-icon> 排班查询</span>
                <div>
                  <el-date-picker 
                    v-model="scheduleQuery.startDate" 
                    type="date" 
                    placeholder="开始日期"
                    size="small"
                  />
                  <span class="mx-2">至</span>
                  <el-date-picker 
                    v-model="scheduleQuery.endDate" 
                    type="date" 
                    placeholder="结束日期"
                    size="small"
                  />
                  <el-button type="primary" size="small" @click="searchSchedule" class="ml-2">
                    <el-icon><Search /></el-icon> 查询
                  </el-button>
                  <el-button type="success" size="small" @click="exportSchedule" class="ml-2">
                    <el-icon><Download /></el-icon> 导出
                  </el-button>
                  <el-button type="warning" size="small" @click="importSchedule" class="ml-2">
                    <el-icon><Upload /></el-icon> 导入 CSV
                  </el-button>
                </div>
              </div>
            </template>
            <el-table 
              :data="displayScheduleData" 
              border 
              v-loading="scheduleLoading"
              class="schedule-table"
              :row-class-name="getRowClassName"
            >
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="weekday" label="星期" width="80" />
              <el-table-column prop="timeSlot" label="时段" width="150" />
              <el-table-column prop="staffDisplay" label="人员安排" min-width="200">
                <template #default="{ row }">
                  <span class="font-medium">{{ row.staffDisplay }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="150" />
            </el-table>
            <div v-if="scheduleRecords.length === 0 && !scheduleLoading" class="text-center text-gray-500 py-4 mt-3">
              暂无排班记录
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Calendar, UserFilled, User, InfoFilled, Check, Refresh,
  CirclePlus, List, Search, Delete, Setting, Clock,
  Download, Upload, Close
} from '@element-plus/icons-vue'

const activeTab = ref('staff')

// 人员配置
const staffConfig = ref({
  coreStaff: '',
  testStaffs: []
})
const isCoreEditing = ref(false)
const isTestEditing = ref(false)

// 请假相关
const leaveForm = ref({
  staffName: '',
  startDate: null,
  endDate: null,
  isFullDay: true,
  startTime: '00:00',
  endTime: '23:59',
  reason: ''
})
const leaveQuery = ref({
  startDate: null,
  endDate: null
})
const leaveRecords = ref([])

// 排班生成
const generateForm = ref({
  startDate: null,
  endDate: null
})

// 排班查询
const scheduleQuery = ref({
  startDate: null,
  endDate: null
})
const scheduleLoading = ref(false)
const scheduleRecords = ref([])

// 计算属性
const allStaffList = computed(() => {
  const list = [...staffConfig.value.testStaffs]
  if (staffConfig.value.coreStaff) {
    list.unshift(staffConfig.value.coreStaff)
  }
  return list
})

const displayScheduleData = computed(() => {
  // 按日期分组并合并相同时段的人员
  const groupedData = {}
  scheduleRecords.value.forEach(record => {
    const dateKey = record.date
    if (!groupedData[dateKey]) {
      groupedData[dateKey] = {}
    }
    
    const timeSlot = record.time_slot
    if (!groupedData[dateKey][timeSlot]) {
      groupedData[dateKey][timeSlot] = {
        staffs: [],
        staffNamesSet: new Set()
      }
    }
    
    if (!groupedData[dateKey][timeSlot].staffNamesSet.has(record.staff_name)) {
      groupedData[dateKey][timeSlot].staffs.push(record)
      groupedData[dateKey][timeSlot].staffNamesSet.add(record.staff_name)
    }
  })
  
  // 转换为数组格式
  const result = []
  Object.keys(groupedData).sort().forEach(date => {
    const dayRecords = groupedData[date]
    const dateObj = new Date(date)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const weekdayStr = weekdays[dateObj.getDay()]
    
    const timeSlotOrder = [
      '8:00～12:00',
      '13:30～17:30',
      '17:30～21:30',
      '8:00～9:00',
      '9:00～12:00',
      '13:30～18:00',
      '18:00～21:00'
    ]
    
    const sortedSlots = Object.keys(dayRecords).sort((a, b) => {
      const indexA = timeSlotOrder.indexOf(a)
      const indexB = timeSlotOrder.indexOf(b)
      if (indexA === -1 && indexB === -1) return 0
      if (indexA === -1) return 1
      if (indexB === -1) return -1
      return indexA - indexB
    })
    
    sortedSlots.forEach(timeSlot => {
      const slotGroup = dayRecords[timeSlot]
      const staffDisplay = slotGroup.staffs.map(s => s.staff_name).join('、') || '空闲'
      
      // 收集备注
      const remarks = new Set()
      slotGroup.staffs.forEach(s => {
        if (s.remark) {
          remarks.add(s.remark)
        }
      })
      const remarkDisplay = Array.from(remarks).join('、')
      
      result.push({
        date,
        weekday: weekdayStr,
        timeSlot,
        staffDisplay,
        remark: remarkDisplay,
        isHoliday: isHolidayDate(date)
      })
    })
  })
  
  return result
})

// 判断是否为节假日
function isHolidayDate(dateStr) {
  const holidaySlots = ['8:00～12:00', '13:30～17:30', '17:30～21:30']
  const dateRecords = scheduleRecords.value.filter(r => r.date === dateStr)
  if (dateRecords.length === 0) return false
  // 如果包含节假日特有的时段，则为节假日
  return dateRecords.some(r => holidaySlots.includes(r.time_slot))
}

// 表格行样式
function getRowClassName({ row }) {
  return row.isHoliday ? 'holiday-row' : 'workday-row'
}

// 加载人员配置
async function loadStaffConfig() {
  try {
    const response = await fetch('/schedule-config/api/staff-config')
    const result = await response.json()
    
    if (result.success) {
      staffConfig.value.coreStaff = result.data.core_staff || ''
      staffConfig.value.testStaffs = result.data.test_staffs || []
      ElMessage.success('人员配置加载成功')
    } else {
      ElMessage.error(result.msg)
    }
  } catch (error) {
    ElMessage.error('加载人员配置失败: ' + error.message)
  }
}

// 保存人员配置
async function saveStaffConfig() {
  if (!staffConfig.value.coreStaff) {
    ElMessage.warning('请填写核心人员姓名')
    return
  }
  
  if (staffConfig.value.testStaffs.length === 0) {
    ElMessage.warning('请至少添加一名测试人员')
    return
  }
  
  try {
    const response = await fetch('/schedule-config/api/staff-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        core_staff: staffConfig.value.coreStaff,
        test_staffs: staffConfig.value.testStaffs
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(result.msg)
      isCoreEditing.value = false
      isTestEditing.value = false
    } else {
      ElMessage.error(result.msg)
    }
  } catch (error) {
    ElMessage.error('保存人员配置失败: ' + error.message)
  }
}

// 切换核心人员编辑模式
function toggleCoreEdit() {
  isCoreEditing.value = !isCoreEditing.value
}

// 切换测试人员编辑模式
function toggleTestEdit() {
  isTestEditing.value = !isTestEditing.value
}

// 添加测试人员
function addTestStaff() {
  staffConfig.value.testStaffs.push('')
}

// 删除测试人员
function removeTestStaff(index) {
  staffConfig.value.testStaffs.splice(index, 1)
}

// 提交请假记录
async function submitLeaveRecord() {
  if (!leaveForm.value.staffName || !leaveForm.value.startDate || !leaveForm.value.endDate) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  try {
    const response = await fetch('/schedule-config/api/leave-records', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        staff_name: leaveForm.value.staffName,
        start_date: formatDateValue(leaveForm.value.startDate),
        end_date: formatDateValue(leaveForm.value.endDate),
        is_full_day: leaveForm.value.isFullDay,
        start_time: leaveForm.value.startTime || '00:00',
        end_time: leaveForm.value.endTime || '23:59',
        reason: leaveForm.value.reason
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(result.msg)
      // 重置表单
      leaveForm.value = {
        staffName: '',
        startDate: null,
        endDate: null,
        isFullDay: true,
        startTime: '00:00',
        endTime: '23:59',
        reason: ''
      }
    } else {
      ElMessage.error(result.msg)
    }
  } catch (error) {
    ElMessage.error('添加请假记录失败: ' + error.message)
  }
}

// 搜索请假记录
async function searchLeaveRecords() {
  if (!leaveQuery.value.startDate || !leaveQuery.value.endDate) {
    ElMessage.warning('请填写查询日期范围')
    return
  }
  
  try {
    const response = await fetch(
      `/schedule-config/api/leave-records?start_date=${formatDateValue(leaveQuery.value.startDate)}&end_date=${formatDateValue(leaveQuery.value.endDate)}`
    )
    const result = await response.json()
    
    if (result.success) {
      leaveRecords.value = result.data
    } else {
      ElMessage.error(result.msg)
    }
  } catch (error) {
    ElMessage.error('查询请假记录失败: ' + error.message)
  }
}

// 删除请假记录
async function deleteLeaveRecord(id) {
  try {
    await ElMessageBox.confirm('确定要删除这条请假记录吗？', '提示', { type: 'warning' })
    
    const response = await fetch('/schedule-config/api/leave-records', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id })
    })
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(result.msg)
      searchLeaveRecords()
    } else {
      ElMessage.error(result.msg)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除请假记录失败: ' + error.message)
    }
  }
}

// 生成排班表
async function generateSchedule() {
  if (!generateForm.value.startDate || !generateForm.value.endDate) {
    ElMessage.warning('请填写排班日期范围')
    return
  }
  
  if (generateForm.value.startDate > generateForm.value.endDate) {
    ElMessage.warning('开始日期不能晚于结束日期')
    return
  }
  
  // 检查是否有已存在的排班记录
  try {
    const checkResponse = await fetch(
      `/schedule-config/api/check-existing-roster?start_date=${formatDateValue(generateForm.value.startDate)}&end_date=${formatDateValue(generateForm.value.endDate)}`
    )
    const checkResult = await checkResponse.json()
    
    if (checkResult.success && checkResult.data && checkResult.data.length > 0) {
      const existingCount = checkResult.total
      const message = `检测到 ${existingCount} 条已存在的排班记录！\n是否清除现有排班后重新生成？`
      
      if (!await ElMessageBox.confirm(message, '提示', { type: 'warning' })) {
        ElMessage.info('已取消生成排班表')
        return
      }
      
      const deleteResponse = await fetch('/schedule-config/api/delete-existing-roster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: formatDateValue(generateForm.value.startDate),
          end_date: formatDateValue(generateForm.value.endDate)
        })
      })
      
      const deleteResult = await deleteResponse.json()
      if (!deleteResult.success) {
        ElMessage.error('清除现有排班失败: ' + deleteResult.msg)
        return
      }
    }
  } catch (error) {
    ElMessage.error('检查现有排班失败: ' + error.message)
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要生成 ${formatDateValue(generateForm.value.startDate)} 至 ${formatDateValue(generateForm.value.endDate)} 的排班表吗？`,
      '确认生成',
      { type: 'warning' }
    )
    
    const response = await fetch('/schedule-config/api/generate-schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_date: formatDateValue(generateForm.value.startDate),
        end_date: formatDateValue(generateForm.value.endDate)
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(result.msg)
    } else {
      ElMessage.error(result.msg)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('生成排班表失败: ' + error.message)
    }
  }
}

// 搜索排班记录
async function searchSchedule() {
  if (!scheduleQuery.value.startDate || !scheduleQuery.value.endDate) {
    ElMessage.warning('请填写查询日期范围')
    return
  }
  
  scheduleLoading.value = true
  try {
    const response = await fetch(
      `/schedule-config/api/schedule-records?start_date=${formatDateValue(scheduleQuery.value.startDate)}&end_date=${formatDateValue(scheduleQuery.value.endDate)}`
    )
    const result = await response.json()
    
    if (result.success) {
      scheduleRecords.value = result.data
    } else {
      ElMessage.error(result.msg)
    }
  } catch (error) {
    ElMessage.error('查询排班记录失败: ' + error.message)
  } finally {
    scheduleLoading.value = false
  }
}

// 导出排班数据
async function exportSchedule() {
  if (!scheduleQuery.value.startDate || !scheduleQuery.value.endDate) {
    ElMessage.warning('请填写查询日期范围')
    return
  }
  
  try {
    const response = await fetch(
      `/schedule-config/api/schedule-records?start_date=${formatDateValue(scheduleQuery.value.startDate)}&end_date=${formatDateValue(scheduleQuery.value.endDate)}`
    )
    const result = await response.json()
    
    if (!result.success || !result.data || result.data.length === 0) {
      ElMessage.warning('没有数据可导出')
      return
    }
    
    let csvContent = "日期,星期,时段,人员,备注\n"
    
    const groupedData = {}
    result.data.forEach(record => {
      const dateKey = record.date
      if (!groupedData[dateKey]) {
        groupedData[dateKey] = {}
      }
      
      if (!groupedData[dateKey][record.time_slot]) {
        groupedData[dateKey][record.time_slot] = []
      }
      
      groupedData[dateKey][record.time_slot].push(record)
    })
    
    const sortedDates = Object.keys(groupedData).sort()
    
    sortedDates.forEach(date => {
      const dayRecords = groupedData[date]
      const timeSlotOrder = [
        '8:00～9:00',
        '9:00～12:00',
        '13:30～18:00',
        '18:00～21:00'
      ]
      const sortedSlots = Object.keys(dayRecords).sort((a, b) => {
        const indexA = timeSlotOrder.indexOf(a)
        const indexB = timeSlotOrder.indexOf(b)
        return indexA - indexB
      })
      
      sortedSlots.forEach(timeSlot => {
        const slotRecords = dayRecords[timeSlot]
        const uniqueStaffs = []
        const staffNamesSet = new Set()
        
        slotRecords.filter(r => r.is_main).forEach(record => {
          if (!staffNamesSet.has(record.staff_name)) {
            uniqueStaffs.push(record)
            staffNamesSet.add(record.staff_name)
          }
        })
        
        slotRecords.filter(r => !r.is_main).forEach(record => {
          if (!staffNamesSet.has(record.staff_name)) {
            uniqueStaffs.push(record)
            staffNamesSet.add(record.staff_name)
          }
        })
        
        let staffDisplay = ''
        if (uniqueStaffs.length > 0) {
          staffDisplay = uniqueStaffs.map(r => r.staff_name).join('、')
        } else {
          staffDisplay = '空闲'
        }
        
        const dateObj = new Date(date)
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        const weekday = weekdays[dateObj.getDay()]
        
        // 收集备注
        let remarkDisplay = ''
        const remarks = new Set()
        slotRecords.forEach(r => {
          if (r.remark) {
            remarks.add(r.remark)
          }
        })
        if (remarks.size > 0) {
          remarkDisplay = Array.from(remarks).join('、')
        }
        
        csvContent += `"${date}","${weekday}","${timeSlot}","${staffDisplay}","${remarkDisplay}"\n`
      })
    })
    
    // 添加 UTF-8 BOM 头，确保 Excel 能正确识别中文
    const bom = new Uint8Array([0xEF, 0xBB, 0xBF])
    const blob = new Blob([bom, csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `排班表_${formatDateValue(scheduleQuery.value.startDate)}_to_${formatDateValue(scheduleQuery.value.endDate)}.csv`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

// 导入排班数据
async function importSchedule() {
  // 创建文件输入元素
  const fileInput = document.createElement('input')
  fileInput.type = 'file'
  fileInput.accept = '.csv'
  fileInput.style.display = 'none'
  
  document.body.appendChild(fileInput)
  
  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0]
    
    if (!file) {
      ElMessage.warning('未选择文件')
      return
    }
    
    if (!file.name.endsWith('.csv')) {
      ElMessage.warning('请上传 CSV 格式的文件')
      return
    }
    
    try {
      // 第一步：上传文件并解析
      const formData = new FormData()
      formData.append('file', file)
      
      const parseResponse = await fetch('/schedule-config/api/import-schedule', {
        method: 'POST',
        body: formData
      })
      
      const parseResult = await parseResponse.json()
      
      if (!parseResult.success) {
        ElMessage.error(parseResult.msg)
        return
      }
      
      // 显示预览信息并确认
      const { start_date, end_date, total_days, total_records } = parseResult.data
      const confirmMessage = `CSV 文件解析成功!\n\n导入预览:\n- 日期范围：${start_date} 至 ${end_date}\n- 共 ${total_days} 天\n- 总计 ${total_records} 条排班记录\n\n⚠️ 注意：此操作将删除指定日期范围内的所有现有排班数据，然后导入新数据。\n\n是否继续？`
      
      if (!await ElMessageBox.confirm(confirmMessage, '确认导入', { type: 'warning' })) {
        ElMessage.info('已取消导入')
        return
      }
      
      // 第二步：确认导入
      const confirmResponse = await fetch('/schedule-config/api/confirm-import-schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          schedule_data: parseResult.data.schedule_data
        })
      })
      
      const confirmResult = await confirmResponse.json()
      
      if (confirmResult.success) {
        ElMessage.success(confirmResult.msg)
        // 导入成功后自动查询该日期范围的排班
        scheduleQuery.value.startDate = new Date(start_date)
        scheduleQuery.value.endDate = new Date(end_date)
        searchSchedule()
      } else {
        ElMessage.error(confirmResult.msg)
      }
    } catch (error) {
      ElMessage.error('导入失败：' + error.message)
    } finally {
      // 清理文件输入元素
      document.body.removeChild(fileInput)
    }
  })
  
  // 触发文件选择对话框
  fileInput.click()
}

// 辅助函数：格式化日期为 YYYY-MM-DD
function formatDateValue(date) {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 辅助函数：格式化日期显示
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 设置默认查询日期
function setDefaultQueryDates() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const thirtyDaysLater = new Date(today)
  thirtyDaysLater.setDate(today.getDate() + 30)
  
  leaveQuery.value.startDate = today
  leaveQuery.value.endDate = thirtyDaysLater
  scheduleQuery.value.startDate = today
  scheduleQuery.value.endDate = thirtyDaysLater
}

onMounted(() => {
  loadStaffConfig()
  setDefaultQueryDates()
})
</script>

<style scoped>
.schedule-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  color: #333;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 主卡片样式 */
.main-card {
  border-radius: 16px;
  transition: all 0.3s ease;
}

.main-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

/* Tabs 样式优化 */
:deep(.el-tabs__header) {
  margin-bottom: 24px;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

/* 卡片通用样式 */
:deep(.el-card) {
  border-radius: 12px;
  transition: all 0.3s ease;
}

:deep(.el-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* 表单样式 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

/* 按钮样式优化 */
:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  border: none;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #66b1ff 0%, #409eff 100%);
  transform: translateY(-1px);
}

:deep(.el-button--success) {
  background: linear-gradient(135deg, #67c23a 0%, #529b2e 100%);
  border: none;
}

:deep(.el-button--success:hover) {
  background: linear-gradient(135deg, #85ce61 0%, #67c23a 100%);
  transform: translateY(-1px);
}

:deep(.el-button--warning) {
  background: linear-gradient(135deg, #e6a23c 0%, #cf9236 100%);
  border: none;
}

:deep(.el-button--warning:hover) {
  background: linear-gradient(135deg, #ebb563 0%, #e6a23c 100%);
  transform: translateY(-1px);
}

:deep(.el-button--danger) {
  background: linear-gradient(135deg, #f56c6c 0%, #dd6161 100%);
  border: none;
}

:deep(.el-button--danger:hover) {
  background: linear-gradient(135deg, #f78989 0%, #f56c6c 100%);
  transform: translateY(-1px);
}

/* 输入框样式 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

/* 日期选择器 */
:deep(.el-date-editor) {
  border-radius: 8px;
}

/* 表格样式优化 */
.schedule-table :deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

.schedule-table :deep(.el-table__row) {
  transition: all 0.2s ease;
}

/* 日常排班行 - 蓝色调 */
.schedule-table :deep(.workday-row) {
  background-color: #f0f7ff;
}

.schedule-table :deep(.workday-row:hover) {
  background-color: #e6f2ff;
  transform: scale(1.01);
}

/* 节假日排班行 - 橙色调 */
.schedule-table :deep(.holiday-row) {
  background-color: #fff7f0;
}

.schedule-table :deep(.holiday-row:hover) {
  background-color: #ffe8d6;
  transform: scale(1.01);
}

/* 节假日行左侧边框标识 */
.schedule-table :deep(.holiday-row td:first-child) {
  border-left: 3px solid #ff9800;
}

/* 日常行左侧边框标识 */
.schedule-table :deep(.workday-row td:first-child) {
  border-left: 3px solid #2196f3;
}

.schedule-table :deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #606266;
}

/* 按钮组样式 */
.button-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.button-group :deep(.el-button) {
  width: 100% !important;
  min-width: 100% !important;
  margin: 0 !important;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 提示框样式 */
:deep(.el-alert) {
  border-radius: 8px;
  padding: 12px 16px;
}

/* 标签样式 */
:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
}

/* 记录项样式 */
.record-item {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.record-item:hover {
  background-color: #f9fafb;
  transform: scale(1.01);
}

/* 间距工具类 */
.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.mx-2 {
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}

.w-full {
  width: 100%;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.space-y-2 > * + * {
  margin-top: 0.5rem;
}

.text-center {
  text-align: center;
}

.text-gray-500 {
  color: #6b7280;
}

.text-sm {
  font-size: 0.875rem;
}

.font-medium {
  font-weight: 500;
}

.font-bold {
  font-weight: 700;
}

.font-semibold {
  font-weight: 600;
}

.py-4 {
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.p-3 {
  padding: 0.75rem;
}

.border {
  border: 1px solid #e5e7eb;
}

.rounded {
  border-radius: 0.375rem;
}

.list-disc {
  list-style-type: disc;
}

.pl-5 {
  padding-left: 1.25rem;
}
</style>
