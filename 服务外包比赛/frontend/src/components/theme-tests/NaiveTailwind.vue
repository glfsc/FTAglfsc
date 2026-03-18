<template>
  <div class="c-root h-full flex flex-col transition-colors duration-[420ms]" :data-theme="theme" @keydown="handleKeydown">
    <div class="c-bg" :data-theme="theme" aria-hidden="true" />
    <div v-if="themeTransition.active" class="c-bg c-bg--from" :data-theme="themeTransition.from" aria-hidden="true" />

    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="pointer-events-none px-3 py-2 c-radius border shadow-2xl backdrop-blur-xl transition-colors duration-[420ms]"
        :class="t.type === 'error' ? 'bg-rose-500/20 border-rose-400/30 text-rose-100' : 'bg-[var(--c-surface-2)] border-[var(--c-border)] text-[var(--c-text)]'"
      >
        <div class="text-sm font-medium">{{ t.message }}</div>
      </div>
    </div>

    <header class="c-glass h-16 px-6 flex items-center justify-between border-b transition-colors duration-[420ms]">
      <div class="flex items-center gap-3">
        <div class="relative">
          <div class="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-violet-600 blur-xl opacity-35"></div>
          <div class="relative w-10 h-10 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] flex items-center justify-center transition-colors duration-[420ms]">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" class="text-cyan-300">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
        </div>
        <div class="leading-tight">
          <div class="text-[15px] font-semibold text-[var(--c-text)] tracking-wide transition-colors duration-[420ms]">故障树生成工作台</div>
          <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">Naive 风格 + Tailwind（拖拽/连线/撤销/粒子）</div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">拖拽节点右下角手柄创建连线</span>
      </div>
    </header>

    <div class="flex-1 min-h-0 p-4 flex gap-4">
      <aside class="c-left-sidebar w-72 c-panel c-glass shadow-2xl overflow-hidden flex flex-col min-h-0 transition-colors duration-[420ms]">
        <div class="px-4 py-3 flex items-center justify-between border-b border-[var(--c-border)] transition-colors duration-[420ms]">
          <div class="text-sm font-semibold transition-colors duration-[420ms]">历史记录</div>
          <button class="text-xs text-[var(--c-text-muted)] hover:text-[var(--c-text)] transition duration-200">清空</button>
        </div>
        <div class="flex-1 min-h-0 overflow-auto p-3 space-y-3">
          <div
            v-for="item in histories"
            :key="item.id"
            class="c-history-item c-radius border px-3 py-2.5 cursor-pointer transition duration-200"
            :class="item.id === selectedHistoryId ? 'border-cyan-400/30 bg-cyan-400/10' : 'border-[var(--c-border)] bg-[var(--c-surface-2)]'"
            @click="selectedHistoryId = item.id"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="text-sm font-medium text-[var(--c-text)] truncate transition-colors duration-[420ms]">{{ item.title }}</div>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-400/10 border border-emerald-400/20 text-emerald-200">{{ item.status }}</span>
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
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 disabled:opacity-40" :disabled="!canUndo" @click="handleUndo">撤销</button>
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 disabled:opacity-40" :disabled="!canRedo" @click="handleRedo">重做</button>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">Ctrl+Z/Ctrl+Y · Tab/方向键/Del</span>
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
                <path :d="edge.path" fill="none" stroke="transparent" stroke-width="14" class="cursor-pointer" @click.stop="handleSelectEdge(edge.id)" />
                <g v-if="edge.id === selectedEdgeId">
                  <circle
                    :cx="edge.endpoints.source.x"
                    :cy="edge.endpoints.source.y"
                    r="7"
                    fill="rgba(34, 211, 238, 0.18)"
                    stroke="rgba(34, 211, 238, 0.65)"
                    stroke-width="2"
                    class="cursor-grab active:cursor-grabbing"
                    @mousedown.stop="handleStartReconnectDrag(edge.id, 'source', $event)"
                  />
                  <circle
                    :cx="edge.endpoints.target.x"
                    :cy="edge.endpoints.target.y"
                    r="7"
                    fill="rgba(167, 139, 250, 0.16)"
                    stroke="rgba(167, 139, 250, 0.70)"
                    stroke-width="2"
                    class="cursor-grab active:cursor-grabbing"
                    @mousedown.stop="handleStartReconnectDrag(edge.id, 'target', $event)"
                  />
                </g>
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
                  <text :x="edge.labelPos.x" :y="edge.labelPos.y + 4" text-anchor="middle" :fill="'var(--c-text)'" class="select-none text-[12px]">
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
              <path
                v-if="reconnectDrag"
                :d="reconnectPreviewPath"
                fill="none"
                stroke="rgba(167, 139, 250, 0.9)"
                stroke-width="2"
                stroke-dasharray="6 6"
                stroke-linecap="round"
              />
            </svg>

            <ParticleBurst ref="particleRef" class="absolute inset-0 z-30" :enabled="particleEnabled" :gravity-decay="0.98" :life-ms="800" :count="20" />

              <div
                v-for="node in nodes"
                :key="node.id"
                class="c-node absolute z-10 w-[220px] h-[92px] border shadow-xl select-none cursor-grab active:cursor-grabbing p-3 transition duration-200"
                :class="[
                  node.id === selectedNodeId ? 'is-selected' : '',
                  node.type === 'top' ? 'border-rose-400/30 bg-rose-500/10' : '',
                  node.type === 'middle' ? 'border-sky-400/30 bg-sky-500/10' : '',
                  node.type === 'basic' ? 'border-emerald-400/30 bg-emerald-500/10' : ''
                ]"
                :style="{ left: node.x + 'px', top: node.y + 'px' }"
                @mousedown="handleNodeMouseDown(node, event)"
                @click.stop="handleSelectNode(node.id, { focus: true })"
                @focus="handleSelectNode(node.id, { effects: false })"
                @keydown.enter.prevent="handleSelectNode(node.id, { focus: true })"
                @keydown.space.prevent="handleSelectNode(node.id, { focus: true })"
                :data-node-id="node.id"
                tabindex="0"
                role="button"
                :aria-label="`节点 ${node.label}（${node.id}），按 Enter 选中，按 Shift+方向键移动`"
              >
                <span class="c-node-glow-inner" v-if="node.id === selectedNodeId" :key="`g1-${nodeEffectKey}`" />
                <span class="c-node-glow-outer" v-if="node.id === selectedNodeId" :key="`g2-${nodeEffectKey}`" />
                <span class="c-node-pulse" v-if="node.id === selectedNodeId" :key="`p-${nodeEffectKey}`" />
                <!-- Hover glow effect -->
                <span class="c-node-hover-glow" v-if="node.id !== selectedNodeId" />
                <div class="flex items-center justify-between text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">
                  <div class="font-semibold text-[var(--c-text)]/90 transition-colors duration-[420ms]">{{ nodeTypeText(node.type) }}</div>
                  <div class="px-2 py-0.5 rounded-full bg-[var(--c-surface-2)]/70 border border-[var(--c-border)] font-semibold text-[var(--c-text)]/85 transition-colors duration-[420ms]">{{ node.gate }}</div>
                </div>
                <div class="mt-1 text-sm font-semibold text-[var(--c-text)] truncate transition-colors duration-[420ms]">{{ node.label }}</div>
                <div class="mt-1 text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">ID：{{ node.id }}</div>
            
                <button
                  class="c-handle absolute -right-3 bottom-2 w-5 h-5 rounded-full border border-cyan-300/40 bg-cyan-400/20 hover:bg-cyan-400/30 transition cursor-crosshair"
                  title="拖拽创建连线"
                  aria-label="从该节点拖拽创建连线"
                  @mousedown.stop="handleStartConnect(node.id, $event)"
                />
              </div>
          </div>
        </div>
      </main>

      <aside class="w-[450px] c-panel c-glass shadow-2xl overflow-hidden flex flex-col min-h-0 transition-colors duration-[420ms]">
        <div class="px-4 py-3 flex items-center justify-between border-b border-[var(--c-border)] transition-colors duration-[420ms]">
          <div class="text-sm font-semibold text-[var(--c-text)] transition-colors duration-[420ms]">{{ selectedEdgeId ? '连线信息' : selectedNodeId ? '节点信息' : '专家辅助系统' }}</div>
          <button class="text-xs text-[var(--c-text-muted)] hover:text-[var(--c-text)] transition duration-200 disabled:opacity-40" :disabled="!selectedNodeId && !selectedEdgeId" @click="clearSelection">关闭</button>
        </div>

        <!-- AI Chat Panel - Default when no node/edge selected -->
        <div v-if="!selectedNodeId && !selectedEdgeId" class="flex-1 flex flex-col">
          <div class="flex-1 p-4 overflow-auto">
            <!-- Expert System Header with Glow Effect -->
            <div class="relative mb-4 p-4 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-xl border border-emerald-400/20">
              <div class="absolute inset-0 bg-gradient-to-r from-emerald-400/5 to-teal-400/5 animate-pulse rounded-xl"></div>
              <div class="relative flex items-center gap-3">
                <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                <h3 class="font-bold text-[var(--c-text)]">专家辅助系统 - Expert Assistant</h3>
              </div>
            </div>
            
            <!-- AI Chat Messages Area -->
            <div class="space-y-4">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-emerald-300">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"></path></svg>
                </div>
                <div class="flex-1">
                  <div class="bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm text-[var(--c-text)]">
                    您好！我是专家辅助系统，可以帮您分析故障树结构、评估概率、优化逻辑门配置等。请问有什么可以帮助您的？
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Input Area -->
          <div class="p-4 border-t border-[var(--c-border)]">
            <div class="flex gap-2">
              <input 
                type="text" 
                placeholder="向 AI 专家提问..." 
                class="flex-1 px-4 py-2.5 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-emerald-400/20 transition-colors duration-[420ms]"
              />
              <button class="px-4 py-2.5 c-radius bg-emerald-500/20 border border-emerald-400/30 text-emerald-200 hover:bg-emerald-500/30 transition">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Edge Properties Panel - Shows when edge selected -->
        <div v-else-if="selectedEdgeId" class="p-4 overflow-auto space-y-3 relative">
          <!-- Edge Highlight Indicator -->
          <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-400 to-violet-400 animate-pulse"></div>
          
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">标签</div>
            <input v-model="edgeForm.label" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" placeholder="例如：因果/证据说明" @blur="commitEdgeForm" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">颜色</div>
              <input v-model="edgeForm.color" type="color" class="w-full h-10 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)]" @change="commitEdgeForm" />
            </div>
            <div class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">粗细</div>
              <input v-model.number="edgeForm.width" type="number" min="1" max="12" step="1" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @change="commitEdgeForm" />
            </div>
          </div>
          <button class="w-full px-3 py-2 c-radius bg-rose-500/15 border border-rose-400/30 text-rose-200 hover:bg-rose-500/25 transition" @click="handleDeleteSelected">删除连线</button>
          <div class="text-xs text-[var(--c-text-muted)] text-center mt-2">或按 Delete 键删除</div>
        </div>

        <!-- Node Properties Panel - Shows when node selected -->
        <div v-else-if="selectedNodeId" class="p-4 overflow-auto space-y-3 relative">
          <!-- Node Highlight Effect -->
          <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-400 to-purple-400 animate-pulse"></div>
          <div class="mb-4 p-3 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-lg border border-indigo-400/20">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
              <span class="text-sm font-semibold text-[var(--c-text)]">Selected: {{ nodeForm.label }}</span>
            </div>
          </div>
          
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">节点名称</div>
            <input v-model="nodeForm.label" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @blur="commitNodeForm" />
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">节点 ID</div>
            <input v-model="nodeForm.id" disabled class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text-muted)] transition-colors duration-[420ms]" />
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">事件类型</div>
            <select v-model="nodeForm.type" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @change="commitNodeForm">
              <option value="top">顶事件</option>
              <option value="middle">中间事件</option>
              <option value="basic">基本事件</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">逻辑门</div>
            <div class="flex gap-2">
              <button class="flex-1 px-3 py-2 c-radius border transition duration-200" :class="nodeForm.gate === 'AND' ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-[var(--c-surface-2)] border-[var(--c-border)] text-[var(--c-text-muted)] hover:bg-[var(--c-surface-3)]'" @click="nodeForm.gate = 'AND'; commitNodeForm()">
                AND
              </button>
              <button class="flex-1 px-3 py-2 c-radius border transition duration-200" :class="nodeForm.gate === 'OR' ? 'bg-cyan-400/15 border-cyan-400/30 text-cyan-200' : 'bg-[var(--c-surface-2)] border-[var(--c-border)] text-[var(--c-text-muted)] hover:bg-[var(--c-surface-3)]'" @click="nodeForm.gate = 'OR'; commitNodeForm()">
                OR
              </button>
            </div>
          </div>
          <div class="space-y-1.5">
            <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">概率</div>
            <input v-model.number="nodeForm.probability" type="number" step="0.001" min="0" max="1" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @change="commitNodeForm" />
          </div>
          <button class="w-full px-3 py-2 c-radius bg-rose-500/15 border border-rose-400/30 text-rose-200 hover:bg-rose-500/25 transition" @click="handleDeleteSelected">删除节点</button>
          <div class="text-xs text-[var(--c-text-muted)] text-center mt-2">或按 Delete 键删除</div>
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
        <button class="px-3.5 py-2 c-radius bg-cyan-500/25 border border-cyan-400/30 text-cyan-100 hover:bg-cyan-500/35 transition">生成</button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import ParticleBurst from './ParticleBurst.vue'
