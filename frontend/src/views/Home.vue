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
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/es-to-excel')">
            <div class="feature-icon" style="background: #ffebee">
              <el-icon size="40" color="#f44336"><Download /></el-icon>
            </div>
            <h3>ES 查询结果转 Excel</h3>
            <p>将 ES 查询结果转换为标准 Excel 格式</p>
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
        <el-col :xs="24" :sm="12" :lg="8">
          <el-card class="feature-card" shadow="hover" @click="goTo('/excel-to-cosmic')">
            <div class="feature-icon" style="background: #e8f5e9">
              <el-icon size="40" color="#4caf50"><Document /></el-icon>
            </div>
            <h3>表格转COSMIC</h3>
            <p>Excel 转 Word (COSMIC格式)</p>
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
  Download,
  Connection,
  Tools,
} from '@element-plus/icons-vue'

const router = useRouter()

const goTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.home-container {
  min-height: calc(100vh - 48px);
}

/* Hero 区域 - Apple 风格 */
.header {
  text-align: center;
  padding: 80px 20px 60px;
  background: var(--apple-bg);
  position: relative;
  overflow: hidden;
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(0, 113, 227, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.header h1 {
  font-size: 56px;
  font-weight: 700;
  letter-spacing: -0.025em;
  margin: 0 0 16px;
  background: linear-gradient(135deg, var(--apple-text) 0%, var(--apple-text-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 1;
}

.header p {
  font-size: 21px;
  font-weight: 400;
  color: var(--apple-text-secondary);
  position: relative;
  z-index: 1;
  letter-spacing: -0.01em;
}

/* 章节卡片 */
.section-card {
  max-width: 1200px;
  margin: 0 auto 60px;
  padding: 0 24px;
  border: none;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

.section-header {
  display: flex;
  align-items: center;
  font-size: 40px;
  font-weight: 700;
  color: var(--apple-text);
  padding: 0 0 40px;
  letter-spacing: -0.02em;
}

.section-header .el-icon {
  margin-right: 16px;
  font-size: 40px;
  color: var(--apple-blue);
}

/* 功能卡片网格 */
.el-row {
  margin: 0 -12px;
}

.el-col {
  padding: 0 12px;
  margin-bottom: 24px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  border-radius: 20px;
  padding: 32px;
  text-align: left;
  border: none;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: var(--apple-card-bg);
  box-shadow: var(--apple-shadow);
  backdrop-filter: blur(20px);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--apple-shadow-hover);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 0 20px;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.05);
}

.feature-card h3 {
  font-size: 21px;
  font-weight: 600;
  color: var(--apple-text);
  margin: 0 0 8px;
  letter-spacing: -0.01em;
}

.feature-card p {
  font-size: 15px;
  color: var(--apple-text-secondary);
  line-height: 1.5;
  margin: 0;
  letter-spacing: -0.01em;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header {
    padding: 60px 20px 40px;
  }
  
  .header h1 {
    font-size: 40px;
  }
  
  .header p {
    font-size: 17px;
  }
  
  .section-header {
    font-size: 32px;
    padding: 0 0 30px;
  }
  
  .section-card {
    margin-bottom: 40px;
    padding: 0 16px;
  }
  
  .feature-card {
    padding: 24px;
  }
  
  .el-col {
    margin-bottom: 16px;
  }
}
</style>
