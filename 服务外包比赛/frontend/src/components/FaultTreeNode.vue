<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core';
import { computed, ref, watch } from 'vue';

interface NodeData {
  id: string;
  label: string;
  type: string;
  gate: string;
  eventId: string;
  probability?: string;
}

const props = defineProps<{
  id: string;
  data: NodeData;
  selected?: boolean;
  editable?: boolean;
}>();

const emit = defineEmits<{
  (e: 'updateData', id: string, data: Partial<NodeData>): void;
  (e: 'requestDelete', id: string): void;
  (e: 'click'): void;
}>();

const isHovered = ref(false);
const isEditing = ref(false);
const editLabel = ref('');
const isConnecting = ref(false);
const isConnectionSource = ref(false);

const nodeStyles = computed(() => {
  if (props.data.type === '1') return {
    bg: 'bg-red-50',
    border: 'border-red-200',
    header: 'bg-red-50 text-red-700',
    ring: 'ring-red-400/30',
    accent: 'from-red-400 to-red-600'
  };
  if (props.data.type === '2') return {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    header: 'bg-blue-50 text-blue-700',
    ring: 'ring-blue-400/30',
    accent: 'from-blue-400 to-blue-600'
  };
  return {
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    header: 'bg-emerald-50 text-emerald-700',
    ring: 'ring-emerald-400/30',
    accent: 'from-emerald-400 to-emerald-600'
  };
});

const gateSymbol = computed(() => {
  if (props.data.gate === '1' || props.data.gate === 'AND') return 'AND';
  if (props.data.gate === '2' || props.data.gate === 'OR') return 'OR';
  return '';
});

const typeLabel = computed(() => {
  if (props.data.type === '1') return 'TOP EVENT';
  if (props.data.type === '2') return 'INTERMEDIATE';
  return 'BASIC EVENT';
});

const startEditing = () => {
  if (props.editable) {
    editLabel.value = props.data.label;
    isEditing.value = true;
  }
};

const saveEdit = () => {
  if (editLabel.value.trim()) {
    emit('updateData', props.id, { label: editLabel.value.trim() });
  }
  isEditing.value = false;
};

const cancelEdit = () => {
  isEditing.value = false;
  editLabel.value = '';
};

const handleRightClick = (event: MouseEvent) => {
  event.preventDefault();
  event.stopPropagation();
  // Could show context menu here
};

const handleNodeClick = (event: MouseEvent) => {
  event.stopPropagation();
  emit('click');
};

const cancelConnection = () => {
  isConnecting.value = false;
  isConnectionSource.value = false;
};

const handleConnectionStart = (event: MouseEvent) => {
  event.stopPropagation();
  startConnection();
};
</script>

