<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { VueFlow, useVueFlow, Connection, Edge, Node, MarkerType, EdgeMouseEvent, BaseEdge } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { Download, FileJson, FileImage, FileText, FileType, ChevronDown, Plus, Upload, Trash2, MessageSquare, LayoutGrid } from 'lucide-vue-next';
import FaultTreeNode from '../components/FaultTreeNode.vue';
import Sidebar from '../components/Sidebar.vue';
import AIChat from '../components/AIChat.vue';
import { jsPDF } from 'jspdf';
import dagre from 'dagre';
import { toPng } from 'html-to-image';
import { Document, Packer, Paragraph, TextRun } from 'docx';
import { saveAs } from 'file-saver';
import { ElMessage } from 'element-plus';
import '@vue-flow/core/dist/style.css';
import '@vue-flow/controls/dist/style.css';

// --- State ---
const nodes = ref<Node[]>([]);
const edges = ref<Edge[]>([]);
const selectedNode = ref<Node | null>(null);
const selectedEdge = ref<Edge | null>(null);
const activeSidebar = ref<'ai' | 'node'>('node'); // Default to node properties
const isExportMenuOpen = ref(false);
const isConnectingMode = ref(false);
const editableMode = ref(true); // Enable editing mode by default

const { onConnect, addEdges, onNodeClick, onPaneClick, onEdgeClick, getNodes, getNodesBounds, getViewport, setViewport, fitView, removeEdges } = useVueFlow();

// --- Layout Logic ---
const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  dagreGraph.setGraph({ rankdir: 'TB', nodesep: 100, ranksep: 100 }); // Top to Bottom

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 208, height: 100 }); // Approx node size (w-52 = 13rem = 208px)
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: { x: nodeWithPosition.x - 104, y: nodeWithPosition.y - 50 }, // Center anchor correction
    };
  });

  return { nodes: layoutedNodes, edges };
};

// --- Event Handlers ---

onConnect((params) => {
  const sourceNode = nodes.value.find(n => n.id === params.source);
  const targetNode = nodes.value.find(n => n.id === params.target);

  // Validation: Top Event (1) cannot connect directly to Basic Event (3)
  if (sourceNode?.data.type === '1' && targetNode?.data.type === '3') {
    ElMessage.error('无效连接：顶事件不能直接连接到基本事件，必须连接到中间事件');
    return;
  }
  
  // Check for duplicate connection
  const exists = edges.value.some(e => e.source === params.source && e.target === params.target);
  if (exists) {
    ElMessage.warning('该连接已存在');
    return;
  }

  addEdges([{ ...params, type: 'smoothstep', markerEnd: MarkerType.ArrowClosed, style: { stroke: '#667eea', strokeWidth: 2 } }]);
  
  // Exit connecting mode after successful connection
  if (isConnectingMode.value) {
    isConnectingMode.value = false;
    ElMessage.success('连线创建成功！拖动节点可调整位置');
  }
});

onNodeClick(({ node }) => {
  selectedNode.value = node;
  selectedEdge.value = null; // Deselect edge
  activeSidebar.value = 'node'; // Switch to node properties
});

onEdgeClick(({ edge }) => {
  selectedEdge.value = edge;
  selectedNode.value = null; // Deselect node
  activeSidebar.value = 'ai'; // Switch to AI chat for edge analysis
  ElMessage.info('已选中连线，可在 AI 助手中分析该连接关系');
});

onPaneClick(() => {
  selectedNode.value = null;
  selectedEdge.value = null;
  activeSidebar.value = 'node'; // Revert to node panel when deselecting
});

const handleAddNode = () => {
  const id = `node-${Date.now()}`;
  const newNode: Node = {
    id,
    type: 'faultNode',
    position: { x: Math.random() * 500 + 100, y: Math.random() * 500 + 100 },
    data: {
      label: 'New Event',
      type: '3', // Basic Event
      gate: '',
      eventId: id.slice(-6),
      probability: '',
    },
  };
  nodes.value.push(newNode);
};

