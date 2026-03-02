<template>
  <div class="export-page">
    <div class="page-header">
      <h2><el-icon><Download /></el-icon> 结果导出与逻辑诊断</h2>
      <p class="description">导出故障树分析结果，支持多种格式</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="14">
        <el-card class="export-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><FolderOpened /></el-icon> 导出配置</span>
              <el-tag type="success">步骤 6/6</el-tag>
            </div>
          </template>

          <el-form label-width="120px" size="large">
            <el-form-item label="导出格式">
              <el-radio-group v-model="exportFormat" size="large">
                <el-radio-button label="json">
                  <el-icon><Document /></el-icon>
                  JSON数据
                </el-radio-button>
                <el-radio-button label="png">
                  <el-icon><Picture /></el-icon>
                  PNG图片
                </el-radio-button>
                <el-radio-button label="svg">
                  <el-icon><Picture /></el-icon>
                  SVG矢量图
                </el-radio-button>
                <el-radio-button label="excel">
                  <el-icon><Document /></el-icon>
                  Excel表格
                </el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="包含内容">
              <el-checkbox-group v-model="exportContent">
                <el-checkbox label="tree">故障树结构</el-checkbox>
                <el-checkbox label="events">故障事件列表</el-checkbox>
                <el-checkbox label="gates">逻辑门关系</el-checkbox>
                <el-checkbox label="analysis">分析报告</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="文件名">
              <el-input 
                v-model="filename" 
                placeholder="fault_tree_report"
                :suffix="'.' + exportFormat"
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                size="large"
                :loading="exporting"
                @click="handleExport"
              >
                <el-icon><Download /></el-icon>
                立即导出
              </el-button>
              <el-button size="large" @click="previewExport">
                <el-icon><View /></el-icon>
                预览
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="diagnosis-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataAnalysis /></el-icon> 逻辑诊断报告</span>
              <el-button type="primary" size="small" @click="runDiagnosis">
                <el-icon><Refresh /></el-icon>
                运行诊断
              </el-button>
            </div>
          </template>

          <el-descriptions :column="2" border v-if="diagnosisResult">
            <el-descriptions-item label="诊断状态">
              <el-tag :type="diagnosisResult.status === 'pass' ? 'success' : 'warning'">
                {{ diagnosisResult.status === 'pass' ? '通过' : '需优化' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="诊断时间">
              {{ diagnosisResult.time }}
            </el-descriptions-item>
            <el-descriptions-item label="逻辑完整性">
              <el-progress :percentage="diagnosisResult.completeness" />
            </el-descriptions-item>
            <el-descriptions-item label="结构合理性">
              <el-progress :percentage="diagnosisResult.rationality" />
            </el-descriptions-item>
          </el-descriptions>

          <el-empty v-else description="暂无诊断结果" :image-size="100">
            <el-button type="primary" @click="runDiagnosis">开始诊断</el-button>
          </el-empty>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="history-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Clock /></el-icon> 导出历史</span>
              <el-tag>{{ exportHistory.length }} 条记录</el-tag>
            </div>
          </template>

          <el-timeline v-if="exportHistory.length > 0">
            <el-timeline-item
              v-for="item in exportHistory"
              :key="item.id"
              :timestamp="item.time"
              placement="top"
            >
              <el-card shadow="hover">
                <div class="history-item">
                  <div class="item-info">
                    <p><strong>{{ item.filename }}</strong></p>
                    <el-tag size="small" type="info">{{ item.format.toUpperCase() }}</el-tag>
                  </div>
                  <el-button 
                    type="primary" 
                    size="small"
                    @click="downloadFile(item)"
                  >
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>

          <el-empty v-else description="暂无导出记录" :image-size="100" />
        </el-card>

        <el-card class="summary-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span><el-icon><DataLine /></el-icon> 系统总结</span>
          </template>

          <el-result
            icon="success"
            title="故障树分析完成"
            sub-title="系统已完成全流程分析"
          >
            <template #extra>
              <el-space direction="vertical" style="width: 100%">
                <el-statistic-group>
                  <el-statistic title="处理文件" :value="1" />
                  <el-statistic title="提取事件" :value="3" />
                </el-statistic-group>
                <el-statistic-group>
                  <el-statistic title="生成节点" :value="4" />
                  <el-statistic title="逻辑门" :value="1" />
                </el-statistic-group>
                <el-button type="primary" @click="startNew">
                  <el-icon><RefreshRight /></el-icon>
                  开始新分析
                </el-button>
              </el-space>
            </template>
          </el-result>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Download, FolderOpened, Document, Picture, View,
  DataAnalysis, Refresh, Clock, DataLine, RefreshRight
} from '@element-plus/icons-vue'
import { exportFaultTree } from '@/api'

const route = useRoute()
const router = useRouter()
const exportFormat = ref('json')
const exportContent = ref(['tree', 'events', 'gates'])
const filename = ref('fault_tree_report')
const exporting = ref(false)
const exportHistory = ref([])
const diagnosisResult = ref(null)

const handleExport = async () => {
  const treeId = route.query.treeId || 'mock-tree-id'

  exporting.value = true

  try {
    const result = await exportFaultTree(treeId, exportFormat.value)
    
    ElMessage.success('导出成功')
    
    exportHistory.value.unshift({
      id: Date.now(),
      filename: `${filename.value}.${exportFormat.value}`,
      format: exportFormat.value,
      time: new Date().toLocaleString(),
      download_url: result.download_url
    })
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const previewExport = () => {
  ElMessage.info('预览功能开发中...')
}

const runDiagnosis = () => {
  ElMessage.info('正在运行逻辑诊断...')
  
  setTimeout(() => {
    diagnosisResult.value = {
      status: 'pass',
      time: new Date().toLocaleString(),
      completeness: 95,
      rationality: 92
    }
    ElMessage.success('诊断完成')
  }, 1500)
}

const downloadFile = (item) => {
  window.open(item.download_url, '_blank')
  ElMessage.success('开始下载')
}

const startNew = () => {
  router.push('/upload')
}
</script>

<style scoped>
.export-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.description {
  color: #606266;
  font-size: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-info p {
  margin: 0;
}
</style>