import { HistoryManager, canAddEdge, createIncrementId, defaultClone, resolveDragCollision, snapToGrid } from './naiveTailwindCore'

const props = defineProps({
  initialAutoAlign: { type: Boolean, default: true },
  initialAllowMultipleEdges: { type: Boolean, default: false },
  initialParticleEnabled: { type: Boolean, default: true }
})

const histories = ref([
  { id: 'h-1', title: '空压机无法启动', time: '2026/03/16 09:12', status: 'done' },
  { id: 'h-2', title: '电机过热报警', time: '2026/03/15 16:33', status: 'done' },
  { id: 'h-3', title: '控制回路异常', time: '2026/03/14 11:08', status: 'done' }
])

const selectedHistoryId = ref(histories.value[0]?.id ?? '')
const connectMode = ref(false)
const inputText = ref('')
const theme = ref('dark')
const themeTransition = reactive({ active: false, from: 'dark', timer: 0 })
const soundEnabled = ref(false)
const nodeEffectKey = ref(0)
const autoAlign = ref(true) // Default: enabled
const allowMultipleEdges = ref(false) // Default: single edge mode
const particleEnabled = ref(true) // Default: enabled
const particleRef = ref(null)

const toasts = ref([])
const toast = (message, type = 'info') => {
  const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
  toasts.value.push({ id, message: String(message ?? ''), type })
  window.setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }, 1800)
}

