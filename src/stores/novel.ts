import { defineStore } from 'pinia'
import { ref } from 'vue'
import { novelsApi, charactersApi, relationshipsApi } from '@/api'
import type { Novel, Character, Relationship, GraphData, Chapter } from '@/types'


export const useNovelStore = defineStore('novel', () => {
  const novels = ref<Novel[]>([])
  const currentNovel = ref<Novel | null>(null)
  const chapters = ref<Chapter[]>([])
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
    } catch (error: unknown) {
      console.error('Failed to fetch novels:', error)
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
    } catch (error: unknown) {
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
      graphData.value = {
        nodes: [],
        links: []
      }
      return graphData.value
    }
  }

  return {
    novels,
    currentNovel,
    chapters,
    characters,
    relationships,
    graphData,
    loading,
    fetchNovels,
    fetchNovel,
    fetchChapters,
    importNovel,
    deleteNovel,
    fetchCharacters,
    fetchRelationships,
    fetchGraphData
  }
})
