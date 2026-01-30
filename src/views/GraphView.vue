<template>
  <div class="graph-view">
    <PageHeader title="人物关系图谱" subtitle="可视化展示小说中的人物关系网络" />

    <!-- 工具栏 -->
    <BaseCard class="graph-toolbar">
      <div class="toolbar-left">
        <el-select 
          v-model="selectedNovelId" 
          placeholder="选择小说" 
          @change="handleNovelChange"
        >
          <el-option
            v-for="novel in novels"
            :key="novel.id"
            :label="novel.title"
            :value="novel.id"
          />
        </el-select>

        <el-select v-model="layoutType" placeholder="布局方式">
          <el-option label="力导向布局" value="force" />
          <el-option label="环形布局" value="circular" />
        </el-select>
      </div>

      <div class="toolbar-right">
        <el-button-group>
          <el-button @click="zoomIn" title="放大">
            <el-icon><ZoomIn /></el-icon>
          </el-button>
          <el-button @click="zoomOut" title="缩小">
            <el-icon><ZoomOut /></el-icon>
          </el-button>
          <el-button @click="resetZoom" title="重置">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </el-button-group>

        <el-button @click="handleExportImage">
          <el-icon><Download /></el-icon>
          导出图片
        </el-button>
      </div>
    </BaseCard>

    <!-- 图谱容器 -->
    <BaseCard class="graph-container" no-padding>
      <LoadingOverlay :loading="loading" />
      
      <EmptyState 
        v-if="!selectedNovelId || (!graphData.nodes.length && !loading)"
        :type="!selectedNovelId ? 'search' : 'graph'"
        :title="getEmptyStateTitle()"
        :description="getEmptyStateDescription()"
      >
        <el-button 
          v-if="selectedNovelId && currentNovel?.analysis_status !== 'completed'" 
          type="primary" 
          @click="goToAnalysis"
        >
          前往分析
        </el-button>
        <el-button 
          v-if="selectedNovelId && graphData.nodes.length === 0 && !loading && currentNovel?.analysis_status === 'completed'" 
          type="primary" 
          @click="loadGraphData"
        >
          重新加载
        </el-button>
        <p v-if="neo4jError" class="error-text">{{ neo4jError }}</p>
      </EmptyState>

      <!-- 改用 v-if 替代 v-show，确保 ECharts 仅在容器可见时初始化 -->
      <div 
        v-if="selectedNovelId && !loading && graphData.nodes.length"
        ref="chartRef" 
        class="chart"
      ></div>

      <!-- 筛选面板 -->
      <GraphFilter 
        v-if="selectedNovelId && graphData.nodes.length"
        v-model:visible-relation-types="visibleRelationTypes"
        v-model:importance-threshold="importanceThreshold"
        :relation-types="relationTypes"
        :node-count="filteredNodes.length"
        :link-count="filteredLinks.length"
        @change="renderGraph"
      />
    </BaseCard>

    <!-- 人物详情侧边栏 -->
    <CharacterDrawer 
      v-model:visible="drawerVisible"
      :character="selectedCharacter"
      :relations="selectedCharacterRelations"
      @select-character="selectCharacterById"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ZoomIn, ZoomOut, FullScreen, Download } from '@element-plus/icons-vue'
import { useNovelStore } from '@/stores/novel'
import type { GraphData, Relationship, GraphNode, GraphLink } from '@/types'
import { getRelationLabel } from '@/utils/relations'
// 导入公共资源
import BaseCard from '@/components/common/BaseCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import { useECharts } from '@/composables/useECharts'
import { useNovelSelection } from '@/composables/useNovelSelection'
// 导入子组件
import GraphFilter from '@/components/graph/GraphFilter.vue'
import CharacterDrawer from '@/components/graph/CharacterDrawer.vue'
import type { DrawerCharacter, CharacterRelation } from '@/components/graph/CharacterDrawer.vue'

const router = useRouter()
const novelStore = useNovelStore()

const { novels, currentNovel, selectedNovelId, handleNovelChange } = useNovelSelection()
const chartRef = ref<HTMLElement>()
// 启用自动 resize 和可见性监听
const { setOption, getInstance, resize, isVisible } = useECharts(chartRef, undefined, {
  autoResize: true,
  watchVisibility: true
})

const layoutType = ref<'force' | 'circular'>('force')
const drawerVisible = ref(false)

