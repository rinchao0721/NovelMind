import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface Settings {
  defaultProvider: string
  openai: {
    apiKey: string
    baseUrl: string
    model: string
  }
  claude: {
    apiKey: string
    model: string
  }
  deepseek: {
    apiKey: string
    model: string
  }
  qwen: {
    apiKey: string
    model: string
  }
  custom: {
    apiKey: string
    baseUrl: string
    model: string
  }
  neo4j: {
    uri: string
    user: string
    password: string
  }
  theme: string
  language: string
  defaultAnalysisDepth: string
  autoSave: boolean
  dataPath: string
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<Settings | null>(null)
  const loading = ref(false)

  // 加载设置
  const loadSettings = async (): Promise<Settings | null> => {
    loading.value = true
    try {
      const response = await api.get('/api/settings')
      settings.value = response.data
      return settings.value
    } catch (error) {
      console.error('Failed to load settings:', error)
      // 从本地存储加载
      const saved = localStorage.getItem('novelmind_settings')
      if (saved) {
        settings.value = JSON.parse(saved)
      }
      return settings.value
    } finally {
      loading.value = false
    }
  }

  // 保存设置
  const saveSettings = async (newSettings: Settings): Promise<void> => {
    loading.value = true
    try {
      await api.put('/api/settings', newSettings)
      settings.value = newSettings
    } catch (error) {
      console.error('Failed to save settings to server:', error)
    }
    // 同时保存到本地存储
    localStorage.setItem('novelmind_settings', JSON.stringify(newSettings))
    settings.value = newSettings
    loading.value = false
  }

  // 测试 LLM 连接
  const testLLMConnection = async (provider: string, config: any): Promise<boolean> => {
    try {
      const response = await api.post('/api/settings/llm/test', {
        provider,
        config
      })
      return response.data.success
    } catch (error) {
      console.error('Failed to test LLM connection:', error)
      return false
    }
  }

  // 测试 Neo4j 连接
  const testNeo4jConnection = async (config: any): Promise<boolean> => {
    try {
      const response = await api.post('/api/settings/neo4j/test', config)
      return response.data.success
    } catch (error) {
      console.error('Failed to test Neo4j connection:', error)
      return false
    }
  }

  return {
    settings,
    loading,
    loadSettings,
    saveSettings,
    testLLMConnection,
    testNeo4jConnection
  }
})
