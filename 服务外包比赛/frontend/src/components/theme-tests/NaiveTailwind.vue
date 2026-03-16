<template>
  <div
    class="c-root h-full flex flex-col transition-colors duration-[420ms]"
    :data-theme="theme"
    @keydown="handleKeydown"
  >
    <header class="c-glass h-16 px-6 flex items-center justify-between border-b transition-colors duration-[420ms]">
      <div class="flex items-center gap-3">
        <div class="relative">
          <div class="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-violet-600 blur-xl opacity-35"></div>
          <div class="relative w-10 h-10 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] flex items-center justify-center transition-colors duration-[420ms]">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" class="text-cyan-300">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
        </div>
        <div class="leading-tight">
          <div class="text-[15px] font-semibold text-[var(--c-text)] tracking-wide transition-colors duration-[420ms]">故障树生成工作台</div>
          <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">Naive 风格 + Tailwind（玻璃/主题/交互强化）</div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button class="px-3.5 py-2 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200" @click="toggleTheme">
          {{ theme === 'dark' ? '浅色模式' : '深色模式' }}
        </button>
        <button
          class="px-3.5 py-2 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200"
          @click="soundEnabled = !soundEnabled"
        >
          声音：{{ soundEnabled ? '开' : '关' }}
        </button>
        <button class="px-3.5 py-2 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200" @click="handleAddNode">
          新增节点
        </button>
        <button class="px-3.5 py-2 c-radius bg-rose-500/15 border border-rose-400/30 text-rose-200 hover:bg-rose-500/25 transition disabled:opacity-40" :disabled="!selectedNodeId && !selectedEdgeId" @click="handleDeleteSelected">
          删除选中
        </button>
        <button class="px-3.5 py-2 c-radius bg-emerald-500/15 border border-emerald-400/30 text-emerald-200 hover:bg-emerald-500/25 transition">
          导出
        </button>
      </div>
    </header>

    <div class="flex-1 min-h-0 p-4 flex gap-4">
      <aside class="w-72 c-panel c-glass shadow-2xl overflow-hidden flex flex-col min-h-0 transition-colors duration-[420ms]">
        <div class="px-4 py-3 flex items-center justify-between border-b border-[var(--c-border)] transition-colors duration-[420ms]">
          <div class="text-sm font-semibold text-[var(--c-text)] transition-colors duration-[420ms]">历史记录</div>
          <button class="text-xs text-[var(--c-text-muted)] hover:text-[var(--c-text)] transition duration-200">清空</button>
        </div>
        <div class="flex-1 min-h-0 overflow-auto p-3 space-y-3">
          <div
            v-for="item in histories"
            :key="item.id"
            class="c-radius border px-3 py-2.5 cursor-pointer transition duration-200"
            :class="item.id === selectedHistoryId ? 'border-cyan-400/30 bg-cyan-400/10' : 'border-[var(--c-border)] bg-[var(--c-surface-2)] hover:bg-[var(--c-surface-3)]'"
            @click="selectedHistoryId = item.id"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="text-sm font-medium text-[var(--c-text)] truncate transition-colors duration-[420ms]">{{ item.title }}</div>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-400/10 border border-emerald-400/20 text-emerald-200">
                {{ item.status }}
              </span>
            </div>
            <div class="mt-2 flex items-center justify-between">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">{{ item.time }}</div>
              <button class="text-xs text-rose-200/80 hover:text-rose-200 transition" @click.stop="handleDeleteHistory(item.id)">删除</button>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 min-w-0 min-h-0 flex flex-col gap-3">
        <div class="c-panel c-glass shadow-2xl px-3 py-2 flex items-center justify-between transition-colors duration-[420ms]">
          <div class="flex items-center gap-2">
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200" @click="handleAddNode">新增</button>
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 disabled:opacity-40" :disabled="!selectedNodeId && !selectedEdgeId" @click="handleDeleteSelected">删除</button>
            <button
              class="px-3 py-1.5 c-radius border transition duration-200"
              :class="connectMode ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-[var(--c-surface-2)] border-[var(--c-border)] text-[var(--c-text-muted)] hover:bg-[var(--c-surface-3)]'"
              @click="connectMode = !connectMode"
            >
              连接：{{ connectMode ? '开' : '关' }}
            </button>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200">AI</button>
            <span class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">Tab/方向键/Del 支持</span>
          </div>
        </div>

        <div class="flex-1 min-h-0 c-panel c-glass shadow-2xl overflow-hidden transition-colors duration-[420ms]">
          <div
            ref="canvasRef"
            class="relative h-full w-full outline-none"
            tabindex="0"
            :class="connectMode ? 'ring-2 ring-cyan-400/25' : ''"
            @click="handleCanvasClick"
            @mousemove="handleCanvasMouseMove"
            @mouseup="handleCanvasMouseUp"
          >
            <div class="absolute inset-0 c-grid opacity-30 transition-opacity duration-[420ms]"></div>
            <svg class="absolute inset-0" :width="canvasSize.width" :height="canvasSize.height">
              <defs>
                <filter id="c-edge-glow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              <g v-for="edge in edgeRenders" :key="edge.id">
                <path
                  :d="edge.path"
                  fill="none"
                  :stroke="edge.style.color"
                  :stroke-width="edge.style.width"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  :stroke-dasharray="edge.style.pattern === 'dashed' ? '8 8' : '0'"
                  :filter="edge.id === selectedEdgeId ? 'url(#c-edge-glow)' : 'none'"
                  class="cursor-pointer"
                  @click.stop="handleSelectEdge(edge.id)"
                />
                <path
                  :d="edge.path"
                  fill="none"
                  stroke="transparent"
                  stroke-width="14"
                  class="cursor-pointer"
                  @click.stop="handleSelectEdge(edge.id)"
                />
                <g v-if="edge.label">
                  <rect
                    :x="edge.labelPos.x - edge.labelBox.w / 2"
                    :y="edge.labelPos.y - edge.labelBox.h / 2"
                    :width="edge.labelBox.w"
                    :height="edge.labelBox.h"
                    rx="10"
                    :fill="'var(--c-surface-2)'"
                    :stroke="'var(--c-border)'"
                    fill-opacity="0.92"
                    stroke-width="1"
                  />
                  <text
                    :x="edge.labelPos.x"
                    :y="edge.labelPos.y + 4"
                    text-anchor="middle"
                    :fill="'var(--c-text)'"
                    class="select-none text-[12px]"
                  >
                    {{ edge.label }}
                  </text>
                </g>
              </g>

              <path
                v-if="connectDrag"
                :d="connectPreviewPath"
                fill="none"
                stroke="rgba(34, 211, 238, 0.9)"
                stroke-width="2"
                stroke-dasharray="6 6"
                stroke-linecap="round"
              />
            </svg>

            <div
              v-for="node in nodes"
              :key="node.id"
              class="c-node absolute w-[220px] h-[92px] border shadow-xl select-none cursor-grab active:cursor-grabbing p-3 transition duration-200"
              :class="[
                node.id === selectedNodeId ? 'is-selected' : '',
                node.type === 'top' ? 'border-rose-400/30 bg-rose-500/10' : '',
                node.type === 'middle' ? 'border-sky-400/30 bg-sky-500/10' : '',
                node.type === 'basic' ? 'border-emerald-400/30 bg-emerald-500/10' : ''
              ]"
              :style="{ left: node.x + 'px', top: node.y + 'px' }"
              @mousedown="handleNodeMouseDown(node, $event)"
              @click.stop="handleSelectNode(node.id)"
              :data-node-id="node.id"
            >
              <span class="c-node-pulse" v-if="node.id === selectedNodeId" :key="nodePulseKey" />
              <div class="flex items-center justify-between text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">
                <div class="font-semibold text-[var(--c-text)]/90 transition-colors duration-[420ms]">{{ nodeTypeText(node.type) }}</div>
                <div class="px-2 py-0.5 rounded-full bg-[var(--c-surface-2)]/70 border border-[var(--c-border)] font-semibold text-[var(--c-text)]/85 transition-colors duration-[420ms]">{{ node.gate }}</div>
              </div>
              <div class="mt-1 text-sm font-semibold text-[var(--c-text)] truncate transition-colors duration-[420ms]">{{ node.label }}</div>
              <div class="mt-1 text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">ID：{{ node.id }}</div>

              <button
                class="c-handle absolute -right-2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border border-cyan-300/40 bg-cyan-400/20 hover:bg-cyan-400/30 transition"
                title="拖拽创建连线"
                @mousedown.stop="handleStartConnect(node.id, $event)"
              />
            </div>
          </div>
        </div>
      </main>

      <aside class="w-80 c-panel c-glass shadow-2xl overflow-hidden flex flex-col min-h-0 transition-colors duration-[420ms]">
        <div class="px-4 py-3 flex items-center justify-between border-b border-[var(--c-border)] transition-colors duration-[420ms]">
          <div class="text-sm font-semibold text-[var(--c-text)] transition-colors duration-[420ms]">
            {{ selectedEdgeId ? '连线信息' : '节点信息' }}
          </div>
          <button class="text-xs text-[var(--c-text-muted)] hover:text-[var(--c-text)] transition duration-200 disabled:opacity-40" :disabled="!selectedNodeId && !selectedEdgeId" @click="clearSelection">关闭</button>
        </div>
        <div v-if="selectedEdgeId" class="p-4 overflow-auto space-y-3">
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">标签</div>
            <input v-model="edgeForm.label" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" placeholder="例如：因果/证据说明" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">颜色</div>
              <input v-model="edgeForm.color" type="color" class="w-full h-10 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)]" />
            </div>
            <div class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">粗细</div>
              <input v-model.number="edgeForm.width" type="number" min="1" max="12" step="1" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">线型</div>
              <select v-model="edgeForm.pattern" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]">
                <option value="solid">实线</option>
                <option value="dashed">虚线</option>
              </select>
            </div>
            <div class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">路径</div>
              <select v-model="edgeForm.shape" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]">
                <option value="smart">智能正交</option>
                <option value="smooth">圆角曲线</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 pt-1">
            <button
              class="px-3 py-2 c-radius bg-cyan-500/15 border border-cyan-400/30 text-cyan-200 hover:bg-cyan-500/25 transition"
              @click="startReconnect('source')"
            >
              重新连接起点
            </button>
            <button
              class="px-3 py-2 c-radius bg-cyan-500/15 border border-cyan-400/30 text-cyan-200 hover:bg-cyan-500/25 transition"
              @click="startReconnect('target')"
            >
              重新连接终点
            </button>
          </div>
          <button class="w-full px-3 py-2 c-radius bg-rose-500/15 border border-rose-400/30 text-rose-200 hover:bg-rose-500/25 transition" @click="handleDeleteSelected">删除连线</button>
          <div v-if="reconnectMode" class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">
            重新连接模式：请点击画布上的节点以设置{{ reconnectEnd === 'source' ? '起点' : '终点' }}（Esc 取消）
          </div>
        </div>
        <div v-else-if="selectedNodeId" class="p-4 overflow-auto space-y-3">
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">节点名称</div>
            <input v-model="nodeForm.label" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" />
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">节点 ID</div>
            <input v-model="nodeForm.id" disabled class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text-muted)] transition-colors duration-[420ms]" />
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">事件类型</div>
            <select v-model="nodeForm.type" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]">
              <option value="top">顶事件</option>
              <option value="middle">中间事件</option>
              <option value="basic">基本事件</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">逻辑门</div>
            <div class="flex gap-2">
              <button
                class="flex-1 px-3 py-2 c-radius border transition duration-200"
                :class="nodeForm.gate === 'AND' ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-[var(--c-surface-2)] border-[var(--c-border)] text-[var(--c-text-muted)] hover:bg-[var(--c-surface-3)]'"
                @click="nodeForm.gate = 'AND'"
              >
                AND
              </button>
              <button
                class="flex-1 px-3 py-2 c-radius border transition duration-200"
                :class="nodeForm.gate === 'OR' ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-[var(--c-surface-2)] border-[var(--c-border)] text-[var(--c-text-muted)] hover:bg-[var(--c-surface-3)]'"
                @click="nodeForm.gate = 'OR'"
              >
                OR
              </button>
            </div>
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">概率</div>
            <input v-model.number="nodeForm.probability" type="number" step="0.001" min="0" max="1" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" />
          </div>
          <button class="w-full px-3 py-2 c-radius bg-rose-500/15 border border-rose-400/30 text-rose-200 hover:bg-rose-500/25 transition" @click="handleDeleteSelected">删除节点</button>
        </div>
        <div v-else class="p-4 text-sm text-[var(--c-text-muted)] transition-colors duration-[420ms]">选择画布中的节点或连线以编辑属性</div>
      </aside>
    </div>

    <footer class="c-glass p-4 border-t border-[var(--c-border)] transition-colors duration-[420ms]">
      <div class="flex items-start gap-3">
        <textarea v-model="inputText" rows="3" class="flex-1 min-w-0 px-4 py-3 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" placeholder="上传文本 → 抽取 → 生成 → 人工调整 → 导出"></textarea>
        <label class="px-3.5 py-2 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 cursor-pointer">
          上传 .txt
          <input type="file" class="hidden" @change="handleNativeFileChange" />
        </label>
        <button class="px-3.5 py-2 c-radius bg-cyan-500/25 border border-cyan-400/30 text-cyan-100 hover:bg-cyan-500/35 transition">
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
const theme = ref('dark')
const soundEnabled = ref(false)
const nodePulseKey = ref(0)