const selectedCharacter = ref<DrawerCharacter | null>(null)
const selectedCharacterRelations = ref<CharacterRelation[]>([])
const importanceThreshold = ref(0)
const loading = ref(false)
const neo4jError = ref('')
const graphData = ref<GraphData>({
  nodes: [],
  links: []
})

const goToAnalysis = () => {
  router.push(`/analysis?id=${selectedNovelId.value}`)
}

const getEmptyStateTitle = () => {
  if (!selectedNovelId.value) return '请选择小说'
  if (currentNovel.value?.analysis_status !== 'completed') return '尚未进行分析'
  if (neo4jError.value.includes('Network Error') || neo4jError.value.includes('ERR_CONNECTION')) {
    return '无法连接到后端服务'
  }
  return '暂无图谱数据'
}

const getEmptyStateDescription = () => {
  if (!selectedNovelId.value) return '选择上方小说以查看人物关系图谱'
  if (currentNovel.value?.analysis_status !== 'completed') return '该小说还未进行人物关系分析，请先运行分析任务'
  if (neo4jError.value.includes('Network Error') || neo4jError.value.includes('ERR_CONNECTION')) {
    return '请检查后端服务是否正常运行。如果问题持续，请尝试重新启动应用。'
  }
  return '分析已完成，但未能构建关系网络。可能是分析过程中未提取到人物关系数据，请尝试重新分析。'
}

const relationTypes = [
  { label: '亲属', value: 'family', color: '#f56c6c' },
  { label: '朋友', value: 'friend', color: '#67c23a' },
  { label: '敌对', value: 'enemy', color: '#909399' },
  { label: '恋人', value: 'lover', color: '#e6a23c' },
  { label: '同事', value: 'colleague', color: '#409eff' },
  { label: '其他', value: 'other', color: '#c0c4cc' }
]

const visibleRelationTypes = ref(relationTypes.map(t => t.value))

const filteredNodes = computed(() => {
  return graphData.value.nodes.filter(
    n => n.importance * 100 >= importanceThreshold.value
  )
})

const filteredLinks = computed(() => {
  const nodeIds = new Set(filteredNodes.value.map(n => n.id))
  return graphData.value.links.filter(
    l => visibleRelationTypes.value.includes(l.type) &&
         nodeIds.has(l.source) &&
         nodeIds.has(l.target)
  )
})

const loadGraphData = async () => {
  if (!selectedNovelId.value) return
  
  loading.value = true
  neo4jError.value = ''
  try {
    const data = await novelStore.fetchGraphData(selectedNovelId.value)
    graphData.value = data
    if (data.nodes.length === 0 && currentNovel.value?.analysis_status === 'completed') {
       neo4jError.value = '未找到图谱数据，可能是分析结果为空'
    }
  } catch (error) {
    console.error('Failed to load graph data:', error)
    neo4jError.value = '加载失败: ' + (error instanceof Error ? error.message : '未知错误')
  } finally {
    loading.value = false
    // 等待 loading 变为 false 后，DOM 更新完成再渲染
    await nextTick()
    if (graphData.value.nodes.length > 0) {
      renderGraph()
    }
  }
}

watch(selectedNovelId, (newId) => {
    if (newId) {
        loadGraphData()
    }
}, { immediate: true })

const renderGraph = () => {
  if (graphData.value.nodes.length === 0) return

  const categories = [
    { name: '主角' },
    { name: '重要角色' },
    { name: '次要角色' }
  ]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: unknown) => {
        const item = params as echarts.DefaultLabelFormatterCallbackParams
        if (item.dataType === 'node') {
          const node = item.data as GraphNode
          return `<b>${node.name}</b><br/>重要性: ${(node.importance * 100).toFixed(0)}%`
        } else {
          const link = item.data as GraphLink & { sourceName?: string; targetName?: string }
          return `${link.sourceName || link.source} → ${link.targetName || link.target}<br/>关系: ${getRelationLabel(link.type)}`
        }
      }
    },
    legend: {
      data: categories.map(c => c.name),
      orient: 'vertical',
      right: 10,
      top: 10,
      backgroundColor: 'rgba(255, 255, 255, 0.7)',
      borderRadius: 4,
      padding: 6
    },
    series: [{
      type: 'graph',
      layout: layoutType.value,
      data: filteredNodes.value.map(node => ({
        ...node,
        symbolSize: node.importance * 50 + 20,
        category: node.importance >= 0.8 ? 0 : node.importance >= 0.5 ? 1 : 2,
        label: {
          show: true,
          fontSize: 12
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2
        }
      })),
      links: filteredLinks.value.map(link => ({
        ...link,
        sourceName: graphData.value.nodes.find(n => n.id === link.source)?.name,
        targetName: graphData.value.nodes.find(n => n.id === link.target)?.name,
        lineStyle: {
          color: getRelationColor(link.type),
          width: Math.max(link.value / 3, 1),
          curveness: 0.1
        }
      })),
      categories,
      roam: true,
      draggable: true,
      force: {
        repulsion: 400,
        edgeLength: [80, 200],
        gravity: 0.1,
        layoutAnimation: true
      },
      circular: {
        rotateLabel: true
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 5
        },
        label: {
          fontSize: 14,
          fontWeight: 'bold'
        }
      }
    }]
  }

  setOption(option)
  
  const chart = getInstance()
  chart?.off('click')
  chart?.on('click', (params: echarts.ECElementEvent) => {
    if (params.dataType === 'node') {
      showCharacterDetail(params.data as GraphNode)
    }
  })
}

