<template>
  <div ref="rootRef" class="c-root h-full flex flex-col transition-colors duration-[420ms] relative" :data-theme="theme" :data-font-size="fontSizeLevel" @keydown="handleKeydown">
    <div class="c-bg" :data-theme="theme" aria-hidden="true"></div>
    <div v-if="themeTransition.active" class="c-bg c-bg--from" :data-theme="themeTransition.from" aria-hidden="true"></div>

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

    <header 
      v-if="!isFullscreen"
      class="c-glass h-16 px-6 flex items-center justify-between border-b transition-colors duration-[420ms]"
    >
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
        <span class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">拖拽节点下方手柄创建连线 · 将连线拖到节点上方圆点完成连接</span>
      </div>
    </header>

    <div class="flex-1 min-h-0 flex transition-all duration-[420ms] relative" :class="isFullscreen ? 'p-0 gap-0' : 'p-4 gap-4'">
      <aside 
        class="c-left-sidebar c-panel c-glass shadow-2xl overflow-hidden flex flex-col min-h-0 transition-all duration-300 relative"
        :class="leftSidebarCollapsed ? 'w-0 border-0 opacity-0' : 'w-72'"
      >
        <div class="px-4 py-3 flex items-center justify-between border-b border-[var(--c-border)] transition-colors duration-[420ms]">
          <div class="text-sm font-semibold transition-colors duration-[420ms]">历史记录</div>
          <button class="text-xs text-[var(--c-text-muted)] hover:text-[var(--c-text)] transition duration-200" @click="handleClearHistories">清空</button>
        </div>
        <div class="flex-1 min-h-0 overflow-auto p-3 space-y-3">
          <div
            v-for="item in histories"
            :key="item.id"
            class="c-history-item c-radius border px-3 py-2.5 cursor-pointer transition duration-200"
            :class="item.id === selectedHistoryId ? 'border-cyan-400/30 bg-cyan-400/10' : 'border-[var(--c-border)] bg-[var(--c-surface-2)]'"
            @click="handleSelectHistory(item.id)"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="text-sm font-medium text-[var(--c-text)] transition-colors duration-[420ms]">{{ item.title }}</div>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-400/10 border border-emerald-400/20 text-emerald-200 whitespace-nowrap">{{ item.status }}</span>
            </div>
            <div class="mt-2 flex items-center justify-between flex-wrap gap-2">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">{{ item.time }}</div>
              <button class="text-xs text-rose-200/80 hover:text-rose-200 transition" @click.stop="handleDeleteHistory(item.id)">删除</button>
            </div>
          </div>
        </div>
      </aside>

      <!-- Left Sidebar Toggle Button -->
      <div 
        class="flex items-center justify-center w-10 h-full cursor-pointer hover:bg-white/5 transition-colors group z-20"
        @click="toggleLeftSidebar"
        :title="leftSidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
      >
        <div class="w-4 h-24 rounded-full bg-[var(--c-border)] group-hover:bg-cyan-400/50 transition-colors flex items-center justify-center shadow-lg">
          <svg 
            class="w-8 h-8 text-[var(--c-text-muted)] group-hover:text-cyan-400 transition-transform duration-300"
            :class="leftSidebarCollapsed ? 'rotate-180' : ''"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </div>
      </div>

      <main class="flex-1 min-w-0 min-h-0 flex flex-col transition-all duration-[420ms] relative" :class="isFullscreen ? 'gap-0' : 'gap-3'">
        <div 
          class="c-panel c-glass shadow-2xl px-3 h-14 flex items-center justify-between transition-colors duration-[420ms] z-50"
          :class="isFullscreen ? 'rounded-none border-x-0 border-t-0' : ''"
        >
          <div class="flex items-center gap-2 h-full">
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 disabled:opacity-40" :disabled="!canUndo" @click="handleUndo">撤销</button>
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 disabled:opacity-40" :disabled="!canRedo" @click="handleRedo">重做</button>
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200" @click="handleAddNode">新增节点</button>
            <div class="relative gate-menu-container h-full flex items-center">
              <button
                class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200"
                @click.stop="showGateMenu = !showGateMenu"
              >新增逻辑门</button>
              <div
                v-if="showGateMenu"
                class="absolute top-[calc(100%-6px)] left-1/2 -translate-x-1/2 w-44 c-glass border border-[var(--c-border)] rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-[9999] overflow-hidden pointer-events-auto"
                @click.stop
              >
                <button @click="handleAddGate('AND')" class="w-full px-4 py-3 text-left text-sm text-[var(--c-text)] hover:bg-cyan-500/20 transition-colors flex items-center justify-between">
                  <span>与门</span>
                  <span class="text-xs text-[var(--c-text-muted)]">AND</span>
                </button>
                <button @click="handleAddGate('OR')" class="w-full px-4 py-3 text-left text-sm text-[var(--c-text)] border-t border-[var(--c-border)] hover:bg-violet-500/20 transition-colors flex items-center justify-between">
                  <span>或门</span>
                  <span class="text-xs text-[var(--c-text-muted)]">OR</span>
                </button>
              </div>
            </div>
            <button class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 disabled:opacity-40" :disabled="!selectedNodeId && !selectedEdgeId" @click="handleDeleteSelected">删除</button>
            <div class="w-[1px] h-4 bg-[var(--c-border)] mx-1"></div>
            
            <!-- Export Button Container - Restored h-full and flex items-center for vertical centering -->
            <div class="relative export-menu-container h-full flex items-center">
              <button 
                class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 flex items-center justify-center gap-1.5 disabled:opacity-50"
                @click.stop="showExportMenu = !showExportMenu"
                :disabled="isExporting"
              >
                <svg v-if="!isExporting" class="w-4 h-4 flex-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <svg v-else class="w-4 h-4 animate-spin flex-none" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="whitespace-nowrap">{{ isExporting ? '...' : '导出' }}</span>
              </button>
              
              <!-- Export Dropdown - Positioned relative to the toolbar bottom to ensure "sticker" effect over canvas -->
              <div 
                v-if="showExportMenu" 
                class="absolute top-[calc(100%-6px)] left-1/2 -translate-x-1/2 w-48 c-glass border border-[var(--c-border)] rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-[9999] overflow-hidden pointer-events-auto"
                @click.stop
              >
                <button @click="exportAsImage" class="w-full px-4 py-3 text-left text-sm text-[var(--c-text)] hover:bg-cyan-500/20 transition-colors flex items-center gap-3">
                  <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  <span>导出为图片</span>
                </button>
                <button @click="exportAsPDF" class="w-full px-4 py-3 text-left text-sm text-[var(--c-text)] border-t border-[var(--c-border)] hover:bg-violet-500/20 transition-colors flex items-center gap-3">
                  <svg class="w-4 h-4 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 9h1v2h-1zM9 13h1v2h-1zM12 9h1v2h-1zM12 13h1v2h-1z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  <span>导出为 PDF</span>
                </button>
              </div>
            </div>

            <div class="w-[1px] h-4 bg-[var(--c-border)] mx-1"></div>
            <div class="flex items-center gap-1 bg-[var(--c-surface-2)] p-1 c-radius border border-[var(--c-border)]">
              <button 
                v-for="lvl in fontSizeLevels"
                :key="lvl.value"
                @click="setFontSize(lvl.value)"
                class="px-2.5 py-1 text-xs rounded-md transition-all duration-200"
                :class="fontSizeLevel === lvl.value ? 'bg-cyan-500 text-white shadow-lg' : 'text-[var(--c-text-muted)] hover:text-[var(--c-text)] hover:bg-[var(--c-surface-3)]'"
              >
                {{ lvl.label }}
              </button>
            </div>
            <div class="w-[1px] h-4 bg-[var(--c-border)] mx-1"></div>
            <button 
              class="px-3 py-1.5 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 flex items-center gap-1.5" 
              @click="toggleFullscreen"
              :title="isFullscreen ? '退出全屏' : '沉浸式模式'"
            >
              <svg v-if="!isFullscreen" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>{{ isFullscreen ? '退出沉浸' : '沉浸模式' }}</span>
            </button>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">Ctrl+Z/Ctrl+Y · Tab/方向键/Del</span>
          </div>
        </div>

        <div 
          class="flex-1 min-h-0 c-panel c-glass shadow-2xl overflow-hidden transition-all duration-[420ms]"
          :class="isFullscreen ? 'rounded-none border-0 shadow-none' : ''"
        >
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
                  <feGaussianBlur stdDeviation="3" result="blur"></feGaussianBlur>
                  <feMerge>
                    <feMergeNode in="blur"></feMergeNode>
                    <feMergeNode in="SourceGraphic"></feMergeNode>
                  </feMerge>
                </filter>
              </defs>

              <g v-for="edge in edgeRenders" :key="edge.id">
                <path
                  v-if="edge.selectable && edge.id === selectedEdgeId"
                  :d="edge.path"
                  fill="none"
                  :stroke="edge.style.color"
                  :stroke-width="edge.style.width + 10"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  opacity="0.18"
                />
                <path
                  v-if="edge.selectable && edge.id === selectedEdgeId"
                  :d="edge.path"
                  fill="none"
                  :stroke="edge.style.color"
                  :stroke-width="edge.style.width + 6"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  opacity="0.28"
                />
                <path
                  :d="edge.path"
                  fill="none"
                  :stroke="edge.style.color"
                  :stroke-width="edge.style.width"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  :class="edge.selectable ? 'cursor-pointer' : 'pointer-events-none'"
                  @click.stop="edge.selectable && handleSelectEdge(edge.id)"
                />
                <path v-if="edge.selectable" :d="edge.path" fill="none" stroke="transparent" stroke-width="14" class="cursor-pointer" @click.stop="handleSelectEdge(edge.id)" />
                <g v-if="edge.selectable && edge.id === selectedEdgeId">
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
              </g>

              <path
                v-if="connectDrag"
                :d="connectPreviewPath"
                fill="none"
                stroke="rgba(34, 211, 238, 0.9)"
                stroke-width="3"
                stroke-linecap="round"
              />
              <path
                v-if="reconnectDrag"
                :d="reconnectPreviewPath"
                fill="none"
                stroke="rgba(167, 139, 250, 0.9)"
                stroke-width="3"
                stroke-linecap="round"
              />
            </svg>

            <ParticleBurst ref="particleRef" class="absolute inset-0 z-30 pointer-events-none" :enabled="particleEnabled" :gravity-decay="0.98" :life-ms="800" :count="20"></ParticleBurst>

            <template v-for="node in nodes" :key="node.id">
              <div
                v-if="node.type === 'gate'"
                class="c-gate-node absolute z-20 select-none cursor-grab active:cursor-grabbing transition duration-200 flex items-center justify-center"
                :class="node.id === selectedNodeId ? 'is-selected' : ''"
                :style="{ left: node.x + 'px', top: node.y + 'px', width: gateWidth + 'px', height: gateHeight + 'px' }"
                @mousedown="handleNodeMouseDown(node, $event)"
                @click.stop="handleSelectNode(node.id, { focus: true })"
                @focus="handleSelectNode(node.id, { effects: false })"
                @keydown.enter.prevent="handleSelectNode(node.id, { focus: true })"
                @keydown.space.prevent="handleSelectNode(node.id, { focus: true })"
                :data-node-id="node.id"
                tabindex="0"
                role="button"
                :aria-label="`逻辑门 ${node.gate}，按 Enter 选中`"
              >
                <span class="c-node-glow-inner" v-if="node.id === selectedNodeId" :key="'g1-' + nodeEffectKey"></span>
                <span class="c-node-glow-outer" v-if="node.id === selectedNodeId" :key="'g2-' + nodeEffectKey"></span>
                <span class="c-node-pulse" v-if="node.id === selectedNodeId" :key="'p-' + nodeEffectKey"></span>
                <svg class="w-full h-full" viewBox="0 0 120 80" fill="none">
                  <path
                    v-if="node.gate === 'AND'"
                    d="M 14 72 L 14 42 C 14 24 32 12 60 12 C 88 12 106 24 106 42 L 106 72 Z"
                    fill="rgba(59, 130, 246, 0.20)"
                    stroke="rgba(37, 99, 235, 0.95)"
                    stroke-width="3.2"
                  />
                  <path
                    v-else
                    d="M 16 72 C 26 46 40 24 60 16 C 80 24 94 46 104 72 C 88 66 74 64 60 64 C 46 64 32 66 16 72 Z"
                    fill="rgba(249, 115, 22, 0.20)"
                    stroke="rgba(234, 88, 12, 0.95)"
                    stroke-width="3.2"
                  />
                  <text
                    x="60"
                    y="50"
                    text-anchor="middle"
                    font-size="22"
                    font-weight="700"
                    fill="var(--c-text)"
                  >{{ node.gate }}</text>
                </svg>
                <div
                  class="c-handle absolute left-1/2 -translate-x-1/2 -bottom-3 w-9 h-9 rounded-full border-2 border-cyan-300/40 bg-cyan-400/20 hover:bg-cyan-400/40 cursor-crosshair flex items-center justify-center z-20"
                  title="点击创建连线"
                  role="button"
                  :data-node-id="node.id"
                  data-handle="out"
                  @mousedown.stop
                  @click.stop="handleStartConnect(node.id, $event, 'out')"
                >
                  <div class="w-3.5 h-3.5 rounded-full bg-cyan-300 shadow-[0_0_8px_rgba(34,211,238,0.6)]"></div>
                </div>
                <div
                  class="c-handle absolute left-1/2 -translate-x-1/2 -top-3 w-9 h-9 rounded-full border-2 border-violet-300/40 bg-violet-400/15 hover:bg-violet-400/30 cursor-crosshair flex items-center justify-center z-20"
                  title="点击此处或节点完成连接"
                  role="button"
                  :data-node-id="node.id"
                  data-handle="in"
                  @mousedown.stop
                  @click.stop="handleStartConnect(node.id, $event, 'in')"
                >
                  <div class="w-3.5 h-3.5 rounded-full bg-violet-300/60"></div>
                </div>
              </div>

              <div
                v-else
                class="c-node absolute z-10 border-2 shadow-xl select-none cursor-grab active:cursor-grabbing p-4 transition duration-200 flex flex-col justify-center"
                :class="[
                  node.id === selectedNodeId ? 'is-selected' : '',
                  node.type === 'top' ? 'border-rose-600 bg-rose-50' : '',
                  node.type === 'middle' ? 'border-sky-700 bg-sky-50' : '',
                  node.type === 'basic' ? 'border-emerald-700 bg-emerald-50' : ''
                ]"
                :style="{ left: node.x + 'px', top: node.y + 'px' }"
                @mousedown="handleNodeMouseDown(node, $event)"
                @click.stop="handleSelectNode(node.id, { focus: true })"
                @focus="handleSelectNode(node.id, { effects: false })"
                @keydown.enter.prevent="handleSelectNode(node.id, { focus: true })"
                @keydown.space.prevent="handleSelectNode(node.id, { focus: true })"
                :data-node-id="node.id"
                tabindex="0"
                role="button"
                :aria-label="`节点 ${node.label}，按 Enter 选中，按 Shift+方向键移动`"
              >
                <span class="c-node-glow-inner" v-if="node.id === selectedNodeId" :key="'g1-' + nodeEffectKey"></span>
                <span class="c-node-glow-outer" v-if="node.id === selectedNodeId" :key="'g2-' + nodeEffectKey"></span>
                <span class="c-node-pulse" v-if="node.id === selectedNodeId" :key="'p-' + nodeEffectKey"></span>
                <span class="c-node-hover-glow" v-if="node.id !== selectedNodeId"></span>
                <div class="flex items-center justify-between text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms] gap-2">
                  <div class="font-semibold text-[var(--c-text)]/90 transition-colors duration-[420ms] whitespace-nowrap">{{ nodeTypeText(node.type) }}</div>
                  <div class="px-2 py-0.5 rounded-full bg-[var(--c-surface-2)]/70 border border-[var(--c-border)] font-semibold text-[var(--c-text)]/85 transition-colors duration-[420ms] whitespace-nowrap">{{ node.probability }}</div>
                </div>
                <div class="mt-2 text-sm font-semibold text-[var(--c-text)] transition-colors duration-[420ms] leading-snug">{{ node.label }}</div>
            
                <div
                  class="c-handle absolute left-1/2 -translate-x-1/2 -bottom-4 w-10 h-10 rounded-full border-2 border-cyan-300/40 bg-cyan-400/20 hover:bg-cyan-400/40 cursor-crosshair flex items-center justify-center z-20"
                  title="点击创建连线"
                  role="button"
                  :data-node-id="node.id"
                  data-handle="out"
                  @mousedown.stop
                  @click.stop="handleStartConnect(node.id, $event, 'out')"
                >
                  <div class="w-4 h-4 rounded-full bg-cyan-300 shadow-[0_0_8px_rgba(34,211,238,0.6)]"></div>
                </div>
                <div
                  class="c-handle absolute left-1/2 -translate-x-1/2 -top-4 w-10 h-10 rounded-full border-2 border-violet-300/40 bg-violet-400/15 hover:bg-violet-400/30 cursor-crosshair flex items-center justify-center z-20"
                  title="点击此处或节点完成连接"
                  role="button"
                  :data-node-id="node.id"
                  data-handle="in"
                  @mousedown.stop
                  @click.stop="handleStartConnect(node.id, $event, 'in')"
                >
                  <div class="w-4 h-4 rounded-full bg-violet-300/60"></div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </main>

      <!-- Right Sidebar Overlay Container -->
      <div 
        class="fixed right-0 top-0 bottom-0 flex z-[100]"
        :class="[
          isFullscreen ? 'h-screen' : 'h-full !absolute',
          isResizingRight ? 'transition-none pointer-events-auto' : 'transition-all duration-[420ms]'
        ]"
      >
        <!-- Right Sidebar Toggle Button (similar to left) -->
        <div 
          class="flex items-center justify-center w-10 h-full cursor-pointer hover:bg-white/5 transition-colors group z-20"
          @click="toggleRightSidebar"
          :title="rightSidebarCollapsed ? '展开右侧栏' : '收起右侧栏'"
        >
          <div class="w-4 h-24 rounded-full bg-[var(--c-border)] group-hover:bg-cyan-400/50 transition-colors flex items-center justify-center shadow-lg">
            <svg 
              class="w-8 h-8 text-[var(--c-text-muted)] group-hover:text-cyan-400 transition-transform duration-300"
              :class="rightSidebarCollapsed ? '' : 'rotate-180'"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"
            >
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </div>
        </div>

        <!-- Resizer Handle - Only visible when not collapsed -->
        <div 
          v-if="!rightSidebarCollapsed"
          class="w-2 h-full cursor-col-resize hover:bg-cyan-400/40 transition-colors flex items-center justify-center group bg-black/5 backdrop-blur-sm border-l border-[var(--c-border)] select-none"
          @mousedown="startResizingRight"
        >
          <div class="w-1 h-24 rounded-full bg-[var(--c-border)] group-hover:bg-cyan-400/60 transition-colors shadow-sm"></div>
        </div>

        <aside 
          class="c-panel c-glass shadow-2xl overflow-hidden flex flex-col min-h-0 border-l border-[var(--c-border)] rounded-none"
          :class="[
            isResizingRight ? 'transition-none' : 'transition-all duration-300',
            rightSidebarCollapsed ? 'w-0 border-0 opacity-0 invisible' : ''
          ]"
          :style="{ width: rightSidebarCollapsed ? '0px' : rightSidebarWidth + 'px' }"
        >
          <div class="px-4 py-3 flex items-center justify-between border-b border-[var(--c-border)] transition-colors duration-[420ms]">
            <div class="text-sm font-semibold text-[var(--c-text)] transition-colors duration-[420ms]">{{ selectedEdgeId ? '连线信息' : selectedNodeId ? '节点信息' : '专家辅助系统' }}</div>
            <button class="text-xs text-[var(--c-text-muted)] hover:text-[var(--c-text)] transition duration-200 disabled:opacity-40" :disabled="!selectedNodeId && !selectedEdgeId" @click="clearSelection">关闭</button>
          </div>

          <!-- AI Chat Panel - Default when no node/edge selected -->
          <div v-if="!selectedNodeId && !selectedEdgeId" class="flex-1 flex flex-col min-h-0">
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
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3.005 0 013.75-2.906z"></path></svg>
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
                <span class="text-sm font-semibold text-[var(--c-text)]">Selected: {{ isGateSelected ? (nodeForm.gate + ' 门') : nodeForm.label }}</span>
              </div>
            </div>
            
            <div v-if="!isGateSelected" class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">节点名称</div>
              <input v-model="nodeForm.label" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @blur="commitNodeForm" />
            </div>
            
            <div v-if="!isGateSelected" class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">事件类型</div>
              <select v-model="nodeForm.type" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @change="commitNodeForm">
                <option value="top" style="background: #ffffff; color: #0f172a;">顶事件</option>
                <option value="middle" style="background: #ffffff; color: #0f172a;">中间事件</option>
                <option value="basic" style="background: #ffffff; color: #0f172a;">基本事件</option>
              </select>
            </div>
            <div v-if="isGateSelected" class="space-y-1.5">
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
            <div v-if="!isGateSelected" class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">概率</div>
              <input v-model.number="nodeForm.probability" type="number" step="0.001" min="0" max="1" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @change="commitNodeForm" />
            </div>
            <div v-if="!isGateSelected" class="space-y-1.5">
              <div class="text-xs text-[var(--c-text-muted)] transition-colors duration-[420ms]">来源</div>
              <input v-model="nodeForm.source" placeholder="例如：文档抽取 / 手工输入 / 外部系统" class="w-full px-3 py-2 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" @blur="commitNodeForm" />
            </div>
            <button
              class="w-full px-3 py-2 c-radius border transition"
              :class="isGateSelected ? 'bg-rose-600/30 border-rose-400/45 text-rose-100 hover:bg-rose-600/40' : 'bg-red-600/70 border-red-300/60 text-white hover:bg-red-600/80'"
              @click="handleDeleteSelected"
            >删除</button>
            <div class="text-xs text-[var(--c-text-muted)] text-center mt-2">或按 Delete 键删除</div>
          </div>

          <div v-else class="p-4 text-sm text-[var(--c-text-muted)] transition-colors duration-[420ms]">选择画布中的节点或连线以编辑属性</div>
        </aside>
      </div>
    </div>

    <footer 
      v-if="!isFullscreen"
      class="c-glass p-4 border-t border-[var(--c-border)] transition-colors duration-[420ms]"
    >
      <div class="flex items-start gap-3">
        <textarea v-model="inputText" rows="3" class="flex-1 min-w-0 px-4 py-3 c-radius bg-[var(--c-surface-2)] border border-[var(--c-border)] text-[var(--c-text)] placeholder-[var(--c-text-muted)]/60 focus:outline-none focus:ring-2 focus:ring-cyan-400/20 transition-colors duration-[420ms]" placeholder="上传文本 → 抽取 → 生成 → 人工调整 → 导出"></textarea>
        <div class="flex flex-col items-start gap-1">
          <label class="px-3.5 py-2 c-radius c-glass border border-[var(--c-border)] text-[var(--c-text)] hover:bg-[var(--c-surface-3)] transition duration-200 cursor-pointer">
            上传 .json/.txt
            <input type="file" accept=".json,.txt,application/json,text/plain" class="hidden" @change="handleNativeFileChange" />
          </label>
          <div v-if="uploadDisplay" class="text-[11px] text-[var(--c-text-muted)] transition-colors duration-[420ms] whitespace-nowrap">{{ uploadDisplay }}</div>
        </div>
        <button
          class="px-3.5 py-2 c-radius border transition disabled:opacity-60 disabled:cursor-not-allowed"
          :class="hasUploadedSuccess ? 'bg-cyan-500/55 border-cyan-300/65 text-cyan-50 hover:bg-cyan-500/65' : 'bg-cyan-500/20 border-cyan-400/25 text-cyan-100 hover:bg-cyan-500/28'"
          :disabled="!canGenerate"
          @click="handleGenerateFromJson"
        >生成</button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import * as htmlToImage from 'html-to-image'
