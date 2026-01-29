import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import App from './App.vue'
import router from './router'
import { setApiBaseUrl } from './api'
import './assets/styles/main.scss'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// Initialize app with dynamic port
const init = async () => {
  // If running in Electron, get the dynamic port
  if (window.electronAPI) {
    try {
      const port = await window.electronAPI.getBackendPort()
      if (port) {
        setApiBaseUrl(port)
      }
    } catch (e) {
      console.error('Failed to initialize backend connection:', e)
    }
  }
  
  app.mount('#app')
}

init()
