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
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.header {
  text-align: center;
  padding: 50px 0;
  margin-bottom: 40px;
  position: relative;
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.header h1 {
  font-size: 48px;
  color: white;
  margin-bottom: 15px;
  font-weight: 700;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.header p {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
  position: relative;
  z-index: 1;
}

.section-card {
  margin-bottom: 35px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.section-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
}

.section-header {
  display: flex;
  align-items: center;
  font-size: 22px;
  font-weight: 700;
  color: #333;
  padding: 5px 0;
}

.section-header .el-icon {
  margin-right: 12px;
  font-size: 26px;
  color: #667eea;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  border: 2px solid transparent;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.feature-card:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: #667eea;
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.25);
}

.feature-icon {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-card:hover .feature-icon {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.feature-card h3 {
  font-size: 20px;
  color: #333;
  margin: 15px 0 10px;
  font-weight: 600;
}

.feature-card p {
  font-size: 15px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header h1 {
    font-size: 36px;
  }
  
  .header p {
    font-size: 16px;
  }
  
  .section-card {
    margin-bottom: 25px;
  }
  
  .feature-card {
    margin-bottom: 15px;
  }
}
</style>