const canvasRef = ref(null)
const canvasSize = ref({ width: 1, height: 1 })

const nodeWidth = 220
const nodeHeight = 92
const safePadding = 8
const gridStep = 18

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

const history = new HistoryManager({ capacity: 50, clone: defaultClone })
const historyVersion = ref(0)
const syncHistory = () => {
  historyVersion.value = history.version
}
const canUndo = computed(() => {
  historyVersion.value
  return history.canUndo()
})
const canRedo = computed(() => {
  historyVersion.value
  return history.canRedo()
})
const exec = (command) => {
  history.execute(command)
  syncHistory()
}
const handleUndo = () => {
  history.undo()
  syncHistory()
}
const handleRedo = () => {
  history.redo()
  syncHistory()
}

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

watch(
  selectedNodeId,
  () => {
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
  },
  { immediate: true }
)

watch(
  selectedEdgeId,
  () => {
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
  },
  { immediate: true }
)

const nodeTypeText = (type) => {
  if (type === 'top') return '顶事件'
  if (type === 'middle') return '中间事件'
  return '基本事件'
}

const getNodeAnchor = (nodeId) => {
  const node = nodes.value.find((n) => n.id === nodeId)
  if (!node) return { in: { x: 0, y: 0 }, out: { x: 0, y: 0 } }
  // Modified: Output at bottom-right corner where handle is
  return {
    in: { x: node.x + nodeWidth / 2, y: node.y }, // Top center for input
    out: { x: node.x + nodeWidth, y: node.y + nodeHeight - 16 } // Bottom-right corner (where handle is)
  }
}

