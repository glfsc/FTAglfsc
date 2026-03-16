<template>
  <div class="a-shell">
    <header class="a-header">
      <div class="a-brand">
        <el-icon :size="22"><Platform /></el-icon>
        <div class="a-title">
          <div class="a-title-main">故障树生成工作台</div>
          <div class="a-title-sub">Element Plus + 传统 CSS（工业/企业风格）</div>
        </div>
      </div>
      <div class="a-header-actions">
        <el-tag type="success" effect="light">在线</el-tag>
        <el-button-group>
          <el-button type="primary" :icon="Plus" @click="handleAddNode">新增节点</el-button>
          <el-button type="danger" :icon="Delete" :disabled="!selectedNodeId" @click="handleDeleteSelected">删除选中</el-button>
          <el-button type="success" :icon="Download">导出</el-button>
        </el-button-group>
      </div>
    </header>

    <div class="a-main">
      <aside class="a-left">
        <div class="a-panel-header">
          <div class="a-panel-title">历史记录</div>
          <el-button text size="small">清空</el-button>
        </div>
        <el-scrollbar class="a-scroll">
          <div class="a-history">
            <div
              v-for="item in histories"
              :key="item.id"
              class="a-history-item"
              :class="{ active: item.id === selectedHistoryId }"
              @click="selectedHistoryId = item.id"
            >
              <div class="a-history-top">
                <div class="a-history-name">{{ item.title }}</div>
                <el-tag size="small" type="success" effect="plain">{{ item.status }}</el-tag>
              </div>
              <div class="a-history-bottom">
                <div class="a-history-time">{{ item.time }}</div>
                <el-button text type="danger" size="small" @click.stop="handleDeleteHistory(item.id)">删除</el-button>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </aside>

      <main class="a-center">
        <div class="a-toolbar">
          <div class="a-toolbar-left">
            <el-button size="small" :icon="Plus" @click="handleAddNode">新增节点</el-button>
            <el-button size="small" :icon="Delete" :disabled="!selectedNodeId" @click="handleDeleteSelected">删除选中</el-button>
            <el-button size="small" :icon="Connection" :type="connectMode ? 'primary' : 'default'" @click="connectMode = !connectMode">
              连接模式：{{ connectMode ? '开' : '关' }}
            </el-button>
          </div>
          <div class="a-toolbar-right">
            <el-button size="small" :icon="MagicStick">AI</el-button>
            <el-dropdown>
              <el-button size="small" :icon="Download">导出</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>导出 PNG</el-dropdown-item>
                  <el-dropdown-item>导出 PDF</el-dropdown-item>
                  <el-dropdown-item>导出 JSON</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div class="a-canvas-wrap">
          <div ref="canvasRef" class="a-canvas" @click="selectedNodeId = null">
            <svg class="a-wires" :width="canvasSize.width" :height="canvasSize.height">
              <line
                v-for="edge in edges"
                :key="edge.id"
                :x1="getNodeCenter(edge.source).x"
                :y1="getNodeCenter(edge.source).yBottom"
                :x2="getNodeCenter(edge.target).x"
                :y2="getNodeCenter(edge.target).yTop"
                class="a-wire"
              />
            </svg>

            <div
              v-for="node in nodes"
              :key="node.id"
              class="a-node"
              :class="[node.type, { selected: node.id === selectedNodeId }]"
              :style="{ left: node.x + 'px', top: node.y + 'px' }"
              @mousedown="handleNodeMouseDown(node, $event)"
              @click.stop="selectedNodeId = node.id"
            >
              <div class="a-node-head">
                <div class="a-node-kind">{{ nodeTypeText(node.type) }}</div>
                <div class="a-node-gate">{{ node.gate }}</div>
              </div>
              <div class="a-node-label">{{ node.label }}</div>
              <div class="a-node-meta">ID：{{ node.id }}</div>
            </div>
          </div>
        </div>
      </main>

      <aside class="a-right">
        <div class="a-panel-header">
          <div class="a-panel-title">节点信息</div>
          <el-button text size="small" :disabled="!selectedNodeId" @click="selectedNodeId = null">关闭</el-button>
        </div>

        <div v-if="selectedNodeId" class="a-form">
          <el-form label-width="86px" size="small">
            <el-form-item label="节点名称">
              <el-input v-model="nodeForm.label" />
            </el-form-item>
            <el-form-item label="节点 ID">
              <el-input v-model="nodeForm.id" disabled />
            </el-form-item>
            <el-form-item label="事件类型">
              <el-select v-model="nodeForm.type" style="width: 100%">
                <el-option label="顶事件" value="top" />
                <el-option label="中间事件" value="middle" />
                <el-option label="基本事件" value="basic" />
              </el-select>
            </el-form-item>
            <el-form-item label="逻辑门">
              <el-radio-group v-model="nodeForm.gate">
                <el-radio-button label="AND" />
                <el-radio-button label="OR" />
              </el-radio-group>
            </el-form-item>
            <el-form-item label="概率">
              <el-input-number v-model="nodeForm.probability" :min="0" :max="1" :step="0.001" :precision="3" style="width: 100%" />
            </el-form-item>
          </el-form>

          <div class="a-danger">
            <el-button type="danger" plain style="width: 100%" @click="handleDeleteSelected">删除节点</el-button>
          </div>
        </div>

        <div v-else class="a-empty">
          选择画布中的节点以编辑属性
        </div>
      </aside>
    </div>

    <footer class="a-bottom">
      <div class="a-bottom-left">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          resize="none"
          placeholder="粘贴故障描述文本，或上传 .txt 文件后点击生成"
        />
      </div>
      <div class="a-bottom-right">
        <el-upload action="#" :auto-upload="false" :show-file-list="false" @change="handleFileChange">
          <el-button :icon="Upload">上传 .txt</el-button>
        </el-upload>
        <el-button type="primary" :icon="Promotion">生成</el-button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { Connection, Delete, Download, MagicStick, Platform, Plus, Promotion, Upload } from '@element-plus/icons-vue'

