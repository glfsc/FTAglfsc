<script setup lang="ts">
import { ref, watch } from 'vue';
import { X, Settings, Trash2, Type, GitBranch, Activity, AlertCircle } from 'lucide-vue-next';

interface NodeData {
  id: string;
  label: string;
  type: string;
  gate: string;
  probability?: string;
}

const props = defineProps<{
  node: NodeData | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'update', id: string, data: Partial<NodeData>): void;
  (e: 'delete', id: string): void;
}>();

const form = ref({
  label: '',
  type: '3',
  gate: '',
  probability: '',
});

watch(() => props.node, (newNode) => {
  if (newNode) {
    form.value = {
      label: newNode.label,
      type: newNode.type,
      gate: newNode.gate,
      probability: newNode.probability || '',
    };
  }
}, { immediate: true });

const updateNode = () => {
  if (!props.node) return;
  emit('update', props.node.id, {
    label: form.value.label,
    type: form.value.type,
    gate: form.value.gate,
    probability: form.value.probability,
  });
};

const deleteNode = () => {
  if (!props.node) return;
  if (confirm('Are you sure you want to delete this node?')) {
    emit('delete', props.node.id);
    emit('close'); // Signal to close/deselect
  }
};
</script>

<template>
  <div class="h-full flex flex-col bg-gradient-to-b from-white to-slate-50">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-5 border-b border-slate-100 bg-white/80 backdrop-blur-md sticky top-0 z-10 shadow-sm">
      <div class="flex items-center gap-3">
        <div class="bg-gradient-to-br from-indigo-500 to-purple-600 p-2.5 rounded-xl text-white shadow-lg">
          <Settings class="w-5 h-5" />
        </div>
        <div>
          <h2 class="font-bold text-slate-800 text-base leading-tight">Node Properties</h2>
          <p class="text-xs text-slate-400 font-medium mt-0.5">Edit selected event details</p>
        </div>
      </div>
      <button 
        @click="$emit('close')" 
        class="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-600 transition-all active:scale-95" 
        title="Close"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- Content -->
    <div v-if="node" class="flex-1 overflow-y-auto p-6 space-y-8">
      
      <!-- Basic Info Section -->
      <div class="space-y-5">
        <div class="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
          <Type class="w-3 h-3" />
          <span>General Information</span>
        </div>

        <div class="space-y-1.5">
          <label class="block text-sm font-medium text-slate-700">Event Name</label>
          <input 
            v-model="form.label" 
            @change="updateNode"
            type="text" 
            class="w-full px-4 py-2.5 bg-gradient-to-r from-slate-50 to-white border border-slate-200 rounded-xl text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 transition-all shadow-sm hover:shadow-md"
            placeholder="Enter event name..."
          />
        </div>

        <div class="space-y-1.5">
          <label class="block text-sm font-medium text-slate-700">Event Type</label>
          <div class="relative">
            <select 
              v-model="form.type" 
              @change="updateNode"
              class="w-full px-4 py-2.5 bg-gradient-to-r from-slate-50 to-white border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 transition-all appearance-none cursor-pointer shadow-sm hover:shadow-md"
            >
              <option value="1">● Top Event (Root)</option>
              <option value="2">◆ Intermediate Event</option>
              <option value="3">■ Basic Event (Leaf)</option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>
      </div>

      <hr class="border-slate-100" />

      <!-- Logic Section -->
      <div v-if="form.type !== '3'" class="space-y-5 animate-in fade-in slide-in-from-top-2 duration-200">
        <div class="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
          <GitBranch class="w-3 h-3" />
          <span>Logic Gate</span>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <button 
            @click="form.gate = '2'; updateNode()"
            class="relative flex flex-col items-center justify-center gap-2 py-4 px-3 rounded-2xl border-2 transition-all active:scale-[0.98] shadow-sm hover:shadow-md"
            :class="form.gate === '2' || form.gate === 'OR' ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-400 text-orange-700' : 'bg-white border-slate-100 text-slate-500 hover:border-slate-300 hover:bg-slate-50'"
          >
            <div class="text-2xl">≥1</div>
            <div class="font-bold text-sm">OR Gate</div>
            <div class="text-[10px] opacity-70 text-center px-2">Any input triggers output</div>
            <div v-if="form.gate === '2' || form.gate === 'OR'" class="absolute top-2 right-2 w-2.5 h-2.5 bg-orange-500 rounded-full animate-pulse"></div>
          </button>
          
          <button 
            @click="form.gate = '1'; updateNode()"
            class="relative flex flex-col items-center justify-center gap-2 py-4 px-3 rounded-2xl border-2 transition-all active:scale-[0.98] shadow-sm hover:shadow-md"
            :class="form.gate === '1' || form.gate === 'AND' ? 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-400 text-purple-700' : 'bg-white border-slate-100 text-slate-500 hover:border-slate-300 hover:bg-slate-50'"
          >
            <div class="text-2xl">&</div>
            <div class="font-bold text-sm">AND Gate</div>
            <div class="text-[10px] opacity-70 text-center px-2">All inputs required</div>
            <div v-if="form.gate === '1' || form.gate === 'AND'" class="absolute top-2 right-2 w-2.5 h-2.5 bg-purple-500 rounded-full animate-pulse"></div>
          </button>
        </div>
      </div>

      <!-- Probability Section -->
      <div class="space-y-5">
        <div class="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
          <Activity class="w-3 h-3" />
          <span>Quantitative Analysis</span>
        </div>

        <div class="space-y-1.5">
          <label class="block text-sm font-medium text-slate-700">Probability</label>
          <div class="relative">
            <input 
              v-model="form.probability" 
              @change="updateNode"
              type="text" 
              placeholder="e.g. 0.001"
              class="w-full pl-4 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 font-mono placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
            <div class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs font-medium">%</div>
          </div>
          <p class="text-xs text-slate-400 px-1">Enter probability value between 0 and 1.</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="pt-6 mt-auto">
        <div class="p-4 bg-red-50 rounded-xl border border-red-100 space-y-3">
          <div class="flex items-start gap-3">
            <AlertCircle class="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <h4 class="text-sm font-bold text-red-700">Danger Zone</h4>
              <p class="text-xs text-red-600/80 mt-1">Deleting this node will remove it and all its connections permanently.</p>
            </div>
          </div>
          <button 
            @click="deleteNode"
            class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-white border border-red-200 text-red-600 rounded-lg hover:bg-red-50 hover:border-red-300 transition-all text-sm font-bold shadow-sm active:scale-[0.98]"
          >
            <Trash2 class="w-4 h-4" />
            Delete Node
          </button>
        </div>
      </div>

    </div>
    <div v-else class="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-400">
      <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
        <Settings class="w-8 h-8 text-slate-300" />
      </div>
      <p class="text-sm font-medium text-slate-500">No Node Selected</p>
      <p class="text-xs mt-1 max-w-[200px]">Click on any node in the canvas to view and edit its properties.</p>
    </div>
  </div>
</template>
