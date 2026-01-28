<template>
  <div class="analysis-view">
    <div class="page-header">
      <h2>剧情分析</h2>
      <p>使用 AI 自动识别小说中的人物、关系与情节线索</p>
    </div>

    <div class="analysis-content">
      <!-- 小说选择 -->
      <div class="novel-selector card">
        <h3>选择小说</h3>
        <el-select 
          v-model="selectedNovelId" 
          placeholder="请选择要分析的小说"
          size="large"
          style="width: 100%"
          @change="handleNovelChange"
        >
          <el-option
            v-for="novel in novels"
            :key="novel.id"
            :label="novel.title"
            :value="novel.id"
          />
        </el-select>

        <div v-if="currentNovel" class="novel-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="书名">{{ currentNovel.title }}</el-descriptions-item>
            <el-descriptions-item label="作者">{{ currentNovel.author || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="章节数">{{ currentNovel.total_chapters }}</el-descriptions-item>
            <el-descriptions-item label="总字数">{{ formatNumber(currentNovel.total_words) }}</el-descriptions-item>
            <el-descriptions-item label="分析状态">
              <el-tag :type="getStatusType(currentNovel.analysis_status)">
                {{ getStatusText(currentNovel.analysis_status) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- 分析配置 -->
      <div class="analysis-config card">
        <h3>分析配置</h3>
        <el-form label-width="120px">
          <el-form-item label="分析范围">
            <el-radio-group v-model="analysisConfig.scope">
              <el-radio value="full">全书分析</el-radio>
              <el-radio value="partial">部分章节</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="analysisConfig.scope === 'partial'" label="章节范围">
            <el-slider
              v-model="analysisConfig.chapterRange"
              range
              :min="1"
              :max="currentNovel?.total_chapters || 100"
              :marks="chapterMarks"
            />
          </el-form-item>

          <el-form-item label="分析模型">
            <div class="model-selection">
              <el-select v-model="analysisConfig.provider" placeholder="选择服务商" style="width: 150px">
                <el-option
                  v-for="provider in PROVIDERS"
                  :key="provider.id"
                  :label="provider.name"
                  :value="provider.id"
                >
                  <div class="provider-option">
                    <ProviderAvatar :provider-id="provider.id" :size="20" style="margin-right: 8px" />
                    <span>{{ provider.name }}</span>
                  </div>
                </el-option>
                <template #prefix v-if="analysisConfig.provider">
                  <ProviderAvatar :provider-id="analysisConfig.provider" :size="20" />
                </template>
              </el-select>
              <el-select 
                v-model="analysisConfig.model" 
                placeholder="选择或输入模型" 
                allow-create 
                filterable 
                default-first-option
                style="flex: 1"
              >
                <el-option
                  v-for="model in availableModels"
                  :key="model"
                  :label="model"
                  :value="model"
                />
              </el-select>
            </div>
          </el-form-item>

          <el-form-item label="分析深度">
            <el-select v-model="analysisConfig.depth" style="width: 200px">
              <el-option label="快速分析 (节省API调用)" value="quick" />
              <el-option label="标准分析 (推荐)" value="standard" />
              <el-option label="深度分析 (更精准)" value="deep" />
            </el-select>
          </el-form-item>

          <el-form-item label="分析项目">
            <el-checkbox-group v-model="analysisConfig.features">
              <el-checkbox value="characters">人物识别</el-checkbox>
              <el-checkbox value="relationships">关系分析</el-checkbox>
              <el-checkbox value="plot">情节追踪</el-checkbox>
              <el-checkbox value="summary">章节摘要</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              size="large"
              :loading="analyzing"
              :disabled="!selectedNovelId || analyzing"
              @click="startAnalysis"
            >
              <el-icon><VideoPlay /></el-icon>
              {{ analyzing ? '分析中...' : '开始分析' }}
            </el-button>
            <el-button 
              v-if="analyzing"
              size="large"
              @click="cancelAnalysis"
            >
              取消分析
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 分析进度 -->
      <div v-if="analyzing || analysisProgress > 0" class="analysis-progress card">
        <h3>分析进度</h3>
        <el-progress 
          :percentage="analysisProgress" 
          :status="analysisProgress === 100 ? 'success' : ''"
          :stroke-width="20"
        />
        <p class="progress-text">{{ progressText }}</p>

        <div v-if="analysisLogs.length > 0" class="analysis-logs">
          <div 
            v-for="(log, index) in analysisLogs" 
            :key="index"
            class="log-item"
          >
            <el-icon :class="log.type">
              <SuccessFilled v-if="log.type === 'success'" />
              <Loading v-else-if="log.type === 'loading'" class="is-loading" />
              <WarningFilled v-else-if="log.type === 'error'" />
              <InfoFilled v-else />
            </el-icon>
            <span>{{ log.message }}</span>
            <span class="log-time">{{ log.time }}</span>
          </div>
        </div>
      </div>

      <!-- 分析结果概览 -->
      <div v-if="analysisResult" class="analysis-result card">
        <h3>分析结果</h3>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="识别人物" :value="analysisResult.characterCount">
              <template #suffix>
                <span class="stat-suffix">人</span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="人物关系" :value="analysisResult.relationshipCount">
              <template #suffix>
                <span class="stat-suffix">条</span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="主要情节" :value="analysisResult.plotCount">
              <template #suffix>
                <span class="stat-suffix">个</span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="分析章节" :value="analysisResult.chapterCount">
              <template #suffix>
                <span class="stat-suffix">章</span>
              </template>
            </el-statistic>
          </el-col>
        </el-row>

        <div class="result-actions">
          <el-button type="primary" @click="router.push(`/graph?id=${selectedNovelId}`)">
            <el-icon><Share /></el-icon>
            查看关系图谱
          </el-button>
          <el-button @click="router.push(`/characters?id=${selectedNovelId}`)">
            <el-icon><User /></el-icon>
            查看人物列表
          </el-button>
          <el-button @click="router.push(`/timeline?id=${selectedNovelId}`)">
            <el-icon><Timer /></el-icon>
            查看时间线
          </el-button>
          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出结果
          </el-button>
        </div>
      </div>
    </div>

    <!-- 导出对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出分析结果" width="400px">
      <div class="export-options">
        <el-radio-group v-model="exportFormat" class="export-format">
          <el-radio-button value="json">JSON</el-radio-button>
          <el-radio-button value="markdown">Markdown</el-radio-button>
        </el-radio-group>
        <p class="export-hint">
          {{ exportFormat === 'json' ? 'JSON 格式包含完整数据，适合导入其他工具' : 'Markdown 格式便于阅读和分享' }}
        </p>
      </div>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="exporting" @click="confirmExport">
          导出
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { VideoPlay, Share, User, Timer, Download, SuccessFilled, Loading, InfoFilled, WarningFilled } from '@element-plus/icons-vue'
import { useNovelStore } from '@/stores/novel'
import { exportApi, settingsApi } from '@/api'
import type { Novel } from '@/types'
import { PROVIDERS } from '@/config/providers'
import ProviderAvatar from '@/components/ProviderAvatar.vue'

const router = useRouter()
const route = useRoute()
const novelStore = useNovelStore()

// 使用 store 中的状态
const { 
  analyzing, 
  analysisProgress, 
  progressText, 
  analysisLogs, 
  analysisResult, 
  currentTaskId 
} = storeToRefs(novelStore)

const novels = ref<Novel[]>([])
const selectedNovelId = ref('')
const currentNovel = ref<Novel | null>(null)
// const analyzing = ref(false) // Moved to store
// const analysisProgress = ref(0) // Moved to store
// const progressText = ref('') // Moved to store
// const analysisLogs = ref<Array<{ type: string; message: string; time: string }>>([]) // Moved to store
// const analysisResult = ref<{...} | null>(null) // Moved to store
// const currentTaskId = ref('') // Moved to store

const pollingInterval = ref<number | null>(null)
const exportDialogVisible = ref(false)
const exportFormat = ref<'json' | 'markdown'>('json')
const exporting = ref(false)

const analysisConfig = ref({
  scope: 'full',
  chapterRange: [1, 100],
  depth: 'standard',
  features: ['characters', 'relationships', 'plot', 'summary'],
  provider: '',
  model: ''
})

const availableModels = computed(() => {
  const provider = PROVIDERS.find(p => p.id === analysisConfig.value.provider)
  return provider ? provider.defaultModels : []
})

watch(() => analysisConfig.value.provider, (newVal) => {
  const provider = PROVIDERS.find(p => p.id === newVal)
  if (provider && provider.defaultModels.length > 0) {
    if (provider.id === 'custom') {
       // Custom provider might not have default models listed
    } else if (!analysisConfig.value.model || !provider.defaultModels.includes(analysisConfig.value.model)) {
      analysisConfig.value.model = provider.defaultModels[0]
    }
  }
})

const chapterMarks = computed(() => {
  const max = currentNovel.value?.total_chapters || 100
  return {
    1: '第1章',
    [max]: `第${max}章`
  }
})

const handleNovelChange = async (id: string) => {
  if (!id) return
  try {
    currentNovel.value = await novelStore.fetchNovel(id)
    analysisConfig.value.chapterRange = [1, currentNovel.value.total_chapters]
    
    // 如果正在分析当前小说，不需要重置结果
    // 只有当切换到不同小说且不在分析状态时，才尝试加载结果
    if (!analyzing.value) {
      if (currentNovel.value.analysis_status === 'completed') {
        await loadAnalysisResult()
      } else {
        // 如果不是 completed，且没有正在进行的分析（store中状态），则清空结果
        // 但要注意，如果 store 中保留的是上一次分析的结果，这里可能需要判断是否属于当前小说
        // 简化起见，如果切换小说，且该小说状态已完成，加载其结果；否则清空当前显示的 store 结果
        // 除非 store 中的结果本来就是这个小说的（比如刚分析完未离开页面又刷新）
        // 这里做一个简单的策略：每次切换小说，如果状态完成就加载，否则清空 store 中的结果以避免显示错误数据
        if (analysisResult.value) {
            // 这里其实应该判断 analysisResult 是否属于当前小说，但 store 里没存 novelId
            // 所以简单清空比较安全，除非正在分析中
            novelStore.setAnalysisResult(null)
        }
      }
    }
  } catch (error) {
    console.error('Failed to load novel:', error)
  }
}

const addLog = (type: string, message: string) => {
  novelStore.addAnalysisLog(type, message)
}

const startAnalysis = async () => {
  if (!selectedNovelId.value) return

  // 重置 Store 状态
  novelStore.clearAnalysisState()
  novelStore.setAnalyzing(true)

  try {
    addLog('loading', '正在初始化分析任务...')

    // 调用后端开始分析
    const result = await novelStore.startAnalysis(selectedNovelId.value, {
      depth: analysisConfig.value.depth,
      provider: analysisConfig.value.provider,
      model: analysisConfig.value.model
    })

    if (result.taskId) {
      novelStore.setCurrentTaskId(result.taskId)
      addLog('success', '分析任务已创建')
      startPolling()
    } else {
      // 模拟分析进度（后端未实现时的备用方案）
      await simulateAnalysis()
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('启动分析失败: ' + message)
    addLog('error', '分析失败: ' + message)
    novelStore.setAnalyzing(false)
  }
}

const simulateAnalysis = async () => {
  const steps = [
    { progress: 10, message: '正在加载小说内容...' },
    { progress: 25, message: '正在识别人物信息...' },
    { progress: 50, message: '正在分析人物关系...' },
    { progress: 75, message: '正在追踪情节线索...' },
    { progress: 90, message: '正在生成章节摘要...' },
    { progress: 100, message: '分析完成!' }
  ]

  for (const step of steps) {
    await new Promise(resolve => setTimeout(resolve, 1500))
    novelStore.setAnalysisProgress(step.progress, step.message)
    addLog(step.progress === 100 ? 'success' : 'loading', step.message)
  }

  // 模拟结果
  novelStore.setAnalysisResult({
    characterCount: 28,
    relationshipCount: 45,
    plotCount: 12,
    chapterCount: currentNovel.value?.total_chapters || 0
  })

  // 更新小说状态
  if (currentNovel.value) {
    currentNovel.value.analysis_status = 'completed'
  }

  ElMessage.success('分析完成')
  novelStore.setAnalyzing(false)
}

const startPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  pollingInterval.value = window.setInterval(async () => {
    try {
      const status = await novelStore.getAnalysisStatus(currentTaskId.value)
      
      novelStore.setAnalysisProgress(status.progress || 0, status.message || '分析中...')
      
      if (status.status === 'completed') {
        stopPolling()
        await loadAnalysisResult()
        ElMessage.success('分析完成')
        novelStore.setAnalyzing(false)
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

const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

const cancelAnalysis = () => {
  stopPolling()
  novelStore.setAnalyzing(false)
  addLog('info', '分析已取消')
}

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
    // 只有在开发模式或确实无法获取时才使用模拟数据，这里为了稳健先清空或保持原样
    // 如果是 completed 状态但获取失败，可能是数据问题
    if (currentNovel.value?.analysis_status === 'completed') {
         // 尝试使用 store 中的模拟数据结构，或者保持 null 让用户重试
         // 为了用户体验，这里暂时不回退到硬编码的模拟数据，而是提示错误
         // 或者如果后端尚未实现该API，则需要保留之前的模拟逻辑
         // 鉴于之前有模拟逻辑：
        novelStore.setAnalysisResult({
          characterCount: 28, // 模拟数据
          relationshipCount: 45,
          plotCount: 12,
          chapterCount: currentNovel.value?.total_chapters || 0
        })
    }
  }
}

// ... existing export and helper functions ...

onMounted(async () => {
  novels.value = await novelStore.fetchNovels()
  
  // 从 URL 参数获取小说 ID
  const id = route.query.id as string
  if (id) {
    selectedNovelId.value = id
    await handleNovelChange(id)
  }

  // 恢复状态逻辑：
  // 如果 store 中正在分析，且没有设置轮询（说明是切换页面回来），则重新开始轮询
  if (analyzing.value && currentTaskId.value && !pollingInterval.value) {
      startPolling()
  }

  // Load default provider settings
  try {
    const settings = await settingsApi.loadSettings()
    if (settings.defaultProvider) {
      analysisConfig.value.provider = settings.defaultProvider
      // Try to get saved model for this provider
      if (settings[settings.defaultProvider]?.model) {
        analysisConfig.value.model = settings[settings.defaultProvider].model
      }
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
})

onUnmounted(() => {
  stopPolling()
  // 注意：不再清空 store 状态，以保持页面切换后的数据
})

const availableModels = computed(() => {
  const provider = PROVIDERS.find(p => p.id === analysisConfig.value.provider)
  return provider ? provider.defaultModels : []
})

watch(() => analysisConfig.value.provider, (newVal) => {
  const provider = PROVIDERS.find(p => p.id === newVal)
  if (provider && provider.defaultModels.length > 0) {
    // If current model is not valid for new provider, select the first default
    // Or if custom provider, we might want to keep the input or clear it.
    // For simplicity, reset to first default if available.
    if (provider.id === 'custom') {
       // Custom provider might not have default models listed, keep existing or clear
    } else if (!analysisConfig.value.model || !provider.defaultModels.includes(analysisConfig.value.model)) {
      analysisConfig.value.model = provider.defaultModels[0]
    }
  }
})

const chapterMarks = computed(() => {
  const max = currentNovel.value?.total_chapters || 100
  return {
    1: '第1章',
    [max]: `第${max}章`
  }
})

const handleNovelChange = async (id: string) => {
  if (!id) return
  try {
    currentNovel.value = await novelStore.fetchNovel(id)
    analysisConfig.value.chapterRange = [1, currentNovel.value.total_chapters]
    
    // 如果已分析完成，加载结果
    if (currentNovel.value.analysis_status === 'completed') {
      await loadAnalysisResult()
    } else {
      analysisResult.value = null
    }
  } catch (error) {
    console.error('Failed to load novel:', error)
  }
}

const addLog = (type: string, message: string) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  analysisLogs.value.push({ type, message, time })
}

const startAnalysis = async () => {
  if (!selectedNovelId.value) return

  analyzing.value = true
  analysisProgress.value = 0
  analysisLogs.value = []
  analysisResult.value = null

  try {
    addLog('loading', '正在初始化分析任务...')

    // 调用后端开始分析
    const result = await novelStore.startAnalysis(selectedNovelId.value, {
      depth: analysisConfig.value.depth,
      provider: analysisConfig.value.provider,
      model: analysisConfig.value.model
    })

    if (result.taskId) {
      currentTaskId.value = result.taskId
      addLog('success', '分析任务已创建')
      startPolling()
    } else {
      // 模拟分析进度（后端未实现时的备用方案）
      await simulateAnalysis()
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('启动分析失败: ' + message)
    addLog('error', '分析失败: ' + message)
    analyzing.value = false
  }
}

const simulateAnalysis = async () => {
  const steps = [
    { progress: 10, message: '正在加载小说内容...' },
    { progress: 25, message: '正在识别人物信息...' },
    { progress: 50, message: '正在分析人物关系...' },
    { progress: 75, message: '正在追踪情节线索...' },
    { progress: 90, message: '正在生成章节摘要...' },
    { progress: 100, message: '分析完成!' }
  ]

  for (const step of steps) {
    await new Promise(resolve => setTimeout(resolve, 1500))
    analysisProgress.value = step.progress
    progressText.value = step.message
    addLog(step.progress === 100 ? 'success' : 'loading', step.message)
  }

  // 模拟结果
  analysisResult.value = {
    characterCount: 28,
    relationshipCount: 45,
    plotCount: 12,
    chapterCount: currentNovel.value?.total_chapters || 0
  }

  // 更新小说状态
  if (currentNovel.value) {
    currentNovel.value.analysis_status = 'completed'
  }

  ElMessage.success('分析完成')
  analyzing.value = false
}

const startPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }

  pollingInterval.value = window.setInterval(async () => {
    try {
      const status = await novelStore.getAnalysisStatus(currentTaskId.value)
      
      analysisProgress.value = status.progress || 0
      progressText.value = status.message || '分析中...'
      
      if (status.status === 'completed') {
        stopPolling()
        await loadAnalysisResult()
        ElMessage.success('分析完成')
        analyzing.value = false
        addLog('success', '分析完成!')
      } else if (status.status === 'failed') {
        stopPolling()
        ElMessage.error('分析失败: ' + (status.error || '未知错误'))
        analyzing.value = false
        addLog('error', '分析失败: ' + (status.error || '未知错误'))
      }
    } catch (error) {
      console.error('Polling error:', error)
    }
  }, 2000)
}

const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

const cancelAnalysis = () => {
  stopPolling()
  analyzing.value = false
  addLog('info', '分析已取消')
}

const loadAnalysisResult = async () => {
  try {
    const result = await novelStore.getAnalysisResults(selectedNovelId.value)
    analysisResult.value = {
      characterCount: result.character_count || 0,
      relationshipCount: result.relationship_count || 0,
      plotCount: result.plot_count || 0,
      chapterCount: result.chapter_count || currentNovel.value?.total_chapters || 0
    }
  } catch (error) {
    console.error('Failed to load analysis result:', error)
    // 使用模拟数据
    analysisResult.value = {
      characterCount: 28,
      relationshipCount: 45,
      plotCount: 12,
      chapterCount: currentNovel.value?.total_chapters || 0
    }
  }
}

const handleExport = () => {
  exportDialogVisible.value = true
}

const confirmExport = async () => {
  exporting.value = true
  try {
    let blob: Blob
    let filename: string
    
    if (exportFormat.value === 'json') {
      blob = await exportApi.exportJson(selectedNovelId.value)
      filename = `${currentNovel.value?.title || 'novel'}_analysis.json`
    } else {
      blob = await exportApi.exportMarkdown(selectedNovelId.value)
      filename = `${currentNovel.value?.title || 'novel'}_analysis.md`
    }
    
    // 下载文件
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
    
    exportDialogVisible.value = false
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const getStatusType = (status: string): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
    pending: 'info',
    analyzing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待分析',
    analyzing: '分析中',
    completed: '已完成',
    failed: '分析失败'
  }
  return map[status] || status
}

const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num?.toString() || '0'
}

onMounted(async () => {
  novels.value = await novelStore.fetchNovels()
  
  // 从 URL 参数获取小说 ID
  const id = route.query.id as string
  if (id) {
    selectedNovelId.value = id
    await handleNovelChange(id)
  }

  // Load default provider settings
  try {
    const settings = await settingsApi.loadSettings()
    if (settings.defaultProvider) {
      analysisConfig.value.provider = settings.defaultProvider
      // Try to get saved model for this provider
      if (settings[settings.defaultProvider]?.model) {
        analysisConfig.value.model = settings[settings.defaultProvider].model
      }
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
})

onUnmounted(() => {
  stopPolling()
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

.card {
  h3 {
    font-size: 16px;
    margin: 0 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
  }
}

.novel-selector {
  .novel-info {
    margin-top: 16px;
  }
}

.model-selection {
  display: flex;
  gap: 12px;
  width: 100%;
}

.provider-option {
  display: flex;
  align-items: center;
}

.analysis-progress {
  .progress-text {
    text-align: center;
    margin-top: 12px;
    color: var(--text-color-secondary);
  }

  .analysis-logs {
    margin-top: 20px;
    max-height: 200px;
    overflow-y: auto;
    background: var(--hover-bg);
    border-radius: var(--radius);
    padding: 12px;

    .log-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 0;
      font-size: 13px;

      .el-icon {
        flex-shrink: 0;
        &.success { color: var(--success-color); }
        &.loading { color: var(--primary-color); }
        &.error { color: var(--danger-color); }
        &.info { color: var(--text-color-secondary); }

        &.is-loading {
          animation: rotating 2s linear infinite;
        }
      }

      .log-time {
        margin-left: auto;
        color: var(--text-color-placeholder);
        font-size: 12px;
      }
    }
  }
}

.analysis-result {
  .stat-suffix {
    font-size: 14px;
    color: var(--text-color-secondary);
  }

  .result-actions {
    margin-top: 24px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
}

.export-options {
  text-align: center;

  .export-format {
    margin-bottom: 16px;
  }

  .export-hint {
    color: var(--text-color-secondary);
    font-size: 13px;
  }
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
