<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MarkerType, VueFlow, useVueFlow, type Edge, type Node } from '@vue-flow/core'
import dagre from 'dagre'
import FaultTreeNode from '@/components/FaultTreeNode.vue'
import Sidebar from '@/components/Sidebar.vue'
import AIChat from '@/components/AIChat.vue'
import { generateFaultTreeFromFile, uploadFile } from '@/api'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/controls/dist/style.css'

type Stage = 'idle' | 'uploading' | 'extracting' | 'generating' | 'visualizing' | 'done' | 'error'

const stage = ref<Stage>('idle')
const topEvent = ref('')
const textInput = ref('')
const fileList = ref<any[]>([])
const history = ref<any[]>([])
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const selectedNode = ref<Node | null>(null)
const activeRightTab = ref<'node' | 'ai'>('node')

const { onConnect, addEdges, onNodeClick, onPaneClick, fitView } = useVueFlow()

const canGenerate = computed(() => fileList.value.length > 0 || !!textInput.value.trim())

const stageLabel = computed(() => {
  const map: Record<Stage, string> = {
    idle: 'Ready',
    uploading: 'Uploading',
    extracting: 'Extracting',
    generating: 'Generating',
    visualizing: 'Rendering',
    done: 'Done',
    error: 'Error',
  }
  return map[stage.value]
})

const aiContext = computed(() => ({
  nodes: nodes.value.map((n) => ({
    id: n.id,
    label: (n.data as any)?.label,
    type: (n.data as any)?.type,
    gate: (n.data as any)?.gate,
  })),
  edges: edges.value.map((e) => ({ source: e.source, target: e.target })),
}))

const persistHistory = () => {
  localStorage.setItem('ft_history', JSON.stringify(history.value.slice(0, 50)))
}

const loadHistory = () => {
  try {
    const raw = localStorage.getItem('ft_history')
    history.value = raw ? JSON.parse(raw) : []
  } catch {
    history.value = []
  }
}

const getLayoutedElements = (inNodes: Node[], inEdges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  dagreGraph.setGraph({ rankdir: 'TB', nodesep: 90, ranksep: 120 })
  inNodes.forEach((n) => dagreGraph.setNode(n.id, { width: 240, height: 120 }))
  inEdges.forEach((e) => dagreGraph.setEdge(e.source, e.target))
  dagre.layout(dagreGraph)
  return {
    nodes: inNodes.map((n) => {
      const p = dagreGraph.node(n.id)
      return { ...n, position: { x: p.x - 120, y: p.y - 60 } }
    }),
    edges: inEdges,
  }
}

const parseTreeData = (treeData: any) => {
  if (!treeData?.nodeList || !treeData?.linkList) {
    ElMessage.warning('Invalid tree data')
    return
  }
  if (treeData?.attr?.topEvent) {
    topEvent.value = String(treeData.attr.topEvent)
  }
  const rawNodes: Node[] = treeData.nodeList
    .filter((n: any) => n.type !== '1')
    .map((n: any) => ({
      id: n.id,
      type: 'faultNode',
      position: { x: 0, y: 0 },
      data: {
        label: n.name,
        type: n.type,
        gate: n.gate,
        eventId: n.event?.id || n.id,
        probability: n.event?.probability,
      },
    }))
  const rawEdges: Edge[] = treeData.linkList.map((l: any) => {
    const edgeId = 'e' + l.sourceId + '-' + l.targetId
    return {
      id: edgeId,
      source: l.targetId,
      target: l.sourceId,
      type: 'smoothstep',
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { stroke: '#667eea', strokeWidth: 2 },
    }
  })
  const layouted = getLayoutedElements(rawNodes, rawEdges)
  nodes.value = layouted.nodes
  edges.value = layouted.edges
  setTimeout(() => fitView({ padding: 0.2 }), 60)
}

const handleFileChange = (files: FileList | null) => {
  if (!files) return
  fileList.value = Array.from(files).map((f) => ({ name: f.name, size: f.size, file: f }))
}

const handleGenerate = async () => {
  if (!canGenerate.value) {
    ElMessage.warning('Please upload file or input text')
    return
  }
  try {
    stage.value = 'uploading'
    let fileId = ''
    if (fileList.value.length > 0) {
      const formData = new FormData()
      formData.append('file', fileList.value[0].file)
      console.log('Uploading file:', fileList.value[0].name)
      const uploadRes = await uploadFile(formData)
      fileId = uploadRes.file_id
      console.log('Upload success, fileId:', fileId)
    } else if (textInput.value.trim()) {
      const blob = new Blob([textInput.value], { type: 'text/plain' })
      const formData = new FormData()
      formData.append('file', blob, 'input.txt')
      console.log('Uploading text input')
      const uploadRes = await uploadFile(formData)
      fileId = uploadRes.file_id
      console.log('Upload success, fileId:', fileId)
    }
    stage.value = 'extracting'
    console.log('Calling generateFaultTreeFromFile with:', { file_id: fileId, top_event: topEvent.value })
    const genRes = await generateFaultTreeFromFile({
      file_id: fileId,
      top_event: topEvent.value || 'Top Event',
    })
    console.log('Generation success:', genRes)
    stage.value = 'visualizing'
    const treeData = genRes.data
    parseTreeData(treeData)
    history.value = [
      {
        id: fileId,
        time: new Date().toLocaleString(),
        topEvent: topEvent.value || 'Unnamed',
        filename: fileList.value[0]?.name || 'input.txt',
        treeData,
      },
      ...history.value.filter((h) => h.id !== fileId),
    ]
    persistHistory()
    stage.value = 'done'
    ElMessage.success('Tree generated')
  } catch (err: any) {
    stage.value = 'error'
    console.error('Generation error:', err)
    ElMessage.error(err.response?.data?.detail || err.message || 'Generation failed')
  }
}

