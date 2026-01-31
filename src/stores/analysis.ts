import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analysisApi } from '@/api'
import { useNovelStore } from './novel'
import type { AnalysisTask, AnalysisResult, AnalysisLog, AnalysisConfig } from '@/types'

export const useAnalysisStore = defineStore('analysis', () => {
  const novelStore = useNovelStore()
  
  const currentTask = ref<AnalysisTask | null>(null)
  const analysisResult = ref<AnalysisResult | null>(null)
  const analysisLogs = ref<AnalysisLog[]>([])
  const analysisProgress = ref(0)
  const progressText = ref('')
  const analyzing = ref(false)
  const loading = ref(false)

  // 开始分析
  const startAnalysis = async (novelId: string, config: AnalysisConfig): Promise<AnalysisTask> => {
    loading.value = true
    analyzing.value = true

    try {
      const data = await analysisApi.startAnalysis(novelId, config)
      currentTask.value = data
      return data
    } catch (error: unknown) {
      console.error('Failed to start analysis:', error)
      analyzing.value = false
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取分析状态
  const getAnalysisStatus = async (taskId: string): Promise<AnalysisTask> => {
    try {
      const data = await analysisApi.getStatus(taskId)
      currentTask.value = data
      
      // 更新本地进度
      if (data.progress !== undefined) {
        analysisProgress.value = data.progress
      }
      
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
        analyzing.value = false
      }

      return data
    } catch (error: unknown) {
      console.error('Failed to get analysis status:', error)
      throw error
    }
  }

  // 获取分析结果 (按小说 ID)
  const getAnalysisResult = async (novelId: string): Promise<AnalysisResult> => {
    try {
      const data = await analysisApi.getResults(novelId)
      analysisResult.value = data
      return data
    } catch (error) {
      console.error('Failed to get analysis result:', error)
      throw error
    }
  }

  // 取消分析
  const cancelAnalysis = async (taskId: string): Promise<void> => {
    try {
      await analysisApi.cancelAnalysis(taskId)
      if (currentTask.value?.id === taskId) {
        currentTask.value.status = 'cancelled'
      }
      analyzing.value = false
      addAnalysisLog('info', '分析已取消')
    } catch (error) {
      console.error('Failed to cancel analysis:', error)
      throw error
    }
  }

  // 重置分析结果
  const resetAnalysis = async (novelId: string): Promise<void> => {
    try {
      await analysisApi.deleteResults(novelId)
      if (analysisResult.value?.novel_id === novelId) {
        analysisResult.value = null
      }
      // 刷新 novelStore 中的小说状态
      await novelStore.fetchNovel(novelId)
    } catch (error) {
      console.error('Failed to reset analysis:', error)
      throw error
    }
  }

  // 辅助方法
  const setAnalysisProgress = (progress: number, text: string = '') => {
    analysisProgress.value = progress
    if (text) {
      progressText.value = text
    }
  }

  const addAnalysisLog = (type: AnalysisLog['type'], message: string) => {
    analysisLogs.value.push({
      type,
      message,
      time: new Date().toLocaleTimeString()
    })
  }

  const clearProgressState = () => {
    currentTask.value = null
    analysisLogs.value = []
    analysisProgress.value = 0
    progressText.value = ''
    // Note: Does NOT clear analyzing or analysisResult
  }

  const clearState = () => {
    currentTask.value = null
    analysisResult.value = null
    analysisLogs.value = []
    analysisProgress.value = 0
    progressText.value = ''
    analyzing.value = false
  }

  return {
    currentTask,
    analysisResult,
    analysisLogs,
    analysisProgress,
    progressText,
    analyzing,
    loading,
    startAnalysis,
    getAnalysisStatus,
    getAnalysisResult,
    cancelAnalysis,
    resetAnalysis,
    setAnalysisProgress,
    addAnalysisLog,
    clearProgressState,
    clearState
  }
})
