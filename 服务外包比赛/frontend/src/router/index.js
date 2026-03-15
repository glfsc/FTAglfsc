import { createRouter, createWebHistory } from 'vue-router'
import StudioPage from '../pages/StudioPage.vue'
import UploadPage from '../pages/UploadPage.vue'
import GeneratePage from '../pages/GeneratePage.vue'
import VerifyPage from '../pages/VerifyPage.vue'
import FaultTreeVisualization from '../pages/FaultTreeVisualization.vue'

const routes = [
  {
    path: '/',
    redirect: '/studio'
  },
  {
    path: '/studio',
    name: 'Studio',
    component: StudioPage,
    meta: { title: 'Fault Tree Studio' }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadPage,
    meta: { title: 'Upload' }
  },
  {
    path: '/generate',
    name: 'Generate',
    component: GeneratePage,
    meta: { title: 'Generate' }
  },
  {
    path: '/verify',
    name: 'Verify',
    component: VerifyPage,
    meta: { title: 'Verify' }
  },
  {
    path: '/visualization',
    name: 'Visualization',
    component: FaultTreeVisualization,
    meta: { title: 'Visualization' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