const canvasRef = ref(null)
const canvasSize = ref({ width: 1, height: 1 })

const nodeWidth = 220
const nodeHeight = 92

const nodes = ref([
  { id: 'N-1', label: '空压机无法启动', type: 'top', gate: 'OR', probability: 0.01, x: 360, y: 40 },
  { id: 'N-2', label: '控制系统故障', type: 'middle', gate: 'AND', probability: 0.02, x: 160, y: 170 },
  { id: 'N-3', label: '电源异常', type: 'middle', gate: 'OR', probability: 0.03, x: 360, y: 170 },
  { id: 'N-4', label: '机械卡阻', type: 'middle', gate: 'OR', probability: 0.01, x: 560, y: 170 },
  { id: 'N-5', label: 'PLC 通讯异常', type: 'basic', gate: 'OR', probability: 0.004, x: 80, y: 320 },
  { id: 'N-6', label: '压力传感器异常', type: 'basic', gate: 'OR', probability: 0.006, x: 240, y: 320 }
])

const edges = ref([
  { id: 'E-1', source: 'N-1', target: 'N-2', label: 'OR 分支', style: { color: '#22d3ee', width: 2, pattern: 'solid', shape: 'smart' } },
  { id: 'E-2', source: 'N-1', target: 'N-3', label: '证据：供电异常', style: { color: '#a78bfa', width: 2, pattern: 'dashed', shape: 'smart' } },
  { id: 'E-3', source: 'N-1', target: 'N-4', label: '', style: { color: '#38bdf8', width: 2, pattern: 'solid', shape: 'smart' } },
  { id: 'E-4', source: 'N-2', target: 'N-5', label: 'AND 输入', style: { color: '#34d399', width: 2, pattern: 'solid', shape: 'smart' } },
  { id: 'E-5', source: 'N-2', target: 'N-6', label: '', style: { color: '#34d399', width: 2, pattern: 'solid', shape: 'smart' } }
])

