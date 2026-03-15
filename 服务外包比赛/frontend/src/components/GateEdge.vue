<script setup lang="ts">
import { computed } from 'vue';
import { getSimpleBezierPath } from '@vue-flow/core';

interface GateEdgeData {
  gateType?: string; // 'OR' or 'AND'
}

const props = defineProps({
  id: { type: String, required: true },
  source: { type: String, required: true },
  target: { type: String, required: true },
  sourceX: { type: Number, required: true },
  sourceY: { type: Number, required: true },
  sourcePosition: { type: String, required: true },
  targetX: { type: Number, required: true },
  targetY: { type: Number, required: true },
  targetPosition: { type: String, required: true },
  data: { type: Object as () => GateEdgeData, default: () => ({}) },
  selected: { type: Boolean, default: false },
  markerEnd: { type: String, default: '' }
});

const [edgePath, labelX, labelY] = getSimpleBezierPath({
  sourceX: props.sourceX,
  sourceY: props.sourceY,
  sourcePosition: props.sourcePosition,
  targetX: props.targetX,
  targetY: props.targetY,
  targetPosition: props.targetPosition,
});

const gateSymbol = computed(() => {
  if (props.data?.gateType === 'AND' || props.data?.gateType === '1') {
    return '∧';
  }
  if (props.data?.gateType === 'OR' || props.data?.gateType === '2') {
    return '∨';
  }
  return '';
});

const getGateStyle = () => {
  if (props.selected) {
    return {
      stroke: '#ef4444',
      strokeWidth: 3,
      fill: '#ef4444',
    };
  }
  return {
    stroke: '#94a3b8',
    strokeWidth: 2,
    fill: '#94a3b8',
  };
};
</script>

<template>
  <g>
    <!-- Edge path -->
    <path
      :id="props.id"
      class="vue-flow__edge-path"
      :d="edgePath"
      :style="getGateStyle()"
      :marker-end="props.markerEnd ? props.markerEnd : undefined"
    />
    
    <!-- Gate symbol label -->
    <g
      v-if="gateSymbol"
      :transform="`translate(${labelX}, ${labelY})`"
      class="gate-label"
    >
      <!-- Background circle -->
      <circle
        r="10"
        fill="white"
        stroke="#94a3b8"
        stroke-width="1.5"
      />
      
      <!-- Gate symbol text -->
      <text
        text-anchor="middle"
        dominant-baseline="central"
        font-size="14"
        font-weight="bold"
        fill="#94a3b8"
      >
        {{ gateSymbol }}
      </text>
    </g>
  </g>
</template>

<style scoped>
.gate-label {
  cursor: pointer;
  transition: all 0.2s;
}

.gate-label:hover circle {
  fill: #f1f5f9;
  stroke: #64748b;
}

.gate-label:hover text {
  fill: #64748b;
}
</style>
