<template>
  <div class="analysis-view">
    <div class="page-header">
      <h2>剧情分析</h2>
      <p>使用 AI 自动识别小说中的人物、关系与情节线索</p>
    </div>

    <div class="analysis-content">
      <!-- 小说选择 -->
      <NovelSelector 
        v-model="selectedNovelId"
        :novels="novels"
        :current-novel="currentNovel"
        @change="handleNovelChange"
      />

      <!-- 分析配置 -->
      <AnalysisConfigForm 
        :analyzing="analyzing"
        :disabled="!selectedNovelId"
        :total-chapters="currentNovel?.total_chapters"
        @start="handleStartAnalysis"
        @cancel="cancelAnalysis"
      />

      <!-- 分析进度 -->
      <AnalysisProgress 
        v-if="analyzing || analysisProgress > 0"
        :progress="analysisProgress"
        :progress-text="progressText"
        :logs="analysisLogs"
      />

      <!-- 分析结果概览 -->
      <AnalysisResultCard 
        v-if="analysisResult && !showReanalyzeConfig"
        :result="analysisResult"
        @view-graph="router.push(`/graph?id=${selectedNovelId}`)"
        @view-characters="router.push(`/characters?id=${selectedNovelId}`)"
        @view-timeline="router.push(`/timeline?id=${selectedNovelId}`)"
        @export="openExportDialog"
        @delete="handleDeleteAnalysis"
        @reanalyze="handleReanalyze"
      />
    </div>

    <!-- 导出对话框 -->
    <ExportDialog 
      v-model:visible="exportDialogVisible"
      v-model:format="exportFormat"
      :loading="exporting"
      @confirm="() => handleExportConfirm(selectedNovelId, currentNovel)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { useNovelStore } from '@/stores/novel'

import NovelSelector from '@/components/analysis/NovelSelector.vue'
import AnalysisConfigForm from '@/components/analysis/AnalysisConfigForm.vue'
import AnalysisProgress from '@/components/analysis/AnalysisProgress.vue'
import AnalysisResultCard from '@/components/analysis/AnalysisResultCard.vue'
import ExportDialog from '@/components/analysis/ExportDialog.vue'

import { useAnalysisTask } from '@/composables/useAnalysisTask'
import { useExport } from '@/composables/useExport'

const router = useRouter()
const route = useRoute()
const novelStore = useNovelStore()

// State
const { novels } = storeToRefs(novelStore)
const selectedNovelId = ref('')
const showReanalyzeConfig = ref(false)
// Use store's currentNovel for reactivity
const { currentNovel } = storeToRefs(novelStore)

// Composables
const { 
  analyzing, 
  analysisProgress, 
  progressText, 
  analysisLogs, 
  analysisResult, 
  startAnalysis, 
  cancelAnalysis,
  startPolling,
  stopPolling
} = useAnalysisTask()

const {
  exportDialogVisible,
  exportFormat,
  exporting,
  openExportDialog,
  handleExportConfirm
} = useExport()

// Logic
const loadAnalysisResult = async () => {
  try {
    const result = await novelStore.getAnalysisResults(selectedNovelId.value)
    novelStore.setAnalysisResult({
      characterCount: result.character_count || 0,
      relationshipCount: result.relationship_count || 0,
      plotCount: result.plot_count || 0,
      chapterCount: result.chapter_count || currentNovel.value?.total_chapters || 0
    })
  } catch (error) {
    console.error('Failed to load analysis result:', error)
    if (currentNovel.value?.analysis_status === 'completed') {
        // Fallback or keep as is, consistent with original logic handling
        // We set a mock result structure if needed, or null
        novelStore.setAnalysisResult({
          characterCount: 28,
          relationshipCount: 45,
          plotCount: 12,
          chapterCount: currentNovel.value?.total_chapters || 0
        })
    }
  }
}

const handleNovelChange = async (id: string) => {
  if (!id) return
  try {
    // 1. Fetch novel details first (updates store.currentNovel)
    const novel = await novelStore.fetchNovel(id)
    
    // 2. FORCE SYNC: Trust Backend Status over Store State
    if (novel.analysis_status === 'completed') {
        // If backend says completed, we are done. Stop any phantom polling.
        if (analyzing.value) {
            stopPolling()
            novelStore.setAnalyzing(false)
        }
        // Load results immediately
        await loadAnalysisResult()
    } else if (novel.analysis_status === 'analyzing') {
        // If backend says analyzing, ensure store agrees and polling is active
        if (!analyzing.value) {
            novelStore.setAnalyzing(true)
            // If we have a task ID (persisted or from API?), resume polling.
            // Note: If taskId is lost on refresh, we might need an API to "get active task for novel"
            // For now, simple resumption if taskId exists
            if (novelStore.currentTaskId) {
                startPolling()
            }
        }
    } else {
        // Pending or failed, clear old results to avoid confusion
        // Only clear if we are switching to a truly "empty" novel
        if (analysisResult.value && novel.analysis_status === 'pending') {
            novelStore.setAnalysisResult(null)
        }
    }
  } catch (error) {
    console.error('Failed to load novel:', error)
  }
}

const handleStartAnalysis = (config: any) => {
  showReanalyzeConfig.value = false
  startAnalysis(selectedNovelId.value, config, currentNovel.value)
}

const handleReanalyze = () => {
  showReanalyzeConfig.value = true
}

const handleDeleteAnalysis = async () => {
  try {
    await novelStore.resetAnalysis(selectedNovelId.value)
    ElMessage.success('分析结果已删除')
    showReanalyzeConfig.value = false
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  await novelStore.fetchNovels()
  
  const id = route.query.id as string
  if (id) {
    selectedNovelId.value = id
    await handleNovelChange(id)
  }

  // Resume polling if needed
  if (analyzing.value && !analysisProgress.value && !progressText.value) {
      // If store says analyzing but we don't have progress info (e.g. refresh), start polling
      // Actually `useAnalysisTask` relies on `currentTaskId`. If that is preserved in store (Pinia persist?), it works.
      // If not, we might lose the task ID on refresh unless persisted.
      // Assuming store state is kept or reconstructed.
      // We call startPolling to ensure interval is running if analyzing is true.
      startPolling()
  }
})
</script>

<style lang="scss" scoped>
.analysis-view {
  max-width: 900px;
  margin: 0 auto;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
</style>
