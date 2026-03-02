<template>
  <div class="generate-page">
    <div class="page-header">
      <h2><el-icon><Share /></el-icon> 故障树生成与可视化</h2>
      <p class="description">基于提取的知识自动构建故障树层级结构</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="18">
        <el-card class="graph-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><View /></el-icon> 故障树图形编辑器</span>
              <div class="header-actions">
                <el-button-group>
                  <el-button size="small" @click="zoomIn">
                    <el-icon><ZoomIn /></el-icon>
                  </el-button>
                  <el-button size="small" @click="zoomOut">
                    <el-icon><ZoomOut /></el-icon>
                  </el-button>
                  <el-button size="small" @click="resetView">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </el-button-group>
                <el-button type="primary" size="small" @click="saveTree">
                  <el-icon><Select /></el-icon>
                  保存
                </el-button>
                <el-button type="success" size="small" @click="goToVerify">
                  <el-icon><Right /></el-icon>
                  逻辑检验
                </el-button>
              </div>
            </div>
          </template>

          <div class="graph-container" ref="graphContainer">
            <div id="mxgraph-container" :style="{ 
              width: '100%', 
              height: '600px', 
              border: '1px solid #dcdfe6',
              background: '#fafafa'
            }">
              <div v-if="!currentTreeId" class="empty-state">
                <el-empty description="暂无故障树数据">
                  <el-button type="primary" @click="generateTree">
                    <el-icon><MagicStick /></el-icon>
                    生成故障树
                  </el-button>
                </el-empty>
              </div>
              <div v-else class="tree-view">
                <!-- mxGraph渲染区域 -->
                <div style="padding: 50px; text-align: center;">
                  <el-result
                    icon="success"
                    title="故障树已生成"
                    sub-title="图形编辑功能需要集成mxGraph库"
                  >
                    <template #extra>
                      <el-space>
                        <el-button type="primary" @click="goToVerify">进入检验</el-button>
                        <el-button @click="regenerateTree">重新生成</el-button>
                      </el-space>
                    </template>
                  </el-result>
                </div>
              </div>
            </div>
          </div>

          <div class="toolbar">
            <el-space wrap>
              <el-button-group>
                <el-button size="small">
                  <el-icon><Plus /></el-icon>
                  添加事件节点
                </el-button>
                <el-button size="small">
                  <el-icon><Connection /></el-icon>
                  添加逻辑门
                </el-button>
                <el-button size="small">
                  <el-icon><Delete /></el-icon>
                  删除节点
                </el-button>
              </el-button-group>

              <el-divider direction="vertical" />

              <el-tag>节点总数: {{ nodeCount }}</el-tag>
              <el-tag type="success">层级深度: {{ treeDepth }}</el-tag>
            </el-space>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="config-card" shadow="hover">
          <template #header>
            <span><el-icon><Setting /></el-icon> 生成配置</span>
          </template>

          <el-form label-width="80px" label-position="top">
            <el-form-item label="顶事件">
              <el-input v-model="topEvent" placeholder="系统故障" />
            </el-form-item>

            <el-form-item label="最大深度">
              <el-slider v-model="maxDepth" :min="3" :max="10" show-stops />
            </el-form-item>

            <el-form-item label="布局方式">
              <el-select v-model="layoutType" style="width: 100%">
                <el-option label="自顶向下" value="top-down" />
                <el-option label="自左向右" value="left-right" />
                <el-option label="径向布局" value="radial" />
              </el-select>
            </el-form-item>

            <el-button 
              type="primary" 
              style="width: 100%"
              :loading="generating"
              @click="generateTree"
            >
              <el-icon><MagicStick /></el-icon>
              {{ currentTreeId ? '重新生成' : '生成故障树' }}
            </el-button>
          </el-form>
        </el-card>

        <el-card class="legend-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span><el-icon><InfoFilled /></el-icon> 图例说明</span>
          </template>

          <div class="legend-items">
            <div class="legend-item">
              <div class="legend-icon" style="background: #f56c6c;"></div>
              <span>顶事件</span>
            </div>
            <div class="legend-item">
              <div class="legend-icon" style="background: #e6a23c;"></div>
              <span>中间事件</span>
            </div>
            <div class="legend-item">
              <div class="legend-icon" style="background: #67c23a;"></div>
              <span>底事件</span>
            </div>
            <div class="legend-item">
              <div class="legend-icon diamond" style="background: #409eff;"></div>
              <span>逻辑门</span>
            </div>
          </div>
        </el-card>

        <el-card class="stats-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span><el-icon><DataLine /></el-icon> 树结构统计</span>
          </template>

          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="节点总数">{{ nodeCount }}</el-descriptions-item>
            <el-descriptions-item label="事件节点">{{ eventCount }}</el-descriptions-item>
            <el-descriptions-item label="逻辑门">{{ gateCount }}</el-descriptions-item>
            <el-descriptions-item label="树深度">{{ treeDepth }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Share, View, Setting, MagicStick, Select, Right,
  ZoomIn, ZoomOut, Refresh, Plus, Connection, Delete,
  InfoFilled, DataLine
} from '@element-plus/icons-vue'
import { generateFaultTree, optimizeFaultTree } from '@/api'

const router = useRouter()
const graphContainer = ref(null)
const currentTreeId = ref(null)
const generating = ref(false)

const topEvent = ref('系统故障')
const maxDepth = ref(5)
const layoutType = ref('top-down')

const nodeCount = ref(4)
const eventCount = ref(3)
const gateCount = ref(1)
const treeDepth = ref(2)

const generateTree = async () => {
  generating.value = true

  try {
    const result = await generateFaultTree({
      knowledge_id: 'mock-knowledge-id',
      top_event: topEvent.value,
      max_depth: maxDepth.value
    })
    
    currentTreeId.value = result.tree_id
    nodeCount.value = result.nodes.length
    eventCount.value = result.nodes.filter(n => n.node_type === 'event').length
    gateCount.value = result.nodes.filter(n => n.node_type === 'gate').length
    
    ElMessage.success('故障树生成成功')
    renderTree(result)
  } catch (error) {
    ElMessage.error('故障树生成失败')
  } finally {
    generating.value = false
  }
}

const regenerateTree = () => {
  currentTreeId.value = null
  generateTree()
}

const renderTree = (treeData) => {
  console.log('渲染故障树:', treeData)
  // TODO: 实现mxGraph渲染逻辑
}

const saveTree = async () => {
  if (!currentTreeId.value) {
    ElMessage.warning('请先生成故障树')
    return
  }

  try {
    await optimizeFaultTree({
      tree_id: currentTreeId.value,
      modified_nodes: [],
      modified_edges: []
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const goToVerify = () => {
  if (!currentTreeId.value) {
    ElMessage.warning('请先生成故障树')
    return
  }
  router.push({ path: '/verify', query: { treeId: currentTreeId.value } })
}

const zoomIn = () => ElMessage.info('放大功能')
const zoomOut = () => ElMessage.info('缩小功能')
const resetView = () => ElMessage.info('重置视图')
</script>

<style scoped>
.generate-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.description {
  color: #606266;
  font-size: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.graph-container {
  background: white;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 600px;
}

.toolbar {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-icon {
  width: 30px;
  height: 30px;
  border-radius: 4px;
}

.legend-icon.diamond {
  transform: rotate(45deg);
}
</style>