const handleUpdateNode = (id: string, data: any) => {
  const nodeIndex = nodes.value.findIndex((n) => n.id === id);
  if (nodeIndex !== -1) {
    nodes.value[nodeIndex].data = { ...nodes.value[nodeIndex].data, ...data };
    nodes.value = [...nodes.value];
    // Only auto-layout if enabled
    if (editableMode.value) {
      setTimeout(() => {
        const layouted = getLayoutedElements(nodes.value, edges.value);
        nodes.value = layouted.nodes;
      }, 100);
    }
  }
};

const handleDeleteNode = (id: string) => {
  nodes.value = nodes.value.filter((n) => n.id !== id);
  edges.value = edges.value.filter((e) => e.source !== id && e.target !== id);
  selectedNode.value = null;
  activeSidebar.value = 'node';
};

const handleDeleteSelected = () => {
  if (selectedNode.value) {
    handleDeleteNode(selectedNode.value.id);
  } else if (selectedEdge.value) {
    removeEdges([selectedEdge.value.id]);
    ElMessage.success('连线已删除');
    selectedEdge.value = null;
  } else {
    // Batch delete fallback
    const selectedNodes = nodes.value.filter((n) => n.selected);
    if (selectedNodes.length > 0) {
      if (confirm(`确定要删除这 ${selectedNodes.length} 个选中的节点吗？`)) {
        const idsToDelete = new Set(selectedNodes.map((n) => n.id));
        nodes.value = nodes.value.filter((n) => !idsToDelete.has(n.id));
        edges.value = edges.value.filter((e) => !idsToDelete.has(e.source) && !idsToDelete.has(e.target));
        ElMessage.success(`已删除 ${selectedNodes.length} 个节点及相关连线`);
      }
    }
  }
};

const toggleConnectingMode = () => {
  isConnectingMode.value = !isConnectingMode.value;
  if (isConnectingMode.value) {
    ElMessage.success('已进入连线模式，点击节点下方的连接点并拖动到另一个节点创建连线，拖动节点可调整位置');
    // Highlight all connection handles
    document.querySelectorAll('.vue-flow__handle').forEach(handle => {
      (handle as HTMLElement).style.opacity = '1';
      (handle as HTMLElement).style.scale = '1.3';
    });
  } else {
    ElMessage.info('已退出连线模式');
    // Restore normal handle appearance
    document.querySelectorAll('.vue-flow__handle').forEach(handle => {
      (handle as HTMLElement).style.opacity = '';
      (handle as HTMLElement).style.scale = '';
    });
  }
};

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target?.result as string);
      if (json.nodeList && json.linkList) {
        const rawNodes = json.nodeList.map((n: any) => ({
          id: n.id,
          type: 'faultNode',
          position: { x: 0, y: 0 }, // Position will be calculated
          data: {
            label: n.name,
            type: n.type,
            gate: n.gate,
            eventId: n.event?.id || n.id,
            probability: n.event?.probability,
          },
        }));
        
        const rawEdges = json.linkList.map((l: any) => ({
          id: `e${l.sourceId}-${l.targetId}`,
          source: l.targetId, // Parent
          target: l.sourceId, // Child
          type: 'smoothstep',
          markerEnd: MarkerType.ArrowClosed,
        }));

        const layouted = getLayoutedElements(rawNodes, rawEdges);
        nodes.value = layouted.nodes;
        edges.value = layouted.edges;
        
        setTimeout(() => fitView({ padding: 0.2 }), 50);

      } else {
        alert('Invalid JSON format');
      }
    } catch (error) {
      console.error('Error parsing JSON:', error);
      alert('Error parsing JSON file');
    }
  };
  reader.readAsText(file);
};

// --- Export Logic ---