import { jsPDF } from 'jspdf'
import ParticleBurst from './ParticleBurst.vue'
import { HistoryManager, canAddEdge, createIncrementId, defaultClone, deleteEdge, deleteNodeAndRelatedEdges, normalizeEdgeStyle, pointsToPolylinePath, resolveDragCollision, snapToGrid } from './naiveTailwindCore'

const props = defineProps({
  initialAutoAlign: { type: Boolean, default: true },
  initialAllowMultipleEdges: { type: Boolean, default: false },
  initialParticleEnabled: { type: Boolean, default: true }
})

const fontSizeLevel = ref('lg') // 'xs', 'sm', 'lg', 'xl'
const fontSizeLevels = [
  { label: '小', value: 'xs' },
  { label: '中', value: 'sm' },
  { label: '大', value: 'lg' },
  { label: '超大', value: 'xl' }
]

const nodeWidth = computed(() => {
  if (fontSizeLevel.value === 'xs') return 190
  if (fontSizeLevel.value === 'sm') return 220
  if (fontSizeLevel.value === 'lg') return 280
  if (fontSizeLevel.value === 'xl') return 380
  return 220
})

const nodeHeight = computed(() => {
  if (fontSizeLevel.value === 'xs') return 80
  if (fontSizeLevel.value === 'sm') return 92
  if (fontSizeLevel.value === 'lg') return 120
  if (fontSizeLevel.value === 'xl') return 180
  return 92
})

