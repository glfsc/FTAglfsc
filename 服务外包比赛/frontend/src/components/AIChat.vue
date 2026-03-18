<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { X, MessageSquare, Send, Loader2, Bot, User, Sparkles, RefreshCw } from 'lucide-vue-next';
import api from '@/api';

interface ChatMessage {
  role: 'user' | 'model';
  text: string;
}

const props = defineProps<{
  context: any; // The fault tree structure
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'update-tree', data: any): void;
}>();

const messages = ref<ChatMessage[]>([]);
const input = ref('');
const isLoading = ref(false);
const chatEndRef = ref<HTMLDivElement | null>(null);

// Scroll to bottom on new message
watch(messages, async () => {
  await nextTick();
  if (chatEndRef.value) {
    chatEndRef.value.scrollIntoView({ behavior: 'smooth' });
  }
}, { deep: true });

const handleSendMessage = async () => {
  if (!input.value.trim() || isLoading.value) return;

  const userMessage = input.value.trim();
  messages.value.push({ role: 'user', text: userMessage });
  input.value = '';
  isLoading.value = true;

  try {
    // Call backend API for Qwen-max
    const response = await api.post('/ai/chat', {
      messages: [
        ...messages.value.slice(0, -1).map(m => ({ 
          role: m.role === 'model' ? 'assistant' : m.role, 
          content: m.text 
        })),
        { role: 'user', content: userMessage }
      ],
      context: props.context
    });

    const aiResponse = response.response || "I couldn't generate a response.";
    
    // Check for JSON block to update tree
    const jsonMatch = aiResponse.match(/```json\n([\s\S]*?)\n```/);
    if (jsonMatch) {
      try {
        const newTreeData = JSON.parse(jsonMatch[1]);
        emit('update-tree', newTreeData);
        
        // Remove the JSON block from the displayed message to keep chat clean
        const cleanResponse = aiResponse.replace(/```json\n[\s\S]*?\n```/, '').trim();
        messages.value.push({ role: 'model', text: cleanResponse || "I've updated the fault tree structure for you." });
      } catch (e) {
        console.error("Failed to parse AI generated JSON", e);
        messages.value.push({ role: 'model', text: aiResponse });
      }
    } else {
      messages.value.push({ role: 'model', text: aiResponse });
    }

  } catch (error) {
    console.error('AI Error:', error);
    messages.value.push({ 
      role: 'model', 
      text: "Sorry, I encountered an error connecting to the AI service. Please check your configuration." 
    });
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="h-full flex flex-col bg-white">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-5 border-b border-slate-100 bg-white/50 backdrop-blur-sm sticky top-0 z-10">
      <div class="flex items-center gap-3">
        <div class="bg-indigo-600 p-2 rounded-lg text-white shadow-md shadow-indigo-200">
          <Sparkles class="w-5 h-5" />
        </div>
        <div>
          <h2 class="font-bold text-slate-800 text-base leading-tight">AI Analyst</h2>
          <p class="text-xs text-slate-400 font-medium mt-0.5">Powered by Qwen-Max</p>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div class="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50 scroll-smooth">
      <!-- Expert System Header Effect -->
      <div v-if="messages.length === 0" class="relative mb-4 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-100">
        <div class="absolute inset-0 bg-gradient-to-r from-emerald-400/10 to-teal-400/10 animate-pulse rounded-xl"></div>
        <div class="relative flex items-center gap-3">
          <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
          <h3 class="font-bold text-slate-800">专家辅助系统 - Expert Assistant</h3>
        </div>
      </div>
      
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-0 animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-forwards">
        <div class="w-16 h-16 bg-white rounded-2xl shadow-lg flex items-center justify-center mb-2">
          <Bot class="w-8 h-8 text-indigo-500" />
        </div>
        <div>
          <h3 class="font-bold text-slate-700 text-lg">How can I help?</h3>
          <p class="text-sm text-slate-400 mt-1 max-w-[240px] mx-auto">Ask me about event probabilities, cut sets, or logic gates in your tree.</p>
        </div>
        <div class="grid grid-cols-1 gap-2 w-full max-w-xs mt-4">
          <button @click="input = 'Analyze the top event probability'; handleSendMessage()" class="text-xs bg-white border border-slate-200 px-4 py-3 rounded-xl text-slate-600 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all text-left shadow-sm">
            Analyze the top event probability
          </button>
          <button @click="input = 'Create a fault tree for a car engine failure'; handleSendMessage()" class="text-xs bg-white border border-slate-200 px-4 py-3 rounded-xl text-slate-600 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all text-left shadow-sm">
            Create a fault tree for engine failure
          </button>
        </div>
      </div>
      
      <div v-for="(msg, idx) in messages" :key="idx" class="flex gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300" :class="msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'">
        
        <!-- Avatar -->
        <div class="shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm" :class="msg.role === 'user' ? 'bg-indigo-100 text-indigo-600' : 'bg-white border border-slate-100 text-emerald-600'">
          <User v-if="msg.role === 'user'" class="w-4 h-4" />
          <Bot v-else class="w-4 h-4" />
        </div>

        <!-- Bubble -->
        <div 
          class="max-w-[85%] rounded-2xl px-5 py-3.5 text-sm shadow-sm leading-relaxed relative overflow-hidden"
          :class="msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white border border-slate-100 text-slate-700 rounded-tl-none'"
        >
          <!-- Glow effect for AI messages -->
          <div v-if="msg.role === 'model'" class="absolute inset-0 bg-gradient-to-r from-emerald-400/5 to-teal-400/5 animate-pulse pointer-events-none"></div>
          <div class="relative whitespace-pre-wrap">{{ msg.text }}</div>
        </div>
      </div>

      <div v-if="isLoading" class="flex gap-4 animate-in fade-in duration-300">
        <div class="shrink-0 w-8 h-8 rounded-full bg-white border border-slate-100 flex items-center justify-center shadow-sm text-emerald-600">
          <Bot class="w-4 h-4" />
        </div>
        <div class="bg-white border border-slate-100 rounded-2xl rounded-tl-none px-5 py-3.5 shadow-sm flex items-center gap-2">
          <div class="flex gap-1">
            <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
          <span class="text-xs text-slate-400 font-medium ml-1">Analyzing structure...</span>
        </div>
      </div>
      <div ref="chatEndRef" class="h-1"></div>
    </div>

    <!-- Input -->
    <div class="p-4 bg-white border-t border-slate-100">
      <div class="relative flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-2xl p-2 focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all shadow-inner">
        <textarea 
          v-model="input"
          @keydown.enter.prevent="handleSendMessage"
          placeholder="Ask AI about your fault tree..." 
          class="flex-1 bg-transparent border-none text-sm text-slate-800 placeholder:text-slate-400 focus:ring-0 px-3 py-2 max-h-32 min-h-[44px] resize-none"
          :disabled="isLoading"
          rows="1"
        ></textarea>
        <button 
          @click="handleSendMessage"
          :disabled="isLoading || !input.trim()"
          class="p-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95 shadow-md shadow-indigo-200 mb-0.5"
        >
          <Send class="w-4 h-4" />
        </button>
      </div>
      <div class="text-[10px] text-center text-slate-300 mt-2 font-medium">
        AI can make mistakes. Please verify critical safety information.
      </div>
    </div>
  </div>
</template>
