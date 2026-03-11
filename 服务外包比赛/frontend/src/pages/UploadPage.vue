<template>
  <div class="upload-page">
    <div class="page-header">
      <h2><el-icon><Upload /></el-icon> 文件上传与知识抽取</h2>
      <p class="description">上传工业设备手册、故障记录等文档，AI 自动提取故障知识三元组</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="14">
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><FolderOpened /></el-icon> 文件上传区</span>
              <el-tag type="info">步骤 1/2</el-tag>
            </div>
          </template>
          
          <el-upload
            class="upload-dragger"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".docx,.xlsx,.csv,.txt,.pdf,.md"
            :limit="1"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p class="main-text">拖拽文件到此处或<em>点击上传</em></p>
              <p class="sub-text">支持格式：PDF / DOCX / TXT / MD / CSV / XLSX</p>
              <p class="sub-text">文件大小限制：50MB</p>
            </div>
          </el-upload>

          <!-- 添加顶事件输入框 -->
          <div class="top-event-input" style="margin-top: 20px;">
            <el-input
              v-model="topEvent"
              placeholder="请输入顶事件名称（用于文件命名）"
              prefix-icon="Search"
              clearable
            />
            <p class="input-tip">例如：系统宕机、主轴故障、液压系统失效</p>
          </div>

          <div class="action-buttons">
            <el-button 
              type="primary" 
              size="large"
              :loading="processing"
              :disabled="fileList.length === 0 || !topEvent"
              @click="handleProcess"
            >
              <el-icon><MagicStick /></el-icon>
              {{ processing ? '处理中...' : '开始上传并提取知识' }}
            </el-button>
            <el-button 
              size="large"
              @click="resetForm"
              :disabled="fileList.length === 0 || processing"
            >
              清空
            </el-button>
          </div>

          <el-progress 
            v-if="progress > 0"
            :percentage="progress"
            :status="progress === 100 ? 'success' : ''"
            :stroke-width="8"
            style="margin-top: 20px"
          />
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <span><el-icon><InfoFilled /></el-icon> 处理流程</span>
          </template>
          <el-timeline>
            <el-timeline-item timestamp="步骤 1" placement="top">
              <p>上传工业设备相关文档</p>
            </el-timeline-item>
            <el-timeline-item timestamp="步骤 2" placement="top">
              <p>AI 自动提取故障三元组</p>
            </el-timeline-item>
            <el-timeline-item timestamp="结果" placement="top">
              <p>生成 JSON 文件并保存到服务器</p>
            </el-timeline-item>
            <el-timeline-item timestamp="下一步" placement="top" type="primary">
              <p>手动触发生成故障树可视化</p>
            </el-timeline-item>
          </el-timeline>

          <el-divider />

          <div class="stats">
            <el-statistic title="已处理文件" :value="processedCount" />
            <el-statistic title="提取成功率" :value="successRate" suffix="%" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 处理结果展示 -->
    <el-card class="result-card" shadow="hover" v-if="extractResult">
      <template #header>
        <div class="card-header">
          <span><el-icon><SuccessFilled /></el-icon> 知识提取结果</span>
          <el-tag type="success">{{ extractResult.triplets?.length || 0 }} 个三元组</el-tag>
        </div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="任务 ID">{{ extractResult.task_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ extractResult.status }}</el-descriptions-item>
        <el-descriptions-item label="输出文件">{{ extractResult.output_file }}</el-descriptions-item>
        <el-descriptions-item label="三元组数量">{{ extractResult.triplets?.length || 0 }}</el-descriptions-item>
        <el-descriptions-item label="事件数量">{{ extractResult.events?.length || 0 }}</el-descriptions-item>
        <el-descriptions-item label="逻辑门数量">{{ extractResult.gates?.length || 0 }}</el-descriptions-item>
        <el-descriptions-item label="平均置信度">
          {{ (extractResult.accuracy_metrics?.avg_confidence || 0).toFixed(2) }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="result-actions">
        <el-button type="success" size="large" @click="viewJsonFile">
          <el-icon><Document /></el-icon>
          查看 JSON 文件
        </el-button>
        <el-button type="primary" size="large" @click="goToGenerate">
          <el-icon><Right /></el-icon>
          生成故障树
        </el-button>
        <el-button size="large" @click="downloadTriples">
          <el-icon><Download /></el-icon>
          下载三元组
        </el-button>
      </div>

      <!-- 三元组预览 -->
      <el-collapse v-if="extractResult.triplets && extractResult.triplets.length > 0">
        <el-collapse-item title="查看前 5 个三元组预览" name="1">
          <el-table :data="extractResult.triplets.slice(0, 5)" stripe max-height="400">
            <el-table-column prop="subject_name" label="主语" min-width="150" />
            <el-table-column prop="relation" label="关系" width="150">
              <template #default="{ row }">
                <el-tag size="small" :type="row.relation === 'jointly_resultsIn' ? 'warning' : 'primary'">
                  {{ row.relation }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="object_name" label="宾语" min-width="150" />
            <el-table-column prop="confidence" label="置信度" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="row.confidence > 0.9 ? 'success' : 'info'">
                  {{ row.confidence.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Upload, UploadFilled, FolderOpened, Document, 
  InfoFilled, Right, MagicStick, SuccessFilled, Download
} from '@element-plus/icons-vue'
import { uploadFile, extractKnowledge } from '@/api'

const router = useRouter()
const fileList = ref([])
const topEvent = ref('')  // 新增顶事件
const processing = ref(false)
const progress = ref(0)
const extractResult = ref(null)
const processedCount = ref(0)
const successRate = ref(100)

const handleFileChange = (file) => {
  fileList.value = [file]
}

const resetForm = () => {
  fileList.value = []
  topEvent.value = ''
  extractResult.value = null
  progress.value = 0
}

const handleProcess = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  if (!topEvent.value) {
    ElMessage.warning('请输入顶事件名称')
    return
  }

  processing.value = true
  progress.value = 0
  extractResult.value = null

  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 10
    }
  }, 300)

  try {
    // 步骤 1: 上传文件
    ElMessage.info('正在上传文件...')
    const file = fileList.value[0].raw
    const uploadResult = await uploadFile(file)
    
    // 步骤 2: 提取知识（传入顶事件）
    ElMessage.info(`正在提取知识（顶事件：${topEvent.value}）...`)
    const result = await extractKnowledge({
      file_id: uploadResult.file_id,
      mode: 'multimodal',
      top_event: topEvent.value  // 传入顶事件
    })
    
    clearInterval(progressInterval)
    progress.value = 100

    extractResult.value = result
    processedCount.value++

    ElMessage.success({
      message: `知识提取成功！共提取 ${result.triplets?.length || 0} 个三元组`,
      duration: 3000
    })

    fileList.value = []
    
    setTimeout(() => {
      progress.value = 0
    }, 2000)
  } catch (error) {
    clearInterval(progressInterval)
    progress.value = 0
    console.error('处理失败:', error)
    ElMessage.error('处理失败，请重试')
  } finally {
    processing.value = false
  }
}

