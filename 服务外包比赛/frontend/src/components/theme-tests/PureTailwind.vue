<template>
  <div class="h-full flex flex-col bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
    <header class="h-16 px-6 flex items-center justify-between border-b border-white/10 bg-white/5 backdrop-blur-xl">
      <div class="flex items-center gap-3">
        <div class="relative">
          <div class="absolute -inset-1 bg-gradient-to-r from-cyan-400 to-purple-600 blur-xl opacity-35 animate-pulse"></div>
          <div class="relative w-10 h-10 rounded-xl bg-gradient-to-r from-cyan-400 to-purple-500 flex items-center justify-center shadow-lg shadow-cyan-500/10">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="white">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
        </div>
        <div class="leading-tight">
          <div class="text-[15px] font-bold text-white tracking-wide">故障树生成工作台</div>
          <div class="text-xs text-white/60">纯 Tailwind + 手写组件（高自由度/精细交互）</div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button class="group relative px-3.5 py-2 rounded-xl bg-emerald-500/20 border border-emerald-400/30 text-emerald-100 hover:bg-emerald-500/30 transition" @click="handleAddNode">
          <span class="relative flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            新增节点
          </span>
        </button>
        <button class="group relative px-3.5 py-2 rounded-xl bg-rose-500/20 border border-rose-400/30 text-rose-100 hover:bg-rose-500/30 transition disabled:opacity-40" :disabled="!selectedNodeId" @click="handleDeleteSelected">
          <span class="relative flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
            删除选中
          </span>
        </button>
        <button class="group relative px-3.5 py-2 rounded-xl bg-sky-500/20 border border-sky-400/30 text-sky-100 hover:bg-sky-500/30 transition">
          <span class="relative flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            导出
          </span>
        </button>
      </div>
    </header>

    <div class="flex-1 min-h-0 p-4 flex gap-4">
      <aside class="w-72 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl overflow-hidden flex flex-col min-h-0">
        <div class="px-4 py-3 flex items-center justify-between border-b border-white/10">
          <div class="text-sm font-semibold text-white/90 flex items-center gap-2">
            <span class="text-yellow-300">📚</span> 历史记录
          </div>
          <button class="text-xs text-white/60 hover:text-white/85 transition">清空</button>
        </div>
        <div class="flex-1 min-h-0 overflow-auto p-3 space-y-3">
          <div
            v-for="item in histories"
            :key="item.id"
            class="rounded-xl border px-3 py-2.5 cursor-pointer transition group"
            :class="item.id === selectedHistoryId ? 'border-cyan-400/30 bg-cyan-400/10' : 'border-white/10 bg-white/5 hover:bg-white/10'"
            @click="selectedHistoryId = item.id"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="text-sm font-medium text-white truncate">{{ item.title }}</div>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-400/10 border border-emerald-400/20 text-emerald-200">
                {{ item.status }}
              </span>
            </div>
            <div class="mt-2 flex items-center justify-between">
              <div class="text-xs text-white/55">{{ item.time }}</div>
              <button class="text-xs text-rose-200/80 hover:text-rose-200 transition" @click.stop="handleDeleteHistory(item.id)">删除</button>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 min-w-0 min-h-0 flex flex-col gap-3">
        <div class="rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl px-3 py-2 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <button class="px-3 py-1.5 rounded-xl bg-white/10 border border-white/15 text-white/85 hover:bg-white/15 transition" @click="handleAddNode">新增</button>
            <button class="px-3 py-1.5 rounded-xl bg-white/10 border border-white/15 text-white/85 hover:bg-white/15 transition disabled:opacity-40" :disabled="!selectedNodeId" @click="handleDeleteSelected">删除</button>
            <button
              class="px-3 py-1.5 rounded-xl border transition"
              :class="connectMode ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-white/10 border-white/15 text-white/80 hover:bg-white/15'"
              @click="connectMode = !connectMode"
            >
              连接：{{ connectMode ? '开' : '关' }}
            </button>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-3 py-1.5 rounded-xl bg-white/10 border border-white/15 text-white/85 hover:bg-white/15 transition">AI</button>
            <span class="text-xs text-white/55">拖拽调整节点</span>
          </div>
        </div>

        <div class="flex-1 min-h-0 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl overflow-hidden">
          <div ref="canvasRef" class="relative h-full w-full" :class="connectMode ? 'ring-2 ring-cyan-400/25' : ''" @click="selectedNodeId = null">
            <div class="absolute inset-0 bg-[radial-gradient(#94a3b8_1px,transparent_1px)] [background-size:18px_18px] opacity-20"></div>
            <svg class="absolute inset-0 pointer-events-none" :width="canvasSize.width" :height="canvasSize.height">
              <line
                v-for="edge in edges"
                :key="edge.id"
                :x1="getNodeCenter(edge.source).x"
                :y1="getNodeCenter(edge.source).yBottom"
                :x2="getNodeCenter(edge.target).x"
                :y2="getNodeCenter(edge.target).yTop"
                class="stroke-white/35"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>

            <div
              v-for="node in nodes"
              :key="node.id"
              class="absolute w-[220px] h-[86px] rounded-2xl border shadow-xl select-none cursor-grab active:cursor-grabbing p-3 transition"
              :class="[
                node.id === selectedNodeId ? 'ring-2 ring-cyan-400/30 -translate-y-0.5' : '',
                node.type === 'top' ? 'border-rose-400/25 bg-rose-500/10' : '',
                node.type === 'middle' ? 'border-sky-400/25 bg-sky-500/10' : '',
                node.type === 'basic' ? 'border-emerald-400/25 bg-emerald-500/10' : ''
              ]"
              :style="{ left: node.x + 'px', top: node.y + 'px' }"
              @mousedown="handleNodeMouseDown(node, $event)"
              @click.stop="selectedNodeId = node.id"
            >
              <div class="flex items-center justify-between text-xs text-white/60">
                <div class="font-semibold text-white/80">{{ nodeTypeText(node.type) }}</div>
                <div class="px-2 py-0.5 rounded-full bg-white/5 border border-white/10 font-semibold text-white/80">{{ node.gate }}</div>
              </div>
              <div class="mt-1 text-sm font-semibold text-white truncate">{{ node.label }}</div>
              <div class="mt-1 text-xs text-white/55">ID：{{ node.id }}</div>
            </div>
          </div>
        </div>
      </main>

      <aside class="w-80 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl shadow-2xl overflow-hidden flex flex-col min-h-0">
        <div class="px-4 py-3 flex items-center justify-between border-b border-white/10">
          <div class="text-sm font-semibold text-white/90">节点信息</div>
          <button class="text-xs text-white/60 hover:text-white/85 transition disabled:opacity-40" :disabled="!selectedNodeId" @click="selectedNodeId = null">关闭</button>
        </div>
        <div v-if="selectedNodeId" class="p-4 overflow-auto space-y-3">
          <div class="space-y-1.5">
            <div class="text-xs text-white/60">节点名称</div>
            <input v-model="nodeForm.label" class="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/35 focus:outline-none focus:ring-2 focus:ring-cyan-400/20" />
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-white/60">节点 ID</div>
            <input v-model="nodeForm.id" disabled class="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white/60" />
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-white/60">事件类型</div>
            <select v-model="nodeForm.type" class="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/20">
              <option value="top">顶事件</option>
              <option value="middle">中间事件</option>
              <option value="basic">基本事件</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-white/60">逻辑门</div>
            <div class="grid grid-cols-2 gap-2">
              <button
                class="px-3 py-2 rounded-xl border transition"
                :class="nodeForm.gate === 'AND' ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-white/5 border-white/10 text-white/70 hover:bg-white/10'"
                @click="nodeForm.gate = 'AND'"
              >
                AND
              </button>
              <button
                class="px-3 py-2 rounded-xl border transition"
                :class="nodeForm.gate === 'OR' ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-white/5 border-white/10 text-white/70 hover:bg-white/10'"
                @click="nodeForm.gate = 'OR'"
              >
                OR
              </button>
            </div>
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-white/60">概率</div>
            <input v-model.number="nodeForm.probability" type="number" step="0.001" min="0" max="1" class="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/20" />
          </div>
          <button class="w-full px-3 py-2 rounded-xl bg-rose-500/20 border border-rose-400/30 text-rose-100 hover:bg-rose-500/30 transition" @click="handleDeleteSelected">删除节点</button>
        </div>
        <div v-else class="p-4 text-sm text-white/55">选择画布中的节点以编辑属性</div>
      </aside>
    </div>

    <footer class="p-4 border-t border-white/10 bg-white/5 backdrop-blur-xl">
      <div class="flex items-start gap-3">
        <textarea v-model="inputText" rows="3" class="flex-1 min-w-0 px-4 py-3 rounded-2xl bg-white/5 border border-white/10 text-white placeholder-white/35 focus:outline-none focus:ring-2 focus:ring-cyan-400/20" placeholder="上传文本 → 抽取 → 生成 → 人工调整 → 导出"></textarea>
        <label class="group px-3.5 py-2 rounded-xl bg-white/10 border border-white/15 text-white/85 hover:bg-white/15 transition cursor-pointer flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
          </svg>
          上传 .txt
          <input type="file" class="hidden" @change="handleNativeFileChange" />
        </label>
        <button class="group px-3.5 py-2 rounded-xl bg-cyan-500/25 border border-cyan-400/30 text-cyan-100 hover:bg-cyan-500/35 transition flex items-center gap-2">
          <svg class="w-5 h-5 group-hover:rotate-45 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
          生成
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

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

const handleNativeFileChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  inputText.value = `已选择文件：${file.name}\n\n` + inputText.value
}
</script>

<style scoped>
</style>
