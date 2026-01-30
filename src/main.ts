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

// Initialize backend connection with retry mechanism
const initBackendConnection = async (maxRetries = 5, delay = 500): Promise<number> => {
  console.log('[Init] Initializing backend connection...')
  
  // If not running in Electron, use default port
  if (!window.electronAPI) {
    console.log('[Init] Not running in Electron, using default port 5001')
    return 5001
  }

  // Try to get port from Electron with retries
  for (let i = 0; i < maxRetries; i++) {
    try {
      console.log(`[Init] Attempt ${i + 1}/${maxRetries} to get backend port...`)
      const port = await window.electronAPI.getBackendPort()
      
      if (port && port > 0) {
        console.log(`[Init] ✅ Successfully got backend port: ${port}`)
        return port
      } else {
        console.warn(`[Init] ⚠️ Invalid port received: ${port}`)
      }
    } catch (e) {
      console.error(`[Init] ❌ Attempt ${i + 1} failed:`, e)
    }
    
    // Wait before retry (except on last attempt)
    if (i < maxRetries - 1) {
      console.log(`[Init] Waiting ${delay}ms before retry...`)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  
  // Fallback to default port
  console.warn('[Init] ⚠️ All attempts failed, falling back to default port 5001')
  return 5001
}

// Initialize app with dynamic port
const init = async () => {
  try {
    // Get backend port with retry mechanism
    const port = await initBackendConnection()
    
    // Set API base URL
    setApiBaseUrl(port)
    console.log(`[Init] API base URL set to: http://localhost:${port}`)
    
    // Mount app
    app.mount('#app')
    console.log('[Init] ✅ App mounted successfully')
  } catch (error) {
    console.error('[Init] ❌ Fatal error during initialization:', error)
    // Mount app anyway with default configuration
    app.mount('#app')
  }
}

init()