const viewJsonFile = () => {
  if (extractResult.value?.output_file) {
    ElMessage.info(`JSON 文件路径：${extractResult.value.output_file}`)
    // 可以添加打开文件浏览器的功能
  }
}

const downloadTriples = () => {
  if (extractResult.value?.output_file) {
    // 从完整路径提取文件名
    const filename = extractResult.value.output_file.split('/').pop()
    // 使用新的下载接口
    window.open(`/api/v1/fault-tree/download-triplets/${filename}`, '_blank')
    ElMessage.success('下载已开始')
  }
}

const goToGenerate = () => {
  if (extractResult.value && extractResult.value.triplets?.length > 0) {
    router.push('/generate')
  } else {
    ElMessage.warning('请先完成知识提取')
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  color: white;
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.description {
  color: rgba(255, 255, 255, 0.95);
  font-size: 16px;
  margin: 0;
  letter-spacing: 0.5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 18px;
  color: #1f2937;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 10px;
}

.upload-card, .info-card, .result-card {
  margin-bottom: 20px;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.upload-card:hover,
.info-card:hover,
.result-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.upload-dragger {
  width: 100%;
  border: 3px dashed #e5e7eb !important;
  border-radius: 16px !important;
  transition: all 0.3s;
  background: linear-gradient(to bottom right, #f9fafb, #f3f4f6) !important;
}

.upload-dragger:hover {
  border-color: #667eea !important;
  background: linear-gradient(to bottom right, #eff6ff, #fef2ff) !important;
  transform: scale(1.01);
}

.upload-icon {
  font-size: 80px;
  color: #667eea;
  margin-bottom: 20px;
  transition: all 0.3s;
}

.upload-dragger:hover .upload-icon {
  transform: scale(1.1) rotate(5deg);
  color: #764ba2;
}

.upload-text .main-text {
  font-size: 16px;
  color: #606266;
  margin: 10px 0;
  font-weight: 500;
}

.upload-text .main-text em {
  color: #667eea;
  font-style: normal;
  font-weight: 600;
}

.upload-text .sub-text {
  font-size: 13px;
  color: #909399;
  margin: 5px 0;
}

.action-buttons {
  margin-top: 25px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.result-actions {
  margin: 25px 0;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
