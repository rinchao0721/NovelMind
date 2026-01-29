import { defineStore } from 'pinia'
import { ref } from 'vue'
import { novelsApi, analysisApi, charactersApi, relationshipsApi } from '@/api'
import type { Novel, Character, Relationship, GraphData } from '@/types'

// Analysis types
export interface AnalysisResult {
  characterCount: number
  relationshipCount: number
  plotCount: number
  chapterCount: number
}

export interface AnalysisLog {
  type: string
  message: string
  time: string
}

export const useNovelStore = defineStore('novel', () => {
  const novels = ref<Novel[]>([])
  const currentNovel = ref<Novel | null>(null)
  const chapters = ref<any[]>([])
  const characters = ref<Character[]>([])
  const relationships = ref<Relationship[]>([])
  const graphData = ref<GraphData | null>(null)
  const loading = ref(false)

  // Analysis state
  const analyzing = ref(false)
  const analysisProgress = ref(0)
  const progressText = ref('')
  const analysisLogs = ref<AnalysisLog[]>([])
  const analysisResult = ref<AnalysisResult | null>(null)
  const currentTaskId = ref('')

  // 获取小说列表
  const fetchNovels = async (): Promise<Novel[]> => {
    loading.value = true
    try {
      const data = await novelsApi.list()
      novels.value = data
      return novels.value
    } catch (error) {
      console.error('Failed to fetch novels:', error)
      // 返回模拟数据用于开发
      novels.value = []
      return novels.value
    } finally {
      loading.value = false
    }
  }

  // 获取单个小说
  const fetchNovel = async (id: string): Promise<Novel> => {
    loading.value = true
    try {
      const data = await novelsApi.get(id)
      currentNovel.value = data
      
      // Sync with list
      const index = novels.value.findIndex(n => n.id === id)
      if (index !== -1) {
        novels.value[index] = data
      }
      
      return currentNovel.value!
    } catch (error) {
      console.error('Failed to fetch novel:', error)
      // 返回模拟数据
      const found = novels.value.find(n => n.id === id)
      if (found) {
        currentNovel.value = found
      } else {
        throw error
      }
      return currentNovel.value!
    } finally {
      loading.value = false
    }
  }

  // 导入小说
  const importNovel = async (file: File): Promise<Novel> => {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const data = await novelsApi.upload(formData)
      novels.value.unshift(data)
      return data
    } catch (error) {
      console.error('Failed to import novel:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除小说
  const deleteNovel = async (id: string): Promise<void> => {
    try {
      await novelsApi.delete(id)
      novels.value = novels.value.filter(n => n.id !== id)
    } catch (error) {
      console.error('Failed to delete novel:', error)
      throw error
    }
  }

  // 获取章节列表
  const fetchChapters = async (novelId: string) => {
    try {
      const data = await novelsApi.getChapters(novelId)
      chapters.value = data
      return chapters.value
    } catch (error) {
      console.error('Failed to fetch chapters:', error)
      chapters.value = []
      return chapters.value
    }
  }

  // 获取人物列表
  const fetchCharacters = async (novelId: string): Promise<Character[]> => {
    try {
      const data = await charactersApi.list(novelId)
      characters.value = data
      return characters.value
    } catch (error) {
      console.error('Failed to fetch characters:', error)
      // 返回模拟数据
      characters.value = []
      return characters.value
    }
  }

  // 获取关系列表
  const fetchRelationships = async (novelId: string): Promise<Relationship[]> => {
    try {
      const data = await relationshipsApi.list(novelId)
      relationships.value = data
      return relationships.value
    } catch (error) {
      console.error('Failed to fetch relationships:', error)
      // 返回模拟数据
      relationships.value = []
      return relationships.value
    }
  }

  // 获取图谱数据
  const fetchGraphData = async (novelId: string): Promise<GraphData> => {
    try {
      const data = await relationshipsApi.getGraph(novelId)
      graphData.value = data
      return graphData.value!
    } catch (error) {
      console.error('Failed to fetch graph data:', error)
      // 返回模拟数据
      graphData.value = {
        nodes: [],
        links: []
      }
      return graphData.value
    }
  }

  // 开始分析
  const startAnalysis = async (novelId: string, options?: { depth?: string; provider?: string; model?: string }) => {
    try {
      const result = await analysisApi.startAnalysis(novelId, options)
      // 更新小说状态
      const novel = novels.value.find(n => n.id === novelId)
      if (novel) {
        novel.analysis_status = 'analyzing'
      }
      return result
    } catch (error) {
      console.error('Failed to start analysis:', error)
      throw error
    }
  }

  // 获取分析状态
  const getAnalysisStatus = async (taskId: string) => {
    try {
      return await analysisApi.getStatus(taskId)
    } catch (error) {
      console.error('Failed to get analysis status:', error)
      throw error
    }
  }

  // 获取分析结果
  const getAnalysisResults = async (novelId: string) => {
    try {
      return await analysisApi.getResults(novelId)
    } catch (error) {
      console.error('Failed to get analysis results:', error)
      throw error
    }
  }

  // 重置分析结果
  const resetAnalysis = async (novelId: string) => {
    try {
      await analysisApi.deleteResults(novelId)
      
      // Update local state
      const novel = novels.value.find(n => n.id === novelId)
      if (novel) {
        novel.analysis_status = 'pending'
      }
      if (currentNovel.value && currentNovel.value.id === novelId) {
        currentNovel.value.analysis_status = 'pending'
      }
      
      clearAnalysisState()
    } catch (error) {
      console.error('Failed to reset analysis:', error)
      throw error
    }
  }

  // 设置分析进度
  const setAnalysisProgress = (progress: number, text: string = '') => {
    analysisProgress.value = progress
    if (text) {
      progressText.value = text
    }
  }

  // 添加分析日志
  const addAnalysisLog = (type: string, message: string) => {
    analysisLogs.value.push({
      type,
      message,
      time: new Date().toLocaleTimeString()
    })
  }

  // 设置分析结果
  const setAnalysisResult = (result: AnalysisResult | null) => {
    analysisResult.value = result
  }

  // 清空分析状态
  const clearAnalysisState = () => {
    analyzing.value = false
    analysisProgress.value = 0
    progressText.value = ''
    analysisLogs.value = []
    analysisResult.value = null
    currentTaskId.value = ''
  }

  // 设置分析中状态
  const setAnalyzing = (value: boolean) => {
    analyzing.value = value
  }

  // 设置当前任务 ID
  const setCurrentTaskId = (taskId: string) => {
    currentTaskId.value = taskId
  }

  return {
    novels,
    currentNovel,
    chapters,
    characters,
    relationships,
    graphData,
    loading,
    // Analysis state
    analyzing,
    analysisProgress,
    progressText,
    analysisLogs,
    analysisResult,
    currentTaskId,
    // Methods
    fetchNovels,
    fetchNovel,
    fetchChapters,
    importNovel,
    deleteNovel,
    fetchCharacters,
    fetchRelationships,
    fetchGraphData,
    startAnalysis,
    getAnalysisStatus,
    getAnalysisResults,
    resetAnalysis,
    // Analysis methods
    setAnalysisProgress,
    addAnalysisLog,
    setAnalysisResult,
    clearAnalysisState,
    setAnalyzing,
    setCurrentTaskId
  }
})