const histories = ref([
  { id: 'h-1', title: '空压机无法启动', time: '2026/03/16 09:12', status: 'done' },
  { id: 'h-2', title: '电机过热报警', time: '2026/03/15 16:33', status: 'done' },
  { id: 'h-3', title: '控制回路异常', time: '2026/03/14 11:08', status: 'done' }
])

const selectedHistoryId = ref(histories.value[0]?.id ?? '')
const connectMode = ref(false)
const inputText = ref('')

const canvasRef = ref(null)
const canvasSize = ref({ width: 1, height: 1 })

const nodeWidth = 220
const nodeHeight = 86

const nodes = ref([
  { id: 'N-1', label: '空压机无法启动', type: 'top', gate: 'OR', probability: 0.01, x: 360, y: 40 },
  { id: 'N-2', label: '控制系统故障', type: 'middle', gate: 'AND', probability: 0.02, x: 160, y: 170 },
  { id: 'N-3', label: '电源异常', type: 'middle', gate: 'OR', probability: 0.03, x: 360, y: 170 },
  { id: 'N-4', label: '机械卡阻', type: 'middle', gate: 'OR', probability: 0.01, x: 560, y: 170 },
  { id: 'N-5', label: 'PLC 通讯异常', type: 'basic', gate: 'OR', probability: 0.004, x: 80, y: 320 },
  { id: 'N-6', label: '压力传感器异常', type: 'basic', gate: 'OR', probability: 0.006, x: 240, y: 320 }
])

const edges = ref([
  { id: 'E-1', source: 'N-1', target: 'N-2' },
  { id: 'E-2', source: 'N-1', target: 'N-3' },
  { id: 'E-3', source: 'N-1', target: 'N-4' },
  { id: 'E-4', source: 'N-2', target: 'N-5' },
  { id: 'E-5', source: 'N-2', target: 'N-6' }
])

