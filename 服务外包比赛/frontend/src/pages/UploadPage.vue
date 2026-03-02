<template>
  <div class="upload-page">
    <div class="page-header">
      <h2><el-icon><Upload /></el-icon> 工业文本输入</h2>
      <p class="description">上传工业设备手册、故障记录等文档，支持多种格式</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="14">
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><FolderOpened /></el-icon> 文件上传区</span>
              <el-tag type="info">步骤 1/6</el-tag>
            </div>
          </template>
          
          <el-upload
            class="upload-dragger"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".docx,.xlsx,.csv,.txt"
            :limit="1"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p class="main-text">拖拽文件到此处或<em>点击上传</em></p>
              <p class="sub-text">支持格式：DOCX / XLSX / CSV / TXT</p>
              <p class="sub-text">文件大小限制：50MB</p>
            </div>
          </el-upload>

          <div class="action-buttons">
            <el-button 
              type="primary" 
              size="large"
              :loading="uploading"
              :disabled="fileList.length === 0"
              @click="handleUpload"
            >
              <el-icon><Upload /></el-icon>
              开始上传并解析
            </el-button>
            <el-button 
              size="large"
              @click="fileList = []"
              :disabled="fileList.length === 0"
            >
              清空
            </el-button>
          </div>

          <el-progress 
            v-if="uploadProgress > 0"
            :percentage="uploadProgress"
            :status="uploadProgress === 100 ? 'success' : ''"
            :stroke-width="8"
            style="margin-top: 20px"
          />
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <span><el-icon><InfoFilled /></el-icon> 使用说明</span>
          </template>
          <el-timeline>
            <el-timeline-item timestamp="步骤 1" placement="top">
              <p>选择或拖拽工业设备相关文档</p>
            </el-timeline-item>
            <el-timeline-item timestamp="步骤 2" placement="top">
              <p>系统自动解析文档内容</p>
            </el-timeline-item>
            <el-timeline-item timestamp="步骤 3" placement="top">
              <p>提取故障相关知识</p>
            </el-timeline-item>
            <el-timeline-item timestamp="步骤 4" placement="top">
              <p>生成故障树结构</p>
            </el-timeline-item>
          </el-timeline>

          <el-divider />

          <div class="stats">
            <el-statistic title="已处理文件" :value="uploadedFiles.length" />
            <el-statistic title="成功率" :value="100" suffix="%" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="files-card" shadow="hover" v-if="uploadedFiles.length > 0">
      <template #header>
        <div class="card-header">
          <span><el-icon><Document /></el-icon> 已上传文件列表</span>
          <el-tag type="success">{{ uploadedFiles.length }} 个文件</el-tag>
        </div>
      </template>
      <el-table :data="uploadedFiles" stripe>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="filename" label="文件名" min-width="200">
          <template #default="{ row }">
            <el-icon><Document /></el-icon>
            <span style="margin-left: 8px">{{ row.filename }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="120" :formatter="formatSize" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'info'">
              {{ row.status === 'success' ? '已解析' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="解析结果" min-width="200" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToExtract(row.file_id)">
              <el-icon><Right /></el-icon>
              提取知识
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Upload, UploadFilled, FolderOpened, Document, 
  InfoFilled, Right 
} from '@element-plus/icons-vue'
import { uploadFile } from '@/api'

const router = useRouter()
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadedFiles = ref([])

const handleFileChange = (file) => {
  fileList.value = [file]
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  uploadProgress.value = 0

  const progressInterval = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += 10
    }
  }, 200)

  try {
    const file = fileList.value[0].raw
    const result = await uploadFile(file)
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    ElMessage.success({
      message: '文件上传成功！',
      duration: 2000
    })
    
    uploadedFiles.value.unshift(result)
    fileList.value = []
    
    setTimeout(() => {
      uploadProgress.value = 0
    }, 2000)
  } catch (error) {
    clearInterval(progressInterval)
    uploadProgress.value = 0
    ElMessage.error('文件上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

const formatSize = (row) => {
  const size = row.file_size
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  return (size / 1024 / 1024).toFixed(2) + ' MB'
}

const goToExtract = (fileId) => {
  router.push({ path: '/extract', query: { fileId } })
}
</script>

<style scoped>
.upload-page {
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

.upload-card, .info-card, .files-card {
  margin-bottom: 20px;
}

.upload-dragger {
  width: 100%;
}

.upload-icon {
  font-size: 80px;
  color: #409EFF;
  margin-bottom: 20px;
}

.upload-text .main-text {
  font-size: 16px;
  color: #606266;
  margin: 10px 0;
}

.upload-text .main-text em {
  color: #409EFF;
  font-style: normal;
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

.stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.files-card {
  animation: slideUp 0.5s ease;
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
