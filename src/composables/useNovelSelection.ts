import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useNovelStore } from '@/stores/novel'

export function useNovelSelection() {
  const route = useRoute()
  const router = useRouter()
  const novelStore = useNovelStore()
  const { novels, currentNovel, loading: novelLoading } = storeToRefs(novelStore)

  const selectedNovelId = ref('')

  const handleNovelChange = async (id: string) => {
    if (!id) return
    selectedNovelId.value = id
    await novelStore.fetchNovel(id)
    
    // Sync with URL if needed
    if (route.query.id !== id) {
      router.replace({ query: { ...route.query, id } })
    }
  }

  const loadNovels = async () => {
    if (novels.value.length === 0) {
      await novelStore.fetchNovels()
    }
    
    // Auto-select from URL
    const idFromUrl = route.query.id as string
    if (idFromUrl) {
      selectedNovelId.value = idFromUrl
      await novelStore.fetchNovel(idFromUrl)
    } else if (novels.value.length > 0 && !selectedNovelId.value) {
      // Optional: Auto-select first novel
      // await handleNovelChange(novels.value[0].id)
    }
  }

  onMounted(() => {
    loadNovels()
  })

  // Watch for external URL changes
  watch(() => route.query.id, (newId) => {
    if (newId && newId !== selectedNovelId.value) {
      selectedNovelId.value = newId as string
      novelStore.fetchNovel(newId as string)
    }
  })

  return {
    novels,
    currentNovel,
    selectedNovelId,
    novelLoading,
    handleNovelChange,
    loadNovels
  }
}