const selectedNodeId = ref('N-3')

const selectedNode = computed(() => nodes.value.find((n) => n.id === selectedNodeId.value) ?? null)

const nodeForm = reactive({
  id: '',
  label: '',
  type: 'middle',
  gate: 'AND',
  probability: 0.001
})

watch(selectedNodeId, () => {
  if (!selectedNode.value) {
    nodeForm.id = ''
    nodeForm.label = ''
    nodeForm.type = 'middle'
    nodeForm.gate = 'AND'
    nodeForm.probability = 0.001
    return
  }

  nodeForm.id = selectedNode.value.id
  nodeForm.label = selectedNode.value.label
  nodeForm.type = selectedNode.value.type
  nodeForm.gate = selectedNode.value.gate
  nodeForm.probability = selectedNode.value.probability
}, { immediate: true })

watch(nodeForm, () => {
  if (!selectedNode.value) return
  selectedNode.value.label = nodeForm.label
  selectedNode.value.type = nodeForm.type
  selectedNode.value.gate = nodeForm.gate
  selectedNode.value.probability = nodeForm.probability
}, { deep: true })

const nodeTypeText = (type) => {
  if (type === 'top') return '顶事件'
  if (type === 'middle') return '中间事件'
  return '基本事件'
}

const getNodeCenter = (nodeId) => {
  const node = nodes.value.find((n) => n.id === nodeId)
  if (!node) return { x: 0, yTop: 0, yBottom: 0 }
  return {
    x: node.x + nodeWidth / 2,
    yTop: node.y,
    yBottom: node.y + nodeHeight
  }
}

const updateCanvasSize = () => {
  if (!canvasRef.value) return
  canvasSize.value = {
    width: canvasRef.value.clientWidth,
    height: canvasRef.value.clientHeight
  }
}

onMounted(() => {
  updateCanvasSize()
  window.addEventListener('resize', updateCanvasSize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateCanvasSize)
  window.removeEventListener('mousemove', handleDragging)
  window.removeEventListener('mouseup', stopDragging)
})

const dragging = ref(null)

const handleNodeMouseDown = (node, event) => {
  if (!canvasRef.value) return
  selectedNodeId.value = node.id
  const rect = canvasRef.value.getBoundingClientRect()
  dragging.value = {
    id: node.id,
    offsetX: event.clientX - rect.left - node.x,
    offsetY: event.clientY - rect.top - node.y
  }
  window.addEventListener('mousemove', handleDragging)
  window.addEventListener('mouseup', stopDragging)
}

const handleDragging = (event) => {
  if (!dragging.value || !canvasRef.value) return
  const node = nodes.value.find((n) => n.id === dragging.value.id)
  if (!node) return
  const rect = canvasRef.value.getBoundingClientRect()
  const nextX = event.clientX - rect.left - dragging.value.offsetX
  const nextY = event.clientY - rect.top - dragging.value.offsetY
  node.x = Math.max(12, Math.min(nextX, rect.width - nodeWidth - 12))
  node.y = Math.max(12, Math.min(nextY, rect.height - nodeHeight - 12))
}

const stopDragging = () => {
  dragging.value = null
  window.removeEventListener('mousemove', handleDragging)
  window.removeEventListener('mouseup', stopDragging)
}

const handleAddNode = () => {
  const nextIndex = nodes.value.length + 1
  nodes.value.push({
    id: `N-${nextIndex}`,
    label: `新节点 ${nextIndex}`,
    type: 'basic',
    gate: 'OR',
    probability: 0.001,
    x: 80 + (nextIndex % 5) * 120,
    y: 420
  })
  selectedNodeId.value = `N-${nextIndex}`
}

const handleDeleteSelected = () => {
  if (!selectedNodeId.value) return
  const deleteId = selectedNodeId.value
  nodes.value = nodes.value.filter((n) => n.id !== deleteId)
  edges.value = edges.value.filter((e) => e.source !== deleteId && e.target !== deleteId)
  selectedNodeId.value = ''
}

