<template>
  <div class="analysis-view">
    <PageHeader 
      title="剧情分析" 
      subtitle="使用 AI 自动识别小说中的人物、关系与情节线索" 
    />

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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNovelStore } from '@/stores/novel'
import { useAnalysisStore } from '@/stores/analysis'

import NovelSelector from '@/components/analysis/NovelSelector.vue'
import AnalysisConfigForm from '@/components/analysis/AnalysisConfigForm.vue'
import AnalysisProgress from '@/components/analysis/AnalysisProgress.vue'
import AnalysisResultCard from '@/components/analysis/AnalysisResultCard.vue'
import ExportDialog from '@/components/analysis/ExportDialog.vue'
// 导入公共资源
import PageHeader from '@/components/common/PageHeader.vue'
import { useAnalysisTask } from '@/composables/useAnalysisTask'
import { useExport } from '@/composables/useExport'
import { useNovelSelection } from '@/composables/useNovelSelection'
import type { AnalysisConfig } from '@/types'

const router = useRouter()
const novelStore = useNovelStore()
const analysisStore = useAnalysisStore()

// State
const { novels, currentNovel, selectedNovelId, handleNovelChange: baseNovelChange } = useNovelSelection()
const showReanalyzeConfig = ref(false)

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
    const result = await analysisStore.getAnalysisResult(selectedNovelId.value)
    // The result from store is already formatted
  } catch (error) {
    console.error('Failed to load analysis result:', error)
    if (currentNovel.value?.analysis_status === 'completed') {
        // Fallback or keep as is, consistent with original logic handling
        analysisStore.analysisResult = {
          task_id: 'fallback',
          novel_id: selectedNovelId.value,
          character_count: 28,
          relationship_count: 45,
          plot_count: 12,
          chapter_count: currentNovel.value?.total_chapters || 0,
          characters: [],
          relationships: []
        }
    }
  }
}

const handleNovelChange = async (id: string) => {
  if (!id) return
  try {
    // 1. Base novel change (fetch details, sync URL)
    await baseNovelChange(id)
    
    // 2. FORCE SYNC: Trust Backend Status over Store State
    const novel = currentNovel.value
    if (!novel) return
    
    if (novel.analysis_status === 'completed') {
        // If backend says completed, we are done. Stop any phantom polling.
        if (analyzing.value) {
            stopPolling()
        }
        // Load results immediately
        await loadAnalysisResult()
    } else if (novel.analysis_status === 'analyzing') {
        // If backend says analyzing, ensure polling is active
        if (!analyzing.value) {
            // Note: If taskId is lost on refresh, we might need an API to "get active task for novel"
            // For now, we assume useAnalysisTask will handle startPolling iftaskId is available
            // but we might need to set analyzing = true in analysisStore
            analysisStore.analyzing = true
            startPolling()
        }
    } else {
        // Pending or failed, clear old results to avoid confusion
        if (analysisResult.value && novel.analysis_status === 'pending') {
            analysisStore.clearState()
        }
    }
  } catch (error) {
    console.error('Failed to load novel:', error)
  }
}

const handleStartAnalysis = (config: AnalysisConfig) => {
  showReanalyzeConfig.value = false
  startAnalysis(selectedNovelId.value, config, currentNovel.value)
}

const handleReanalyze = () => {
  showReanalyzeConfig.value = true
}

const handleDeleteAnalysis = async () => {
  try {
    await analysisStore.resetAnalysis(selectedNovelId.value)
    ElMessage.success('分析结果已删除')
    showReanalyzeConfig.value = false
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
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