const updateCanvasSize = () => {
  if (!canvasRef.value) return
  canvasSize.value = { width: canvasRef.value.clientWidth, height: canvasRef.value.clientHeight }
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

const updateNodeById = (id, patch) => {
  const node = nodes.value.find((n) => n.id === id)
  if (!node) return
  Object.assign(node, patch)
}

const updateEdgeById = (id, patch) => {
  const edge = edges.value.find((e) => e.id === id)
  if (!edge) return
  Object.assign(edge, patch)
}

const commitNodeForm = () => {
  if (!selectedNode.value) return
  const id = selectedNode.value.id
  const before = {}
  const after = {}
  for (const k of ['label', 'type', 'gate', 'probability']) {
    const cur = selectedNode.value[k]
    const next = nodeForm[k]
    if (cur !== next) {
      before[k] = cur
      after[k] = next
    }
  }
  if (!Object.keys(before).length) return
  exec({ do: () => updateNodeById(id, after), undo: () => updateNodeById(id, before) })
}

const commitEdgeForm = () => {
  if (!selectedEdge.value) return
  const id = selectedEdge.value.id
  const nextStyle = { color: edgeForm.color, width: Number(edgeForm.width) || 2, pattern: edgeForm.pattern, shape: edgeForm.shape }
  const before = { label: selectedEdge.value.label ?? '', style: defaultClone(selectedEdge.value.style ?? {}) }
  const after = { label: edgeForm.label, style: nextStyle }
  if (before.label === after.label && JSON.stringify(before.style) === JSON.stringify(after.style)) return
  exec({ do: () => updateEdgeById(id, after), undo: () => updateEdgeById(id, before) })
}

const dragging = ref(null)

const handleNodeMouseDown = (node, event) => {
  if (!canvasRef.value) return
  handleSelectNode(node.id)
  const rect = canvasRef.value.getBoundingClientRect()
  dragging.value = { id: node.id, startX: node.x, startY: node.y, offsetX: event.clientX - rect.left - node.x, offsetY: event.clientY - rect.top - node.y }
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
  const minX = 12
  const minY = 12
  const maxX = rect.width - nodeWidth - 12
  const maxY = rect.height - nodeHeight - 12
  const proposed = { x: Math.max(minX, Math.min(nextX, maxX)), y: Math.max(minY, Math.min(nextY, maxY)) }

  if (!autoAlign.value) {
    node.x = proposed.x
    node.y = proposed.y
    return
  }

  const resolved = resolveDragCollision({
    movingId: node.id,
    proposed,
    nodes: nodes.value,
    nodeWidth,
    nodeHeight,
    safePadding,
    gridStep,
    bounds: { minX, minY, maxX, maxY }
  })
  node.x = resolved.x
  node.y = resolved.y
}

const stopDragging = () => {
  if (dragging.value) {
    const id = dragging.value.id
    const node = nodes.value.find((n) => n.id === id)
    if (node) {
      const before = { x: dragging.value.startX, y: dragging.value.startY }
      const after = { x: node.x, y: node.y }
      if (before.x !== after.x || before.y !== after.y) exec({ do: () => updateNodeById(id, after), undo: () => updateNodeById(id, before) })
    }
  }
  dragging.value = null
  window.removeEventListener('mousemove', handleDragging)
  window.removeEventListener('mouseup', stopDragging)
}

const maxNumber = (ids, prefix) => {
  let max = 0
  for (const id of ids) {
    if (!id?.startsWith(prefix)) continue
    const n = Number(id.slice(prefix.length))
    if (Number.isFinite(n)) max = Math.max(max, n)
  }
  return max
}

const nextNodeId = createIncrementId('N-', maxNumber(nodes.value.map((n) => n.id), 'N-') + 1)
const nextEdgeId = createIncrementId('E-', maxNumber(edges.value.map((e) => e.id), 'E-') + 1)

const deleteEdgeById = (id) => {
  edges.value = edges.value.filter((e) => e.id !== id)
}

const deleteNodeById = (id) => {
  nodes.value = nodes.value.filter((n) => n.id !== id)
  edges.value = edges.value.filter((e) => e.source !== id && e.target !== id)
}

const addNode = () => {
  const id = nextNodeId()
  const rect = canvasRef.value?.getBoundingClientRect?.()
  const bounds = rect ? { minX: 12, minY: 12, maxX: rect.width - nodeWidth - 12, maxY: rect.height - nodeHeight - 12 } : { minX: 12, minY: 12, maxX: 1200, maxY: 900 }
  const baseX = 80 + (nodes.value.length % 5) * 120
  const baseY = 420
  const proposed = { x: snapToGrid(baseX, gridStep), y: snapToGrid(baseY, gridStep) }
  const pos = autoAlign.value ? resolveDragCollision({ movingId: id, proposed, nodes: nodes.value, nodeWidth, nodeHeight, safePadding, gridStep, bounds }) : proposed
  const node = { id, label: `新节点 ${id.slice(2)}`, type: 'basic', gate: 'OR', probability: 0.001, x: pos.x, y: pos.y }

  exec({
    do: () => nodes.value.push(node),
    undo: () => {
      deleteNodeById(id)
      if (selectedNodeId.value === id) selectedNodeId.value = ''
      if (selectedEdgeId.value) selectedEdgeId.value = ''
    }
  })
  handleSelectNode(id)
  return id
}

const handleAddNode = () => addNode()

const handleDeleteSelected = () => {
  if (selectedEdgeId.value) {
    const deleteEdgeId = selectedEdgeId.value
    const edgeSnapshot = defaultClone(edges.value.find((e) => e.id === deleteEdgeId))
    exec({
      do: () => {
        deleteEdgeById(deleteEdgeId)
        selectedEdgeId.value = ''
      },
      undo: () => {
        if (edgeSnapshot) edges.value.push(edgeSnapshot)
      }
    })
    return
  }

  if (!selectedNodeId.value) return
  const deleteNodeId = selectedNodeId.value
  const nodeSnapshot = defaultClone(nodes.value.find((n) => n.id === deleteNodeId))
  const edgeSnapshots = defaultClone(edges.value.filter((e) => e.source === deleteNodeId || e.target === deleteNodeId))
  exec({
    do: () => {
      deleteNodeById(deleteNodeId)
      selectedNodeId.value = ''
      selectedEdgeId.value = ''
    },
    undo: () => {
      if (nodeSnapshot) nodes.value.push(nodeSnapshot)
      if (Array.isArray(edgeSnapshots) && edgeSnapshots.length) edges.value.push(...edgeSnapshots)
    }
  })
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
  reconnectDrag.value = null
}

const toggleTheme = () => {
  const next = theme.value === 'dark' ? 'light' : 'dark'
  themeTransition.from = theme.value
  themeTransition.active = true
  theme.value = next
  window.clearTimeout(themeTransition.timer)
  themeTransition.timer = window.setTimeout(() => {
    themeTransition.active = false
  }, 440)
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

const reconnectMode = ref(false)
const reconnectEnd = ref('target')
const startReconnect = (end) => {
  if (!selectedEdgeId.value) return
  reconnectMode.value = true
  reconnectEnd.value = end
}

const focusNode = async (id) => {
  await nextTick()
  const el = canvasRef.value?.querySelector?.(`[data-node-id="${CSS.escape(id)}"]`)
  el?.focus?.()
}

const handleSelectNode = (id, { effects = true, focus = false } = {}) => {
  selectedEdgeId.value = ''
  selectedNodeId.value = id
  if (effects) {
    nodeEffectKey.value += 1
    playClickSound()
    if (particleEnabled.value) {
      const node = nodes.value.find((n) => n.id === id)
      if (node) particleRef.value?.burst?.(node.x + nodeWidth / 2, node.y + nodeHeight / 2)
    }
  }
  if (focus) focusNode(id)

  if (reconnectMode.value && selectedEdge.value) {
    const edgeId = selectedEdge.value.id
    const before = { source: selectedEdge.value.source, target: selectedEdge.value.target }
    const after = reconnectEnd.value === 'source' ? { source: id, target: selectedEdge.value.target } : { source: selectedEdge.value.source, target: id }
    if (!canAddEdge(edges.value, after.source, after.target, { allowMultipleEdges: allowMultipleEdges.value, ignoreEdgeId: edgeId })) {
      toast('两节点只能有一条连线', 'error')
      reconnectMode.value = false
      return
    }
    exec({ do: () => updateEdgeById(edgeId, after), undo: () => updateEdgeById(edgeId, before) })
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
  const points = [
    from,
    { x: Math.max(from.x + 30, (from.x + to.x) / 2), y: from.y },
    { x: Math.max(from.x + 30, (from.x + to.x) / 2), y: to.y },
    to
  ]
  return pointsToRoundedPath(points, 10)
})

const handleStartConnect = (fromId, event) => {
  if (!canvasRef.value) return
  const fromNode = nodes.value.find(n => n.id === fromId)
  
  // Validation: Check if trying to connect from Top Event to Basic Event
  if (fromNode?.type === 'top') {
    // Will validate on drop, but can show warning hint here if needed
  }
  
  connectDrag.value = { fromId, to: { x: event.clientX - rect.left, y: event.clientY - rect.top } }
}

const reconnectDrag = ref(null)
const reconnectPreviewPath = computed(() => {
  if (!reconnectDrag.value) return ''
  const edge = edges.value.find((e) => e.id === reconnectDrag.value.edgeId)
  if (!edge) return ''
  const to = reconnectDrag.value.to
  const fixed = reconnectDrag.value.end === 'source' ? getNodeAnchor(edge.target).in : getNodeAnchor(edge.source).out
  const points = [
    fixed,
    { x: (fixed.x + to.x) / 2, y: fixed.y },
    { x: (fixed.x + to.x) / 2, y: to.y },
    to
  ]
  return pointsToRoundedPath(points, 10)
})

const handleStartReconnectDrag = (edgeId, end, event) => {
  if (!canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  reconnectDrag.value = { edgeId, end, to: { x: event.clientX - rect.left, y: event.clientY - rect.top } }
}

const handleCanvasMouseMove = (event) => {
  if (!canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  if (connectDrag.value) connectDrag.value.to = { x: event.clientX - rect.left, y: event.clientY - rect.top }
  if (reconnectDrag.value) reconnectDrag.value.to = { x: event.clientX - rect.left, y: event.clientY - rect.top }
}

const handleCanvasMouseUp = (event) => {
  if (reconnectDrag.value) {
    const nodeEl = event.target?.closest?.('[data-node-id]')
    const nextNodeId = nodeEl?.dataset?.nodeId
    const drag = reconnectDrag.value
    reconnectDrag.value = null
    if (!nextNodeId) return
    const edge = edges.value.find((e) => e.id === drag.edgeId)
    if (!edge) return
    const before = { source: edge.source, target: edge.target }
    const after = drag.end === 'source' ? { source: nextNodeId, target: edge.target } : { source: edge.source, target: nextNodeId }
    if (after.source === after.target) return
    if (!canAddEdge(edges.value, after.source, after.target, { allowMultipleEdges: allowMultipleEdges.value, ignoreEdgeId: edge.id })) {
      toast('两节点只能有一条连线', 'error')
      return
    }
    exec({ do: () => updateEdgeById(edge.id, after), undo: () => updateEdgeById(edge.id, before) })
    return
  }

  if (!connectDrag.value) return
  const nodeEl = event.target?.closest?.('[data-node-id]')
  const targetId = nodeEl?.dataset?.nodeId
  const fromId = connectDrag.value.fromId
  connectDrag.value = null
  if (!targetId || targetId === fromId) return
  
  // Validation: Top Event cannot connect to Basic Event
  const fromNode = nodes.value.find(n => n.id === fromId)
  const targetNode = nodes.value.find(n => n.id === targetId)
  if (fromNode?.type === 'top' && targetNode?.type === 'basic') {
    toast('无效连接：顶事件不能直接连接到基本事件，必须连接到中间事件', 'error')
    return
  }
  
  if (!canAddEdge(edges.value, fromId, targetId, { allowMultipleEdges: allowMultipleEdges.value })) {
    toast('两节点只能有一条连线', 'error')
    return
  }

  const id = nextEdgeId()
  const edge = { id, source: fromId, target: targetId, label: '', style: { color: '#22d3ee', width: 2, pattern: 'solid', shape: 'smart' } }
  exec({
    do: () => edges.value.push(edge),
    undo: () => {
      deleteEdgeById(id)
      if (selectedEdgeId.value === id) selectedEdgeId.value = ''
    }
  })
}

const handleGlobalKeydown = (event) => {
  const el = event.target
  const tag = el?.tagName?.toLowerCase?.()
  const isTyping = tag === 'input' || tag === 'textarea' || el?.isContentEditable

  if (!isTyping && (event.ctrlKey || event.metaKey) && (event.key === 'z' || event.key === 'Z')) {
    event.preventDefault()
    handleUndo()
    return
  }
  if (!isTyping && (event.ctrlKey || event.metaKey) && (event.key === 'y' || event.key === 'Y')) {
    event.preventDefault()
    handleRedo()
    return
  }

  if (event.key === 'Escape') {
    reconnectMode.value = false
    connectDrag.value = null
    reconnectDrag.value = null
    return
  }

  // Delete with Delete or Backspace key
  if (!isTyping && (event.key === 'Delete' || event.key === 'Backspace')) {
    if (selectedEdgeId.value || selectedNodeId.value) {
      event.preventDefault()
      handleDeleteSelected()
    }
  }

  if (!selectedNodeId.value) return
  const node = nodes.value.find((n) => n.id === selectedNodeId.value)
  if (!node) return

  const isArrow = event.key === 'ArrowLeft' || event.key === 'ArrowRight' || event.key === 'ArrowUp' || event.key === 'ArrowDown'
  if (!isTyping && isArrow && !event.shiftKey) {
    const nextId = findNextNodeByDirection(selectedNodeId.value, event.key)
    if (nextId) {
      event.preventDefault()
      handleSelectNode(nextId, { focus: true })
      return
    }
  }

  const step = event.shiftKey ? 20 : 8
  const rect = canvasRef.value?.getBoundingClientRect?.()
  const maxX = rect ? rect.width - nodeWidth - 12 : Infinity
  const maxY = rect ? rect.height - nodeHeight - 12 : Infinity
  const minX = 12
  const minY = 12

  const before = { x: node.x, y: node.y }
  let next = { x: node.x, y: node.y }
  if (event.key === 'ArrowLeft') next.x = Math.max(minX, node.x - step)
  if (event.key === 'ArrowRight') next.x = Math.min(maxX, node.x + step)
  if (event.key === 'ArrowUp') next.y = Math.max(minY, node.y - step)
  if (event.key === 'ArrowDown') next.y = Math.min(maxY, node.y + step)
  if (before.x === next.x && before.y === next.y) return

  if (autoAlign.value) {
    const resolved = resolveDragCollision({
      movingId: node.id,
      proposed: { x: next.x, y: next.y },
      nodes: nodes.value,
      nodeWidth,
      nodeHeight,
      safePadding,
      gridStep,
      bounds: { minX, minY, maxX, maxY }
    })
    next = { x: resolved.x, y: resolved.y }
  }

  exec({ do: () => updateNodeById(node.id, next), undo: () => updateNodeById(node.id, before) })
}

const handleKeydown = (event) => {
  if (event.key !== 'Tab') return
  event.preventDefault()
  const ids = nodes.value.map((n) => n.id)
  if (ids.length === 0) return
  const currentIndex = Math.max(0, ids.indexOf(selectedNodeId.value))
  const nextIndex = (currentIndex + (event.shiftKey ? -1 : 1) + ids.length) % ids.length
  handleSelectNode(ids[nextIndex], { focus: true })
}

const findNextNodeByDirection = (fromId, key) => {
  const from = nodes.value.find((n) => n.id === fromId)
  if (!from) return ''
  const fromCx = from.x + nodeWidth / 2
  const fromCy = from.y + nodeHeight / 2
  let bestId = ''
  let bestScore = Infinity

  for (const cand of nodes.value) {
    if (!cand || cand.id === fromId) continue
    const cx = cand.x + nodeWidth / 2
    const cy = cand.y + nodeHeight / 2
    const dx = cx - fromCx
    const dy = cy - fromCy
    const isRight = key === 'ArrowRight' && dx > 8
    const isLeft = key === 'ArrowLeft' && dx < -8
    const isDown = key === 'ArrowDown' && dy > 8
    const isUp = key === 'ArrowUp' && dy < -8
    if (!(isRight || isLeft || isDown || isUp)) continue
    const primary = key === 'ArrowLeft' || key === 'ArrowRight' ? Math.abs(dx) : Math.abs(dy)
    const secondary = key === 'ArrowLeft' || key === 'ArrowRight' ? Math.abs(dy) : Math.abs(dx)
    const score = primary + secondary * 0.28
    if (score < bestScore) {
      bestScore = score
      bestId = cand.id
    }
  }

  return bestId
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
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) blocked[y * cols + x] = 1
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
  const dirs = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1]
  ]
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
  const startKey = start.y * cols + start.x
  const goalKey = goal.y * cols + goal.x
  const open = new Map()
  const cameFrom = new Map()
  const gScore = new Map()
  const fScore = new Map()
  const h = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y)
  const getScore = (map, key) => map.get(key) ?? Infinity
  gScore.set(startKey, 0)
  fScore.set(startKey, h(start, goal))
  open.set(startKey, start)
  const dirs = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1]
  ]

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
      if (nx < 0 || ny < 0 || nx >= grid.cols || ny >= grid.rows) continue
      const nkey = ny * cols + nx
      if (grid.blocked[nkey] && nkey !== goalKey) continue
      const tentative = currentG + 1
      if (tentative < getScore(gScore, nkey)) {
        cameFrom.set(nkey, currentKey)
        gScore.set(nkey, tentative)
        fScore.set(nkey, tentative + h({ x: nx, y: ny }, goal))
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

const pointsToBezierPath = (from, to) => {
  // Use smooth bezier curves with better control points
  const dx = to.x - from.x
  const dy = to.y - from.y
  const c1 = { x: from.x + Math.max(80, Math.min(200, dx * 0.5)), y: from.y + dy * 0.3 }
  const c2 = { x: to.x - Math.max(80, Math.min(200, dx * 0.5)), y: to.y - dy * 0.3 }
  return `M ${from.x} ${from.y} C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${to.x} ${to.y}`
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
      return { x: points[i - 1].x + (points[i].x - points[i - 1].x) * t, y: points[i - 1].y + (points[i].y - points[i - 1].y) * t }
    }
    acc += l
  }
  return points[Math.floor(points.length / 2)]
}

