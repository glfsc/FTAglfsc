<template>
  <div class="traditional-container">
    <!-- 顶部表头 -->
    <header class="header">
      <div class="logo">
        <el-icon :size="28"><Platform /></el-icon>
        <span>故障树分析系统 - Element Plus + 传统 CSS</span>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus">新增</el-button>
        <el-button type="danger" :icon="Delete">删除</el-button>
        <el-button type="success" :icon="Download">导出</el-button>
      </div>
    </header>

    <!-- 中部可视化区域 -->
    <main class="visualization-area">
      <div class="visualization-panel">
        <div class="panel-header">
          <h3>故障树可视化</h3>
          <el-tag type="info">传统 CSS 样式</el-tag>
        </div>
        <div class="canvas">
          <div class="tree-node root">顶事件</div>
          <div class="tree-connector"></div>
          <div class="tree-node intermediate">中间事件 1</div>
          <div class="tree-node intermediate">中间事件 2</div>
        </div>
      </div>
      
      <!-- 左侧历史记录 -->
      <aside class="history-panel">
        <h4>历史记录</h4>
        <el-menu>
          <el-menu-item index="1">
            <el-icon><Document /></el-icon>
            <span>空压机故障树 v1</span>
          </el-menu-item>
          <el-menu-item index="2">
            <el-icon><Document /></el-icon>
            <span>电气系统故障树 v2</span>
          </el-menu-item>
        </el-menu>
      </aside>
    </main>

    <!-- 底部提问区 -->
    <footer class="input-area">
      <el-input 
        v-model="query" 
        placeholder="请输入您的问题，例如：如何优化故障树结构？"
        prefix-icon="ChatDotRound"
        size="large"
      />
      <el-button type="primary" size="large" :icon="Promotion">提交</el-button>
      <el-upload action="#" :auto-upload="false">
        <el-button :icon="Upload">上传文件</el-button>
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
.traditional-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px 25px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.visualization-area {
  display: flex;
  flex: 1;
  gap: 20px;
  margin-bottom: 20px;
}

.visualization-panel {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e4e7ed;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
}

.canvas {
  height: calc(100% - 80px);
  background: #f9fafc;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.tree-node {
  padding: 15px 30px;
  border-radius: 6px;
  font-weight: bold;
  animation: slideIn 0.5s ease-out;
}

.tree-node.root {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.tree-node.intermediate {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.tree-connector {
  width: 2px;
  height: 30px;
  background: #dcdfe6;
}

.history-panel {
  width: 250px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.history-panel h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.input-area {
  display: flex;
  gap: 15px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.input-area .el-input {
  flex: 1;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