onNodeClick(({ node }) => {
  selectedNode.value = node
  activeRightTab.value = 'node'
})

onPaneClick(() => {
  selectedNode.value = null
})

onConnect((connection) => {
  addEdges({
    ...connection,
    type: 'smoothstep',
    markerEnd: { type: MarkerType.ArrowClosed },
    style: { stroke: '#667eea', strokeWidth: 2 },
  })
})

onMounted(() => {
  loadHistory()
})
</script>

<template>
  <div class="studio">
    <div class="navbar">
      <h1>Fault Tree Studio</h1>
      <span class="status" :class="stage">{{ stageLabel }}</span>
    </div>
    <div class="container">
      <div class="sidebar">
        <h3>History</h3>
        <div class="history">
          <div v-for="item in history" :key="item.id" class="item" @click="() => { topEvent = item.topEvent; parseTreeData(item.treeData); stage = 'done' }">
            <div class="title">{{ item.topEvent }}</div>
            <div class="time">{{ item.time }}</div>
          </div>
        </div>
      </div>
      <div class="main">
        <div class="canvas">
          <VueFlow v-model:nodes="nodes" v-model:edges="edges">
            <Background />
            <Controls />
            <template #node-faultNode="{ data, selected, id }">
              <FaultTreeNode :id="id" :data="data" :selected="selected" editable />
            </template>
          </VueFlow>
        </div>
        <div class="input-area">
          <div class="form">
            <div class="row">
              <div class="col">
                <label>Top Event</label>
                <el-input v-model="topEvent" placeholder="Enter top event (optional)" size="small" />
              </div>
              <div class="col">
                <label>Upload File</label>
                <div class="file-input">
                  <input type="file" @change="(e) => handleFileChange((e.target as HTMLInputElement).files)" accept=".txt,.pdf,.docx,.md" />
                  <span>{{ fileList.length > 0 ? fileList[0].name : 'Select file' }}</span>
                </div>
              </div>
            </div>
            <div class="row">
              <el-input v-model="textInput" type="textarea" placeholder="Or input text..." :rows="2" size="small" />
            </div>
            <el-button :disabled="!canGenerate" :loading="stage !== 'idle' && stage !== 'done' && stage !== 'error'" @click="handleGenerate" type="primary" size="large" style="width: 100%">
              {{ stage === 'idle' ? 'Generate Fault Tree' : stageLabel }}
            </el-button>
          </div>
        </div>
      </div>
      <div class="rightbar">
        <el-tabs v-model="activeRightTab">
          <el-tab-pane label="Properties" name="node">
            <Sidebar v-if="selectedNode" :node="selectedNode" @update-node="(data) => Object.assign(selectedNode!.data, data)" />
            <div v-else style="padding: 20px; text-align: center; color: #999;">Click node</div>
          </el-tab-pane>
          <el-tab-pane label="AI" name="ai">
            <AIChat :context="aiContext" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<style scoped>
.studio { display: flex; flex-direction: column; height: 100vh; background: #f5f7fa; }
.navbar { height: 56px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; justify-content: space-between; align-items: center; padding: 0 24px; }
.navbar h1 { margin: 0; font-size: 18px; font-weight: 700; }
.status { padding: 4px 12px; background: rgba(255,255,255,0.2); border-radius: 12px; font-size: 12px; }
.container { flex: 1; display: flex; gap: 0; overflow: hidden; }
.sidebar { width: 200px; background: white; border-right: 1px solid #e4e7eb; display: flex; flex-direction: column; padding: 16px; overflow: hidden; }
.sidebar h3 { margin: 0 0 12px 0; font-size: 13px; }
.history { flex: 1; overflow-y: auto; }
.history .item { padding: 10px; margin-bottom: 8px; background: #f8fafc; border-radius: 6px; cursor: pointer; }
.history .item:hover { background: #eef2ff; }
.history .title { font-size: 12px; font-weight: 600; }
.history .time { font-size: 11px; color: #999; margin-top: 4px; }
.main { flex: 1; display: flex; flex-direction: column; background: white; }
.canvas { flex: 1; position: relative; overflow: hidden; }
.input-area { height: 180px; background: white; border-top: 1px solid #e4e7eb; padding: 12px 16px; overflow-y: auto; }
.form { display: flex; flex-direction: column; gap: 10px; }
.row { display: flex; gap: 12px; }
.col { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.col label { font-size: 12px; font-weight: 600; }
.file-input { position: relative; display: flex; align-items: center; height: 32px; padding: 0 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; cursor: pointer; font-size: 12px; }
.file-input input { position: absolute; opacity: 0; width: 100%; height: 100%; cursor: pointer; }
.rightbar { width: 260px; background: white; border-left: 1px solid #e4e7eb; display: flex; flex-direction: column; overflow: hidden; }
:deep(.el-tabs) { height: 100%; display: flex; flex-direction: column; }
:deep(.el-tabs__content) { flex: 1; overflow-y: auto; }
</style>