const setFontSize = (level) => {
  fontSizeLevel.value = level
  toast(`已切换字号：${fontSizeLevels.find(l => l.value === level).label}`, 'info')
}

const histories = ref([
  { id: 'h-1', title: '空压机无法启动', time: '2026/03/16 09:12', status: 'done' },
  { id: 'h-2', title: '电机过热报警', time: '2026/03/15 16:33', status: 'done' },
  { id: 'h-3', title: '控制回路异常', time: '2026/03/14 11:08', status: 'done' }
])

const selectedHistoryId = ref(histories.value[0]?.id ?? '')
const connectMode = ref(false)
const inputText = ref('')
const uploadState = reactive({ fileName: '', status: 'idle', progress: 0, text: '' })
const uploadDisplay = computed(() => {
  if (!uploadState.fileName) return ''
  if (uploadState.status === 'reading') return `${uploadState.fileName}...${uploadState.progress}%`
  if (uploadState.status === 'done') return `${uploadState.fileName}...√`
  if (uploadState.status === 'error') return `${uploadState.fileName}...×`
  return ''
})
const hasUploadedSuccess = computed(() => uploadState.status === 'done' && !!uploadState.fileName && String(uploadState.text || '').trim().length > 0)
const canGenerate = computed(() => hasUploadedSuccess.value || String(inputText.value || '').trim().length > 0)
const theme = ref('light')
const themeTransition = reactive({ active: false, from: 'light', timer: 0 })
const soundEnabled = ref(false)
const nodeEffectKey = ref(0)
const autoAlign = ref(true) // Default: enabled
const allowMultipleEdges = ref(false) // Default: single edge mode
const particleEnabled = ref(true) // Default: enabled
const particleRef = ref(null)

const rootRef = ref(null)
const isFullscreen = ref(false)
const savedTheme = ref('light')

const leftSidebarCollapsed = ref(false)
const rightSidebarCollapsed = ref(false)
const rightSidebarWidth = ref(450)
const isResizingRight = ref(false)

const toggleLeftSidebar = () => {
  leftSidebarCollapsed.value = !leftSidebarCollapsed.value
}

const toggleRightSidebar = () => {
  rightSidebarCollapsed.value = !rightSidebarCollapsed.value
}

const startResizingRight = (e) => {
  isResizingRight.value = true
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  window.addEventListener('mousemove', handleResizingRight)
  window.addEventListener('mouseup', stopResizingRight)
}

const handleResizingRight = (e) => {
  if (!isResizingRight.value) return
  // Calculate width relative to the right edge of the window for stability
  const newWidth = window.innerWidth - e.clientX
  // Limit the width from 200px to almost full screen width
  const maxWidth = window.innerWidth - 48
  if (newWidth > 200 && newWidth < maxWidth) {
    rightSidebarWidth.value = newWidth
  }
}

const stopResizingRight = () => {
  isResizingRight.value = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', handleResizingRight)
  window.removeEventListener('mouseup', stopResizingRight)
}

const isExporting = ref(false)
const showExportMenu = ref(false)
const showGateMenu = ref(false)

const computeGraphBounds = () => {
  const pad = 28
  if (!nodes.value.length) {
    return { minX: 0, minY: 0, maxX: canvasSize.value.width, maxY: canvasSize.value.height, width: canvasSize.value.width, height: canvasSize.value.height, pad }
  }
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  for (const n of nodes.value) {
    if (!n) continue
    const w = n.type === 'gate' ? gateWidth.value : nodeWidth.value
    const h = n.type === 'gate' ? gateHeight.value : nodeHeight.value
    minX = Math.min(minX, n.x)
    minY = Math.min(minY, n.y)
    maxX = Math.max(maxX, n.x + w)
    maxY = Math.max(maxY, n.y + h)
  }
  const width = Math.max(1, Math.ceil(maxX - minX + pad * 2))
  const height = Math.max(1, Math.ceil(maxY - minY + pad * 2))
  return { minX, minY, maxX, maxY, width, height, pad }
}