const selectedNodeId = ref('N-3')
const selectedNode = computed(() => nodes.value.find((n) => n.id === selectedNodeId.value) ?? null)
const selectedEdgeId = ref('')
const selectedEdge = computed(() => edges.value.find((e) => e.id === selectedEdgeId.value) ?? null)

const edgeForm = reactive({
  id: '',
  source: '',
  target: '',
  label: '',
  color: '#22d3ee',
  width: 2,
  pattern: 'solid',
  shape: 'smart'
})

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

watch(selectedEdgeId, () => {
  if (!selectedEdge.value) {
    edgeForm.id = ''
    edgeForm.source = ''
    edgeForm.target = ''
    edgeForm.label = ''
    edgeForm.color = '#22d3ee'
    edgeForm.width = 2
    edgeForm.pattern = 'solid'
    edgeForm.shape = 'smart'
    return
  }

  edgeForm.id = selectedEdge.value.id
  edgeForm.source = selectedEdge.value.source
  edgeForm.target = selectedEdge.value.target
  edgeForm.label = selectedEdge.value.label ?? ''
  edgeForm.color = selectedEdge.value.style?.color ?? '#22d3ee'
  edgeForm.width = selectedEdge.value.style?.width ?? 2
  edgeForm.pattern = selectedEdge.value.style?.pattern ?? 'solid'
  edgeForm.shape = selectedEdge.value.style?.shape ?? 'smart'
}, { immediate: true })

