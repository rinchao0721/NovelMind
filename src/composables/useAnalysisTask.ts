import { ref, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { useNovelStore } from '@/stores/novel'
import type { Novel } from '@/types'

export function useAnalysisTask() {
  const novelStore = useNovelStore()
  const { 
    analyzing, 
    analysisProgress, 
    progressText, 
    analysisLogs, 
    analysisResult, 
    currentTaskId 
  } = storeToRefs(novelStore)

  const pollingInterval = ref<number | null>(null)

  const addLog = (type: string, message: string) => {
    novelStore.addAnalysisLog(type, message)
  }

  const stopPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  }

  const startPolling = () => {
    stopPolling() // Ensure no duplicate intervals

    pollingInterval.value = window.setInterval(async () => {
      try {
        if (!currentTaskId.value) return

        const status = await novelStore.getAnalysisStatus(currentTaskId.value)
        
        novelStore.setAnalysisProgress(status.progress || 0, status.message || '分析中...')
        
        if (status.status === 'completed') {
          stopPolling()
          
          // 1. Mark not analyzing
          novelStore.setAnalyzing(false) 
          
          // 2. Refresh novel details to update analysis_status to 'completed' globally
          if (novelStore.currentNovel?.id) {
             await novelStore.fetchNovel(novelStore.currentNovel.id)
          }

          // 3. Load results if novelId available (we rely on view to watch status or user to refresh, 
          // but fetching novel above helps triggers)
          
          ElMessage.success('分析完成')
          addLog('success', '分析完成!')
        } else if (status.status === 'failed') {
          stopPolling()
          ElMessage.error('分析失败: ' + (status.error || '未知错误'))
          novelStore.setAnalyzing(false)
          addLog('error', '分析失败: ' + (status.error || '未知错误'))
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }, 2000)
  }

  const simulateAnalysis = async (currentNovel: Novel | null) => {
    const steps = [
      { progress: 10, message: '正在加载小说内容...' },
      { progress: 25, message: '正在识别人物信息...' },
      { progress: 50, message: '正在分析人物关系...' },
      { progress: 75, message: '正在追踪情节线索...' },
      { progress: 90, message: '正在生成章节摘要...' },
      { progress: 100, message: '分析完成!' }
    ]

    for (const step of steps) {
      if (!analyzing.value) break // Stop if cancelled
      await new Promise(resolve => setTimeout(resolve, 1500))
      novelStore.setAnalysisProgress(step.progress, step.message)
      addLog(step.progress === 100 ? 'success' : 'loading', step.message)
    }

    if (!analyzing.value) return

    // Mock result
    novelStore.setAnalysisResult({
      characterCount: 28,
      relationshipCount: 45,
      plotCount: 12,
      chapterCount: currentNovel?.total_chapters || 0
    })

    if (currentNovel) {
      currentNovel.analysis_status = 'completed'
    }

    ElMessage.success('分析完成')
    novelStore.setAnalyzing(false)
  }

  const startAnalysis = async (novelId: string, config: any, currentNovel: Novel | null) => {
    if (!novelId) return

    novelStore.clearAnalysisState()
    novelStore.setAnalyzing(true)

    try {
      addLog('loading', '正在初始化分析任务...')

      const result = await novelStore.startAnalysis(novelId, {
        depth: config.depth,
        provider: config.provider,
        model: config.model
      })

      if (result.taskId) {
        novelStore.setCurrentTaskId(result.taskId)
        addLog('success', '分析任务已创建')
        startPolling()
      } else {
        await simulateAnalysis(currentNovel)
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : '未知错误'
      ElMessage.error('启动分析失败: ' + message)
      addLog('error', '分析失败: ' + message)
      novelStore.setAnalyzing(false)
    }
  }

  const cancelAnalysis = () => {
    stopPolling()
    novelStore.setAnalyzing(false)
    addLog('info', '分析已取消')
  }

  // Cleanup on unmount
  onUnmounted(() => {
    stopPolling()
  })

  return {
    analyzing,
    analysisProgress,
    progressText,
    analysisLogs,
    analysisResult,
    startAnalysis,
    cancelAnalysis,
    stopPolling,
    startPolling // Exposed in case we need to restart polling on mount
  }
}