const exportToPDF = () => {
  const doc = new jsPDF({
    orientation: 'landscape',
    unit: 'pt',
  });

  const allNodes = getNodes.value;
  allNodes.forEach((node) => {
    const { x, y } = node.position;
    const w = 208;
    const h = 100;

    // Node Box
    doc.setDrawColor(0);
    doc.setFillColor(255, 255, 255);
    doc.rect(x, y, w, h, 'FD');

    // Text Configuration
    doc.setFont("helvetica", "normal");
    doc.setTextColor(0);

    // Label (Name)
    doc.setFontSize(10);
    const splitLabel = doc.splitTextToSize(node.data.label, w - 20);
    doc.text(splitLabel, x + 10, y + 25);

    // Gate Info (if applicable)
    if (node.data.type !== '3') {
      let gateText = "";
      if (node.data.gate === '1' || node.data.gate === 'AND') gateText = "Logic: AND Gate";
      else if (node.data.gate === '2' || node.data.gate === 'OR') gateText = "Logic: OR Gate";
      
      if (gateText) {
        doc.setFontSize(8);
        doc.setTextColor(100);
        doc.text(gateText, x + 10, y + h - 15);
      }
    }
  });

  // Edges
  edges.value.forEach((edge) => {
    const sourceNode = allNodes.find((n) => n.id === edge.source);
    const targetNode = allNodes.find((n) => n.id === edge.target);
    if (sourceNode && targetNode) {
      const sx = sourceNode.position.x + 104;
      const sy = sourceNode.position.y + 100;
      const tx = targetNode.position.x + 104;
      const ty = targetNode.position.y;

      doc.setDrawColor(0);
      doc.setLineWidth(1);
      
      // Orthogonal line
      const midY = (sy + ty) / 2;
      doc.line(sx, sy, sx, midY);
      doc.line(sx, midY, tx, midY);
      doc.line(tx, midY, tx, ty);
    }
  });

  doc.save('fault-tree-structure.pdf');
  isExportMenuOpen.value = false;
};

const exportToImage = async () => {
  const element = document.querySelector('.vue-flow__pane') as HTMLElement;
  if (element) {
    const dataUrl = await toPng(element, { backgroundColor: '#fff' });
    const link = document.createElement('a');
    link.download = 'fault-tree.png';
    link.href = dataUrl;
    link.click();
  }
  isExportMenuOpen.value = false;
};

const exportToJSON = () => {
  const data = {
    nodeList: nodes.value.map(n => ({
      id: n.id,
      name: n.data.label,
      type: n.data.type,
      gate: n.data.gate,
      x: n.position.x,
      y: n.position.y,
      event: {
        id: n.data.eventId,
        probability: n.data.probability
      }
    })),
    linkList: edges.value.map(e => ({
      sourceId: e.target, // Reverse mapping to match import format (child -> parent)
      targetId: e.source
    }))
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  saveAs(blob, 'fault-tree.json');
  isExportMenuOpen.value = false;
};

const exportToDocx = () => {
  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        new Paragraph({
          children: [
            new TextRun({
              text: "Fault Tree Analysis Report",
              bold: true,
              size: 32,
            }),
          ],
        }),
        new Paragraph({ text: "" }), // Spacer
        ...nodes.value.map(n => {
          return new Paragraph({
            children: [
              new TextRun({
                text: `Event: ${n.data.label} (${n.data.eventId})`,
                bold: true,
              }),
              new TextRun({
                text: `\nType: ${n.data.type === '1' ? 'Top' : n.data.type === '2' ? 'Intermediate' : 'Basic'}`,
                break: 1,
              }),
              new TextRun({
                text: `\nProbability: ${n.data.probability || 'N/A'}`,
                break: 1,
              }),
              new TextRun({
                text: "\n",
                break: 1,
              })
            ]
          });
        })
      ],
    }],
  });

  Packer.toBlob(doc).then((blob) => {
    saveAs(blob, "fault-tree-report.docx");
  });
  isExportMenuOpen.value = false;
};

// --- Context for AI ---
const aiContext = computed(() => ({
  nodes: nodes.value.map(n => ({
    id: n.id,
    label: n.data.label,
    type: n.data.type,
    gate: n.data.gate,
    probability: n.data.probability
  })),
  edges: edges.value.map(e => ({
    source: e.source,
    target: e.target
  }))
}));

// Highlight selected edges
const getEdgeStyle = (edge: Edge) => {
  if (selectedEdge.value?.id === edge.id) {
    return { stroke: '#ef4444', strokeWidth: 4 };
  }
  return { stroke: '#667eea', strokeWidth: 2 };
};