const handleDeleteHistory = (id) => {
  histories.value = histories.value.filter((h) => h.id !== id)
  if (selectedHistoryId.value === id) selectedHistoryId.value = histories.value[0]?.id ?? ''
}

const handleFileChange = (file) => {
  inputText.value = `已选择文件：${file?.name ?? ''}\n\n` + inputText.value
}
</script>

<style scoped>
.a-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f6f8fb;
}

.a-header {
  height: 56px;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid #e6ebf2;
}

.a-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #1f2a37;
}

.a-title {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.a-title-main {
  font-size: 15px;
  font-weight: 700;
}

.a-title-sub {
  font-size: 12px;
  color: #6b7280;
}

.a-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.a-main {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 12px;
  padding: 12px;
}

.a-left,
.a-right {
  width: 300px;
  background: #ffffff;
  border: 1px solid #e6ebf2;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.a-center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.a-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 12px 10px;
  border-bottom: 1px solid #eef2f6;
}

.a-panel-title {
  font-weight: 700;
  font-size: 13px;
  color: #111827;
}

.a-scroll {
  flex: 1;
  min-height: 0;
}

.a-history {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.a-history-item {
  border: 1px solid #eef2f6;
  border-radius: 10px;
  padding: 10px 10px 8px;
  background: #fbfcfe;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.a-history-item:hover {
  background: #f7fbff;
  border-color: #dbeafe;
}

.a-history-item.active {
  border-color: #93c5fd;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.a-history-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.a-history-name {
  font-weight: 600;
  font-size: 13px;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.a-history-bottom {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.a-history-time {
  font-size: 12px;
  color: #6b7280;
}

.a-toolbar {
  background: #ffffff;
  border: 1px solid #e6ebf2;
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.a-toolbar-left,
.a-toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.a-canvas-wrap {
  flex: 1;
  min-height: 0;
  background: #ffffff;
  border: 1px solid #e6ebf2;
  border-radius: 10px;
  overflow: hidden;
}

.a-canvas {
  position: relative;
  height: 100%;
  width: 100%;
  background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
  background-size: 16px 16px;
  background-position: 0 0;
}

.a-wires {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.a-wire {
  stroke: #93a4b8;
  stroke-width: 2;
  stroke-linecap: round;
}

.a-node {
  position: absolute;
  width: 220px;
  height: 86px;
  border-radius: 10px;
  border: 1px solid #dbeafe;
  background: #ffffff;
  box-shadow: 0 10px 18px rgba(15, 23, 42, 0.06);
  cursor: grab;
  user-select: none;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
}

.a-node:active {
  cursor: grabbing;
}

.a-node.selected {
  border-color: #60a5fa;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25), 0 16px 24px rgba(15, 23, 42, 0.08);
  transform: translateY(-1px);
}

.a-node.top {
  border-color: #fecaca;
  background: #fff7f7;
}

.a-node.middle {
  border-color: #bfdbfe;
  background: #f4faff;
}

.a-node.basic {
  border-color: #bbf7d0;
  background: #f6fffa;
}

.a-node-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
}

.a-node-kind {
  font-weight: 700;
}

.a-node-gate {
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.6);
  background: rgba(248, 250, 252, 0.7);
  font-weight: 700;
  color: #334155;
}

.a-node-label {
  font-weight: 700;
  color: #0f172a;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.a-node-meta {
  font-size: 12px;
  color: #64748b;
}

.a-right {
  padding-bottom: 10px;
}

.a-form {
  padding: 10px 12px 0;
  overflow: auto;
}

.a-danger {
  padding: 0 12px 12px;
}

.a-empty {
  padding: 12px;
  color: #6b7280;
  font-size: 13px;
}

.a-bottom {
  display: flex;
  gap: 10px;
  padding: 12px;
  background: #ffffff;
  border-top: 1px solid #e6ebf2;
}

.a-bottom-left {
  flex: 1;
  min-width: 0;
}

.a-bottom-right {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
</style>
