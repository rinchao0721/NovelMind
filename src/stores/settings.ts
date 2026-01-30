import { defineStore } from 'pinia'
import { ref } from 'vue'
import { settingsApi } from '@/api'
import type { Settings, ProviderConfig } from '@/types'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<Settings | null>(null)
  const loading = ref(false)

  // 加载设置
  const loadSettings = async (): Promise<Settings | null> => {
    loading.value = true
    try {
      const data = await settingsApi.loadSettings()
      settings.value = data
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
      await settingsApi.saveSettings(newSettings)
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
  const testLLMConnection = async (provider: string, config: ProviderConfig): Promise<boolean> => {
    try {
      const result = await settingsApi.testProvider(provider, config)
      return result.success
    } catch (error) {
      console.error('Failed to test LLM connection:', error)
      return false
    }
  }

  return {
    settings,
    loading,
    loadSettings,
    saveSettings,
    testLLMConnection
  }
})
