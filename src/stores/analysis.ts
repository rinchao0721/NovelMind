import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'
import type { AnalysisTask, AnalysisResult } from '@/types'

export const useAnalysisStore = defineStore('analysis', () => {
  const currentTask = ref<AnalysisTask | null>(null)
  const analysisResult = ref<AnalysisResult | null>(null)
  const loading = ref(false)

  // 开始分析
  const startAnalysis = async (novelId: string, config: any): Promise<AnalysisTask> => {
    loading.value = true
    try {
      const response = await api.post('/api/analysis/start', {
        novel_id: novelId,
        ...config
      })
      currentTask.value = response.data
      return currentTask.value!
    } catch (error) {
      console.error('Failed to start analysis:', error)
      // 模拟任务
      currentTask.value = {
        id: Date.now().toString(),
        novel_id: novelId,
        status: 'analyzing',
        progress: 0,
        started_at: new Date().toISOString(),
        completed_at: null,
        error_message: null
      }
      return currentTask.value
    } finally {
      loading.value = false
    }
  }

  // 获取分析状态
  const getAnalysisStatus = async (taskId: string): Promise<AnalysisTask> => {
    try {
      const response = await api.get(`/api/analysis/${taskId}/status`)
      currentTask.value = response.data
      return currentTask.value!
    } catch (error) {
      console.error('Failed to get analysis status:', error)
      throw error
    }
  }

  // 获取分析结果
  const getAnalysisResult = async (taskId: string): Promise<AnalysisResult> => {
    try {
      const response = await api.get(`/api/analysis/${taskId}/result`)
      analysisResult.value = response.data
      return analysisResult.value!
    } catch (error) {
      console.error('Failed to get analysis result:', error)
      throw error
    }
  }

  // 取消分析
  const cancelAnalysis = async (taskId: string): Promise<void> => {
    try {
      await api.post(`/api/analysis/${taskId}/cancel`)
      if (currentTask.value?.id === taskId) {
        currentTask.value.status = 'cancelled'
      }
    } catch (error) {
      console.error('Failed to cancel analysis:', error)
      throw error
    }
  }

  return {
    currentTask,
    analysisResult,
    loading,
    startAnalysis,
    getAnalysisStatus,
    getAnalysisResult,
    cancelAnalysis
  }
})
