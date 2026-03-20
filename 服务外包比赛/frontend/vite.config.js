import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      onwarn(warning, warn) {
        // 忽略 source map 相关警告
        if (warning.code === 'SOURCEMAP_ERROR') {
          return;
        }
        warn(warning);
      }
    }
  },
  optimizeDeps: {
    exclude: ['jspdf'] // 预构建时排除 jspdf，避免 source map 问题
  },
  logLevel: process.env.NODE_ENV === 'development' ? 'error' : 'info' // 开发环境只显示错误，忽略 source map 警告
})