const getNodePorts = (nodeId) => {
  const a = getNodeAnchor(nodeId)
  const offset = 26
  return {
    out: a.out,
    outOuter: { x: a.out.x + offset, y: a.out.y },
    in: a.in,
    inOuter: { x: a.in.x, y: a.in.y - offset }
  }
}

const appendUniquePoint = (list, point) => {
  const last = list[list.length - 1]
  if (last && Math.abs(last.x - point.x) < 0.5 && Math.abs(last.y - point.y) < 0.5) return
  list.push(point)
}

const computeSmartPathPoints = (sourceId, targetId, grid) => {
  const source = getNodePorts(sourceId)
  const target = getNodePorts(targetId)
  const startCell = findNearestFree(grid, clampToGrid(grid, source.outOuter))
  const goalCell = findNearestFree(grid, clampToGrid(grid, target.inOuter))
  const cellPath = aStar(grid, startCell, goalCell)
  if (!cellPath || cellPath.length < 2) return [source.out, target.in]
  const pts = cellPath.map((c) => ({ x: c.x * grid.step + grid.step / 2, y: c.y * grid.step + grid.step / 2 }))
  pts[0] = source.outOuter
  pts[pts.length - 1] = target.inOuter
  const route = simplifyPoints(pts)
  const out = []
  appendUniquePoint(out, source.out)
  appendUniquePoint(out, source.outOuter)
  for (let i = 1; i < route.length - 1; i++) appendUniquePoint(out, route[i])
  appendUniquePoint(out, target.inOuter)
  appendUniquePoint(out, target.in)
  return out
}

