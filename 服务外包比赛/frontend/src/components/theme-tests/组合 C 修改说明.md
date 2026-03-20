# 组合 C（NaiveTailwind）修改说明

## 修改文件
- `D:\CSSO\服务外包比赛\frontend\src\components\theme-tests\NaiveTailwind.vue`

## 完成的修改内容

### 1. ✅ 删除右上方组件
**修改位置：** Header 区域（第 32-45 行）
- ❌ 删除"浅色模式"切换按钮
- ❌ 删除"声音"开关按钮  
- ✅ 保留"新增节点"和"删除选中"按钮

### 2. ✅ 简化画布上方工具栏
**修改位置：** 工具栏区域（第 75-96 行）
- ❌ 删除"连接"开关按钮
- ❌ 删除"自动排列"开关按钮
- ❌ 删除"粒子"开关按钮
- ❌ 删除"多连线"开关按钮
- ✅ 保留撤销、重做、新增、删除按钮

### 3. ✅ 设置默认配置
**修改位置：** 响应式变量声明（第 376-378 行）
```javascript
const autoAlign = ref(true)        // 默认开启自动排列
const allowMultipleEdges = ref(false) // 默认单连线模式
const particleEnabled = ref(true)     // 默认开启粒子效果
```

### 4. ✅ 修改连线方向
**修改位置：** `getNodeAnchor` 函数（第 485-492 行）
```javascript
// 修改前：输入在顶部，输出在右侧
return {
  in: { x: node.x + nodeWidth / 2, y: node.y },
  out: { x: node.x + nodeWidth, y: node.y + nodeHeight / 2 }
}

// 修改后：输入在顶部，输出在底部
return {
  in: { x: node.x + nodeWidth / 2, y: node.y },           // Top center
  out: { x: node.x + nodeWidth / 2, y: node.y + nodeHeight } // Bottom center
}
```

### 5. ✅ 添加连接验证规则
**修改位置：** `handleCanvasMouseUp` 函数（第 873-882 行）
```javascript
// Validation: Top Event cannot connect to Basic Event
const fromNode = nodes.value.find(n => n.id === fromId)
const targetNode = nodes.value.find(n => n.id === targetId)
if (fromNode?.type === 'top' && targetNode?.type === 'basic') {
  toast('无效连接：顶事件不能直接连接到基本事件，必须连接到中间事件', 'error')
  return
}
```

### 6. ✅ 增强节点光效
**修改位置：** 
- 节点模板（第 218-222 行）：添加悬停光效元素
- CSS 样式（第 1406-1420 行）：添加悬停光效样式

```vue
<!-- 选中光效 -->
<span class="c-node-glow-inner" v-if="node.id === selectedNodeId" />
<span class="c-node-glow-outer" v-if="node.id === selectedNodeId" />
<span class="c-node-pulse" v-if="node.id === selectedNodeId" />
<!-- 悬停光效 -->
<span class="c-node-hover-glow" v-if="node.id !== selectedNodeId" />
```

```css
.c-node-hover-glow {
  position: absolute;
  inset: -4px;
  border-radius: 16px 24px 14px 26px;
  background: radial-gradient(50% 40% at 50% 50%, rgba(34, 211, 238, 0.15), transparent 70%);
  filter: blur(8px);
  opacity: 0;
  transition: opacity 220ms ease;
}

.c-node:hover .c-node-hover-glow {
  opacity: 1;
}
```

### 7. ✅ 调整右侧栏布局
**修改位置：** 右侧栏（第 239-320 行）

#### 宽度调整
```vue
<!-- 修改前：w-80 (320px) -->
<aside class="w-80 c-panel ...">

<!-- 修改后：w-[450px] -->
<aside class="w-[450px] c-panel ...">
```

#### 标题动态显示
```vue
<div class="text-sm font-semibold text-[var(--c-text)]">
  {{ selectedEdgeId ? '连线信息' : selectedNodeId ? '节点信息' : '专家辅助系统' }}
</div>
```

#### 专家辅助系统界面（未选择节点时显示）
```vue
<div v-if="!selectedNodeId && !selectedEdgeId" class="flex-1 flex flex-col">
  <!-- 专家系统头部（带脉冲光效） -->
  <div class="relative mb-4 p-4 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-xl border border-emerald-400/20">
    <div class="absolute inset-0 bg-gradient-to-r from-emerald-400/5 to-teal-400/5 animate-pulse rounded-xl"></div>
    <div class="relative flex items-center gap-3">
      <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
      <h3 class="font-bold text-[var(--c-text)]">专家辅助系统 - Expert Assistant</h3>
    </div>
  </div>
  
  <!-- AI 对话消息区 -->
  <div class="space-y-4">
    <div class="flex items-start gap-3">
      <div class="w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-emerald-300">
        <svg>...</svg>
      </div>
      <div class="flex-1">
        <div class="bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm text-[var(--c-text)]">
          您好！我是专家辅助系统，可以帮您分析故障树结构、评估概率、优化逻辑门配置等。请问有什么可以帮助您的？
        </div>
      </div>
    </div>
  </div>
  
  <!-- 输入框区域 -->
  <div class="p-4 border-t border-[var(--c-border)]">
    <div class="flex gap-2">
      <input type="text" placeholder="向 AI 专家提问..." />
      <button>发送</button>
    </div>
  </div>
</div>
```

