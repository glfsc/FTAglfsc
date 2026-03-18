import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const ensureTailwindCdnLoaded = () => {
  if (typeof document === 'undefined') return Promise.resolve()
  if (document.querySelector('script[data-tailwindcdn="true"]')) return Promise.resolve()

  return new Promise((resolve) => {
    const script = document.createElement('script')
    script.src = 'https://cdn.tailwindcss.com'
    script.async = true
    script.setAttribute('data-tailwindcdn', 'true')
    script.onload = () => resolve()
    script.onerror = () => resolve()
    document.head.appendChild(script)
  })
}

const bootstrap = async () => {
  const shouldLoadTailwindNow =
    typeof window !== 'undefined' && window.location.pathname.startsWith('/test-theme')
  if (shouldLoadTailwindNow) await ensureTailwindCdnLoaded()

  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)
  app.use(router)
  app.use(ElementPlus)

  router.afterEach(async (to) => {
    if (to.path.startsWith('/test-theme')) await ensureTailwindCdnLoaded()
  })

  app.mount('#app')
}

bootstrap()