const handleAIUpdate = (newTreeData: any) => {
  if (newTreeData.nodeList && newTreeData.linkList) {
    const rawNodes = newTreeData.nodeList.map((n: any) => ({
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
    }));
    
    const rawEdges = newTreeData.linkList.map((l: any) => ({
      id: `e${l.sourceId}-${l.targetId}`,
      source: l.targetId,
      target: l.sourceId,
      type: 'smoothstep',
      markerEnd: MarkerType.ArrowClosed,
    }));

    const layouted = getLayoutedElements(rawNodes, rawEdges);
    nodes.value = layouted.nodes;
    edges.value = layouted.edges;
    
    setTimeout(() => fitView({ padding: 0.2 }), 50);
  }
};

// Load initial data from route params or session storage
onMounted(() => {
  // Try to load from session storage first
  const savedTree = sessionStorage.getItem('generatedFaultTree');
  if (savedTree) {
    try {
      const treeData = JSON.parse(savedTree);
      handleAIUpdate(treeData);
    } catch (e) {
      console.error('Failed to load saved tree:', e);
    }
  }
});

</script>

<template>
  <div class="visualization-container">
    <!-- Header -->
    <div class="visualization-header">
      <div class="header-left">
        <div class="logo-section">
          <div class="logo-icon">
            <LayoutGrid class="w-6 h-6" />
          </div>
          <div class="logo-text">
            <h1>Fault Tree Analysis System</h1>
            <p>工业设备故障树智能生成系统</p>
          </div>
        </div>
      </div>
      <div class="header-right">
        <button 
          @click="activeSidebar = 'ai'"
          class="ai-assistant-btn"
          :class="{ active: activeSidebar === 'ai' }"
          title="Switch to AI Chat"
        >
          <MessageSquare class="w-5 h-5" />
          <span>AI Assistant</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-group">
          <button @click="handleAddNode" class="toolbar-btn" title="Add Event">
            <Plus class="w-5 h-5" />
            <span>Add Event</span>
          </button>
          <div class="toolbar-divider"></div>
          <button @click="toggleConnectingMode" class="toolbar-btn" :class="{ active: isConnectingMode }" title="Connect Nodes">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="6" cy="6" r="3"/>
              <circle cx="18" cy="18" r="3"/>
              <line x1="6" y1="9" x2="6" y2="18"/>
              <line x1="18" y1="6" x2="18" y2="15"/>
              <path d="M6 12 C6 15, 18 9, 18 12"/>
            </svg>
            <span>{{ isConnectingMode ? '连线中...' : '连接节点' }}</span>
          </button>
          <div class="toolbar-divider"></div>
          <button @click="editableMode = !editableMode" class="toolbar-btn" :class="{ active: editableMode }" title="Toggle Edit Mode">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            <span>{{ editableMode ? '编辑模式' : '查看模式' }}</span>
          </button>
          <div class="toolbar-divider"></div>
          <button @click="handleDeleteSelected" class="toolbar-btn" :disabled="!selectedNode && !selectedEdge" title="Delete">
            <Trash2 class="w-5 h-5" />
            <span>Delete</span>
          </button>
          <div class="toolbar-divider"></div>
          <label class="toolbar-btn" title="Import">
            <Upload class="w-5 h-5" />
            <span>Import</span>
            <input type="file" accept=".json" @change="handleFileUpload" class="hidden" />
          </label>
          <div class="toolbar-divider"></div>
          <div class="dropdown">
            <button class="toolbar-btn" @click="isExportMenuOpen = !isExportMenuOpen">
              <Download class="w-5 h-5" />
              <span>Export</span>
              <ChevronDown class="w-4 h-4" />
            </button>
            <div v-if="isExportMenuOpen" class="dropdown-menu">
              <button @click="exportToPDF" class="dropdown-item">
                <FileType class="w-4 h-4" />
                <span>PDF Document</span>
              </button>
              <button @click="exportToImage" class="dropdown-item">
                <FileImage class="w-4 h-4" />
                <span>PNG Image</span>
              </button>
              <button @click="exportToJSON" class="dropdown-item">
                <FileJson class="w-4 h-4" />
                <span>JSON Data</span>
              </button>
              <button @click="exportToDocx" class="dropdown-item">
                <FileText class="w-4 h-4" />
                <span>Word Document</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Canvas -->
      <div class="canvas-container">
        <!-- Status Bar -->
        <div class="status-bar">
          <div class="status-item">
            <span class="status-label">模式:</span>
            <el-tag :type="editableMode ? 'success' : 'info'" size="small">
              {{ editableMode ? '可编辑' : '只读' }}
            </el-tag>
          </div>
          <div class="status-item">
            <span class="status-label">节点:</span>
            <span class="status-value">{{ nodes.length }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">连线:</span>
            <span class="status-value">{{ edges.length }}</span>
          </div>
          <div class="status-item" v-if="selectedNode">
            <span class="status-label">选中节点:</span>
            <el-tag type="warning" size="small">{{ selectedNode.data.label }}</el-tag>
          </div>
          <div class="status-item" v-if="selectedEdge">
            <span class="status-label">选中连线:</span>
            <el-tag type="danger" size="small">高亮显示</el-tag>
          </div>
          <div class="status-item" v-if="isConnectingMode">
            <span class="status-label">操作:</span>
            <el-tag type="warning" size="small">连线中 - 拖动节点调整位置</el-tag>
          </div>
        </div>
        
        <VueFlow
          v-model:nodes="nodes"
          v-model:edges="edges"
          :default-viewport="{ zoom: 1 }"
          :min-zoom="0.2"
          :max-zoom="4"
          fit-view-on-init
          class="fault-tree-flow"
          :delete-key-code="'Backspace'"
        >
          <template #node-faultNode="props">
            <FaultTreeNode 
              :id="props.id" 
              :data="props.data" 
              :selected="props.selected"
              :editable="true"
            />
          </template>
          
          <template #edge-smoothstep="props">
            <BaseEdge 
              :id="props.id" 
              :path="props.path" 
              :style="getEdgeStyle(props)" 
              :marker-end="MarkerType.ArrowClosed"
            />
          </template>
          
          <Background pattern-color="#aaa" :gap="20" variant="dots" />
          <Controls class="flow-controls" />
        </VueFlow>
      </div>
    </div>

    <!-- Right Sidebar - Always Visible -->
    <div class="sidebar sidebar-open">
      <!-- Node Properties Panel - Shows when node is selected -->
      <div class="sidebar-panel" :class="{ active: activeSidebar === 'node' && selectedNode }">
        <Sidebar 
          :node="selectedNode ? { id: selectedNode.id, ...selectedNode.data } : null"
          @close="activeSidebar = 'node'; selectedNode = null" 
          @update="handleUpdateNode"
          @delete="handleDeleteNode"
        />
      </div>

      <!-- AI Chat Panel - Shows when AI button clicked or edge selected -->
      <div class="sidebar-panel" :class="{ active: activeSidebar === 'ai' || (selectedEdge && activeSidebar !== 'node') }">
        <AIChat 
          :context="aiContext"
          @update-tree="handleAIUpdate"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.visualization-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Header */
.visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.logo-text h1 {
  font-size: 22px;
  font-weight: 700;
  color: white;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.logo-text p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  margin: 4px 0 0 0;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
}

.ai-assistant-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-assistant-btn:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.ai-assistant-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.toolbar-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn:disabled:hover {
  background: white;
  border-color: #e5e7eb;
  color: #374151;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #e5e7eb;
  margin: 0 4px;
}

/* Dropdown */
.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 200px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 8px;
  z-index: 100;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  background: none;
  border: none;
  border-radius: 6px;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.dropdown-item:hover {
  background: #f9fafb;
  color: #667eea;
}

/* Canvas */
.canvas-container {
  flex: 1;
  overflow: hidden;
  background: white;
  position: relative;
}

/* Status Bar */
.status-bar {
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  display: flex;
  gap: 16px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(8px);
  z-index: 1000;
  align-items: center;
  flex-wrap: wrap;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.status-label {
  color: #6b7280;
  font-weight: 500;
}

.status-value {
  color: #1f2937;
  font-weight: 600;
  font-family: monospace;
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

/* Sidebar - Always Visible on Right */
.sidebar {
  width: 400px;
  border-left: 1px solid #e5e7eb;
  background: linear-gradient(to bottom, #ffffff, #f8f9fa);
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.sidebar-panel {
  width: 400px;
  height: 100%;
  display: none;
  overflow-y: auto;
}

.sidebar-panel.active {
  display: block;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
