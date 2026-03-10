<template>
  <div class="upload-page">
    <div class="page-header">
      <h2><el-icon><Upload /></el-icon> 知识三元组上传</h2>
      <p class="description">将结构化的故障知识三元组写入知识图谱</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <span><el-icon><Document /></el-icon> 上传方式一：手动输入 JSON</span>
          </template>

          <el-input
            v-model="jsonInput"
            type="textarea"
            :rows="10"
            placeholder='请输入 JSON 格式的三元组，支持两种格式：

格式 1（直接数组）：
[
  {
    "subject_name": "登机梯电机过热",
    "subject_type": "BasicEvent",
    "relation": "resultsIn",
    "object_name": "电机停机保护",
    "object_type": "IntermediateEvent",
    "confidence": 0.92,
    "source": "维修手册 P45"
  }
]

格式 2（带 triplets 字段）：
{
  "triplets": [ ... ]
}'
          />

          <!-- 新增：顶事件输入框 -->
          <div style="margin-top: 15px;">
            <el-label style="font-weight: 600; margin-bottom: 8px; display: block;">
              <el-icon><Search /></el-icon> 顶事件名称
            </el-label>
            <el-input
              v-model="topEventInput"
              placeholder="请输入顶事件名称，例如：登机梯无法展开"
              prefix-icon="Search"
              size="large"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <div style="margin-top: 5px; font-size: 12px; color: #909399;">
              💡 系统会根据该顶事件自动构建完整的故障树
            </div>
          </div>

          <el-button
            type="primary"
            style="width: 100%; margin-top: 15px;"
            @click="validateAndUpload"
            :loading="uploading"
            size="large"
          >
            <el-icon><Upload /></el-icon>
            {{ uploading ? '处理中...' : '上传三元组并生成故障树' }}
          </el-button>

          <!-- 新增：下载和查看按钮 -->
          <div v-if="generatedTreeData" style="margin-top: 10px; display: flex; gap: 10px;">
            <el-button
              type="success"
              style="flex: 1;"
              @click="downloadFaultTree"
              size="large"
            >
              <el-icon><Download /></el-icon>
              下载故障树 JSON
            </el-button>
            <el-button
              type="info"
              style="flex: 1;"
              @click="viewGeneratedJSON"
              size="large"
            >
              <el-icon><Document /></el-icon>
              查看 JSON 内容
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="example-card" shadow="hover">
          <template #header>
            <span><el-icon><InfoFilled /></el-icon> 数据格式说明</span>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="subject_name">
              主体名称（故障事件名）
            </el-descriptions-item>
            <el-descriptions-item label="subject_type">
              主体类型：BasicEvent / IntermediateEvent / TopEvent
            </el-descriptions-item>
            <el-descriptions-item label="relation">
              关系类型：resultsIn / causedBy / relatedTo / jointly_resultsIn
            </el-descriptions-item>
            <el-descriptions-item label="object_name">
              客体名称（结果事件名）
            </el-descriptions-item>
            <el-descriptions-item label="object_type">
              客体类型：BasicEvent / IntermediateEvent / TopEvent
            </el-descriptions-item>
            <el-descriptions-item label="confidence">
              置信度：0.0 - 1.0
            </el-descriptions-item>
            <el-descriptions-item label="source">
              数据来源（可选）
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="提示"
            type="info"
            :closable="false"
            style="margin-top: 15px;"
          >
            <p>• 支持批量上传多个三元组</p>
            <p>• 系统会自动去重和合并重复边的证据</p>
            <p>• 置信度用于后续路径过滤和权重计算</p>
          </el-alert>
        </el-card>

        <el-card class="history-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span><el-icon><Clock /></el-icon> 上传历史</span>
          </template>

          <el-timeline>
            <el-timeline-item
              v-for="(record, index) in uploadHistory"
              :key="index"
              :timestamp="record.time"
              placement="top"
              :type="record.status === 'success' ? 'success' : 'danger'"
            >
              <el-card>
                <p>成功入库 {{ record.inserted }} 条</p>
                <p v-if="record.skipped > 0" style="color: #e6a23c;">
                  拦截脏数据 {{ record.skipped }} 条
                </p>
                <p v-if="record.duplicates > 0" style="color: #909399;">
                  内存去重 {{ record.duplicates }} 条
                </p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, Document, InfoFilled, Clock, Download } from '@element-plus/icons-vue'
