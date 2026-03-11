<template>
  <div class="generate-page">
    <div class="page-header">
      <h2><el-icon><Upload /></el-icon> 知识三元组上传与故障树生成</h2>
      <p class="description">将结构化的故障知识三元组写入知识图谱并生成可视化故障树</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <span><el-icon><Document /></el-icon> 上传方式一：手动输入 JSON</span>
          </template>

          <el-input
            v-model="jsonInput"
            type="textarea"
            :rows="10"
            placeholder='请输入 JSON 格式的三元组，支持两种格式：

格式 1（直接数组）：
[
  {
    "subject_name": "登机梯电机过热",
    "subject_type": "BasicEvent",
    "relation": "resultsIn",
    "object_name": "电机停机保护",
    "object_type": "IntermediateEvent",
    "confidence": 0.92,
    "source": "维修手册 P45"
  }
]

格式 2（带 triplets 字段）：
{
  "triplets": [ ... ]
}'
          />

          <!-- 新增：顶事件输入框 -->
          <div style="margin-top: 15px;">
            <el-label style="font-weight: 600; margin-bottom: 8px; display: block;">
              <el-icon><Search /></el-icon> 顶事件名称
            </el-label>
            <el-input
              v-model="topEventInput"
              placeholder="请输入顶事件名称，例如：登机梯无法展开"
              prefix-icon="Search"
              size="large"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <div style="margin-top: 5px; font-size: 12px; color: #909399;">
              💡 系统会根据该顶事件自动构建完整的故障树
            </div>
          </div>

          <el-button
            type="primary"
            style="width: 100%; margin-top: 15px;"
            @click="validateAndUpload"
            :loading="uploading"
            size="large"
          >
            <el-icon><Upload /></el-icon>
            {{ uploading ? '处理中...' : '上传三元组并生成故障树' }}
          </el-button>

          <!-- 操作按钮组 -->
          <div v-if="generatedTreeData" style="margin-top: 10px; display: flex; gap: 10px;">
            <el-button
              type="success"
              style="flex: 1;"
              @click="downloadFaultTree"
              size="large"
            >
              <el-icon><Download /></el-icon>
              下载 JSON
            </el-button>
            <el-button
              type="info"
              style="flex: 1;"
              @click="viewGeneratedJSON"
              size="large"
            >
              <el-icon><Document /></el-icon>
              查看内容
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="example-card" shadow="hover">
          <template #header>
            <span><el-icon><InfoFilled /></el-icon> 数据格式说明</span>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="subject_name">
              主体名称（故障事件名）
            </el-descriptions-item>
            <el-descriptions-item label="subject_type">
              主体类型：BasicEvent / IntermediateEvent / TopEvent
            </el-descriptions-item>
            <el-descriptions-item label="relation">
              关系类型：resultsIn / causedBy / relatedTo / jointly_resultsIn
            </el-descriptions-item>
            <el-descriptions-item label="object_name">
              客体名称（结果事件名）
            </el-descriptions-item>
            <el-descriptions-item label="object_type">
              客体类型：BasicEvent / IntermediateEvent / TopEvent
            </el-descriptions-item>
            <el-descriptions-item label="confidence">
              置信度：0.0 - 1.0
            </el-descriptions-item>
            <el-descriptions-item label="source">
              数据来源（可选）
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="提示"
            type="info"
            :closable="false"
            style="margin-top: 15px;"
          >
            <p>• 支持批量上传多个三元组</p>
            <p>• 系统会自动去重和合并重复边的证据</p>
            <p>• 置信度用于后续路径过滤和权重计算</p>
          </el-alert>
        </el-card>

        <el-card class="history-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span><el-icon><Clock /></el-icon> 上传历史</span>
          </template>

          <el-timeline>
            <el-timeline-item
              v-for="(record, index) in uploadHistory"
              :key="index"
              :timestamp="record.time"
              placement="top"
              :type="record.status === 'success' ? 'success' : 'danger'"
            >
              <el-card>
                <p>成功入库 {{ record.inserted }} 条</p>
                <p v-if="record.skipped > 0" style="color: #e6a23c;">
                  拦截脏数据 {{ record.skipped }} 条
                </p>
                <p v-if="record.duplicates > 0" style="color: #909399;">
                  内存去重 {{ record.duplicates }} 条
                </p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 内嵌故障树可视化区域 - 始终显示 -->
    <div class="visualization-section" v-if="generatedTreeData || treeNodes.length > 0">
      <el-card class="viz-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><DataAnalysis /></el-icon> 故障树可视化</span>
            <el-tag v-if="generatedTreeData" type="success">已生成</el-tag>
            <el-tag v-else type="info">等待生成</el-tag>
          </div>
        </template>

        <div class="visualization-container">
          <div class="tree-placeholder" v-if="!treeNodes.length && !generatedTreeData">
            <el-empty description="请上传三元组并输入顶事件名称以生成故障树">
              <template #image>
                <el-icon :size="100"><DataAnalysis /></el-icon>
              </template>
            </el-empty>
          </div>
          <div class="tree-placeholder" v-else-if="!treeNodes.length && generatedTreeData">
            <el-empty description="正在解析故障树数据...">
              <el-button type="primary" @click="parseTreeData">重新加载</el-button>
            </el-empty>
          </div>
          <div v-else class="tree-display">
            <!-- 集成 VueFlow 组件 -->
            <VueFlow
              v-model:nodes="treeNodes"
              v-model:edges="treeEdges"
              :default-viewport="{ zoom: 0.8 }"
              :min-zoom="0.2"
              :max-zoom="4"
              fit-view-on-init
              class="fault-tree-flow"
              :delete-key-code="'Backspace'"
              @node-click="onNodeClick"
              @edge-click="onEdgeClick"
              @pane-click="onPaneClick"
            >
              <template #node-faultNode="props">
                <FaultTreeNode 
                  :id="props.id" 
                  :data="props.data" 
                  :selected="props.selected"
                  :editable="true"
                />
              </template>
              
              <template #edge-default="props">
                <GateEdge 
                  v-bind="props"
                />
              </template>
              
              <Background pattern-color="#aaa" :gap="20" variant="dots" />
              <Controls class="flow-controls" />
            </VueFlow>
          </div>
        </div>

        <!-- 工具栏 -->
        <div class="toolbar-actions">
          <el-button-group>
            <el-button @click="toggleAIChat">
              <el-icon><ChatDotRound /></el-icon>
              AI 助手
            </el-button>
            <el-button @click="handleAddNode">
              <el-icon><Plus /></el-icon>
              添加节点
            </el-button>
            <el-button @click="toggleAutoLayout">
              <el-icon><Grid /></el-icon>
              {{ isAutoLayoutEnabled ? '自动布局：开' : '自动布局：关' }}
            </el-button>
          </el-button-group>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, Document, InfoFilled, Clock, Download, View, DataAnalysis, ChatDotRound, Plus, Grid } from '@element-plus/icons-vue'