const showCharacterDetail = (nodeData: GraphNode & Record<string, any>) => {
  selectedCharacter.value = {
    ...nodeData,
    aliases: nodeData.aliases || [],
    first_appearance: nodeData.firstAppearance || 1,
    description: nodeData.description || '暂无描述',
    personality: nodeData.personality || '暂无分析'
  }
  
  selectedCharacterRelations.value = graphData.value.links
    .filter(l => l.source === nodeData.id || l.target === nodeData.id)
    .map(l => {
      const isSource = l.source === nodeData.id
      const targetId = isSource ? l.target : l.source
      const targetNode = graphData.value.nodes.find(n => n.id === targetId)
      return {
        id: l.source + '-' + l.target,
        targetId,
        targetName: targetNode?.name || targetId,
        type: l.type as Relationship['type']
      }
    })
  
  drawerVisible.value = true
}

const selectCharacterById = (id: string) => {
  const node = graphData.value.nodes.find(n => n.id === id)
  if (node) {
    showCharacterDetail(node)
  }
}

const getRelationColor = (type: string): string => {
  const rel = relationTypes.find(r => r.value === type)
  return rel?.color || '#c0c4cc'
}

const zoomIn = () => {
  const chart = getInstance()
  if (!chart) return
  const option = chart.getOption() as echarts.EChartsOption
  const series = option.series as echarts.SeriesOption[]
  const currentZoom = (series?.[0] as any)?.zoom || 1
  chart.setOption({ series: [{ zoom: currentZoom * 1.2 }] })
}

const zoomOut = () => {
  const chart = getInstance()
  if (!chart) return
  const option = chart.getOption() as echarts.EChartsOption
  const series = option.series as echarts.SeriesOption[]
  const currentZoom = (series?.[0] as any)?.zoom || 1
  chart.setOption({ series: [{ zoom: currentZoom / 1.2 }] })
}

const resetZoom = () => {
  const chart = getInstance()
  if (!chart) return
  chart.setOption({ series: [{ zoom: 1, center: ['50%', '50%'] }] })
}

const handleExportImage = () => {
  const chart = getInstance()
  if (!chart) return
  const url = chart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  const link = document.createElement('a')
  link.download = `${currentNovel.value?.title || 'graph'}-关系图谱.png`
  link.href = url
  link.click()
}

watch(layoutType, () => {
  renderGraph()
})

// 监听可见性变化，容器变为可见时调整大小
watch(isVisible, async (visible) => {
  if (visible && graphData.value.nodes.length > 0) {
    await nextTick()
    resize()
  }
})

// 监听筛选条件变化，调整图表大小
watch([importanceThreshold, visibleRelationTypes], async () => {
  if (graphData.value.nodes.length > 0) {
    await nextTick()
    resize()
  }
}, { deep: true })
</script>

<style lang="scss" scoped>
.graph-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 48px);
}

.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  :deep(.card-body) {
    display: flex;
    justify-content: space-between;
    width: 100%;
    padding: 12px 16px;
  }

  .toolbar-left,
  .toolbar-right {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.graph-container {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
  min-height: 500px;

  :deep(.card-body) {
    flex: 1;
    display: flex;
    flex-direction: row;
    align-items: stretch;
    justify-content: flex-start;
    padding: 0;
    position: relative;
  }

  .chart {
    flex: 1;
    min-height: 500px;
    min-width: 400px;
  }

  .empty-state {
    flex: 1;
  }

  .error-text {
    font-size: 12px;
    margin-top: 5px;
    color: #f56c6c;
  }
}
</style>
