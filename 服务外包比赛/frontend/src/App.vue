<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="logo">
            <h1>工业设备故障树智能生成系统</h1>
            <p>Fault Tree Intelligent Generation System</p>
          </div>
          <el-menu
            mode="horizontal"
            :router="true"
            :default-active="$route.path"
            background-color="#545c64"
            text-color="#fff"
            active-text-color="#ffd04b"
          >
            <el-menu-item index="/upload">
              <el-icon><Upload /></el-icon>
              <span>知识抽取</span>
            </el-menu-item>
            <el-menu-item index="/generate">
              <el-icon><Connection /></el-icon>
              <span>故障树生成</span>
            </el-menu-item>
            <el-menu-item index="/visualization">
              <el-icon><DataAnalysis /></el-icon>
              <span>故障树可视化</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { Upload, Connection, CircleCheck, DataAnalysis } from '@element-plus/icons-vue'
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
  background: linear-gradient(to bottom right, #f8f9fa, #e9ecef);
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