watch(edgeForm, () => {
  if (!selectedEdge.value) return
  selectedEdge.value.label = edgeForm.label
  selectedEdge.value.style = {
    color: edgeForm.color,
    width: Number(edgeForm.width) || 2,
    pattern: edgeForm.pattern,
    shape: edgeForm.shape
  }
}, { deep: true })

const nodeTypeText = (type) => {
  if (type === 'top') return '顶事件'
  if (type === 'middle') return '中间事件'
  return '基本事件'
}

const getNodeAnchor = (nodeId) => {
  const node = nodes.value.find((n) => n.id === nodeId)
  if (!node) return { in: { x: 0, y: 0 }, out: { x: 0, y: 0 } }
  return {
    in: { x: node.x + nodeWidth / 2, y: node.y },
    out: { x: node.x + nodeWidth, y: node.y + nodeHeight / 2 }
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
  window.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateCanvasSize)
  window.removeEventListener('mousemove', handleDragging)
  window.removeEventListener('mouseup', stopDragging)
  window.removeEventListener('keydown', handleGlobalKeydown)
})

const dragging = ref(null)

const handleNodeMouseDown = (node, event) => {
  if (!canvasRef.value) return
  handleSelectNode(node.id)
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
  handleSelectNode(`N-${nextIndex}`)
}

