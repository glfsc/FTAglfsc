import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from '../pages/UploadPage.vue'
import GeneratePage from '../pages/GeneratePage.vue'
import VerifyPage from '../pages/VerifyPage.vue'
import FaultTreeVisualization from '../pages/FaultTreeVisualization.vue'
import GlobalThemeComparison from '../pages/test/GlobalThemeComparison.vue'

const routes = [
  {
    path: '/',
    redirect: '/upload'
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadPage,
    meta: { title: '文件上传与知识抽取' }
  },
  {
    path: '/generate',
    name: 'Generate',
    component: GeneratePage,
    meta: { title: '故障树生成' }
  },
  {
    path: '/verify',
    name: 'Verify',
    component: VerifyPage,
    meta: { title: '逻辑验证' }
  },
  {
    path: '/visualization',
    name: 'Visualization',
    component: FaultTreeVisualization,
    meta: { title: '故障树可视化' }
  },
  {
    path: '/test-theme',
    name: 'TestTheme',
    component: GlobalThemeComparison,
    meta: { title: '全局界面风格测试' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