const edgeRenders = computed(() => {
  const step = 18
  const grid = buildObstacleGrid(step)
  return edges.value
    .filter((e) => e.source && e.target)
    .map((e) => {
      const style = e.style ?? { color: '#22d3ee', width: 2, pattern: 'solid', shape: 'smart' }
      const endpoints = { source: getNodeAnchor(e.source).out, target: getNodeAnchor(e.target).in }
      if (style.shape === 'bezier') {
        const path = pointsToBezierPath(endpoints.source, endpoints.target)
        const labelPos = { x: (endpoints.source.x + endpoints.target.x) / 2, y: (endpoints.source.y + endpoints.target.y) / 2 }
        const labelBox = computeLabelBox(e.label)
        return { id: e.id, source: e.source, target: e.target, label: e.label ?? '', style, path, labelPos, labelBox, endpoints }
      }

      const points = computeSmartPathPoints(e.source, e.target, grid)
      const radius = style.shape === 'smooth' ? 16 : 10
      const path = pointsToRoundedPath(points, radius)
      const labelPos = computeMidPointOnPolyline(points)
      const labelBox = computeLabelBox(e.label)
      return { id: e.id, source: e.source, target: e.target, label: e.label ?? '', style, path, labelPos, labelBox, endpoints }
    })
})
</script>