const renderGraphToPng = async ({ pixelRatio = 2, maxSide = 4096, maxScale = 3, maxCanvasSide = 8192 } = {}) => {
  if (!canvasRef.value) return ''
  const { minX, minY, width, height, pad } = computeGraphBounds()
  const baseScale = (() => {
    const s = Math.min(maxSide / width, maxSide / height)
    if (!Number.isFinite(s) || s <= 0) return 1
    return Math.min(maxScale, s)
  })()

  const clampToCanvas = (s) => {
    const maxS = Math.min(maxCanvasSide / width, maxCanvasSide / height)
    if (!Number.isFinite(maxS) || maxS <= 0) return 1
    return Math.min(s, maxS)
  }

  const scale = clampToCanvas(baseScale)
  const outW = Math.max(1, Math.round(width * scale))
  const outH = Math.max(1, Math.round(height * scale))
  const safePixelRatio = (() => {
    const pr = Math.min(pixelRatio, maxCanvasSide / outW, maxCanvasSide / outH)
    if (!Number.isFinite(pr) || pr <= 0) return 1
    return Math.max(1, Math.min(pixelRatio, pr))
  })()
  const tx = -minX + pad
  const ty = -minY + pad
  return await htmlToImage.toPng(canvasRef.value, {
    backgroundColor: theme.value === 'dark' ? '#020617' : '#f6f7fb',
    pixelRatio: safePixelRatio,
    cacheBust: true,
    width: outW,
    height: outH,
    style: {
      width: `${canvasSize.value.width}px`,
      height: `${canvasSize.value.height}px`,
      transformOrigin: 'top left',
      transform: `scale(${scale}) translate(${tx}px, ${ty}px)`
    }
  })
}

const exportAsImage = async () => {
  if (!canvasRef.value) return
  isExporting.value = true
  showExportMenu.value = false
  try {
    const maxSide = Math.min(5200, Math.max(1800, Math.max(window.innerWidth || 0, window.innerHeight || 0) * 2.2))
    const dataUrl = await renderGraphToPng({ pixelRatio: 2, maxSide, maxScale: 3, maxCanvasSide: 8192 })
    if (!dataUrl) {
      toast('图片导出失败', 'error')
      return
    }
    const link = document.createElement('a')
    link.download = `故障树-${new Date().getTime()}.png`
    link.href = dataUrl
    document.body.appendChild(link)
    link.click()
    link.remove()
    toast('图片导出成功', 'success')
  } catch (err) {
    console.error('Export error:', err)
    toast(`图片导出失败：${err?.message || err}`, 'error')
  } finally {
    isExporting.value = false
  }
}

const exportAsPDF = async () => {
  if (!canvasRef.value) return
  isExporting.value = true
  showExportMenu.value = false
  try {
    const maxSide = Math.min(5200, Math.max(1800, Math.max(window.innerWidth || 0, window.innerHeight || 0) * 2.2))
    const dataUrl = await renderGraphToPng({ pixelRatio: 2, maxSide, maxScale: 3, maxCanvasSide: 8192 })
    if (!dataUrl) {
      toast('PDF 导出失败', 'error')
      return
    }
    const { width, height } = computeGraphBounds()
    const scale = (() => {
      const s = Math.min(maxSide / width, maxSide / height)
      if (!Number.isFinite(s) || s <= 0) return 1
      return Math.min(4, s)
    })()
    const outW = Math.max(1, Math.round(width * scale))
    const outH = Math.max(1, Math.round(height * scale))
    
    const pdf = new jsPDF({
      orientation: outW >= outH ? 'landscape' : 'portrait',
      unit: 'px',
      format: [outW, outH]
    })
    
    pdf.addImage(dataUrl, 'PNG', 0, 0, outW, outH)
    pdf.save(`故障树-${new Date().getTime()}.pdf`)
    toast('PDF 导出成功', 'success')
  } catch (err) {
    console.error('PDF Export error:', err)
    toast(`PDF 导出失败：${err?.message || err}`, 'error')
  } finally {
    isExporting.value = false
  }
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    if (rootRef.value) {
      savedTheme.value = theme.value
      rootRef.value.requestFullscreen().catch(err => {
        toast(`无法进入全屏模式: ${err.message}`, 'error')
      })
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
  if (!isFullscreen.value) {
    theme.value = savedTheme.value // Restore original theme
  }
}

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

const safePadding = 8
const gridStep = 18

const gateWidth = computed(() => {
  return Math.max(120, Math.round(nodeWidth.value * 0.72))
})

const gateHeight = computed(() => {
  return Math.max(72, Math.round(nodeHeight.value * 0.80))
})

const getNodeSizeForCollision = (n) => {
  if (n?.type === 'gate') return { width: gateWidth.value, height: gateHeight.value }
  return { width: nodeWidth.value, height: nodeHeight.value }
}

const nodes = ref([
  { id: 'N-1', label: '空压机无法启动', type: 'top', probability: 0.01, source: '', x: 360, y: 40 },
  { id: 'G-1', type: 'gate', gate: 'OR', x: 440, y: 160 },
  { id: 'N-2', label: '控制系统故障', type: 'middle', probability: 0.02, source: '', x: 160, y: 220 },
  { id: 'N-3', label: '电源异常', type: 'middle', probability: 0.03, source: '', x: 360, y: 220 },
  { id: 'N-4', label: '机械卡阻', type: 'middle', probability: 0.01, source: '', x: 560, y: 220 },
  { id: 'G-2', type: 'gate', gate: 'AND', x: 240, y: 340 },
  { id: 'N-5', label: 'PLC 通讯异常', type: 'basic', probability: 0.004, source: '', x: 80, y: 420 },
  { id: 'N-6', label: '压力传感器异常', type: 'basic', probability: 0.006, source: '', x: 240, y: 420 }
])

const edges = ref([
  { id: 'E-1', source: 'N-1', target: 'G-1', style: { color: 'rgba(251, 191, 36, 0.85)', width: 4 } },
  { id: 'E-2', source: 'G-1', target: 'N-2', style: { color: '#22d3ee', width: 4 } },
  { id: 'E-3', source: 'G-1', target: 'N-3', style: { color: '#a78bfa', width: 4 } },
  { id: 'E-4', source: 'G-1', target: 'N-4', style: { color: '#38bdf8', width: 4 } },
  { id: 'E-5', source: 'N-2', target: 'G-2', style: { color: 'rgba(251, 191, 36, 0.85)', width: 4 } },
  { id: 'E-6', source: 'G-2', target: 'N-5', style: { color: '#34d399', width: 4 } },
  { id: 'E-7', source: 'G-2', target: 'N-6', style: { color: '#34d399', width: 4 } }
])

const selectedNodeId = ref('N-3')
const selectedNode = computed(() => nodes.value.find((n) => n.id === selectedNodeId.value) ?? null)
const isGateSelected = computed(() => selectedNode.value?.type === 'gate')
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
  color: '#22d3ee',
  width: 4
})

const toPickerColor = (color) => {
  const c = String(color || '').trim()
  if (/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(c)) return c
  const m = c.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i)
  if (m) {
    const toHex2 = (n) => String(Math.max(0, Math.min(255, Number(n) || 0)).toString(16)).padStart(2, '0')
    return `#${toHex2(m[1])}${toHex2(m[2])}${toHex2(m[3])}`
  }
  return '#22d3ee'
}

const parseColorToRgb = (color) => {
  const c = String(color || '').trim()
  if (!c) return null
  const m = c.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i)
  if (m) return { r: Number(m[1]), g: Number(m[2]), b: Number(m[3]) }
  const h = c.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i)
  if (!h) return null
  const hex = h[1].toLowerCase()
  if (hex.length === 3) {
    const r = parseInt(hex[0] + hex[0], 16)
    const g = parseInt(hex[1] + hex[1], 16)
    const b = parseInt(hex[2] + hex[2], 16)
    return { r, g, b }
  }
  const r = parseInt(hex.slice(0, 2), 16)
  const g = parseInt(hex.slice(2, 4), 16)
  const b = parseInt(hex.slice(4, 6), 16)
  return { r, g, b }
}

const isYellowishColor = (color) => {
  const rgb = parseColorToRgb(color)
  if (!rgb) return false
  return rgb.r >= 200 && rgb.g >= 160 && rgb.b <= 120
}

const nodeForm = reactive({
  label: '',
  type: 'middle',
  gate: 'AND',
  probability: 0.001,
  source: ''
})

watch(
  selectedNodeId,
  () => {
    if (!selectedNode.value) {
      nodeForm.label = ''
      nodeForm.type = 'middle'
      nodeForm.gate = 'AND'
      nodeForm.probability = 0.001
      nodeForm.source = ''
      return
    }
    nodeForm.label = selectedNode.value.label ?? ''
    nodeForm.type = selectedNode.value.type
    nodeForm.gate = selectedNode.value.gate ?? 'AND'
    nodeForm.probability = selectedNode.value.probability ?? 0.001
    nodeForm.source = selectedNode.value.source ?? ''
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
      edgeForm.color = '#22d3ee'
      edgeForm.width = 4
      return
    }
    edgeForm.id = selectedEdge.value.id
    edgeForm.source = selectedEdge.value.source
    edgeForm.target = selectedEdge.value.target
    const style = normalizeEdgeStyle(selectedEdge.value.style, { defaultColor: '#22d3ee', defaultWidth: 4 })
    edgeForm.color = toPickerColor(style.color)
    edgeForm.width = style.width
  },
  { immediate: true }
)

const nodeTypeText = (type) => {
  if (type === 'gate') return '逻辑门'
  if (type === 'top') return '顶事件'
  if (type === 'middle') return '中间事件'
  return '基本事件'
}

const getNodeAnchor = (nodeId) => {
  const node = nodes.value.find((n) => n.id === nodeId)
  if (!node) return { in: { x: 0, y: 0 }, out: { x: 0, y: 0 } }
  const isGate = node.type === 'gate'
  const nw = isGate ? gateWidth.value : nodeWidth.value
  const nh = isGate ? gateHeight.value : nodeHeight.value
  return {
    in: { x: node.x + nw / 2, y: node.y },
    out: { x: node.x + nw / 2, y: node.y + nh }
  }
}

const updateCanvasSize = () => {
  if (!canvasRef.value) return
  canvasSize.value = { width: canvasRef.value.clientWidth, height: canvasRef.value.clientHeight }
}

const canvasResizeObserver = ref(null)

const handleGlobalClick = (event) => {
  if (showExportMenu.value && !event.target.closest('.export-menu-container')) {
    showExportMenu.value = false
  }
  if (showGateMenu.value && !event.target.closest('.gate-menu-container')) {
    showGateMenu.value = false
  }
}