<template>
  <div
    class="w-64 relative group"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @contextmenu="handleRightClick"
  >
    <!-- Main Event Box with Clean Card Design -->
    <div 
      class="rounded-xl border-2 shadow-sm transition-all duration-200 bg-white relative z-10 overflow-hidden cursor-pointer"
      :class="[
        nodeStyles.border,
        selected ? `ring-4 ${nodeStyles.ring} shadow-lg scale-[1.02]` :
        isHovered ? 'shadow-md -translate-y-0.5' : 'shadow-sm',
        isConnecting ? 'ring-4 ring-yellow-400/60 animate-pulse' : ''
      ]"
      @dblclick="startEditing"
      @click.right="handleRightClick"
      @click="handleNodeClick"
    >
      <!-- Animated Glow Effect when Selected or Clicked -->
      <div
        v-if="selected || isHovered"
        class="absolute inset-0 bg-gradient-to-r opacity-10 animate-pulse pointer-events-none"
        :class="nodeStyles.accent"
      ></div>
      
      <!-- Click Ripple Effect -->
      <div
        v-if="isHovered"
        class="absolute inset-0 rounded-xl border-2 transition-all duration-300 pointer-events-none"
        :class="[
          selected ? 'border-transparent' : 'border-indigo-400/30',
          selected ? 'shadow-[0_0_20px_rgba(99,102,241,0.5)]' : 'shadow-[0_0_15px_rgba(99,102,241,0.3)]'
        ]"
      ></div>

      <!-- Connection Mode Indicator -->
      <div
        v-if="isConnecting"
        class="absolute inset-0 bg-yellow-400/10 flex items-center justify-center rounded-2xl backdrop-blur-[1px] z-30 pointer-events-none"
      >
        <div class="bg-yellow-500 px-4 py-2 rounded-full text-sm font-bold text-white shadow-xl animate-bounce">
          点击其他节点创建连线
        </div>
      </div>

      <div class="p-3 relative">
        <!-- Header with Badge -->
        <div class="flex items-center justify-between mb-3">
          <div 
            class="px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-md backdrop-blur-sm flex items-center gap-2 shadow-sm"
            :class="nodeStyles.header"
          >
            <span v-if="props.data.type === '1'" class="text-red-600">●</span>
            <span v-else-if="props.data.type === '2'" class="text-blue-600">◆</span>
            <span v-else class="text-emerald-600">■</span>
            <span>{{ typeLabel }}</span>
          </div>
        </div>
          
          <!-- Gate Indicator -->
          <div 
            v-if="data.type !== '3' && data.gate" 
            class="w-8 h-8 rounded-xl flex items-center justify-center font-black text-xs shadow-lg border-2 transform transition-transform hover:scale-110"
            :class="[
              data.gate === '1' || data.gate === 'AND' ? 
                'bg-gradient-to-br from-purple-400 to-purple-600 border-purple-300 text-white' :
                'bg-gradient-to-br from-orange-400 to-orange-600 border-orange-300 text-white'
            ]"
            :title="data.gate === '1' || data.gate === 'AND' ? 'AND Gate' : 'OR Gate'"
          >
            {{ gateSymbol }}
          </div>
        </div>

        <!-- Event Label with Edit Mode -->
        <div v-if="!isEditing" class="text-sm font-semibold text-slate-800 text-center leading-tight mb-3 line-clamp-3 min-h-[2.5rem] flex items-center justify-center px-2">
          {{ data.label }}
        </div>
        <div v-else class="mb-2">
          <el-input
            v-model="editLabel"
            size="small"
            autofocus
            @keyup.enter="saveEdit"
            @keyup.escape="cancelEdit"
            @blur="saveEdit"
          />
        </div>

        <!-- Event ID and Probability -->
        <div class="flex items-center justify-between gap-2 pt-3 border-t border-slate-100">
          <div class="text-[9px] text-slate-400 font-mono truncate max-w-[80px]" :title="data.eventId">
            #{{ data.eventId?.slice(-6) }}
          </div>
          <div v-if="data.probability" class="flex items-center gap-2 bg-slate-50 px-2 py-1 rounded-md border border-slate-200">
            <span class="text-[8px] text-slate-500 uppercase tracking-widest font-bold">PROB</span>
            <span class="text-xs font-mono font-semibold text-slate-700">{{ data.probability }}</span>
          </div>
        </div>

        <!-- Edit Hint -->
        <div
          v-if="editable && isHovered && !isEditing && !isConnecting"
          class="absolute inset-0 bg-black/5 flex items-center justify-center rounded-2xl backdrop-blur-[1px] transition-opacity"
        >
          <div class="flex gap-2">
            <div class="bg-white/90 px-3 py-1.5 rounded-full text-xs font-medium text-slate-700 shadow-lg">
              双击编辑
            </div>
            <div class="bg-white/90 px-3 py-1.5 rounded-full text-xs font-medium text-slate-700 shadow-lg">
              右键菜单
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Connection Handles with Animation and Interaction -->
    <!-- Input handle at TOP - for receiving connections from parent -->
    <Handle 
      type="target" 
      :position="Position.Top" 
      class="!w-6 !h-6 !bg-gradient-to-br !from-indigo-400 !to-indigo-600 !border-2 !border-white !shadow-xl transition-all group-hover:!scale-125 !-top-3 z-20 !opacity-100 hover:!from-green-400 hover:!to-green-600 cursor-crosshair"
      @mouseenter="isHovered = true"
      @mousedown="handleConnectionStart"
    />
    
    <!-- Output handle at BOTTOM - for creating connections to children -->
    <Handle 
      v-if="data.type !== '3'" 
      type="source" 
      :position="Position.Bottom" 
      class="!w-6 !h-6 !bg-gradient-to-br !from-indigo-400 !to-indigo-600 !border-2 !border-white !shadow-xl transition-all group-hover:!scale-125 !-bottom-3 z-20 !opacity-100 hover:!from-green-400 hover:!to-green-600 cursor-crosshair"
      @mouseenter="isHovered = true"
      @mousedown="handleConnectionStart"
    />
    
    <!-- Connection Status Indicator -->
   <!-- Connection Status Indicator -->
<div
  v-if="isConnectionSource"
  class="absolute -inset-2 pointer-events-none z-0"
>
  <div class="w-full h-full rounded-xl border-2 border-dashed border-yellow-400 animate-ping opacity-75"></div>
</div>
</template>

<style scoped>
/* Additional animations */
@keyframes pulse-glow {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
