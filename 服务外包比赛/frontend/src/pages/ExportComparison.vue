<template>
  <div class="export-test-container">
    <!-- 标题 -->
    <div class="header">
      <h1>故障树导出方案对比测试</h1>
      <p>对比不同导出方案的清晰度、性能和文件大小</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="control-group">
        <label>选择导出方案：</label>
        <select v-model="selectedScheme" class="select-input">
          <option value="scheme1">方案一：html2canvas + jsPDF（前端）</option>
          <option value="scheme2">方案二：Puppeteer + Sharp（后端）</option>
          <option value="scheme3">方案三：SVG原生导出</option>
        </select>
      </div>

      <div class="control-group">
        <label>导出质量：</label>
        <select v-model="selectedQuality" class="select-input">
          <option value="fast">快速（1x）</option>
          <option value="standard">标准（2x）</option>
          <option value="high">高质量（3x）</option>
          <option value="ultra">超高质量（4x）</option>
        </select>
      </div>

      <div class="control-group">
        <label>导出格式：</label>
        <div class="format-buttons">
          <button
            v-for="fmt in availableFormats"
            :key="fmt"
            :class="['format-btn', { active: selectedFormat === fmt }]"
            @click="selectedFormat = fmt"
          >
            {{ fmt.toUpperCase() }}
          </button>
        </div>
      </div>

      <div class="button-group">
        <button class="btn btn-primary" @click="handleExport" :disabled="isExporting">
          {{ isExporting ? '导出中...' : '开始导出' }}
        </button>
        <button class="btn btn-secondary" @click="clearResults">清空结果</button>
      </div>
    </div>

    <!-- 进度和消息 -->
    <div v-if="exportMessage" :class="['message', exportSuccess ? 'success' : 'error']">
      {{ exportMessage }}
    </div>

    <!-- 结果对比 -->
    <div v-if="results.length > 0" class="results-container">
      <h2>导出结果对比</h2>
      
      <div class="results-grid">
        <div v-for="(result, index) in results" :key="index" class="result-card">
          <div class="result-header">
            <h3>{{ result.scheme }}</h3>
            <span class="result-time">{{ result.time }}ms</span>
          </div>

          <div class="result-preview">
            <img v-if="result.preview" :src="result.preview" :alt="`Preview ${index}`" />
            <div v-else class="no-preview">无预览</div>
          </div>

          <div class="result-stats">
            <div class="stat-item">
              <span class="stat-label">文件大小：</span>
              <span class="stat-value">{{ formatFileSize(result.fileSize) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">分辨率：</span>
              <span class="stat-value">{{ result.resolution }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">清晰度评分：</span>
              <span class="stat-value">{{ result.quality }}/10</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">格式：</span>
              <span class="stat-value">{{ result.format }}</span>
            </div>
          </div>

          <div class="result-actions">
            <button class="btn-small" @click="downloadResult(result)">下载</button>
            <button class="btn-small" @click="viewDetails(result)">详情</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细对比表格 -->
    <div v-if="results.length > 0" class="comparison-table">
      <h2>详细对比</h2>
      <table>
        <thead>
          <tr>
            <th>方案</th>
            <th>导出时间</th>
            <th>文件大小</th>
            <th>分辨率</th>
            <th>清晰度</th>
            <th>格式</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(result, index) in results" :key="index">
            <td>{{ result.scheme }}</td>
            <td>{{ result.time }}ms</td>
            <td>{{ formatFileSize(result.fileSize) }}</td>
            <td>{{ result.resolution }}</td>
            <td>
              <div class="quality-bar">
                <div class="quality-fill" :style="{ width: result.quality * 10 + '%' }"></div>
              </div>
              {{ result.quality }}/10
            </td>
            <td>{{ result.format }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 建议 -->
    <div v-if="results.length > 0" class="recommendations">
      <h2>推荐方案</h2>
      <div class="recommendation-cards">
        <div class="rec-card">
          <h4>快速预览</h4>
          <p>推荐使用 <strong>方案一</strong>（html2canvas）</p>
          <p class="reason">无需后端，快速集成，适合实时预览</p>
        </div>
        <div class="rec-card">
          <h4>生产环境</h4>
          <p>推荐使用 <strong>方案二</strong>（Puppeteer）</p>
          <p class="reason">高保真渲染，支持任意DPI，最高清晰度</p>
        </div>
        <div class="rec-card">
          <h4>矢量需求</h4>
          <p>推荐使用 <strong>方案三</strong>（SVG原生）</p>
          <p class="reason">保留矢量信息，文件小，可无限缩放</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const selectedScheme = ref('scheme1')
const selectedQuality = ref('standard')
const selectedFormat = ref('png')
const isExporting = ref(false)
const exportMessage = ref('')
const exportSuccess = ref(false)
const results = ref([])

const availableFormats = computed(() => {
  if (selectedScheme.value === 'scheme3') {
    return ['svg', 'pdf', 'png', 'jpg']
  }
  return ['png', 'jpg', 'pdf', 'json']
})

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const handleExport = async () => {
  isExporting.value = true
  exportMessage.value = '导出中...'
  exportSuccess.value = false

  try {
    const startTime = performance.now()
    
    let result = {
      scheme: selectedScheme.value,
      format: selectedFormat.value,
      quality: selectedQuality.value,
      time: 0,
      fileSize: 0,
      resolution: '1200x800',
      qualityScore: 8,
      preview: null,
      data: null
    }

    // 模拟导出
    await new Promise(resolve => setTimeout(resolve, 500))
    
    result.time = Math.round(performance.now() - startTime)
    result.fileSize = Math.random() * 5000000
    result.qualityScore = Math.min(10, 6 + Math.random() * 4)
    
    results.value.push(result)

    exportMessage.value = `${result.scheme} 导出成功！耗时 ${result.time}ms`
    exportSuccess.value = true
  } catch (error) {
    exportMessage.value = `导出失败: ${error.message}`
    exportSuccess.value = false
  } finally {
    isExporting.value = false
  }
}

const downloadResult = (result) => {
  alert(`下载: ${result.scheme} - ${result.format}`)
}

const viewDetails = (result) => {
  alert(`方案: ${result.scheme}\n时间: ${result.time}ms\n大小: ${formatFileSize(result.fileSize)}\n清晰度: ${result.qualityScore}/10`)
}

const clearResults = () => {
  results.value = []
  exportMessage.value = ''
}
</script>

<style scoped>
.export-test-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.header p {
  font-size: 16px;
  color: #64748b;
}

.control-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.control-group {
  margin-bottom: 16px;
}

.control-group label {
  display: block;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 8px;
}

.select-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #0f172a;
}

.format-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.format-btn {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.format-btn.active {
  background: #22d3ee;
  color: white;
  border-color: #22d3ee;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #22d3ee;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #06b6d4;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  font-weight: 500;
}

.message.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.message.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.results-container {
  margin-bottom: 40px;
}

.results-container h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 20px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.result-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.result-header {
  padding: 16px;
  background: #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.result-time {
  font-size: 14px;
  color: #64748b;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
}

.result-preview {
  width: 100%;
  height: 200px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-preview {
  color: #94a3b8;
}

.result-stats {
  padding: 16px;
  border-top: 1px solid #e2e8f0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.stat-label {
  color: #64748b;
  font-weight: 500;
}

.stat-value {
  color: #0f172a;
  font-weight: 600;
}

.result-actions {
  padding: 12px 16px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 8px;
}

.btn-small {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #0f172a;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn-small:hover {
  background: #f1f5f9;
}

.comparison-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.comparison-table h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  padding: 24px 24px 0;
  margin: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f1f5f9;
}

th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #0f172a;
  font-size: 14px;
  border-bottom: 1px solid #e2e8f0;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  font-size: 14px;
  color: #475569;
}

.quality-bar {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.quality-fill {
  height: 100%;
  background: linear-gradient(90deg, #22d3ee, #06b6d4);
}

.recommendations {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.recommendations h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 20px;
}

.recommendation-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.rec-card {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
}

.rec-card h4 {
  font-size: 16px;
  font-weight: 600;
  color: #0369a1;
  margin: 0 0 8px 0;
}

.rec-card p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #0f172a;
}

.rec-card strong {
  color: #0369a1;
}

.reason {
  color: #64748b;
  font-size: 13px;
}
</style>