onMounted(() => {
  updateCanvasSize()
  nextTick(() => {
    updateCanvasSize()
    requestAnimationFrame(() => updateCanvasSize())
  })
  let ro
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(() => updateCanvasSize())
    if (canvasRef.value) ro.observe(canvasRef.value)
  }
  canvasResizeObserver.value = ro ?? null
  window.addEventListener('resize', updateCanvasSize)
  window.addEventListener('keydown', handleGlobalKeydown, true)
  window.addEventListener('click', handleGlobalClick)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateCanvasSize)
  window.removeEventListener('mousemove', handleDragging)
  window.removeEventListener('mouseup', stopDragging)
  window.removeEventListener('keydown', handleGlobalKeydown, true)
  window.removeEventListener('click', handleGlobalClick)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  canvasResizeObserver.value?.disconnect?.()
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
  const isGate = selectedNode.value.type === 'gate'
  const keys = isGate ? ['gate'] : ['label', 'type', 'probability', 'source']
  const before = {}
  const after = {}
  for (const k of keys) {
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
  const nextStyle = normalizeEdgeStyle({ color: edgeForm.color, width: Number(edgeForm.width) || 0 }, { defaultColor: '#22d3ee', defaultWidth: 4 })
  const before = { style: normalizeEdgeStyle(selectedEdge.value.style, { defaultColor: '#22d3ee', defaultWidth: 4 }) }
  const after = { style: nextStyle }
  if (before.style.color === after.style.color && before.style.width === after.style.width) return
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
  const nw = node.type === 'gate' ? gateWidth.value : nodeWidth.value
  const nh = node.type === 'gate' ? gateHeight.value : nodeHeight.value
  const maxX = rect.width - nw - 12
  const maxY = rect.height - nh - 12
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
    nodeWidth: nw,
    nodeHeight: nh,
    getNodeSize: getNodeSizeForCollision,
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
const nextGateId = createIncrementId('G-', maxNumber(nodes.value.map((n) => n.id), 'G-') + 1)
const nextEdgeId = createIncrementId('E-', maxNumber(edges.value.map((e) => e.id), 'E-') + 1)

const deleteEdgeById = (id) => {
  edges.value = deleteEdge(edges.value, id)
}

const deleteNodeById = (id) => {
  if (!id) return
  const nextNodes = nodes.value.filter(n => n.id !== id)
  const nextEdges = edges.value.filter(e => e.source !== id && e.target !== id)
  nodes.value = nextNodes
  edges.value = nextEdges
}

const addNode = () => {
  const id = nextNodeId()
  const rect = canvasRef.value?.getBoundingClientRect?.()
  const nw = nodeWidth.value
  const nh = nodeHeight.value
  const bounds = rect ? { minX: 12, minY: 12, maxX: rect.width - nw - 12, maxY: rect.height - nh - 12 } : { minX: 12, minY: 12, maxX: 1200, maxY: 900 }
  const baseX = 80 + (nodes.value.length % 5) * 120
  const baseY = 420
  const proposed = { x: snapToGrid(baseX, gridStep), y: snapToGrid(baseY, gridStep) }
  const pos = autoAlign.value ? resolveDragCollision({ movingId: id, proposed, nodes: nodes.value, nodeWidth: nw, nodeHeight: nh, getNodeSize: getNodeSizeForCollision, safePadding, gridStep, bounds }) : proposed
  const node = { id, label: `新节点 ${id.slice(2)}`, type: 'basic', probability: 0.001, source: '', x: pos.x, y: pos.y }

  exec({
    do: () => {
      nodes.value = [...nodes.value, node]
      toast(`已添加节点: ${node.label}`)
    },
    undo: () => {
      deleteNodeById(id)
      if (selectedNodeId.value === id) selectedNodeId.value = ''
    }
  })
  handleSelectNode(id)
  return id
}

const handleAddNode = () => addNode()

const addGateNode = (gate) => {
  const id = nextGateId()
  const rect = canvasRef.value?.getBoundingClientRect?.()
  const w = gateWidth.value
  const h = gateHeight.value
  const bounds = rect ? { minX: 12, minY: 12, maxX: rect.width - w - 12, maxY: rect.height - h - 12 } : { minX: 12, minY: 12, maxX: 1200, maxY: 900 }

  const selected = selectedNode.value
  const base = selected && selected.type !== 'gate'
    ? { x: selected.x + nodeWidth.value / 2 - w / 2, y: selected.y + nodeHeight.value + 48 }
    : { x: 360, y: 220 }

  const proposed = { x: snapToGrid(base.x, gridStep), y: snapToGrid(base.y, gridStep) }
  const pos = autoAlign.value ? resolveDragCollision({ movingId: id, proposed, nodes: nodes.value, nodeWidth: w, nodeHeight: h, getNodeSize: getNodeSizeForCollision, safePadding, gridStep, bounds }) : proposed
  const node = { id, type: 'gate', gate: gate === 'OR' ? 'OR' : 'AND', x: pos.x, y: pos.y }

  exec({
    do: () => {
      nodes.value = [...nodes.value, node]
      toast(`已添加逻辑门: ${node.gate}`)
    },
    undo: () => {
      deleteNodeById(id)
      if (selectedNodeId.value === id) selectedNodeId.value = ''
    }
  })
  handleSelectNode(id)
  return id
}

const handleAddGate = (gate) => {
  showGateMenu.value = false
  addGateNode(gate)
}

const mapEventType = (t) => {
  const s = String(t || '').toLowerCase()
  if (s === 'topevent') return 'top'
  if (s === 'intermediateevent') return 'middle'
  if (s === 'basicevent') return 'basic'
  return 'middle'
}

const relationToGate = (r) => {
  const s = String(r || '').toLowerCase()
  if (s.includes('alternatively')) return 'OR'
  if (s.includes('jointly')) return 'AND'
  if (s.includes('compounds')) return 'AND'
  if (s.includes('concurrently')) return 'AND'
  if (s.includes('prerequisite')) return 'AND'
  if (s === 'resultsin') return 'OR'
  return 'OR'
}

const lastTriplets = ref([])

const sanitizeJsonForParsing = (raw) => {
  let t = String(raw ?? '')
  t = t.replace(/^\uFEFF/, '')
  t = t.replace(/[“”]/g, '"')
  t = t.replace(/,\s*([}\]])/g, '$1')
  let out = ''
  let inStr = false
  let quote = ''
  let escaped = false
  for (let i = 0; i < t.length; i++) {
    const c = t[i]
    if (inStr) {
      if (escaped) {
        out += c
        escaped = false
        continue
      }
      if (c === '\\') {
        out += c
        escaped = true
        continue
      }
      if (c === quote) {
        inStr = false
        out += '"'
        continue
      }
      if (c === '\r' || c === '\n') {
        out += ' '
        continue
      }
      const code = c.charCodeAt(0)
      if (code >= 0 && code < 32 && c !== '\t') {
        out += ' '
        continue
      }
      out += c
    } else {
      if (c === '"' || c === "'") {
        inStr = true
        quote = c
        out += '"'
        continue
      }
      out += c
    }
  }
  return out
}

const extractBalancedSlice = (text, startIndex, openChar, closeChar) => {
  const t = String(text ?? '')
  let i = Math.max(0, startIndex)
  if (t[i] !== openChar) return ''
  let depth = 0
  let inStr = false
  let quote = ''
  let escaped = false
  for (; i < t.length; i++) {
    const c = t[i]
    if (inStr) {
      if (escaped) {
        escaped = false
        continue
      }
      if (c === '\\') {
        escaped = true
        continue
      }
      if (c === quote) {
        inStr = false
        continue
      }
      continue
    }
    if (c === '"' || c === "'") {
      inStr = true
      quote = c
      continue
    }
    if (c === openChar) depth += 1
    if (c === closeChar) depth -= 1
    if (depth === 0) return t.slice(startIndex, i + 1)
  }
  return ''
}

const extractTripletsArrayText = (raw) => {
  const t = String(raw ?? '')
  const keyMatch = /"triplets"\s*:/.exec(t)
  if (keyMatch) {
    const afterKeyIndex = keyMatch.index + keyMatch[0].length
    const arrStart = t.indexOf('[', afterKeyIndex)
    if (arrStart !== -1) return extractBalancedSlice(t, arrStart, '[', ']')
  }
  const firstArr = t.indexOf('[')
  if (firstArr !== -1) return extractBalancedSlice(t, firstArr, '[', ']')
  return ''
}

const splitJsonObjectsFromArrayText = (arrayText) => {
  const t = String(arrayText ?? '')
  const out = []
  let i = 0
  while (i < t.length) {
    const open = t.indexOf('{', i)
    if (open === -1) break
    const slice = extractBalancedSlice(t, open, '{', '}')
    if (!slice) break
    out.push(slice)
    i = open + slice.length
  }
  return out
}

const cleanupTripletObjectText = (objText) => {
  let t = sanitizeJsonForParsing(objText)
  t = t.replace(
    /("confidence"\s*:\s*)(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)(\s*),\s*[^"{[\]}]*?(?=\s*")/g,
    '$1$2$3,'
  )
  t = t.replace(/,\s*([}\]])/g, '$1')
  return t
}

const extractTripletsFromText = (text) => {
  try {
    const obj = JSON.parse(String(text ?? ''))
    if (Array.isArray(obj)) return obj
    return Array.isArray(obj?.triplets) ? obj.triplets : []
  } catch {
    try {
      const cleaned = sanitizeJsonForParsing(text)
      const obj2 = JSON.parse(cleaned)
      if (Array.isArray(obj2)) return obj2
      if (Array.isArray(obj2?.triplets)) return obj2.triplets
      const arrayText = extractTripletsArrayText(cleaned)
      if (!arrayText) return []
      const items = splitJsonObjectsFromArrayText(arrayText)
      const res = []
      for (const it of items) {
        const fixed = cleanupTripletObjectText(it)
        try {
          const one = JSON.parse(fixed)
          if (one && typeof one === 'object') res.push(one)
        } catch {}
      }
      return res
    } catch {
      const cleaned2 = sanitizeJsonForParsing(text)
      const arrayText2 = extractTripletsArrayText(cleaned2)
      if (!arrayText2) return []
      const items2 = splitJsonObjectsFromArrayText(arrayText2)
      const res2 = []
      for (const it of items2) {
        const fixed = cleanupTripletObjectText(it)
        try {
          const one = JSON.parse(fixed)
          if (one && typeof one === 'object') res2.push(one)
        } catch {}
      }
      return res2
    }
  }
}

