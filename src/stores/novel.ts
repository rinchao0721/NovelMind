import { defineStore } from 'pinia'
import { ref } from 'vue'
import { novelsApi, analysisApi, charactersApi, relationshipsApi } from '@/api'
import type { Novel, Character, Relationship, GraphData } from '@/types'

export const useNovelStore = defineStore('novel', () => {
  const novels = ref<Novel[]>([])
  const currentNovel = ref<Novel | null>(null)
  const characters = ref<Character[]>([])
  const relationships = ref<Relationship[]>([])
  const graphData = ref<GraphData | null>(null)
  const loading = ref(false)

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
      // 模拟导入
      const novel: Novel = {
        id: Date.now().toString(),
        title: file.name.replace(/\.[^/.]+$/, ''),
        author: '未知',
        file_path: file.name,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        analysis_status: 'pending',
        total_chapters: 0,
        total_words: 0
      }
      novels.value.unshift(novel)
      return novel
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
  const startAnalysis = async (novelId: string, options?: { depth?: string; provider?: string }) => {
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

  return {
    novels,
    currentNovel,
    characters,
    relationships,
    graphData,
    loading,
    fetchNovels,
    fetchNovel,
    importNovel,
    deleteNovel,
    fetchCharacters,
    fetchRelationships,
    fetchGraphData,
    startAnalysis,
    getAnalysisStatus,
    getAnalysisResults
  }
})
