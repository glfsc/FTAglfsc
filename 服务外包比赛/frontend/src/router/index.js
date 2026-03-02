import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from '@/pages/UploadPage.vue'
import ExtractPage from '@/pages/ExtractPage.vue'
import GeneratePage from '@/pages/GeneratePage.vue'
import VerifyPage from '@/pages/VerifyPage.vue'
import ExportPage from '@/pages/ExportPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/upload'
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadPage
  },
  {
    path: '/extract',
    name: 'Extract',
    component: ExtractPage
  },
  {
    path: '/generate',
    name: 'Generate',
    component: GeneratePage
  },
  {
    path: '/verify',
    name: 'Verify',
    component: VerifyPage
  },
  {
    path: '/export',
    name: 'Export',
    component: ExportPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