### 8. ✅ 简化连线信息面板
**修改位置：** 连线属性面板（第 245-281 行）

#### 移除复杂设置项
- ❌ 删除"线型"选择器（实线/虚线）
- ❌ 删除"路径"选择器（智能避障/圆角折线/贝塞尔曲线）
- ❌ 删除"重新连接起点/终点"按钮
- ❌ 删除重新连接模式提示文字

#### 保留基础功能
```vue
<div v-else-if="selectedEdgeId" class="p-4 overflow-auto space-y-3 relative">
  <!-- 高亮指示条 -->
  <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-400 to-violet-400 animate-pulse"></div>
  
  <!-- 标签输入 -->
  <div class="space-y-1.5">
    <div class="text-xs text-[var(--c-text-muted)]">标签</div>
    <input v-model="edgeForm.label" />
  </div>
  
  <!-- 颜色和粗细 -->
  <div class="grid grid-cols-2 gap-3">
    <input v-model="edgeForm.color" type="color" />
    <input v-model.number="edgeForm.width" type="number" />
  </div>
  
  <!-- 删除按钮 -->
  <button @click="handleDeleteSelected">删除连线</button>
</div>
```

## 技术实现细节

### 连接验证逻辑
```javascript
// 在 handleCanvasMouseUp 中验证
const fromNode = nodes.value.find(n => n.id === fromId)
const targetNode = nodes.value.find(n => n.id === targetId)

// 顶事件 -> 基本事件：禁止
if (fromNode?.type === 'top' && targetNode?.type === 'basic') {
  toast('无效连接：顶事件不能直接连接到基本事件', 'error')
  return
}

// 重复连接检查
if (!canAddEdge(edges.value, fromId, targetId, { allowMultipleEdges: false })) {
  toast('两节点只能有一条连线', 'error')
  return
}
```

### 节点光效层次
1. **选中状态**：三层光效（inner + outer + pulse）
2. **悬停状态**：单层淡入光效（hover glow）
3. **默认状态**：无额外光效

### 右侧栏显示逻辑
```javascript
// 根据选择状态动态显示面板
- 未选择任何元素 → 专家辅助系统（AI 对话）
- 选择边 → 连线信息面板（高亮条 + 基础设置）
- 选择节点 → 节点属性面板（高亮条 + 完整表单）
```

## 视觉效果提升

✅ **粒子背景**：默认开启粒子效果  
✅ **自动排列**：默认开启碰撞检测  
✅ **单连线模式**：防止重复连接  
✅ **节点光效**：选中/悬停都有精美光效  
✅ **连线方向**：从下到上的自然流向  
✅ **专家系统**：带脉冲光效的 AI 对话界面  
✅ **简洁界面**：移除冗余控件，保留核心功能  

## 测试建议

1. **连接验证测试**：
   - 尝试从顶事件（红色）直接连到基本事件（绿色），应显示错误提示
   - 尝试在两个节点间创建多条连线，应显示错误提示

2. **光效测试**：
   - 悬停在节点上，查看淡入光效
   - 点击选中节点，查看三层光效（内光晕、外光晕、脉冲）

3. **专家系统测试**：
   - 不选择任何节点，查看右侧栏是否显示专家辅助系统
   - 选择节点后，查看是否切换到节点属性面板
   - 选择连线后，查看是否显示简化的连线信息

4. **连线方向测试**：
   - 新建连线，确认从起点节点下方出发
   - 确认连线到终点节点上方结束

5. **默认配置测试**：
   - 拖动节点，验证自动排列是否生效
   - 观察画布背景，验证粒子效果是否开启
   - 尝试创建重复连线，验证单连线模式

## 注意事项

⚠️ **重要提示：**
- 本次修改仅针对测试文件夹中的组合 C（`NaiveTailwind.vue`）
- 不影响主文件夹中的 `FaultTreeVisualization.vue`
- 所有开关按钮已被移除，相关功能设置为默认开启/关闭
- 连线信息面板已大幅简化，复杂设置项已删除