const handleDeleteSelected = () => {
  if (selectedEdgeId.value) {
    const deleteEdgeId = selectedEdgeId.value
    edges.value = edges.value.filter((e) => e.id !== deleteEdgeId)
    selectedEdgeId.value = ''
    return
  }

  if (!selectedNodeId.value) return
  const deleteNodeId = selectedNodeId.value
  nodes.value = nodes.value.filter((n) => n.id !== deleteNodeId)
  edges.value = edges.value.filter((e) => e.source !== deleteNodeId && e.target !== deleteNodeId)
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

const clearSelection = () => {
  selectedNodeId.value = ''
  selectedEdgeId.value = ''
  reconnectMode.value = false
  reconnectEnd.value = 'target'
}

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

const playClickSound = () => {
  if (!soundEnabled.value) return
  const AudioContextImpl = window.AudioContext || window.webkitAudioContext
  if (!AudioContextImpl) return
  const ctx = new AudioContextImpl()
  const osc = ctx.createOscillator()
  const gain = ctx.createGain()
  osc.type = 'sine'
  osc.frequency.value = 880
  gain.gain.value = 0.0
  osc.connect(gain)
  gain.connect(ctx.destination)
  const now = ctx.currentTime
  gain.gain.setValueAtTime(0.0, now)
  gain.gain.linearRampToValueAtTime(0.06, now + 0.01)
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.08)
  osc.start(now)
  osc.stop(now + 0.09)
  osc.onended = () => ctx.close()
}

const handleSelectNode = (id) => {
  selectedEdgeId.value = ''
  selectedNodeId.value = id
  nodePulseKey.value += 1
  playClickSound()
  if (reconnectMode.value && selectedEdge.value) {
    if (reconnectEnd.value === 'source') selectedEdge.value.source = id
    else selectedEdge.value.target = id
    reconnectMode.value = false
  }
}

const handleSelectEdge = (id) => {
  selectedNodeId.value = ''
  selectedEdgeId.value = id
  playClickSound()
}

const handleCanvasClick = (event) => {
  if (reconnectMode.value) return
  const nodeEl = event.target?.closest?.('[data-node-id]')
  if (nodeEl?.dataset?.nodeId) return
  selectedNodeId.value = ''
  selectedEdgeId.value = ''
}

const connectDrag = ref(null)
const connectPreviewPath = computed(() => {
  if (!connectDrag.value) return ''
  const from = getNodeAnchor(connectDrag.value.fromId).out
  const to = connectDrag.value.to
  const points = [from, { x: Math.max(from.x + 30, (from.x + to.x) / 2), y: from.y }, { x: Math.max(from.x + 30, (from.x + to.x) / 2), y: to.y }, to]
  return pointsToRoundedPath(points, 10)
})

const handleStartConnect = (fromId, event) => {
  if (!canvasRef.value) return
  connectMode.value = true
  const rect = canvasRef.value.getBoundingClientRect()
  connectDrag.value = {
    fromId,
    to: { x: event.clientX - rect.left, y: event.clientY - rect.top }
  }
}

