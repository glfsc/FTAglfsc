<template>
  <div class="h-full flex flex-col bg-slate-50">
    <header class="h-16 px-6 flex items-center justify-between bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-500 text-white shadow-lg">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-white/15 border border-white/20 flex items-center justify-center backdrop-blur">
          <el-icon :size="22"><Platform /></el-icon>
        </div>
        <div class="leading-tight">
          <div class="text-[15px] font-bold tracking-wide">故障树生成工作台</div>
          <div class="text-xs text-white/80">Element Plus + Tailwind（布局/动效/一致性）</div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <el-tag type="success" effect="dark" class="!border-white/20 !bg-white/15 !text-white">在线</el-tag>
        <el-button-group>
          <el-button type="primary" :icon="Plus" class="!bg-white !text-slate-900 !border-white hover:!bg-white/90" @click="handleAddNode">新增节点</el-button>
          <el-button type="danger" :icon="Delete" class="hover:-translate-y-0.5 transition" :disabled="!selectedNodeId" @click="handleDeleteSelected">删除选中</el-button>
          <el-dropdown>
            <el-button type="success" :icon="Download" class="hover:-translate-y-0.5 transition">导出</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>导出 PNG</el-dropdown-item>
                <el-dropdown-item>导出 PDF</el-dropdown-item>
                <el-dropdown-item>导出 JSON</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>
      </div>
    </header>

    <div class="flex-1 min-h-0 p-4 flex gap-4">
      <aside class="w-72 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col min-h-0">
        <div class="px-4 py-3 flex items-center justify-between border-b border-slate-100">
          <div class="text-sm font-semibold text-slate-800">历史记录</div>
          <el-button text size="small">清空</el-button>
        </div>
        <el-scrollbar class="flex-1">
          <div class="p-3 space-y-3">
            <div
              v-for="item in histories"
              :key="item.id"
              class="rounded-xl border px-3 py-2.5 cursor-pointer transition"
              :class="item.id === selectedHistoryId ? 'border-indigo-300 bg-indigo-50' : 'border-slate-200 bg-white hover:bg-slate-50'"
              @click="selectedHistoryId = item.id"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="text-sm font-medium text-slate-900 truncate">{{ item.title }}</div>
                <el-tag size="small" type="success" effect="plain">{{ item.status }}</el-tag>
              </div>
              <div class="mt-2 flex items-center justify-between">
                <div class="text-xs text-slate-500">{{ item.time }}</div>
                <el-button text type="danger" size="small" @click.stop="handleDeleteHistory(item.id)">删除</el-button>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </aside>

      <main class="flex-1 min-w-0 flex flex-col gap-3 min-h-0">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm px-3 py-2 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <el-button size="small" :icon="Plus" class="hover:-translate-y-0.5 transition" @click="handleAddNode">新增节点</el-button>
            <el-button size="small" :icon="Delete" class="hover:-translate-y-0.5 transition" :disabled="!selectedNodeId" @click="handleDeleteSelected">删除选中</el-button>
            <el-button size="small" :icon="Connection" :type="connectMode ? 'primary' : 'default'" class="hover:-translate-y-0.5 transition" @click="connectMode = !connectMode">
              连接模式：{{ connectMode ? '开' : '关' }}
            </el-button>
          </div>
          <div class="flex items-center gap-2">
            <el-button size="small" :icon="MagicStick" class="hover:-translate-y-0.5 transition">AI</el-button>
            <el-tag type="info" effect="plain">画布可拖拽</el-tag>
          </div>
        </div>

        <div class="flex-1 min-h-0 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div ref="canvasRef" class="relative h-full w-full" :class="connectMode ? 'ring-2 ring-indigo-400/40' : ''" @click="selectedNodeId = null">
            <div class="absolute inset-0 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:18px_18px] opacity-60"></div>
            <svg class="absolute inset-0 pointer-events-none" :width="canvasSize.width" :height="canvasSize.height">
              <line
                v-for="edge in edges"
                :key="edge.id"
                :x1="getNodeCenter(edge.source).x"
                :y1="getNodeCenter(edge.source).yBottom"
                :x2="getNodeCenter(edge.target).x"
                :y2="getNodeCenter(edge.target).yTop"
                class="stroke-slate-400/80"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>

            <div
              v-for="node in nodes"
              :key="node.id"
              class="absolute w-[220px] h-[86px] rounded-2xl border shadow-sm select-none cursor-grab active:cursor-grabbing p-3 transition"
              :class="[
                node.id === selectedNodeId ? 'ring-2 ring-indigo-500/35 -translate-y-0.5' : '',
                node.type === 'top' ? 'border-rose-200 bg-rose-50' : '',
                node.type === 'middle' ? 'border-sky-200 bg-sky-50' : '',
                node.type === 'basic' ? 'border-emerald-200 bg-emerald-50' : ''
              ]"
              :style="{ left: node.x + 'px', top: node.y + 'px' }"
              @mousedown="handleNodeMouseDown(node, $event)"
              @click.stop="selectedNodeId = node.id"
            >
              <div class="flex items-center justify-between text-xs text-slate-600">
                <div class="font-semibold">{{ nodeTypeText(node.type) }}</div>
                <div class="px-2 py-0.5 rounded-full bg-white/60 border border-slate-200 font-semibold text-slate-700">{{ node.gate }}</div>
              </div>
              <div class="mt-1 text-sm font-semibold text-slate-900 truncate">{{ node.label }}</div>
              <div class="mt-1 text-xs text-slate-500">ID：{{ node.id }}</div>
            </div>
          </div>
        </div>
      </main>

      <aside class="w-80 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col min-h-0">
        <div class="px-4 py-3 flex items-center justify-between border-b border-slate-100">
          <div class="text-sm font-semibold text-slate-800">节点信息</div>
          <el-button text size="small" :disabled="!selectedNodeId" @click="selectedNodeId = null">关闭</el-button>
        </div>
        <div v-if="selectedNodeId" class="p-4 overflow-auto">
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
          <el-button type="danger" plain class="w-full mt-2" @click="handleDeleteSelected">删除节点</el-button>
        </div>
        <div v-else class="p-4 text-sm text-slate-500">选择画布中的节点以编辑属性</div>
      </aside>
    </div>

    <footer class="p-4 bg-white border-t border-slate-200">
      <div class="flex items-start gap-3">
        <div class="flex-1 min-w-0">
          <el-input v-model="inputText" type="textarea" :rows="3" resize="none" placeholder="上传或粘贴文本 → AI 抽取 → 生成故障树 → 手动校对" />
        </div>
        <div class="flex items-center gap-2">
          <el-upload action="#" :auto-upload="false" :show-file-list="false" @change="handleFileChange">
            <el-button :icon="Upload">上传 .txt</el-button>
          </el-upload>
          <el-button type="primary" :icon="Promotion" class="hover:-translate-y-0.5 transition">生成</el-button>
        </div>
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
</style>
