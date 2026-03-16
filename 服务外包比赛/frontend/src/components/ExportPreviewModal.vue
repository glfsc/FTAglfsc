<script setup lang="ts">
import { ref, computed } from 'vue'
import { FileType, FileImage, FileJson, FileText, X, CheckCircle2, AlertCircle, Clock, Save } from 'lucide-vue-next'

const props = defineProps<{
  visible: boolean
  nodesCount: number
  edgesCount: number
  validationErrors: string[]
}>()

const emit = defineEmits(['close', 'confirm'])

const exportConfig = ref({
  format: 'pdf',
  resolution: '4k',
  margin: 20,
  colorMode: 'color',
  paperSize: 'A4',
  orientation: 'landscape'
})

const estimatedTime = computed(() => {
  const baseTime = 0.5
  const nodeFactor = props.nodesCount * 0.002
  return (baseTime + nodeFactor).toFixed(1)
})

const estimatedSize = computed(() => {
  if (exportConfig.value.format === 'json') return '< 100 KB'
  if (exportConfig.value.format === 'docx') return '1.2 MB'
  const base = props.nodesCount * 1.5
  return (base > 1024 ? (base / 1024).toFixed(1) + ' MB' : base.toFixed(0) + ' KB')
})

const handleConfirm = () => {
  emit('confirm', exportConfig.value)
}
</script>

<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <div class="header-title">
          <Save class="w-5 h-5 text-indigo-600" />
          <span>导出预览与配置</span>
        </div>
        <button @click="$emit('close')" class="close-btn">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="modal-body">
        <!-- Validation Status -->
        <div class="section validation-section" :class="{ 'has-errors': validationErrors.length > 0 }">
          <div class="section-title">
            <CheckCircle2 v-if="validationErrors.length === 0" class="w-4 h-4 text-green-500" />
            <AlertCircle v-else class="w-4 h-4 text-red-500" />
            <span>完整性校验结果</span>
          </div>
          <div v-if="validationErrors.length === 0" class="success-msg">
            所有校验通过，故障树结构完整。
          </div>
          <ul v-else class="error-list">
            <li v-for="(err, i) in validationErrors" :key="i">{{ err }}</li>
          </ul>
        </div>

        <!-- Export Configuration -->
        <div class="section config-section">
          <div class="section-title">导出选项</div>
          <div class="config-grid">
            <div class="config-item">
              <label>导出格式</label>
              <select v-model="exportConfig.format">
                <option value="pdf">PDF Document</option>
                <option value="png">PNG Image</option>
                <option value="svg">SVG Vector</option>
                <option value="docx">Word Document</option>
                <option value="json">JSON Data</option>
              </select>
            </div>

            <template v-if="exportConfig.format === 'pdf'">
              <div class="config-item">
                <label>纸张大小</label>
                <select v-model="exportConfig.paperSize">
                  <option value="A0">A0</option>
                  <option value="A1">A1</option>
                  <option value="A2">A2</option>
                  <option value="A3">A3</option>
                  <option value="A4">A4</option>
                </select>
              </div>
              <div class="config-item">
                <label>方向</label>
                <select v-model="exportConfig.orientation">
                  <option value="portrait">纵向 (Portrait)</option>
                  <option value="landscape">横向 (Landscape)</option>
                </select>
              </div>
            </template>

            <template v-if="exportConfig.format === 'png'">
              <div class="config-item">
                <label>分辨率</label>
                <select v-model="exportConfig.resolution">
                  <option value="720p">720p (Standard)</option>
                  <option value="1080p">1080p (HD)</option>
                  <option value="4k">4K (Ultra HD)</option>
                </select>
              </div>
            </template>

            <div class="config-item">
              <label>页边距 (px)</label>
              <input type="number" v-model="exportConfig.margin" min="0" max="100" />
            </div>

            <div class="config-item">
              <label>颜色模式</label>
              <select v-model="exportConfig.colorMode">
                <option value="color">彩色 (Color)</option>
                <option value="grayscale">灰度 (Grayscale)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="section summary-section">
          <div class="summary-item">
            <Clock class="w-4 h-4 text-gray-400" />
            <span>预计耗时: <strong>{{ estimatedTime }}s</strong></span>
          </div>
          <div class="summary-item">
            <FileType class="w-4 h-4 text-gray-400" />
            <span>预计文件大小: <strong>{{ estimatedSize }}</strong></span>
          </div>
          <div class="summary-item">
            <span class="text-xs text-gray-400">节点: {{ nodesCount }} | 连线: {{ edgesCount }}</span>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="cancel-btn">取消</button>
        <button 
          @click="handleConfirm" 
          class="confirm-btn"
          :disabled="validationErrors.length > 0 && exportConfig.format !== 'json'"
        >
          确认导出
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  width: 500px;
  max-width: 90vw;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 16px;
  color: #111827;
}

.close-btn {
  color: #9ca3af;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #4b5563;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: 70vh;
}

.section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.validation-section {
  padding: 12px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
}

.validation-section.has-errors {
  background: #fef2f2;
  border-color: #fecaca;
}

.success-msg {
  font-size: 13px;
  color: #166534;
}

.error-list {
  margin: 0;
  padding-left: 20px;
  font-size: 12px;
  color: #991b1b;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-item label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
}

.config-item select, .config-item input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #1f2937;
  outline: none;
}

.config-item select:focus, .config-item input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.summary-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4b5563;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  background: white;
  border: 1px solid #d1d5db;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #f9fafb;
}

.confirm-btn {
  padding: 8px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  background: #6366f1;
  border: none;
  transition: all 0.2s;
}

.confirm-btn:hover:not(:disabled) {
  background: #4f46e5;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