const handleCanvasMouseMove = (event) => {
  if (!connectDrag.value || !canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  connectDrag.value.to = { x: event.clientX - rect.left, y: event.clientY - rect.top }
}

const handleCanvasMouseUp = (event) => {
  if (!connectDrag.value) return
  const nodeEl = event.target?.closest?.('[data-node-id]')
  const targetId = nodeEl?.dataset?.nodeId
  const fromId = connectDrag.value.fromId
  connectDrag.value = null
  if (!targetId || targetId === fromId) return

  const nextIndex = edges.value.length + 1
  edges.value.push({
    id: `E-${nextIndex}`,
    source: fromId,
    target: targetId,
    label: '',
    style: { color: '#22d3ee', width: 2, pattern: 'solid', shape: 'smart' }
  })
}

const reconnectMode = ref(false)
const reconnectEnd = ref('target')
const startReconnect = (end) => {
  if (!selectedEdgeId.value) return
  reconnectMode.value = true
  reconnectEnd.value = end
}

const handleGlobalKeydown = (event) => {
  if (event.key === 'Escape') {
    reconnectMode.value = false
    connectDrag.value = null
    return
  }

  if (event.key === 'Delete' || event.key === 'Backspace') {
    if (selectedEdgeId.value || selectedNodeId.value) {
      event.preventDefault()
      handleDeleteSelected()
    }
  }

  if (!selectedNodeId.value) return
  const node = nodes.value.find((n) => n.id === selectedNodeId.value)
  if (!node) return
  const step = event.shiftKey ? 20 : 8
  if (event.key === 'ArrowLeft') node.x = Math.max(12, node.x - step)
  if (event.key === 'ArrowRight') node.x = node.x + step
  if (event.key === 'ArrowUp') node.y = Math.max(12, node.y - step)
  if (event.key === 'ArrowDown') node.y = node.y + step
}

const handleKeydown = (event) => {
  if (event.key !== 'Tab') return
  event.preventDefault()
  const ids = nodes.value.map((n) => n.id)
  if (ids.length === 0) return
  const currentIndex = Math.max(0, ids.indexOf(selectedNodeId.value))
  const nextIndex = (currentIndex + (event.shiftKey ? -1 : 1) + ids.length) % ids.length
  handleSelectNode(ids[nextIndex])
}

const buildObstacleGrid = (step) => {
  const cols = Math.max(1, Math.ceil(canvasSize.value.width / step))
  const rows = Math.max(1, Math.ceil(canvasSize.value.height / step))
  const blocked = new Uint8Array(cols * rows)
  const pad = 16
  for (const n of nodes.value) {
    const x0 = Math.max(0, Math.floor((n.x - pad) / step))
    const y0 = Math.max(0, Math.floor((n.y - pad) / step))
    const x1 = Math.min(cols - 1, Math.floor((n.x + nodeWidth + pad) / step))
    const y1 = Math.min(rows - 1, Math.floor((n.y + nodeHeight + pad) / step))
    for (let y = y0; y <= y1; y++) {
      for (let x = x0; x <= x1; x++) blocked[y * cols + x] = 1
    }
  }
  return { cols, rows, blocked, step }
}

const clampToGrid = (grid, point) => {
  const gx = Math.max(0, Math.min(grid.cols - 1, Math.round(point.x / grid.step)))
  const gy = Math.max(0, Math.min(grid.rows - 1, Math.round(point.y / grid.step)))
  return { x: gx, y: gy }
}

const findNearestFree = (grid, start) => {
  const idx = start.y * grid.cols + start.x
  if (!grid.blocked[idx]) return start
  const q = [start]
  const seen = new Set([`${start.x},${start.y}`])
  const dirs = [[1,0],[-1,0],[0,1],[0,-1]]
  while (q.length) {
    const cur = q.shift()
    for (const [dx, dy] of dirs) {
      const nx = cur.x + dx
      const ny = cur.y + dy
      if (nx < 0 || ny < 0 || nx >= grid.cols || ny >= grid.rows) continue
      const key = `${nx},${ny}`
      if (seen.has(key)) continue
      seen.add(key)
      const nidx = ny * grid.cols + nx
      if (!grid.blocked[nidx]) return { x: nx, y: ny }
      q.push({ x: nx, y: ny })
    }
  }
  return start
}

const aStar = (grid, start, goal) => {
  const cols = grid.cols
  const rows = grid.rows
  const startKey = start.y * cols + start.x
  const goalKey = goal.y * cols + goal.x

  const open = new Map()
  const cameFrom = new Map()
  const gScore = new Map()
  const fScore = new Map()

  const h = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y)
  const setScore = (map, key, v) => map.set(key, v)
  const getScore = (map, key) => map.get(key) ?? Infinity

  setScore(gScore, startKey, 0)
  setScore(fScore, startKey, h(start, goal))
  open.set(startKey, start)

  const dirs = [[1,0],[-1,0],[0,1],[0,-1]]

  while (open.size) {
    let currentKey = null
    let current = null
    let bestF = Infinity
    for (const [key, node] of open) {
      const f = getScore(fScore, key)
      if (f < bestF) {
        bestF = f
        currentKey = key
        current = node
      }
    }
    if (currentKey === null) break
    if (currentKey === goalKey) {
      const path = [current]
      let ck = currentKey
      while (cameFrom.has(ck)) {
        ck = cameFrom.get(ck)
        const x = ck % cols
        const y = Math.floor(ck / cols)
        path.push({ x, y })
      }
      path.reverse()
      return path
    }
    open.delete(currentKey)
    const currentG = getScore(gScore, currentKey)

    for (const [dx, dy] of dirs) {
      const nx = current.x + dx
      const ny = current.y + dy
      if (nx < 0 || ny < 0 || nx >= cols || ny >= rows) continue
      const nkey = ny * cols + nx
      if (grid.blocked[nkey] && nkey !== goalKey) continue
      const tentative = currentG + 1
      if (tentative < getScore(gScore, nkey)) {
        cameFrom.set(nkey, currentKey)
        setScore(gScore, nkey, tentative)
        setScore(fScore, nkey, tentative + h({ x: nx, y: ny }, goal))
        open.set(nkey, { x: nx, y: ny })
      }
    }
  }
  return null
}