import { uploadKnowledge, generateFaultTree, generateAndDownloadFaultTree } from '@/api'
import dagre from 'dagre'
import { VueFlow, MarkerType } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import FaultTreeNode from '../components/FaultTreeNode.vue'
import GateEdge from '../components/GateEdge.vue'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/controls/dist/style.css'

const router = useRouter()
const jsonInput = ref('')
const uploading = ref(false)
const uploadHistory = ref([])
const topEventInput = ref('登机梯无法展开')
const generatedTreeData = ref(null)  // 存储生成的故障树数据
const treeNodes = ref([])
const treeEdges = ref([])
const activeSidebar = ref(null) // 'ai', 'node', 'edge'
const selectedNodeData = ref(null)
const selectedEdgeData = ref(null)
const isAutoLayoutEnabled = ref(true)

const validateAndUpload = async () => {
  if (!jsonInput.value.trim()) {
    ElMessage.warning('请输入 JSON 数据')
    return
  }

  let triplets
  try {
    triplets = JSON.parse(jsonInput.value)
    if (Array.isArray(triplets)) {
      // 直接数组格式
    } else if (triplets.triplets && Array.isArray(triplets.triplets)) {
      triplets = triplets.triplets
    } else {
      throw new Error('JSON 必须是三元组数组格式')
    }
  } catch (error) {
    ElMessage.error(`JSON 格式错误：${error.message}`)
    return
  }

  uploading.value = true

  try {
    // 步骤 1: 上传三元组到知识图谱
    const uploadResponse = await uploadKnowledge(triplets)

    ElMessage.success({
      message: `✅ 三元组入库成功！有效入库 ${uploadResponse.inserted || triplets.length} 条`,
      duration: 2000
    })

    // 步骤 2: 自动生成故障树
    if (topEventInput.value) {
      ElMessage.info(`🌲 正在生成故障树（顶事件：${topEventInput.value}）...`)

      try {
        const treeResponse = await generateFaultTree(topEventInput.value, true)

        ElMessage.success('✅ 故障树生成成功！')

        // 存储生成的故障树数据
        if (treeResponse.data) {
          generatedTreeData.value = treeResponse.data
          sessionStorage.setItem('generatedFaultTree', JSON.stringify(treeResponse.data))
          sessionStorage.setItem('topEventName', topEventInput.value)

          // 显示下载选项
          ElMessage({
            message: '故障树已生成！您可以下载 JSON 文件查看结果',
            type: 'success',
            duration: 5000,
            showClose: true
          })
        }

      } catch (treeError) {
        console.error('故障树生成失败:', treeError)
        ElMessage.warning({
          message: `三元组已入库，但故障树生成失败：${treeError.response?.data?.detail || treeError.message}`,
          duration: 5000
        })
      }
    }

    // 添加到历史记录
    uploadHistory.value.unshift({
      time: new Date().toLocaleString(),
      topEvent: topEventInput.value,
      inserted: uploadResponse.inserted || triplets.length,
      skipped: uploadResponse.skipped || 0,
      duplicates: uploadResponse.duplicates || 0,
      status: 'success',
      treeGenerated: !!generatedTreeData.value
    })

    jsonInput.value = ''

  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(`❌ 操作失败：${error.response?.data?.detail || error.message}`)

    uploadHistory.value.unshift({
      time: new Date().toLocaleString(),
      topEvent: topEventInput.value,
      inserted: 0,
      skipped: 0,
      duplicates: 0,
      status: 'failed',
      treeGenerated: false
    })
  } finally {
    uploading.value = false
  }
}

