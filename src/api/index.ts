import axios from 'axios'
import type { AnalysisConfig, ProviderConfig, Settings } from '@/types'

// Initial base URL - will be updated by setApiBaseUrl
const api = axios.create({
  baseURL: 'http://localhost:5001',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Track API connection status
let isConnected = false
let lastConnectionCheck = 0
const CONNECTION_CHECK_INTERVAL = 5000 // 5 seconds

// Function to update the base URL dynamically
export const setApiBaseUrl = (port: number) => {
  const newBaseURL = `http://localhost:${port}`
  api.defaults.baseURL = newBaseURL
  console.log(`[API] Base URL updated to: ${newBaseURL}`)
  
  // Reset connection status when URL changes
  isConnected = false
  lastConnectionCheck = 0
}

// Function to check API connection
export const checkApiConnection = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health', { timeout: 3000 })
    isConnected = response.status === 200
    lastConnectionCheck = Date.now()
    console.log(`[API] Health check: ${isConnected ? '✅ Connected' : '❌ Failed'}`)
    return isConnected
  } catch (error) {
    isConnected = false
    lastConnectionCheck = Date.now()
    console.error('[API] Health check failed:', error)
    return false
  }
}

// Get current connection status
export const getConnectionStatus = () => {
  return {
    isConnected,
    lastCheck: lastConnectionCheck,
    baseURL: api.defaults.baseURL
  }
}

// 请求拦截器
api.interceptors.request.use(
  async (config) => {
    // Periodic connection check
    const now = Date.now()
    if (!isConnected || (now - lastConnectionCheck > CONNECTION_CHECK_INTERVAL)) {
      // Don't check during health check to avoid recursion
      if (!config.url?.includes('/health')) {
        await checkApiConnection()
      }
    }
    
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // Mark as connected on successful response
    isConnected = true
    
    // Log successful requests (optional: filter by method to reduce noise)
    if (response.config.method !== 'get') {
      console.log(`[API] Success: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    }
    return response
  },
  (error) => {
    // Mark as disconnected on error
    isConnected = false
    
    // 统一错误处理
    if (error.response) {
      const { status, data } = error.response
      console.error(`[API] Error ${status}:`, data)
    } else if (error.request) {
      console.error('[API] Network Error - No response received')
      console.error('[API] Request config:', {
        url: error.config?.url,
        baseURL: error.config?.baseURL,
        method: error.config?.method
      })
      console.error('[API] Possible causes:')
      console.error('  1. Backend server is not running')
      console.error('  2. Backend is running on a different port')
      console.error('  3. CORS configuration issue')
      console.error(`  4. Current base URL: ${api.defaults.baseURL}`)
    } else {
      console.error('[API] Request Setup Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api

// Settings API
export const settingsApi = {
  // Load all settings
  async loadSettings() {
    const response = await api.get('/api/settings')
    return response.data
  },

  // Save all settings
  async saveSettings(settings: Partial<Settings>) {
    const response = await api.post('/api/settings', settings)
    return response.data
  },

  // Test LLM provider connection
  async testProvider(provider: string, config: ProviderConfig) {
    const response = await api.post('/api/settings/test-provider', {
      provider,
      config
    })
    return response.data
  },

  // Get application logs
  async getLogs(lines: number = 500) {
    const response = await api.get('/api/settings/logs', { params: { lines } })
    return response.data
  },

  // Clear application logs
  async clearLogs() {
    const response = await api.delete('/api/settings/logs')
    return response.data
  }
}

// Novels API
export const novelsApi = {
  // Get all novels
  async list() {
    const response = await api.get('/api/novels')
    return response.data
  },

  // Get novel by ID
  async get(id: string) {
    const response = await api.get(`/api/novels/${id}`)
    return response.data
  },

  // Upload novel file
  async upload(formData: FormData) {
    const response = await api.post('/api/novels/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Delete novel
  async delete(id: string) {
    const response = await api.delete(`/api/novels/${id}`)
    return response.data
  },

  // Get novel chapters
  async getChapters(novelId: string) {
    const response = await api.get(`/api/novels/${novelId}/chapters`)
    return response.data
  }
}

// Analysis API
export const analysisApi = {
  // Start novel analysis
  async startAnalysis(novelId: string, options?: AnalysisConfig) {
    const response = await api.post('/api/analysis/start', {
      novel_id: novelId,
      ...options
    })
    return response.data
  },

  // Get analysis status
  async getStatus(taskId: string) {
    const response = await api.get(`/api/analysis/${taskId}/status`)
    return response.data
  },

  // Get analysis result by task ID
  async getResult(taskId: string) {
    const response = await api.get(`/api/analysis/${taskId}/result`)
    return response.data
  },

  // Get analysis results for a novel (latest completed)
  async getResults(novelId: string) {
    const response = await api.get(`/api/analysis/${novelId}/results`)
    return response.data
  },

  // Delete all analysis results for a novel
  async deleteResults(novelId: string) {
    const response = await api.delete(`/api/analysis/${novelId}/results`)
    return response.data
  },

  // Cancel a running task
  async cancelAnalysis(taskId: string) {
    const response = await api.post(`/api/analysis/${taskId}/cancel`)
    return response.data
  }
}

// Characters API
export const charactersApi = {
  // Get all characters for a novel
  async list(novelId: string) {
    const response = await api.get('/api/characters', { params: { novel_id: novelId } })
    return response.data
  },

  // Get character by ID
  async get(characterId: string) {
    const response = await api.get(`/api/characters/${characterId}`)
    return response.data
  },

  // Update character
  async update(characterId: string, data: Partial<import('@/types').Character>) {
    const response = await api.put(`/api/characters/${characterId}`, data)
    return response.data
  }
}

// Relationships API
export const relationshipsApi = {
  // Get all relationships for a novel
  async list(novelId: string) {
    const response = await api.get(`/api/relationships/${novelId}`)
    return response.data
  },

  // Get relationship graph data (for visualization)
  async getGraph(novelId: string) {
    const response = await api.get(`/api/relationships/${novelId}/graph`)
    return response.data
  }
}

// Export API
export const exportApi = {
  // Export analysis results as JSON
  async exportJson(novelId: string) {
    const response = await api.get(`/api/export/${novelId}/json`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Export analysis results as Markdown
  async exportMarkdown(novelId: string) {
    const response = await api.get(`/api/export/${novelId}/markdown`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Export relationship graph as image
  async exportImage(novelId: string, format: 'png' | 'svg' = 'png') {
    const response = await api.get(`/api/export/${novelId}/image`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }
}
