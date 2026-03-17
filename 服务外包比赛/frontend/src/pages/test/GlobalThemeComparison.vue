<template>
  <div class="theme-test-container">
    <el-tabs v-model="activeTheme" type="border-card" class="theme-tabs">
      <el-tab-pane label="组合 A: Element Plus + 传统 CSS" name="element-traditional">
        <ElementTraditional />
      </el-tab-pane>
      <el-tab-pane label="组合 B: Element Plus + Tailwind CSS" name="element-tailwind">
        <ElementTailwind />
      </el-tab-pane>
      <el-tab-pane label="组合 C: Naive UI + Tailwind CSS" name="naive-tailwind">
        <NaiveTailwind />
      </el-tab-pane>
      <el-tab-pane label="组合 D: 纯 Tailwind CSS" name="pure-tailwind">
        <PureTailwind />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ElementTraditional from '../../components/theme-tests/ElementTraditional.vue'
import ElementTailwind from '../../components/theme-tests/ElementTailwind.vue'
import NaiveTailwind from '../../components/theme-tests/NaiveTailwind.vue'
import PureTailwind from '../../components/theme-tests/PureTailwind.vue'

const activeTheme = ref('element-traditional')
</script>

<style scoped>
.theme-test-container {
  padding: 20px;
  height: 100vh;
  background: #f5f7fa;
}

.theme-tabs {
  height: 100%;
}

.theme-tabs :deep(.el-tabs__content) {
  height: calc(100% - 55px);
  overflow-y: auto;
}
</style>