import { uploadKnowledge, generateFaultTree, generateAndDownloadFaultTree } from '@/api'

const router = useRouter()
const jsonInput = ref('')
const uploading = ref(false)
const uploadHistory = ref([])
const topEventInput = ref('登机梯无法展开')
const generatedTreeData = ref(null)  // 存储生成的故障树数据

const validateAndUpload = async () => {
  if (!jsonInput.value.trim()) {
    ElMessage.warning('请输入 JSON 数据')
    return
  }

  let triplets
  try {
    triplets = JSON.parse(jsonInput.value)
    if (Array.isArray(triplets)) {
      // 直接数组格式
    } else if (triplets.triplets && Array.isArray(triplets.triplets)) {
      triplets = triplets.triplets
    } else {
      throw new Error('JSON 必须是三元组数组格式')
    }
  } catch (error) {
    ElMessage.error(`JSON 格式错误：${error.message}`)
    return
  }

  uploading.value = true

  try {
    // 步骤 1: 上传三元组到知识图谱
    const uploadResponse = await uploadKnowledge(triplets)

    ElMessage.success({
      message: `✅ 三元组入库成功！有效入库 ${uploadResponse.inserted || triplets.length} 条`,
      duration: 2000
    })

    // 步骤 2: 自动生成故障树
    if (topEventInput.value) {
      ElMessage.info(`🌲 正在生成故障树（顶事件：${topEventInput.value}）...`)

      try {
        const treeResponse = await generateFaultTree(topEventInput.value, true)

        ElMessage.success('✅ 故障树生成成功！')

        // 存储生成的故障树数据
        if (treeResponse.data) {
          generatedTreeData.value = treeResponse.data
          sessionStorage.setItem('generatedFaultTree', JSON.stringify(treeResponse.data))
          sessionStorage.setItem('topEventName', topEventInput.value)

          // 显示下载选项
          ElMessage({
            message: '故障树已生成！您可以下载 JSON 文件查看结果',
            type: 'success',
            duration: 5000,
            showClose: true
          })
        }

      } catch (treeError) {
        console.error('故障树生成失败:', treeError)
        ElMessage.warning({
          message: `三元组已入库，但故障树生成失败：${treeError.response?.data?.detail || treeError.message}`,
          duration: 5000
        })
      }
    }

    // 添加到历史记录
    uploadHistory.value.unshift({
      time: new Date().toLocaleString(),
      topEvent: topEventInput.value,
      inserted: uploadResponse.inserted || triplets.length,
      skipped: uploadResponse.skipped || 0,
      duplicates: uploadResponse.duplicates || 0,
      status: 'success',
      treeGenerated: !!generatedTreeData.value
    })

    jsonInput.value = ''

  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(`❌ 操作失败：${error.response?.data?.detail || error.message}`)

    uploadHistory.value.unshift({
      time: new Date().toLocaleString(),
      topEvent: topEventInput.value,
      inserted: 0,
      skipped: 0,
      duplicates: 0,
      status: 'failed',
      treeGenerated: false
    })
  } finally {
    uploading.value = false
  }
}

// 新增：下载故障树 JSON 文件
const downloadFaultTree = async () => {
  if (!topEventInput.value) {
    ElMessage.warning('请先输入顶事件名称')
    return
  }

  try {
    ElMessage.info('正在生成并下载故障树 JSON...')

    // 创建下载链接
    const downloadUrl = generateAndDownloadFaultTree(topEventInput.value)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `fault_tree_${topEventInput.value}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('✅ 下载已开始！')

  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error(`下载失败：${error.message}`)
  }
}

// 新增：查看生成的 JSON（在新窗口打开）
const viewGeneratedJSON = () => {
  if (!generatedTreeData.value) {
    ElMessage.warning('暂无生成的故障树数据')
    return
  }

  // 在新窗口显示 JSON
  const jsonWindow = window.open('_blank')
  jsonWindow.document.write('<pre style="font-family: monospace; background: #f5f5f5; padding: 20px;">')
  jsonWindow.document.write(JSON.stringify(generatedTreeData.value, null, 2))
  jsonWindow.document.write('</pre>')
  jsonWindow.document.title = '故障树 JSON 预览'
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

.upload-card,
.example-card,
.history-card {
  border-radius: 8px;
}

:deep(.el-timeline-item__node) {
  font-size: 13px;
}
</style>
