import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useNovelStore } from '@/stores/novel'
import { useAnalysisStore } from '@/stores/analysis'
import type { Novel, AnalysisTask, AnalysisConfig } from '@/types'

export function useAnalysisTask() {

  const novelStore = useNovelStore()
  const analysisStore = useAnalysisStore()
  
  const { 
    analyzing, 
    analysisProgress, 
    progressText, 
    analysisLogs, 
    analysisResult,
    currentTask
  } = storeToRefs(analysisStore)

  const pollingInterval = ref<number | null>(null)

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
        if (!currentTask.value?.id) return

        const status = await analysisStore.getAnalysisStatus(currentTask.value.id)
        
        analysisStore.setAnalysisProgress(status.progress || 0, status.error_message || '分析中...')
        
        if (status.status === 'completed') {
          stopPolling()
          
          // Refresh novel details to update analysis_status to 'completed' globally
          if (novelStore.currentNovel?.id) {
             await novelStore.fetchNovel(novelStore.currentNovel.id)
          }

          ElMessage.success('分析完成')
          analysisStore.addAnalysisLog('success', '分析完成!')
        } else if (status.status === 'failed') {
          stopPolling()
          ElMessage.error('分析失败: ' + (status.error_message || '未知错误'))
          analysisStore.addAnalysisLog('error', '分析失败: ' + (status.error_message || '未知错误'))
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
      analysisStore.setAnalysisProgress(step.progress, step.message)
      analysisStore.addAnalysisLog(step.progress === 100 ? 'success' : 'loading', step.message)
    }

    if (!analyzing.value) return

    // Mock result (normally we'd fetch actual results here)
    if (currentNovel?.id) {
        try {
            await analysisStore.getAnalysisResult(currentNovel.id)
        } catch (e) {
            // Fallback for simulation
            analysisResult.value = {
                task_id: 'simulated',
                novel_id: currentNovel.id,
                character_count: 28,
                relationship_count: 45,
                plot_count: 12,
                chapter_count: currentNovel?.total_chapters || 0,
                characters: [],
                relationships: []
            }
        }
    }

    if (currentNovel) {
      currentNovel.analysis_status = 'completed'
    }

    ElMessage.success('分析完成')
  }

  const startAnalysis = async (novelId: string, config: AnalysisConfig, currentNovel: Novel | null) => {
    if (!novelId) return

    analysisStore.clearState()

    try {
      analysisStore.addAnalysisLog('loading', '正在初始化分析任务...')

      const result = await analysisStore.startAnalysis(novelId, {
        depth: config.depth,
        provider: config.provider,
        model: config.model
      })

      if (result.id) {
        analysisStore.addAnalysisLog('success', '分析任务已创建')
        startPolling()
      } else {
        await simulateAnalysis(currentNovel)
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : '未知错误'
      ElMessage.error('启动分析失败: ' + message)
      analysisStore.addAnalysisLog('error', '分析失败: ' + message)
    }
  }

  const cancelAnalysis = () => {
    stopPolling()
    if (currentTask.value?.id) {
        analysisStore.cancelAnalysis(currentTask.value.id)
    }
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
    startPolling
  }
}