const nameKey = (label, type) => `${String(type || '').toLowerCase()}::${String(label || '').trim()}`

const ensureNode = (label, type, { probability = 0.001, source = '' } = {}) => {
  const key = nameKey(label, type)
  const existing = nodes.value.find(n => nameKey(n.label, n.type) === key)
  if (existing) {
    if (source && !existing.source) existing.source = source
    if (typeof probability === 'number' && !Number.isNaN(probability)) existing.probability = probability
    return existing.id
  }
  const id = nextNodeId()
  const posX = (nodes.value.length % 8) * 120 + 80
  const posY = type === 'top' ? 40 : type === 'middle' ? 220 : 420
  const node = { id, label: String(label || `事件 ${id.slice(2)}`), type, probability, source, x: posX, y: posY }
  nodes.value = [...nodes.value, node]
  return id
}

const buildFromTriplets = (triplets = []) => {
  nodes.value = []
  edges.value = []
  selectedNodeId.value = ''
  selectedEdgeId.value = ''

  const groups = new Map()
  for (const t of triplets || []) {
    const subjType = mapEventType(t?.subject_type)
    const objType = mapEventType(t?.object_type)
    if (String(t?.object_type || '').toLowerCase() === 'logicconstraint') continue
    const subjId = ensureNode(t?.subject_name, subjType, { probability: Number(t?.confidence) || 0.001, source: t?.source || '' })
    const objId = ensureNode(t?.object_name, objType, { probability: Number(t?.confidence) || 0.001, source: t?.source || '' })
    const gateType = relationToGate(t?.relation)
    const g = groups.get(objId) ?? { gate: '', subjects: [] }
    if (!g.subjects.includes(subjId)) g.subjects.push(subjId)
    g.gate = g.gate ? (g.gate === 'OR' || gateType === 'OR' ? 'OR' : 'AND') : gateType
    groups.set(objId, g)
  }

  for (const [objId, info] of groups) {
    const gateId = nextGateId()
    const obj = nodes.value.find(n => n.id === objId)
    const w = gateWidth.value
    const h = gateHeight.value
    const x = obj ? obj.x + (nodeWidth.value / 2) - w / 2 : 360
    const y = obj ? obj.y + nodeHeight.value + 48 : 220
    nodes.value = [...nodes.value, { id: gateId, type: 'gate', gate: info.gate, parentId: objId, x, y }]
    edges.value = [...edges.value, { id: nextEdgeId(), source: objId, target: gateId, style: { color: 'rgba(251, 191, 36, 0.85)', width: 4 } }]
    for (const sId of info.subjects) {
      const color = '#22d3ee'
      edges.value = [...edges.value, { id: nextEdgeId(), source: gateId, target: sId, style: { color, width: 4 } }]
    }
  }

  const layoutGrid = () => {
    const nw = nodeWidth.value
    const nh = nodeHeight.value
    const gw = gateWidth.value
    const gh = gateHeight.value
    const margin = 40
    const gapX = 40
    const gapY = 80

    // Build hierarchy for layout
    const childrenMap = new Map() // parentId -> array of childIds
    const parentMap = new Map()   // childId -> parentId

    edges.value.forEach(e => {
      // In this tree, target is usually the child, source is parent
      // BUT for "gate -> subjects" and "obj -> gate", the direction is:
      // obj -> gate (source: obj, target: gate)
      // gate -> subj (source: gate, target: subj)
      const parentId = e.source
      const childId = e.target
      
      if (!childrenMap.has(parentId)) childrenMap.set(parentId, [])
      childrenMap.get(parentId).push(childId)
      parentMap.set(childId, parentId)
    })

    // Find roots (nodes with no parents)
    const roots = nodes.value.filter(n => !parentMap.has(n.id))
    
    // Calculate widths required for each subtree to prevent overlap
    const subtreeWidth = new Map()
    
    const calculateWidth = (nodeId) => {
      const node = nodes.value.find(n => n.id === nodeId)
      if (!node) return 0
      
      const children = childrenMap.get(nodeId) || []
      const w = node.type === 'gate' ? gw : nw
      
      if (children.length === 0) {
        subtreeWidth.set(nodeId, w)
        return w
      }
      
      let totalChildrenWidth = 0
      children.forEach((childId, index) => {
        totalChildrenWidth += calculateWidth(childId)
        if (index < children.length - 1) totalChildrenWidth += gapX
      })
      
      const width = Math.max(w, totalChildrenWidth)
      subtreeWidth.set(nodeId, width)
      return width
    }
    
    roots.forEach(root => calculateWidth(root.id))

    // Position nodes recursively
    const positionNode = (nodeId, startX, y) => {
      const node = nodes.value.find(n => n.id === nodeId)
      if (!node) return
      
      const width = subtreeWidth.get(nodeId)
      const isGate = node.type === 'gate'
      const w = isGate ? gw : nw
      const h = isGate ? gh : nh
      
      // Center the node within its allocated width
      node.x = startX + (width - w) / 2
      node.y = y
      
      const children = childrenMap.get(nodeId) || []
      let currentX = startX
      
      children.forEach(childId => {
        const childWidth = subtreeWidth.get(childId)
        positionNode(childId, currentX, y + h + gapY)
        currentX += childWidth + gapX
      })
    }

    let currentRootX = margin
    roots.forEach(root => {
      const width = subtreeWidth.get(root.id)
      positionNode(root.id, currentRootX, margin)
      currentRootX += width + gapX * 2
    })
  }
  layoutGrid()
}

const handleGenerateFromJson = () => {
  try {
    const txtInput = String(inputText.value || '').trim()
    const txtUpload = String(uploadState.text || '').trim()
    const listInput = txtInput ? extractTripletsFromText(txtInput) : []
    const listUpload = !listInput.length && txtUpload ? extractTripletsFromText(txtUpload) : []
    const data = listInput.length ? listInput : (listUpload.length ? listUpload : (lastTriplets.value?.length ? lastTriplets.value : []))
    if (!data.length) {
      toast('未找到可用的 triplets（请在输入区粘贴 JSON 或先上传 .json 文件）', 'error')
      return
    }
    buildFromTriplets(data)
    toast(`已根据 JSON 构建故障树（事件 ${nodes.value.length}，连线 ${edges.value.length}）`, 'success')
    addHistoryFromTriplets(data, '手动生成')
  } catch (e) {
    toast(`解析失败：${e?.message || e}`, 'error')
  }
}

const handleDeleteSelected = (event) => {
  // Prevent any other click handlers from firing
  if (event && event.stopPropagation) event.stopPropagation();
  
  const targetNodeId = selectedNodeId.value;
  const targetEdgeId = selectedEdgeId.value;

  // Immediate visual feedback that the click was registered
  if (!targetNodeId && !targetEdgeId) {
    toast('请先点击选中一个节点或一条线', 'info');
    return;
  }

  try {
     // Handle Edge Deletion
     if (targetEdgeId) {
       const edge = edges.value.find(e => e.id === targetEdgeId);
       if (!edge) {
         selectedEdgeId.value = '';
         return;
       }
       // Manual shallow clone to avoid structuredClone issues
       const edgeSnapshot = { ...edge, style: { ...edge.style } };
       
       selectedEdgeId.value = '';
       exec({
         do: () => {
           edges.value = edges.value.filter(e => e.id !== targetEdgeId);
           toast('连线已成功删除');
         },
         undo: () => {
           edges.value = [...edges.value, edgeSnapshot];
           selectedEdgeId.value = targetEdgeId;
         }
       });
       return;
     }

     // Handle Node Deletion
     if (targetNodeId) {
       const node = nodes.value.find(n => n.id === targetNodeId);
       if (!node) {
         toast('选中的节点不存在', 'error');
         selectedNodeId.value = '';
         return;
       }
       
       // Manual shallow clone for the node
       const nodeSnapshot = { ...node };
       const relatedEdges = edges.value.filter(e => e.source === targetNodeId || e.target === targetNodeId);
       // Manual shallow clone for related edges
       const edgeSnapshots = relatedEdges.map(e => ({ ...e, style: { ...e.style } }));
       const nodeLabel = node.label;
       
       selectedNodeId.value = '';
       selectedEdgeId.value = '';
       
       exec({
         do: () => {
           nodes.value = nodes.value.filter(n => n.id !== targetNodeId);
           edges.value = edges.value.filter(e => e.source !== targetNodeId && e.target !== targetNodeId);
           toast(`节点 "${nodeLabel}" 及其连线已删除`);
         },
         undo: () => {
           nodes.value = [...nodes.value, nodeSnapshot];
           edges.value = [...edges.value, ...edgeSnapshots];
           selectedNodeId.value = targetNodeId;
         }
       });
     }
   } catch (err) {
     console.error('Deletion error:', err);
     toast('操作失败: ' + err.message, 'error');
   }
}

const handleDeleteHistory = (id) => {
  histories.value = histories.value.filter((h) => h.id !== id)
  if (selectedHistoryId.value === id) selectedHistoryId.value = histories.value[0]?.id ?? ''
}

const handleSelectHistory = (id) => {
  const item = histories.value.find(h => h.id === id)
  if (!item) return
  selectedHistoryId.value = id
  const snap = item.snapshot
  if (snap && Array.isArray(snap.nodes) && Array.isArray(snap.edges)) {
    nodes.value = snap.nodes.map(n => ({ ...n }))
    edges.value = snap.edges.map(e => ({ ...e, style: { ...(e.style || {}) } }))
    toast(`已切换到：${item.title}`, 'info')
  } else {
    toast('该记录未保存故障树快照', 'error')
  }
}

const handleClearHistories = () => {
  histories.value = []
  selectedHistoryId.value = ''
  toast('历史记录已清空', 'info')
}