<style scoped>
.c-left-sidebar {
  color: var(--left-sidebar-text, var(--c-text));
}

.c-history-item {
  transition: all 0.2s ease;
}

.c-history-item:hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  background: var(--c-surface-3) !important;
}

.c-root {
  position: relative;
  --c-bg-dark: radial-gradient(1200px 600px at 25% 15%, rgba(34, 211, 238, 0.12), transparent 55%),
    radial-gradient(900px 500px at 75% 20%, rgba(167, 139, 250, 0.12), transparent 55%),
    linear-gradient(135deg, #020617 0%, #0b1026 45%, #020617 100%);
  --c-bg-light: radial-gradient(1200px 700px at 20% 15%, rgba(15, 23, 42, 0.05), transparent 55%),
    radial-gradient(900px 520px at 80% 25%, rgba(15, 23, 42, 0.04), transparent 55%),
    linear-gradient(135deg, #f6f7fb 0%, #eef2f6 60%, #f6f7fb 100%);
  --c-bg: var(--c-bg-dark);
  --c-text: rgba(248, 250, 252, 0.96);
  --c-text-muted: rgba(226, 232, 240, 0.68);
  --c-border: rgba(255, 255, 255, 0.12);
  --c-glass-border: rgba(255, 255, 255, 0.16);
  --c-surface: rgba(255, 255, 255, 0.06);
  --c-surface-2: rgba(255, 255, 255, 0.085);
  --c-surface-3: rgba(255, 255, 255, 0.14);
  --c-shadow: 0 24px 70px rgba(0, 0, 0, 0.42);
}

.c-root[data-theme="light"] {
  --c-bg: var(--c-bg-light);
  --c-text: rgba(15, 23, 42, 0.92);
  --c-text-muted: rgba(15, 23, 42, 0.58);
  --c-border: rgba(15, 23, 42, 0.12);
  --c-glass-border: rgba(15, 23, 42, 0.10);
  --c-surface: rgba(255, 255, 255, 0.75);
  --c-surface-2: rgba(255, 255, 255, 0.86);
  --c-surface-3: rgba(255, 255, 255, 0.94);
  --c-shadow: 0 18px 56px rgba(15, 23, 42, 0.16);
}

.c-radius {
  border-radius: 12px 16px 10px 18px;
}

.c-panel {
  border-radius: 14px 22px 12px 24px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  box-shadow: var(--c-shadow);
}

.c-glass {
  background: var(--c-surface);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: inset 0 0 0 1px var(--c-glass-border);
  position: relative;
}

.c-glass::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.10), transparent 42%, rgba(255, 255, 255, 0.06));
  opacity: 0.9;
  pointer-events: none;
}