// 新增：下载故障树 JSON 文件
const downloadFaultTree = async () => {
  if (!topEventInput.value) {
    ElMessage.warning('请先输入顶事件名称')
    return
  }

  try {
    ElMessage.info('正在生成并下载故障树 JSON...')

    // 创建下载链接
    const downloadUrl = generateAndDownloadFaultTree(topEventInput.value)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `fault_tree_${topEventInput.value}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('✅ 下载已开始！')

  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error(`下载失败：${error.message}`)
  }
}

// 新增：查看生成的 JSON（在新窗口打开）
const viewGeneratedJSON = () => {
  if (!generatedTreeData.value) {
    ElMessage.warning('暂无生成的故障树数据')
    return
  }

  // 在新窗口显示 JSON
  const jsonWindow = window.open('_blank')
  jsonWindow.document.write('<pre style="font-family: monospace; background: #f5f5f5; padding: 20px;">')
  jsonWindow.document.write(JSON.stringify(generatedTreeData.value, null, 2))
  jsonWindow.document.write('</pre>')
  jsonWindow.document.title = '故障树 JSON 预览'
}

// 解析故障树数据
const parseTreeData = (treeData = generatedTreeData.value) => {
  if (!treeData || !treeData.nodeList || !treeData.linkList) {
    ElMessage.warning('无效的故障树数据')
    return
  }
  
  // 转换节点数据
  treeNodes.value = treeData.nodeList.map(node => ({
    id: node.id,
    type: 'faultNode',
    position: { x: node.x || 0, y: node.y || 0 },
    data: {
      label: node.name,
      type: node.type,
      gate: node.gate,
      eventId: node.event?.id || node.id,
      probability: node.event?.probability
    }
  }))
  
  // 转换边数据
  treeEdges.value = treeData.linkList.map(link => ({
    id: link.id || `edge-${link.sourceId}-${link.targetId}`,
    source: link.targetId,
    target: link.sourceId,
    type: 'default',
    animated: false,
    data: {
      gateType: link.gateType || '' // 从 linkList 中获取门类型
    },
    style: { stroke: '#94a3b8', strokeWidth: 2 }
  }))
  
  // 自动布局（延迟执行确保节点已渲染）
  setTimeout(() => {
    autoLayout()
    ElMessage.success(`故障树已生成：${treeNodes.value.length}个节点，${treeEdges.value.length}条连接`)
  }, 200)
}

// 自动布局
const autoLayout = () => {
  if (!isAutoLayoutEnabled.value) {
    ElMessage.info('自动布局已禁用，可手动拖动节点调整位置')
    return
  }
  
  const layouted = getLayoutedElements(treeNodes.value, treeEdges.value)
  treeNodes.value = layouted.nodes
  ElMessage.success('布局已优化，可拖动节点调整位置')
}

// 切换自动布局
const toggleAutoLayout = () => {
  isAutoLayoutEnabled.value = !isAutoLayoutEnabled.value
  ElMessage.success(isAutoLayoutEnabled.value ? '已启用自动布局' : '已禁用自动布局')
}

const getLayoutedElements = (nodes, edges) => {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  dagreGraph.setGraph({ 
    rankdir: 'TB',  // Top to Bottom
    nodesep: 80,    // 节点间距
    ranksep: 120    // 层级间距
  })
  
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 220, height: 120 })
  })
  
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })
  
  dagre.layout(dagreGraph)
  
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    return {
      ...node,
      position: { 
        x: nodeWithPosition.x - 110, 
        y: nodeWithPosition.y - 60 
      }
    }
  })
  
  return { nodes: layoutedNodes, edges }
}

// AI 相关功能
const toggleAIChat = () => {
  activeSidebar.value = activeSidebar.value === 'ai' ? null : 'ai'
  ElMessage.info(activeSidebar.value ? 'AI 助手已打开' : 'AI 助手已关闭')
}

const handleAddNode = () => {
  const newNode = {
    id: `node-${Date.now()}`,
    type: 'faultNode',
    position: { x: 100, y: 100 },
    data: {
      label: '新事件',
      type: '3',
      gate: '',
      eventId: `evt-${Date.now()}`,
      probability: ''
    }
  }
  treeNodes.value.push(newNode)
  selectedNodeData.value = newNode.data
  activeSidebar.value = 'node'
  ElMessage.success('节点已添加，请在右侧编辑属性')
}

const aiContext = computed(() => ({
  nodes: treeNodes.value.map(n => ({
    id: n.id,
    label: n.data.label,
    type: n.data.type,
    gate: n.data.gate
  })),
  edges: treeEdges.value.map(e => ({
    source: e.source,
    target: e.target
  }))
}))

// 连线样式
const getEdgeStyle = (edge) => {
  if (selectedEdgeData.value?.id === edge.id) {
    return { stroke: '#ef4444', strokeWidth: 4 }
  }
  return { stroke: '#667eea', strokeWidth: 2 }
}

// 节点点击事件
const onNodeClick = ({ node }) => {
  selectedNodeData.value = node.data
  selectedEdgeData.value = null
  activeSidebar.value = 'node'
  ElMessage.info(`选中节点：${node.data.label}`)
}

// 连线点击事件
const onEdgeClick = ({ edge }) => {
  selectedEdgeData.value = edge
  selectedNodeData.value = null
  activeSidebar.value = 'ai'
  ElMessage.info('已选中连线，可在 AI 助手中分析')
}

// 画布点击事件
const onPaneClick = () => {
  selectedNodeData.value = null
  selectedEdgeData.value = null
  activeSidebar.value = null
}

// 监听故障树数据生成
watch(() => generatedTreeData.value, (newData) => {
  if (newData) {
    parseTreeData(newData)
  }
}, { immediate: true })
</script>

<style scoped>
.upload-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  color: white;
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.description {
  color: rgba(255, 255, 255, 0.95);
  font-size: 16px;
  margin: 0;
  letter-spacing: 0.5px;
}

.upload-card,
.example-card,
.history-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.upload-card:hover,
.example-card:hover,
.history-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.visualization-section {
  margin-top: 30px;
}

.viz-card {
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 18px;
}

.visualization-container {
  position: relative;
  width: 100%;
  height: 600px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.fault-tree-flow {
  width: 100%;
  height: 100%;
}

.flow-controls {
  background: white !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 6px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
}

.tree-placeholder,
.tree-display {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

:deep(.el-timeline-item__node) {
  font-size: 13px;
}
</style>
