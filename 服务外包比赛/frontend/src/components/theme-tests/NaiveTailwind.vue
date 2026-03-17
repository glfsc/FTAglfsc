<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 p-5">
    <!-- 顶部表头 -->
    <header class="flex items-center justify-between bg-white/10 backdrop-blur-lg rounded-xl px-6 py-4 shadow-2xl mb-5 border border-white/20">
      <div class="flex items-center gap-3">
        <div class="text-cyan-400">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <span class="text-xl font-bold text-white tracking-wide">
          故障树分析系统 - Naive UI + Tailwind CSS
        </span>
      </div>
      <div class="flex gap-2">
        <button class="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all duration-300 flex items-center gap-2">
          <span>➕</span> 新增
        </button>
        <button class="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all duration-300 flex items-center gap-2">
          <span>🗑️</span> 删除
        </button>
        <button class="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all duration-300 flex items-center gap-2">
          <span>📥</span> 导出
        </button>
      </div>
    </header>

    <!-- 中部可视化区域 -->
    <main class="flex flex-1 gap-5 mb-5">
      <div class="flex-1 bg-white/10 backdrop-blur-lg rounded-xl p-5 shadow-2xl border border-white/20">
        <div class="flex items-center justify-between mb-5 pb-4 border-b border-white/20">
          <h3 class="text-lg font-semibold text-white">故障树可视化</h3>
          <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-full text-xs text-white font-medium">
            Naive UI 风格
          </span>
        </div>
        <div class="h-full bg-white/5 backdrop-blur-sm border-2 border-dashed border-white/20 rounded-xl flex flex-col items-center justify-center gap-5 p-10">
          <div class="group relative px-8 py-4 rounded-xl font-bold text-white bg-gradient-to-r from-pink-500 to-rose-500 shadow-2xl cursor-pointer overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-r from-pink-600 to-rose-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative z-10">顶事件</div>
            <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
          </div>
          <div class="w-0.5 h-10 bg-gradient-to-b from-white/40 to-white/10"></div>
          <div class="flex gap-4">
            <div class="group px-6 py-3 rounded-xl font-bold text-white bg-gradient-to-r from-cyan-500 to-blue-500 shadow-xl cursor-pointer hover:shadow-2xl transition-all duration-300 hover:scale-105">
              中间事件 1
            </div>
            <div class="group px-6 py-3 rounded-xl font-bold text-white bg-gradient-to-r from-purple-500 to-pink-500 shadow-xl cursor-pointer hover:shadow-2xl transition-all duration-300 hover:scale-105">
              中间事件 2
            </div>
          </div>
        </div>
      </div>
      
      <!-- 左侧历史记录 -->
      <aside class="w-64 bg-white/10 backdrop-blur-lg rounded-xl p-5 shadow-2xl border border-white/20">
        <h4 class="text-base font-semibold text-white mb-4">历史记录</h4>
        <div class="space-y-2">
          <div class="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 cursor-pointer transition-all duration-200 border border-white/10">
            <span class="text-yellow-400">📄</span>
            <span class="text-white text-sm">空压机故障树 v1</span>
          </div>
          <div class="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 cursor-pointer transition-all duration-200 border border-white/10">
            <span class="text-yellow-400">📄</span>
            <span class="text-white text-sm">电气系统故障树 v2</span>
          </div>
        </div>
      </aside>
    </main>

    <!-- 底部提问区 -->
    <footer class="flex gap-4 bg-white/10 backdrop-blur-lg rounded-xl px-5 py-5 shadow-2xl border border-white/20">
      <input 
        v-model="query"
        type="text"
        placeholder="请输入您的问题，例如：如何优化故障树结构？"
        class="flex-1 px-4 py-3 bg-white/20 backdrop-blur rounded-lg text-white placeholder-white/50 border border-white/20 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all"
      />
      <button class="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all duration-300 flex items-center gap-2">
        <span>🚀</span> 提交
      </button>
      <button class="px-6 py-3 bg-white/20 backdrop-blur text-white rounded-lg font-medium hover:bg-white/30 hover:scale-105 transition-all duration-300 flex items-center gap-2 border border-white/20">
        <span>📎</span> 上传文件
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const query = ref('')
</script>

<style scoped>
/* 自定义动画效果 */
@keyframes pulse {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