.c-root[data-theme="light"] .c-glass::before {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.05), transparent 42%, rgba(15, 23, 42, 0.04));
}

.c-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  transform: translateZ(0);
}

.c-bg[data-theme="dark"] {
  background: var(--c-bg-dark);
}

.c-bg[data-theme="light"] {
  background: var(--c-bg-light);
}

.c-bg--from {
  animation: c-bg-fade 440ms ease forwards;
}

@keyframes c-bg-fade {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

.c-root > :not(.c-bg) {
  position: relative;
  z-index: 1;
}

.c-grid {
  background-image: radial-gradient(rgba(148, 163, 184, 0.85) 1px, transparent 1px);
  background-size: 18px 18px;
  background-position: 0 0;
  filter: drop-shadow(0 0 0 rgba(0, 0, 0, 0));
}

.c-node {
  border-radius: 12px 20px 10px 22px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease, filter 220ms ease, background-color 420ms ease, color 420ms ease;
}

.c-node:hover {
  transform: translateY(-1px) scale(1.015);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.22);
}

.c-node-hover-glow {
  position: absolute;
  inset: -4px;
  border-radius: 16px 24px 14px 26px;
  background: radial-gradient(50% 40% at 50% 50%, rgba(34, 211, 238, 0.15), transparent 70%);
  filter: blur(8px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 220ms ease;
}

.c-node:hover .c-node-hover-glow {
  opacity: 1;
}

.c-node.is-selected {
  border-width: 2px;
  box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.28), 0 18px 58px rgba(34, 211, 238, 0.14), 0 28px 78px rgba(167, 139, 250, 0.12);
  transform: translateY(-2px) scale(1.01);
  filter: saturate(1.18) contrast(1.05);
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

.c-node:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.22), 0 24px 70px rgba(0, 0, 0, 0.18);
}

.c-node-glow-inner {
  position: absolute;
  inset: -2px;
  border-radius: 18px 28px 16px 30px;
  background: radial-gradient(65% 55% at 50% 45%, rgba(34, 211, 238, 0.32), transparent 62%);
  filter: blur(7px);
  opacity: 0;
  pointer-events: none;
  animation: c-glow-in 260ms ease-out forwards;
}

.c-node-glow-outer {
  position: absolute;
  inset: -14px;
  border-radius: 26px 38px 22px 40px;
  background: radial-gradient(60% 55% at 50% 50%, rgba(167, 139, 250, 0.22), transparent 65%),
    radial-gradient(70% 60% at 40% 35%, rgba(34, 211, 238, 0.18), transparent 62%);
  filter: blur(12px);
  opacity: 0;
  pointer-events: none;
  animation: c-glow-out 340ms ease-out 80ms forwards;
}

@keyframes c-glow-in {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes c-glow-out {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.c-node-pulse {
  position: absolute;
  inset: -14px;
  border-radius: 24px 34px 24px 34px;
  border: 2px solid rgba(34, 211, 238, 0.20);
  box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.25);
  pointer-events: none;
  animation: c-pulse 560ms ease-out 140ms;
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
  box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.25), 0 10px 26px rgba(34, 211, 238, 0.14);
}

.c-root button {
  transition: transform 200ms ease, box-shadow 200ms ease, background-color 200ms ease, color 200ms ease, border-color 200ms ease;
}

.c-root button:hover {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.14);
}

.c-root svg {
  shape-rendering: geometricPrecision;
}
</style>
