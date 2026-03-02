<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo-section">
            <el-icon :size="32" color="#fff"><Setting /></el-icon>
            <div class="title-group">
              <h1>工业设备故障树智能生成系统</h1>
              <p class="subtitle">Fault Tree Intelligent Generation System</p>
            </div>
          </div>
          <el-menu 
            mode="horizontal" 
            :default-active="activeMenu" 
            router
            background-color="transparent"
            text-color="#fff"
            active-text-color="#ffd04b"
          >
            <el-menu-item index="/upload">
              <el-icon><Upload /></el-icon>
              <span>文本输入</span>
            </el-menu-item>
            <el-menu-item index="/extract">
              <el-icon><DataAnalysis /></el-icon>
              <span>知识提取</span>
            </el-menu-item>
            <el-menu-item index="/generate">
              <el-icon><Share /></el-icon>
              <span>故障树生成</span>
            </el-menu-item>
            <el-menu-item index="/verify">
              <el-icon><CircleCheck /></el-icon>
              <span>逻辑检验</span>
            </el-menu-item>
            <el-menu-item index="/export">
              <el-icon><Download /></el-icon>
              <span>结果导出</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <!-- 流程进度条 -->
      <div class="process-steps">
        <el-steps :active="currentStep" align-center finish-status="success">
          <el-step title="工业文本输入" icon="Upload" />
          <el-step title="知识提取层" icon="DataAnalysis" />
          <el-step title="故障知识提取" icon="Document" />
          <el-step title="故障树生成" icon="Share" />
          <el-step title="可视化呈现" icon="View" />
          <el-step title="逻辑诊断" icon="CircleCheck" />
        </el-steps>
      </div>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

      <el-footer class="app-footer">
        <p>© 2026 第十七届中国大学生服务外包创新创业大赛 A15赛题</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  Setting, Upload, DataAnalysis, Share, 
  CircleCheck, Download, Document, View 
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = ref('/')

const currentStep = computed(() => {
  const stepMap = {
    '/upload': 0,
    '/extract': 2,
    '/generate': 3,
    '/verify': 5,
    '/export': 5
  }
  return stepMap[route.path] || 0
})

watch(() => route.path, (newPath) => {
  activeMenu.value = newPath
}, { immediate: true })
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  height: 70px !important;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 30px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-group h1 {
  font-size: 22px;
  margin: 0;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 2px;
}

.el-menu--horizontal {
  border: none !important;
}

.el-menu-item {
  font-size: 15px;
  font-weight: 500;
  padding: 0 20px !important;
}

.el-menu-item .el-icon {
  margin-right: 5px;
}

.process-steps {
  background: white;
  padding: 25px 50px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.app-main {
  flex: 1;
  background: linear-gradient(to bottom, #f5f7fa 0%, #e8eef5 100%);
  padding: 30px;
  overflow-y: auto;
}

.app-footer {
  background: #2c3e50;
  color: #ecf0f1;
  text-align: center;
  padding: 15px;
  font-size: 13px;
  height: 50px !important;
}

/* 页面切换动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