const formatNow = () => {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}/${p(d.getMonth() + 1)}/${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

const makeSnapshot = () => {
  return {
    nodes: nodes.value.map(n => ({ ...n })),
    edges: edges.value.map(e => ({ ...e, style: { ...(e.style || {}) } }))
  }
}

const deriveTitleFromTriplets = (triplets, fallback = '') => {
  const tList = Array.isArray(triplets) ? triplets : []
  const top = tList.find(t => String(t?.object_type || '').toLowerCase() === 'topevent')
  if (top?.object_name) return String(top.object_name)
  const top2 = tList.find(t => String(t?.subject_type || '').toLowerCase() === 'topevent')
  if (top2?.subject_name) return String(top2.subject_name)
  return fallback || '故障树'
}

const addHistoryFromTriplets = (triplets, sourceLabel = '') => {
  const id = `h-${Date.now().toString(36)}-${Math.random().toString(16).slice(2, 6)}`
  const title = deriveTitleFromTriplets(triplets, sourceLabel)
  const item = { id, title, time: formatNow(), status: 'done', snapshot: makeSnapshot() }
  histories.value = [item, ...histories.value]
  selectedHistoryId.value = id
}

const handleNativeFileChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  uploadState.fileName = file.name
  uploadState.status = 'reading'
  uploadState.progress = 0
  uploadState.text = ''
  lastTriplets.value = []
  reader.onprogress = (e) => {
    if (!e?.lengthComputable) return
    const pct = Math.max(0, Math.min(100, Math.round((e.loaded / e.total) * 100)))
    uploadState.progress = pct
  }
  reader.onload = () => {
    try {
      const text = String(reader.result ?? '')
      const list = extractTripletsFromText(text)
      if (list.length) {
        lastTriplets.value = list
        uploadState.text = text
        uploadState.status = 'done'
        uploadState.progress = 100
        toast(`已载入 ${file.name}，点击“生成”可构建故障树`, 'info')
        return
      }
      uploadState.text = text
      uploadState.status = 'done'
      uploadState.progress = 100
      toast(`已载入 ${file.name}，点击“生成”可解析`, 'info')
    } catch (e) {
      const text = String(reader.result ?? '')
      uploadState.text = text
      uploadState.status = 'done'
      uploadState.progress = 100
      toast(`已载入 ${file.name}，点击“生成”可解析`, 'info')
    }
  }
  reader.onerror = () => {
    uploadState.status = 'error'
    toast('文件读取失败', 'error')
  }
  try {
    reader.readAsText(file, 'utf-8')
  } catch (e) {
    reader.readAsText(file)
  }
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

const validateConnection = (fromId, targetId) => {
  const fromNode = nodes.value.find((n) => n.id === fromId)
  const targetNode = nodes.value.find((n) => n.id === targetId)
  if (!fromNode || !targetNode) return { ok: false, message: '连接失败：节点不存在' }
  const fromIsGate = fromNode.type === 'gate'
  const targetIsGate = targetNode.type === 'gate'
  if (fromIsGate && targetIsGate) return { ok: false, message: '无效连接：逻辑门不能直接连接逻辑门' }
  if (!fromIsGate && !targetIsGate) return { ok: false, message: '无效连接：事件不能直接连接事件，请通过逻辑门连接' }
  return { ok: true, message: '' }
}

const resolveGateUnderEvent = (eventId) => {
  const eventNode = nodes.value.find((n) => n.id === eventId)
  if (!eventNode || eventNode.type === 'gate') return ''
  const linked = edges.value.find((e) => e.source === eventId && nodes.value.find((n) => n.id === e.target)?.type === 'gate')
  if (linked?.target) return linked.target

  const eventCenterX = eventNode.x + nodeWidth.value / 2
  const belowGates = nodes.value
    .filter((n) => n.type === 'gate' && n.y >= eventNode.y)
    .map((g) => {
      const dx = Math.abs(g.x + gateWidth.value / 2 - eventCenterX)
      const dy = Math.max(0, g.y - eventNode.y)
      return { id: g.id, score: dy * 2 + dx }
    })
    .sort((a, b) => a.score - b.score)
  return belowGates[0]?.id ?? ''
}

const resolveEventToEventDrop = ({ fromHandle, fromId, hoveredId }) => {
  const fromNode = nodes.value.find((n) => n.id === fromId)
  const hoveredNode = nodes.value.find((n) => n.id === hoveredId)
  if (!fromNode || !hoveredNode) return hoveredId
  if (fromNode.type === 'gate' || hoveredNode.type === 'gate') return hoveredId
  const gateId = resolveGateUnderEvent(hoveredId)
  return gateId || hoveredId
}

const handleSelectNode = (id, { effects = true, focus = false } = {}) => {
  // If we are currently dragging a connection line, finish it when clicking a node
  if (connectDrag.value) {
    const fromId = connectDrag.value.fromId;
    const fromHandle = connectDrag.value.fromHandle ?? 'out'
    const hoveredId = resolveEventToEventDrop({ fromHandle, fromId, hoveredId: id });
    
    if (fromId !== hoveredId) {
      // Reuse logic from handleCanvasMouseUp
      const sourceId = fromHandle === 'in' ? hoveredId : fromId
      const targetId = fromHandle === 'in' ? fromId : hoveredId
      const validation = validateConnection(sourceId, targetId)
      if (!validation.ok) {
        toast(validation.message, 'error')
      } else if (!canAddEdge(edges.value, sourceId, targetId, { allowMultipleEdges: allowMultipleEdges.value })) {
        toast('两节点只能有一条连线', 'error');
      } else {
        const edgeId = nextEdgeId();
        const edge = { id: edgeId, source: sourceId, target: targetId, style: { color: '#22d3ee', width: 4 } };
        exec({
          do: () => {
            edges.value = [...edges.value, edge];
            toast('连线成功');
          },
          undo: () => {
            edges.value = edges.value.filter(e => e.id !== edgeId);
          }
        });
      }
    }
    connectDrag.value = null;
    return;
  }

  selectedEdgeId.value = ''
  selectedNodeId.value = id
  if (effects) {
    nodeEffectKey.value += 1
    playClickSound()
    if (particleEnabled.value) {
      const node = nodes.value.find((n) => n.id === id)
      if (node) {
        const w = node.type === 'gate' ? gateWidth.value : nodeWidth.value
        const h = node.type === 'gate' ? gateHeight.value : nodeHeight.value
        particleRef.value?.burst?.(node.x + w / 2, node.y + h / 2)
      }
    }
  }
  if (focus) focusNode(id)

  if (reconnectMode.value && selectedEdge.value) {
    const edgeId = selectedEdge.value.id
    const before = { source: selectedEdge.value.source, target: selectedEdge.value.target }
    const after = reconnectEnd.value === 'source' ? { source: id, target: selectedEdge.value.target } : { source: selectedEdge.value.source, target: id }
    const validation = validateConnection(after.source, after.target)
    if (!validation.ok) {
      toast(validation.message, 'error')
      reconnectMode.value = false
      return
    }
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
  if (connectDrag.value) {
    connectDrag.value = null;
  }
  selectedNodeId.value = ''
  selectedEdgeId.value = id
  playClickSound()
}

const handleCanvasClick = (event) => {
  if (reconnectMode.value) return
  
  // If we are currently dragging a connection line, cancel it when clicking blank canvas
  if (connectDrag.value) {
    connectDrag.value = null;
    return;
  }

  const nodeEl = event.target?.closest?.('[data-node-id]')
  if (nodeEl?.dataset?.nodeId) return
  
  // Only clear selection if we're not clicking on a control button
  const controlEl = event.target?.closest?.('button, input, select, textarea')
  if (controlEl) return

  selectedNodeId.value = ''
  selectedEdgeId.value = ''
}

const connectDrag = ref(null)
const connectPreviewPath = computed(() => {
  if (!connectDrag.value) return ''
  const from =
    connectDrag.value.fromHandle === 'in'
      ? getNodeAnchor(connectDrag.value.fromId).in
      : getNodeAnchor(connectDrag.value.fromId).out
  const to = connectDrag.value.to
  const points = [
    from,
    { x: Math.max(from.x + 30, (from.x + to.x) / 2), y: from.y },
    { x: Math.max(from.x + 30, (from.x + to.x) / 2), y: to.y },
    to
  ]
  return pointsToPolylinePath(points)
})

const handleStartConnect = (fromId, event, fromHandle = 'out') => {
  if (!canvasRef.value) return
  const fromNode = nodes.value.find(n => n.id === fromId)
  const rect = canvasRef.value.getBoundingClientRect()
  
  // Initialize connectDrag. The mouseMove handler will update 'to'
  connectDrag.value = { 
    fromId, 
    fromHandle,
    to: { x: event.clientX - rect.left, y: event.clientY - rect.top } 
  }
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
  return pointsToPolylinePath(points)
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
    const drag = reconnectDrag.value
    const selector = drag.end === 'source' ? '[data-handle="out"]' : '[data-handle="in"]'
    const nodeEl = event.target?.closest?.(selector)
    const nextNodeId = nodeEl?.dataset?.nodeId
    reconnectDrag.value = null
    if (!nextNodeId) return
    const edge = edges.value.find((e) => e.id === drag.edgeId)
    if (!edge) return
    const before = { source: edge.source, target: edge.target }
    const rawAfter = drag.end === 'source' ? { source: nextNodeId, target: edge.target } : { source: edge.source, target: nextNodeId }
    const fromIsGate = nodes.value.find((n) => n.id === rawAfter.source)?.type === 'gate'
    const targetIsGate = nodes.value.find((n) => n.id === rawAfter.target)?.type === 'gate'
    const snappedId = (!fromIsGate && !targetIsGate) ? resolveGateUnderEvent(nextNodeId) : ''
    const after = drag.end === 'source'
      ? { source: snappedId || rawAfter.source, target: rawAfter.target }
      : { source: rawAfter.source, target: snappedId || rawAfter.target }
    if (after.source === after.target) return
    const validation = validateConnection(after.source, after.target)
    if (!validation.ok) {
      toast(validation.message, 'error')
      return
    }
    if (!canAddEdge(edges.value, after.source, after.target, { allowMultipleEdges: allowMultipleEdges.value, ignoreEdgeId: edge.id })) {
      toast('两节点只能有一条连线', 'error')
      return
    }
    exec({ do: () => updateEdgeById(edge.id, after), undo: () => updateEdgeById(edge.id, before) })
    return
  }

  if (!connectDrag.value) return
  const fromId = connectDrag.value.fromId
  const fromHandle = connectDrag.value.fromHandle ?? 'out'
  const selector = fromHandle === 'in' ? '[data-handle="out"]' : '[data-handle="in"]'
  const handleEl = event.target?.closest?.(selector)
  const nodeEl = event.target?.closest?.('[data-node-id]')
  const rawHoveredId = handleEl?.dataset?.nodeId ?? nodeEl?.dataset?.nodeId
  connectDrag.value = null
  if (!rawHoveredId || rawHoveredId === fromId) return
  const hoveredId = resolveEventToEventDrop({ fromHandle, fromId, hoveredId: rawHoveredId })
  
  const sourceId = fromHandle === 'in' ? hoveredId : fromId
  const targetId = fromHandle === 'in' ? fromId : hoveredId
  const validation = validateConnection(sourceId, targetId)
  if (!validation.ok) {
    toast(validation.message, 'error')
    return
  }
  
  if (!canAddEdge(edges.value, sourceId, targetId, { allowMultipleEdges: allowMultipleEdges.value })) {
    toast('两节点只能有一条连线', 'error')
    return
  }

  const id = nextEdgeId()
  const edge = { id, source: sourceId, target: targetId, style: { color: '#22d3ee', width: 4 } }
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
  const key = event.key
  const isDeleteKey =
    key === 'Delete' ||
    key === 'Del' ||
    key === 'Backspace' ||
    event.keyCode === 46 ||
    event.keyCode === 8
  if (!isTyping && isDeleteKey) {
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
  const w = node.type === 'gate' ? gateWidth.value : nodeWidth.value
  const h = node.type === 'gate' ? gateHeight.value : nodeHeight.value
  const maxX = rect ? rect.width - w - 12 : Infinity
  const maxY = rect ? rect.height - h - 12 : Infinity
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
      nodeWidth: w,
      nodeHeight: h,
      getNodeSize: getNodeSizeForCollision,
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
    const w = n.type === 'gate' ? gateWidth.value : nodeWidth.value
    const h = n.type === 'gate' ? gateHeight.value : nodeHeight.value
    const x0 = Math.max(0, Math.floor((n.x - pad) / step))
    const y0 = Math.max(0, Math.floor((n.y - pad) / step))
    const x1 = Math.min(cols - 1, Math.floor((n.x + w + pad) / step))
    const y1 = Math.min(rows - 1, Math.floor((n.y + h + pad) / step))
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
    outOuter: { x: a.out.x, y: a.out.y + offset },
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

const normalizePolylinePoints = (points) => {
  const out = []
  for (const p of points ?? []) appendUniquePoint(out, p)
  return out
}

const segmentIntersectsRect = (a, b, rect) => {
  if (!a || !b || !rect) return false
  if (a.x === b.x) {
    const x = a.x
    if (x < rect.left || x > rect.right) return false
    const y0 = Math.min(a.y, b.y)
    const y1 = Math.max(a.y, b.y)
    return y1 >= rect.top && y0 <= rect.bottom
  }
  if (a.y === b.y) {
    const y = a.y
    if (y < rect.top || y > rect.bottom) return false
    const x0 = Math.min(a.x, b.x)
    const x1 = Math.max(a.x, b.x)
    return x1 >= rect.left && x0 <= rect.right
  }
  return segmentIntersectsRect(a, { x: b.x, y: a.y }, rect) || segmentIntersectsRect({ x: b.x, y: a.y }, b, rect)
}

const pathIntersectsNodes = (points, { ignore = new Set() } = {}) => {
  const pad = 14
  const rects = nodes.value.map((n) => ({
    id: n.id,
    left: n.x - pad,
    top: n.y - pad,
    right: n.x + (n.type === 'gate' ? gateWidth.value : nodeWidth.value) + pad,
    bottom: n.y + (n.type === 'gate' ? gateHeight.value : nodeHeight.value) + pad
  }))
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1]
    const b = points[i]
    for (const r of rects) {
      if (ignore.has(r.id)) continue
      if (segmentIntersectsRect(a, b, r)) return true
    }
  }
  return false
}

const computeSmoothOrthoPoints = (sourceId, targetId, grid) => {
  const source = getNodePorts(sourceId)
  const target = getNodePorts(targetId)
  const ignore = new Set([sourceId, targetId])
  const step = gridStep

  const start = source.outOuter
  const end = target.inOuter
  const baseY = snapToGrid((start.y + end.y) / 2, step)
  const minY = 8
  const maxY = Math.max(minY, (canvasSize.value?.height ?? 900) - 8)

  const candidates = []
  for (let k = 0; k <= 14; k++) {
    const dy = k * step
    candidates.push(baseY + dy)
    if (k > 0) candidates.push(baseY - dy)
  }

  for (const y of candidates) {
    if (y < minY || y > maxY) continue
    const pts = normalizePolylinePoints([
      source.out,
      start,
      { x: start.x, y },
      { x: end.x, y },
      end,
      target.in
    ])
    const simplified = simplifyPoints(pts)
    if (!pathIntersectsNodes(simplified, { ignore })) return simplified
  }

  return computeSmartPathPoints(sourceId, targetId, grid)
}

const edgeRenders = computed(() => {
  const step = 18
  const grid = buildObstacleGrid(step)
  return edges.value
    .filter((e) => e.source && e.target)
    .map((e) => {
      const baseStyle = normalizeEdgeStyle(e.style, { defaultColor: '#22d3ee', defaultWidth: 4 })
      const style =
        e.id === selectedEdgeId.value && isYellowishColor(baseStyle.color)
          ? { color: '#fde047', width: Math.min(12, baseStyle.width + 1) }
          : baseStyle
      const endpoints = { source: getNodeAnchor(e.source).out, target: getNodeAnchor(e.target).in }
      const points = computeSmoothOrthoPoints(e.source, e.target, grid)
      const path = pointsToRoundedPath(points, 12)
      return { id: e.id, source: e.source, target: e.target, style, path, endpoints, selectable: true }
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
  background: var(--c-bg-dark); /* Ensure a base background */
  overflow: hidden;
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
  --c-font-size-base: 14px;
  --c-font-size-lg: 16px;
  --c-font-size-xl: 18px;
  --c-node-width: 220px;
  --c-node-height: 92px;
}

.c-root[data-font-size="xs"] {
  --c-font-size-base: 12px;
  --c-font-size-lg: 14px;
  --c-font-size-xl: 16px;
  --c-node-width: 190px;
  --c-node-height: 80px;
}

.c-root[data-font-size="sm"] {
  /* Default values already set in .c-root */
}

.c-root[data-font-size="lg"] {
  --c-font-size-base: 18px;
  --c-font-size-lg: 22px;
  --c-font-size-xl: 26px;
  --c-node-width: 280px;
  --c-node-height: 120px;
}

.c-root[data-font-size="xl"] {
  --c-font-size-base: 22px;
  --c-font-size-lg: 28px;
  --c-font-size-xl: 34px;
  --c-node-width: 380px;
  --c-node-height: 180px;
}

.c-root[data-elderly="true"] {
  /* Keep for backward compatibility or remove if not needed */
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

.c-root:fullscreen {
  width: 100vw !important;
  height: 100vh !important;
  padding: 0 !important;
  margin: 0 !important;
  background: var(--c-bg) !important;
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
  background: var(--c-bg); /* Use current theme background */
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
  width: var(--c-node-width);
  height: var(--c-node-height);
  transition: width 300ms ease, height 300ms ease, transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease, filter 220ms ease, background-color 420ms ease, color 420ms ease;
}

.c-gate-node {
  background: transparent;
  border: none;
  filter: drop-shadow(0 10px 26px rgba(0, 0, 0, 0.22));
  transform: translateZ(0);
}

.c-root[data-font-size="xs"] .text-xs { font-size: 10px !important; }
.c-root[data-font-size="xs"] .text-sm { font-size: 12px !important; }
.c-root[data-font-size="xs"] .text-[15px],
.c-root[data-font-size="xs"] .text-base { font-size: 13px !important; }

.c-root[data-font-size="sm"] .text-xs { font-size: 12px !important; }
.c-root[data-font-size="sm"] .text-sm { font-size: 14px !important; }
.c-root[data-font-size="sm"] .text-[15px],
.c-root[data-font-size="sm"] .text-base { font-size: 15px !important; }

.c-root[data-font-size="lg"] .text-xs { font-size: 18px !important; }
.c-root[data-font-size="lg"] .text-sm { font-size: 22px !important; }
.c-root[data-font-size="lg"] .text-[15px],
.c-root[data-font-size="lg"] .text-base { font-size: 26px !important; }

.c-root[data-font-size="xl"] .text-xs { font-size: 22px !important; }
.c-root[data-font-size="xl"] .text-sm { font-size: 28px !important; }
.c-root[data-font-size="xl"] .text-[15px],
.c-root[data-font-size="xl"] .text-base { font-size: 34px !important; }

.c-node:hover {
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
  }
  to {
    opacity: 1;
  }
}

@keyframes c-glow-out {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
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
  /* Disable transform transition to prevent any "shaking" or movement jump */
  transition: box-shadow 200ms ease, background-color 200ms ease, border-color 200ms ease !important;
}

.c-root button {
  transition: transform 200ms ease, box-shadow 200ms ease, background-color 200ms ease, color 200ms ease, border-color 200ms ease;
}

.c-root button:not(.c-handle):hover {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.14);
}

.c-handle:hover {
  /* Maintain the centering transform without any other movement */
  transform: translateX(-50%) !important;
  box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.45), 0 0 15px rgba(34, 211, 238, 0.25);
}

.c-root svg {
  shape-rendering: geometricPrecision;
}
</style>
