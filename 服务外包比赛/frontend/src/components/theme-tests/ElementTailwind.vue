<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-5">
    <!-- 顶部表头 -->
    <header class="flex items-center justify-between bg-white rounded-lg px-6 py-4 shadow-xl mb-5">
      <div class="flex items-center gap-3">
        <el-icon :size="28" class="text-blue-500"><Platform /></el-icon>
        <span class="text-xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
          故障树分析系统 - Element Plus + Tailwind CSS
        </span>
      </div>
      <div class="flex gap-2">
        <el-button type="primary" :icon="Plus" class="hover:scale-105 transition-transform">新增</el-button>
        <el-button type="danger" :icon="Delete" class="hover:scale-105 transition-transform">删除</el-button>
        <el-button type="success" :icon="Download" class="hover:scale-105 transition-transform">导出</el-button>
      </div>
    </header>

    <!-- 中部可视化区域 -->
    <main class="flex flex-1 gap-5 mb-5">
      <div class="flex-1 bg-white rounded-lg p-5 shadow-xl">
        <div class="flex items-center justify-between mb-5 pb-4 border-b-2 border-gray-200">
          <h3 class="text-lg font-semibold text-gray-700">故障树可视化</h3>
          <el-tag type="info" effect="plain">Tailwind CSS 样式</el-tag>
        </div>
        <div class="h-full bg-gradient-to-br from-gray-50 to-gray-100 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center gap-5 p-10">
          <div class="px-6 py-3 rounded-lg font-bold text-white bg-gradient-to-r from-pink-500 to-red-500 shadow-lg animate-bounce">
            顶事件
          </div>
          <div class="w-0.5 h-8 bg-gray-300"></div>
          <div class="flex gap-4">
            <div class="px-5 py-2.5 rounded-lg font-bold text-white bg-gradient-to-r from-cyan-500 to-blue-500 shadow-md hover:shadow-xl transition-shadow cursor-pointer">
              中间事件 1
            </div>
            <div class="px-5 py-2.5 rounded-lg font-bold text-white bg-gradient-to-r from-blue-500 to-purple-500 shadow-md hover:shadow-xl transition-shadow cursor-pointer">
              中间事件 2
            </div>
          </div>
        </div>
      </div>
      
      <!-- 左侧历史记录 -->
      <aside class="w-64 bg-white rounded-lg p-5 shadow-xl">
        <h4 class="text-base font-semibold text-gray-700 mb-4">历史记录</h4>
        <el-menu>
          <el-menu-item index="1" class="hover:bg-blue-50">
            <el-icon><Document /></el-icon>
            <span>空压机故障树 v1</span>
          </el-menu-item>
          <el-menu-item index="2" class="hover:bg-blue-50">
            <el-icon><Document /></el-icon>
            <span>电气系统故障树 v2</span>
          </el-menu-item>
        </el-menu>
      </aside>
    </main>

    <!-- 底部提问区 -->
    <footer class="flex gap-4 bg-white rounded-lg px-5 py-5 shadow-xl">
      <el-input 
        v-model="query" 
        placeholder="请输入您的问题，例如：如何优化故障树结构？"
        prefix-icon="ChatDotRound"
        size="large"
        class="flex-1"
      />
      <el-button type="primary" size="large" :icon="Promotion" class="hover:scale-105 transition-transform">提交</el-button>
      <el-upload action="#" :auto-upload="false">
        <el-button :icon="Upload" class="hover:scale-105 transition-transform">上传文件</el-button>
      </el-upload>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Platform, Plus, Delete, Download, Document, ChatDotRound, Promotion, Upload } from '@element-plus/icons-vue'

const query = ref('')
</script>

<style scoped>
/* Tailwind CSS 处理大部分样式，这里只需要少量自定义动画 */
.animate-bounce {
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(-5%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}
</style>
