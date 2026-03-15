
D:\CSSO\服务外包比赛\frontend\src\components\GateNode.vue
<script setup lang="ts">import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'

interface GateNodeData {
  gateType: 'AND' | 'OR' | '1' | '2'
}

const props = defineProps<{
  id: string
  data: GateNodeData
  selected?: boolean
}>()

const gateType = computed(() => {
  if (props.data.gateType === '1' || props.data.gateType === 'AND') return 'AND'
  if (props.data.gateType === '2' || props.data.gateType === 'OR') return 'OR'
  return 'OR'
})

const isAND = computed(() => gateType.value === 'AND')
</script>

<template>
  <div class="gate-node" :class="{ 'is-selected': !!selected }">
    <svg 
      viewBox="0 0 60 50" 
      class="gate-svg"
      :class="{ 'gate-and': isAND, 'gate-or': !isAND }"
    >
      <defs>
        <linearGradient :id="`gate-gradient-${id}`" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#f1f5f9;stop-opacity:1" />
        </linearGradient>
      </defs>
      
      <path
        v-if="isAND"
        d="M 15 5 L 45 5 L 45 45 A 15 15 0 0 1 15 45 Z"
        fill="url(#gate-gradient-${id})"
        stroke="#1e293b"
        stroke-width="2"
      />
      
      <path
        v-if="!isAND"
        d="M 15 5 Q 30 20 45 5 L 45 45 Q 30 35 15 45 Z"
        fill="url(#gate-gradient-${id})"
        stroke="#1e293b"
        stroke-width="2"
      />
      
      <text
        x="30"
        y="30"
        text-anchor="middle"
        font-size="14"
        font-weight="bold"
        fill="#1e293b"
        font-family="Arial, sans-serif"
      >
        {{ gateType }}
      </text>
    </svg>
    
    <Handle 
      type="target" 
      :position="Position.Top" 
      class="gate-handle gate-handle--top" 
      :style="{ left: '50%', transform: 'translateX(-50%)' }"
    />
    
    <Handle 
      type="source" 
      :position="Position.Bottom" 
      class="gate-handle gate-handle--bottom" 
      :style="{ left: '50%', transform: 'translateX(-50%)' }"
    />
  </div>
</template>

<style scoped>.gate-node {
  position: relative;
  width: 60px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gate-svg {
  width: 60px;
  height: 50px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  transition: all 0.2s ease;
}

.gate-node:hover .gate-svg {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.15));
}

.gate-node.is-selected .gate-svg {
  filter: drop-shadow(0 0 0 3px rgba(99, 102, 241, 0.4));
  stroke: #6366f1;
  stroke-width: 2.5;
}

.gate-handle {
  width: 8px !important;
  height: 8px !important;
  background: #6366f1 !important;
  border: 2px solid #fff !important;
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.4) !important;
}

.gate-handle--top {
  top: -4px !important;
}

.gate-handle--bottom {
  bottom: -4px !important;
}
</style>