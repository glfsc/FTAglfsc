<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
    <!-- 顶部表头 -->
    <header class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <div class="relative">
          <div class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-lg blur-lg opacity-75 animate-pulse"></div>
          <div class="relative bg-gradient-to-r from-cyan-400 to-purple-500 p-3 rounded-lg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-white tracking-tight">故障树分析系统</h1>
          <p class="text-sm text-gray-400">纯 Tailwind CSS + 手写组件</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button class="group relative px-5 py-2.5 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-medium rounded-lg overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-green-500/50 hover:scale-105">
          <span class="absolute inset-0 w-full h-full bg-gradient-to-r from-green-600 to-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity"></span>
          <span class="relative flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            新增
          </span>
        </button>
        <button class="group relative px-5 py-2.5 bg-gradient-to-r from-red-500 to-pink-500 text-white font-medium rounded-lg overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-red-500/50 hover:scale-105">
          <span class="absolute inset-0 w-full h-full bg-gradient-to-r from-red-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity"></span>
          <span class="relative flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
            删除
          </span>
        </button>
        <button class="group relative px-5 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/50 hover:scale-105">
          <span class="absolute inset-0 w-full h-full bg-gradient-to-r from-blue-600 to-cyan-600 opacity-0 group-hover:opacity-100 transition-opacity"></span>
          <span class="relative flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            导出
          </span>
        </button>
      </div>
    </header>

    <!-- 中部可视化区域 -->
    <main class="flex gap-6 mb-6 flex-1 min-h-0">
      <div class="flex-1 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
          <h3 class="text-lg font-semibold text-white">故障树可视化</h3>
          <span class="px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full text-xs text-white font-medium">
            纯 Tailwind 风格
          </span>
        </div>
        <div class="h-full bg-gradient-to-br from-purple-900/20 to-pink-900/20 border-2 border-dashed border-white/20 rounded-xl flex flex-col items-center justify-center gap-6 p-10">
          <div class="group relative">
            <div class="absolute inset-0 bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity animate-pulse"></div>
            <div class="relative px-10 py-4 bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl font-bold text-white shadow-2xl cursor-pointer transform transition-all duration-300 hover:scale-110">
              顶事件
            </div>
          </div>
          <div class="w-1 h-12 bg-gradient-to-b from-white/30 to-white/10"></div>
          <div class="flex gap-6">
            <div class="group relative">
              <div class="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl blur-lg opacity-0 group-hover:opacity-50 transition-opacity"></div>
              <div class="relative px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl font-bold text-white shadow-xl cursor-pointer transform transition-all duration-300 hover:scale-105">
                中间事件 1
              </div>
            </div>
            <div class="group relative">
              <div class="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur-lg opacity-0 group-hover:opacity-50 transition-opacity"></div>
              <div class="relative px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-bold text-white shadow-xl cursor-pointer transform transition-all duration-300 hover:scale-105">
                中间事件 2
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 左侧历史记录 -->
      <aside class="w-72 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
        <h4 class="text-base font-semibold text-white mb-5 flex items-center gap-2">
          <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/>
          </svg>
          历史记录
        </h4>
        <div class="space-y-3">
          <div class="group flex items-center gap-3 p-4 rounded-xl bg-white/5 hover:bg-white/10 cursor-pointer transition-all duration-200 border border-white/10 hover:border-white/20">
            <div class="text-yellow-400 group-hover:scale-110 transition-transform">📄</div>
            <div class="flex-1">
              <p class="text-white text-sm font-medium">空压机故障树 v1</p>
              <p class="text-gray-400 text-xs mt-1">2 小时前</p>
            </div>
          </div>
          <div class="group flex items-center gap-3 p-4 rounded-xl bg-white/5 hover:bg-white/10 cursor-pointer transition-all duration-200 border border-white/10 hover:border-white/20">
            <div class="text-yellow-400 group-hover:scale-110 transition-transform">📄</div>
            <div class="flex-1">
              <p class="text-white text-sm font-medium">电气系统故障树 v2</p>
              <p class="text-gray-400 text-xs mt-1">昨天</p>
            </div>
          </div>
        </div>
      </aside>
    </main>

    <!-- 底部提问区 -->
    <footer class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl px-6 py-5 shadow-2xl">
      <div class="flex gap-4">
        <div class="relative flex-1">
          <input 
            v-model="query"
            type="text"
            placeholder="请输入您的问题，例如：如何优化故障树结构？"
            class="w-full px-5 py-4 bg-white/10 backdrop-blur rounded-xl text-white placeholder-white/40 border border-white/20 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all duration-300"
          />
          <div class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </div>
        </div>
        <button class="group px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium rounded-xl overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/50 hover:scale-105 flex items-center gap-2">
          <svg class="w-5 h-5 group-hover:rotate-45 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
          提交
        </button>
        <label class="group px-8 py-4 bg-white/10 backdrop-blur text-white font-medium rounded-xl border border-white/20 cursor-pointer transition-all duration-300 hover:bg-white/20 hover:scale-105 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
          </svg>
          上传文件
          <input type="file" class="hidden" />
        </label>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const query = ref('')
</script>

<style scoped>
/* 自定义动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.75;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
