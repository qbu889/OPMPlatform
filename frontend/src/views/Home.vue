<template>
  <div class="home-container">
    <div class="header">
      <el-row justify="center">
        <el-col :span="16">
          <h1>🚀 诺基亚 OPM 系统</h1>
          <p>一站式文档处理与管理系统</p>
        </el-col>
      </el-row>
    </div>

    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <el-icon><OfficeBuilding /></el-icon>
          <span>高效工具</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/clean-event-page')">
            <div class="feature-icon" style="background: #e1f3ff">
              <el-icon size="40" color="#409eff"><Edit /></el-icon>
            </div>
            <h3>事件数据清洗</h3>
            <p>清洗和格式化事件数据，生成标准 JSON 格式</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/sql-formatter')">
            <div class="feature-icon" style="background: #e8f5e9">
              <el-icon size="40" color="#67c23a"><DataBoard /></el-icon>
            </div>
            <h3>SQL ID 格式化</h3>
            <p>快速格式化 ID 列表用于 SQL 查询</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/kafka-generator')">
            <div class="feature-icon" style="background: #f3e5f5">
              <el-icon size="40" color="#9c27b0"><Operation /></el-icon>
            </div>
            <h3>Kafka 消息生成</h3>
            <p>根据 ES 数据生成 Kafka 消息</p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <el-icon><Document /></el-icon>
          <span>文档</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/word-to-md')">
            <div class="feature-icon" style="background: #fff3e0">
              <el-icon size="40" color="#ff9800"><Document /></el-icon>
            </div>
            <h3>Word 转 Markdown</h3>
            <p>将 Word 文档转换为 Markdown 格式</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/markdown-upload')">
            <div class="feature-icon" style="background: #e3f2fd">
              <el-icon size="40" color="#2196f3"><Files /></el-icon>
            </div>
            <h3>Markdown 转 Word</h3>
            <p>将 Markdown 文件转换为业务需求 Word 文档</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/fpa-generator')">
            <div class="feature-icon" style="background: #e8f5e9">
              <el-icon size="40" color="#4caf50"><DataAnalysis /></el-icon>
            </div>
            <h3>FPA 预估表生成</h3>
            <p>从需求文档自动生成 FPA 功能点估算表</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/word-to-excel')">
            <div class="feature-icon" style="background: #e3f2fd">
              <el-icon size="40" color="#03a9f4"><Grid /></el-icon>
            </div>
            <h3>Word 转 Excel</h3>
            <p>解析技术规范书生成软件资产清单</p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <el-icon><Platform /></el-icon>
          <span>智能系统</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/spreadsheet')">
            <div class="feature-icon" style="background: #e8f5e9">
              <el-icon size="40" color="#4caf50"><Grid /></el-icon>
            </div>
            <h3>在线表格</h3>
            <p>类似飞书表格的在线协作系统</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/chatbot')">
            <div class="feature-icon" style="background: #e1f3ff">
              <el-icon size="40" color="#2196f3"><ChatDotRound /></el-icon>
            </div>
            <h3>智能客服</h3>
            <p>基于 Ollama AI 的智能问答系统</p>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/schedule-config')">
            <div class="feature-icon" style="background: #ffebee">
              <el-icon size="40" color="#f44336"><Calendar /></el-icon>
            </div>
            <h3>排班配置管理</h3>
            <p>智能排班系统，自动化人员调度</p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  OfficeBuilding,
  Document,
  Platform,
  Edit,
  DataBoard,
  Operation,
  Files,
  DataAnalysis,
  Grid,
  ChatDotRound,
  Calendar,
} from '@element-plus/icons-vue'

const router = useRouter()

const goTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.home-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.header {
  text-align: center;
  padding: 40px 0;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 42px;
  color: #333;
  margin-bottom: 10px;
}

.header p {
  font-size: 18px;
  color: #666;
}

.section-card {
  margin-bottom: 30px;
  border-radius: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.section-header .el-icon {
  margin-right: 8px;
  font-size: 20px;
  color: #409eff;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 12px;
  padding: 15px;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
}

.feature-card h3 {
  font-size: 18px;
  color: #333;
  margin: 10px 0;
}

.feature-card p {
  font-size: 14px;
  color: #999;
  line-height: 1.6;
}
</style>