const simplifyPoints = (points) => {
  if (points.length <= 2) return points
  const simplified = [points[0]]
  for (let i = 1; i < points.length - 1; i++) {
    const prev = simplified[simplified.length - 1]
    const cur = points[i]
    const next = points[i + 1]
    const dx1 = cur.x - prev.x
    const dy1 = cur.y - prev.y
    const dx2 = next.x - cur.x
    const dy2 = next.y - cur.y
    const collinear = (dx1 === 0 && dx2 === 0) || (dy1 === 0 && dy2 === 0)
    if (!collinear) simplified.push(cur)
  }
  simplified.push(points[points.length - 1])
  return simplified
}

const pointsToRoundedPath = (points, radius) => {
  if (!points.length) return ''
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`
  let d = `M ${points[0].x} ${points[0].y}`
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1]
    const cur = points[i]
    const next = points[i + 1]
    if (!next) {
      d += ` L ${cur.x} ${cur.y}`
      continue
    }
    const v1 = { x: cur.x - prev.x, y: cur.y - prev.y }
    const v2 = { x: next.x - cur.x, y: next.y - cur.y }
    const len1 = Math.hypot(v1.x, v1.y) || 1
    const len2 = Math.hypot(v2.x, v2.y) || 1
    const r = Math.min(radius, len1 / 2, len2 / 2)
    const p1 = { x: cur.x - (v1.x / len1) * r, y: cur.y - (v1.y / len1) * r }
    const p2 = { x: cur.x + (v2.x / len2) * r, y: cur.y + (v2.y / len2) * r }
    d += ` L ${p1.x} ${p1.y} Q ${cur.x} ${cur.y} ${p2.x} ${p2.y}`
  }
  return d
}

const computeLabelBox = (label) => {
  const len = Math.min(28, Math.max(0, (label ?? '').length))
  return { w: 16 + len * 7, h: 22 }
}

const computeMidPointOnPolyline = (points) => {
  if (points.length < 2) return { x: points[0]?.x ?? 0, y: points[0]?.y ?? 0 }
  const segLens = []
  let total = 0
  for (let i = 1; i < points.length; i++) {
    const l = Math.hypot(points[i].x - points[i - 1].x, points[i].y - points[i - 1].y)
    segLens.push(l)
    total += l
  }
  const half = total / 2
  let acc = 0
  for (let i = 1; i < points.length; i++) {
    const l = segLens[i - 1]
    if (acc + l >= half) {
      const t = (half - acc) / (l || 1)
      return {
        x: points[i - 1].x + (points[i].x - points[i - 1].x) * t,
        y: points[i - 1].y + (points[i].y - points[i - 1].y) * t
      }
    }
    acc += l
  }
  return points[Math.floor(points.length / 2)]
}

const computeSmartPathPoints = (sourceId, targetId, grid) => {
  const from = getNodeAnchor(sourceId).out
  const to = getNodeAnchor(targetId).in
  const startCell = findNearestFree(grid, clampToGrid(grid, from))
  const goalCell = findNearestFree(grid, clampToGrid(grid, to))
  const cellPath = aStar(grid, startCell, goalCell)
  if (!cellPath || cellPath.length < 2) return [from, to]
  const pts = cellPath.map((c) => ({ x: c.x * grid.step + grid.step / 2, y: c.y * grid.step + grid.step / 2 }))
  pts[0] = from
  pts[pts.length - 1] = to
  return simplifyPoints(pts)
}

const edgeRenders = computed(() => {
  const step = 18
  const grid = buildObstacleGrid(step)
  return edges.value
    .filter((e) => e.source && e.target)
    .map((e) => {
      const style = e.style ?? { color: '#22d3ee', width: 2, pattern: 'solid', shape: 'smart' }
      const points = computeSmartPathPoints(e.source, e.target, grid)
      const radius = style.shape === 'smooth' ? 14 : 10
      const path = pointsToRoundedPath(points, radius)
      const labelPos = computeMidPointOnPolyline(points)
      const labelBox = computeLabelBox(e.label)
      return {
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label ?? '',
        style,
        path,
        labelPos,
        labelBox
      }
    })
})
</script>

<style scoped>
.c-root {
  --c-bg: radial-gradient(1200px 600px at 25% 15%, rgba(34, 211, 238, 0.12), transparent 55%),
    radial-gradient(900px 500px at 75% 20%, rgba(167, 139, 250, 0.12), transparent 55%),
    linear-gradient(135deg, #020617 0%, #0b1026 45%, #020617 100%);
  --c-text: rgba(248, 250, 252, 0.96);
  --c-text-muted: rgba(226, 232, 240, 0.65);
  --c-border: rgba(255, 255, 255, 0.10);
  --c-surface: rgba(255, 255, 255, 0.06);
  --c-surface-2: rgba(255, 255, 255, 0.08);
  --c-surface-3: rgba(255, 255, 255, 0.12);
  --c-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
  background: var(--c-bg);
}

.c-root[data-theme="light"] {
  --c-bg: radial-gradient(1100px 600px at 20% 20%, rgba(34, 211, 238, 0.20), transparent 55%),
    radial-gradient(900px 520px at 80% 25%, rgba(167, 139, 250, 0.18), transparent 55%),
    linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%);
  --c-text: rgba(15, 23, 42, 0.92);
  --c-text-muted: rgba(15, 23, 42, 0.55);
  --c-border: rgba(15, 23, 42, 0.10);
  --c-surface: rgba(255, 255, 255, 0.72);
  --c-surface-2: rgba(255, 255, 255, 0.82);
  --c-surface-3: rgba(255, 255, 255, 0.92);
  --c-shadow: 0 18px 50px rgba(15, 23, 42, 0.14);
}

.c-radius {
  border-radius: 14px 18px 14px 18px;
}

.c-panel {
  border-radius: 16px 22px 16px 22px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  box-shadow: var(--c-shadow);
}

.c-glass {
  background: var(--c-surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.c-grid {
  background-image: radial-gradient(rgba(148, 163, 184, 0.85) 1px, transparent 1px);
  background-size: 18px 18px;
  background-position: 0 0;
  filter: drop-shadow(0 0 0 rgba(0, 0, 0, 0));
}

.c-node {
  border-radius: 14px 20px 14px 20px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  transition: transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease, background-color 420ms ease, color 420ms ease;
}

.c-node:hover {
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.20);
}

.c-node.is-selected {
  border-width: 2px;
  box-shadow:
    0 0 0 1px rgba(34, 211, 238, 0.25),
    0 18px 55px rgba(34, 211, 238, 0.12),
    0 26px 70px rgba(167, 139, 250, 0.10);
  transform: translateY(-2px);
}

.c-node.is-selected::before {
  content: "";
  position: absolute;
  inset: -6px;
  border-radius: 18px 26px 18px 26px;
  background: radial-gradient(80% 60% at 50% 30%, rgba(34, 211, 238, 0.20), transparent 60%),
    radial-gradient(80% 60% at 50% 70%, rgba(167, 139, 250, 0.16), transparent 60%);
  filter: blur(6px);
  opacity: 0.95;
  pointer-events: none;
}

.c-node-pulse {
  position: absolute;
  inset: -14px;
  border-radius: 24px 34px 24px 34px;
  border: 2px solid rgba(34, 211, 238, 0.20);
  box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.25);
  pointer-events: none;
  animation: c-pulse 520ms ease-out;
}

@keyframes c-pulse {
  0% {
    opacity: 0.0;
    transform: scale(0.96);
    box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.18);
  }
  25% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: scale(1.04);
    box-shadow: 0 0 0 18px rgba(34, 211, 238, 0.0);
  }
}

.c-handle {
  box-shadow:
    0 0 0 1px rgba(34, 211, 238, 0.25),
    0 10px 26px rgba(34, 211, 238, 0.14);
}
</style>
