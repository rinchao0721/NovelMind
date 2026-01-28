<template>
  <div class="graph-view">
    <div class="page-header">
      <h2>人物关系图谱</h2>
      <p>可视化展示小说中的人物关系网络</p>
    </div>

    <!-- 工具栏 -->
    <div class="graph-toolbar card">
      <div class="toolbar-left">
        <el-select v-model="selectedNovelId" placeholder="选择小说" @change="loadGraphData">
          <el-option
            v-for="novel in novels"
            :key="novel.id"
            :label="novel.title"
            :value="novel.id"
          />
        </el-select>

        <el-select v-model="layoutType" placeholder="布局方式" @change="updateLayout">
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

        <el-button @click="exportImage">
          <el-icon><Download /></el-icon>
          导出图片
        </el-button>
      </div>
    </div>

    <!-- 图谱容器 -->
    <div class="graph-container card">
      <div v-if="loading" class="loading-overlay">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <div v-else-if="!selectedNovelId || (!graphData.nodes.length && !loading)" class="empty-state">
        <el-icon><Share /></el-icon>
        <template v-if="!selectedNovelId">
            <h3>请选择小说</h3>
            <p>选择上方小说以查看人物关系图谱</p>
        </template>
        <template v-else-if="currentNovel && currentNovel.analysis_status !== 'completed'">
            <h3>尚未进行分析</h3>
            <p>该小说还未进行人物关系分析</p>
            <el-button type="primary" @click="goToAnalysis">前往分析</el-button>
        </template>
        <template v-else>
            <h3>暂无图谱数据</h3>
            <p>分析已完成，但未能构建关系网络</p>
            <p style="font-size: 12px; margin-top: 5px; color: #f56c6c" v-if="neo4jError">
                {{ neo4jError }}
            </p>
        </template>
      </div>

      <div ref="chartRef" class="chart" v-show="selectedNovelId && !loading && graphData.nodes.length"></div>

      <!-- 筛选面板 -->
      <div class="filter-panel" v-if="selectedNovelId && graphData.nodes.length">
        <h4>关系类型筛选</h4>
        <el-checkbox-group v-model="visibleRelationTypes" @change="updateGraph">
          <el-checkbox 
            v-for="type in relationTypes" 
            :key="type.value" 
            :value="type.value"
          >
            <span class="relation-type" :style="{ '--color': type.color }">
              {{ type.label }}
            </span>
          </el-checkbox>
        </el-checkbox-group>

        <h4>重要性筛选</h4>
        <el-slider
          v-model="importanceThreshold"
          :min="0"
          :max="100"
          :format-tooltip="(val: number) => `重要性 >= ${val}%`"
          @change="updateGraph"
        />

        <h4>统计信息</h4>
        <div class="stats">
          <div class="stat-item">
            <span class="label">人物数量</span>
            <span class="value">{{ filteredNodes.length }}</span>
          </div>
          <div class="stat-item">
            <span class="label">关系数量</span>
            <span class="value">{{ filteredLinks.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 人物详情侧边栏 -->
    <el-drawer
      v-model="drawerVisible"
      :title="selectedCharacter?.name"
      direction="rtl"
      size="400px"
    >
      <template v-if="selectedCharacter">
        <div class="character-detail">
          <div class="detail-section">
            <h4>基本信息</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="别名">
                {{ selectedCharacter.aliases?.join('、') || '无' }}
              </el-descriptions-item>
              <el-descriptions-item label="首次出现">
                第 {{ selectedCharacter.first_appearance }} 章
              </el-descriptions-item>
              <el-descriptions-item label="重要性">
                <el-progress 
                  :percentage="Math.round(selectedCharacter.importance * 100)" 
                  :stroke-width="12"
                />
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="detail-section">
            <h4>人物描述</h4>
            <p>{{ selectedCharacter.description || '暂无描述' }}</p>
          </div>

          <div class="detail-section">
            <h4>性格特点</h4>
            <p>{{ selectedCharacter.personality || '暂无分析' }}</p>
          </div>

          <div class="detail-section">
            <h4>相关人物 ({{ selectedCharacterRelations.length }})</h4>
            <div class="related-characters">
              <div 
                v-for="rel in selectedCharacterRelations" 
                :key="rel.id"
                class="relation-item"
                @click="selectCharacterById(rel.targetId)"
              >
                <span class="name">{{ rel.targetName }}</span>
                <el-tag size="small" :color="getRelationColor(rel.type)">
                  {{ getRelationLabel(rel.type) }}
                </el-tag>
              </div>
              <div v-if="selectedCharacterRelations.length === 0" class="no-relations">
                暂无关联人物
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ZoomIn, ZoomOut, FullScreen, Download, Share, Loading } from '@element-plus/icons-vue'
import { useNovelStore } from '@/stores/novel'
import type { Novel, GraphData } from '@/types'

const router = useRouter()
const route = useRoute()
const novelStore = useNovelStore()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const novels = ref<Novel[]>([])
const selectedNovelId = ref('')
const layoutType = ref('force')
const drawerVisible = ref(false)
const selectedCharacter = ref<any>(null)
const selectedCharacterRelations = ref<any[]>([])
const importanceThreshold = ref(0)
const loading = ref(false)
const neo4jError = ref('')
const graphData = ref<GraphData>({
  nodes: [],
  links: []
})

const currentNovel = computed(() => novelStore.currentNovel)

const goToAnalysis = () => {
  router.push(`/analysis?id=${selectedNovelId.value}`)
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
    // 如果没有节点但状态是完成，可能是数据问题
    if (data.nodes.length === 0 && currentNovel.value?.analysis_status === 'completed') {
       neo4jError.value = '未找到图谱数据，可能是Neo4j连接问题或分析结果为空'
    }
    initChart()
  } catch (error) {
    console.error('Failed to load graph data:', error)
    neo4jError.value = '加载失败: ' + (error instanceof Error ? error.message : '未知错误')
  } finally {
    loading.value = false
  }
}

// 监听小说选择变化以获取详情
watch(selectedNovelId, async (newId) => {
    if (newId) {
        await novelStore.fetchNovel(newId)
        loadGraphData()
    }
})

const initChart = () => {
  if (!chartRef.value || graphData.value.nodes.length === 0) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(chartRef.value)

  updateGraph()

  chart.on('click', (params: any) => {
    if (params.dataType === 'node') {
      showCharacterDetail(params.data)
    }
  })
}

const updateGraph = () => {
  if (!chart) return

  const categories = [
    { name: '主角' },
    { name: '重要角色' },
    { name: '次要角色' }
  ]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<b>${params.data.name}</b><br/>重要性: ${(params.data.importance * 100).toFixed(0)}%`
        } else {
          const link = params.data
          return `${link.sourceName || link.source} → ${link.targetName || link.target}<br/>关系: ${getRelationLabel(link.type)}`
        }
      }
    },
    legend: {
      data: categories.map(c => c.name),
      orient: 'vertical',
      right: 220,
      top: 20
    },
    series: [{
      type: 'graph',
      layout: layoutType.value as 'none' | 'force' | 'circular',
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
      },
      blur: {
        itemStyle: {
          opacity: 0.3
        },
        lineStyle: {
          opacity: 0.1
        }
      }
    }]
  }

  chart.setOption(option, true)
}

const updateLayout = () => {
  if (!chart) return
  chart.setOption({
    series: [{
      layout: layoutType.value
    }]
  })
}

const showCharacterDetail = (nodeData: any) => {
  selectedCharacter.value = {
    ...nodeData,
    aliases: nodeData.aliases || [],
    first_appearance: nodeData.firstAppearance || 1,
    description: nodeData.description || '暂无描述',
    personality: nodeData.personality || '暂无分析'
  }
  
  // 获取相关关系
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
        type: l.type
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

const getRelationLabel = (type: string): string => {
  const rel = relationTypes.find(r => r.value === type)
  return rel?.label || type
}

const zoomIn = () => {
  if (!chart) return
  const option = chart.getOption() as any
  const currentZoom = option.series?.[0]?.zoom || 1
  chart.setOption({ series: [{ zoom: currentZoom * 1.2 }] })
}

const zoomOut = () => {
  if (!chart) return
  const option = chart.getOption() as any
  const currentZoom = option.series?.[0]?.zoom || 1
  chart.setOption({ series: [{ zoom: currentZoom / 1.2 }] })
}

const resetZoom = () => {
  if (!chart) return
  chart.setOption({ series: [{ zoom: 1, center: ['50%', '50%'] }] })
}

const exportImage = () => {
  if (!chart) return
  const url = chart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  })
  const link = document.createElement('a')
  link.download = `${novels.value.find(n => n.id === selectedNovelId.value)?.title || 'graph'}-关系图谱.png`
  link.href = url
  link.click()
}

const handleResize = () => {
  chart?.resize()
}

watch(layoutType, updateLayout)

onMounted(async () => {
  novels.value = await novelStore.fetchNovels()
  
  // 从 URL 获取小说 ID
  const id = route.query.id as string
  if (id) {
    selectedNovelId.value = id
    // Watch will trigger data loading
  }
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', handleResize)
})
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
  padding: 12px 16px !important;
  margin-bottom: 16px;

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
  padding: 0 !important;
  overflow: hidden;
  min-height: 500px;

  .loading-overlay,
  .empty-state {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: var(--text-color-secondary);
    
    .el-icon {
      font-size: 48px;
    }
    
    .is-loading {
      animation: rotating 2s linear infinite;
    }
  }

  .chart {
    flex: 1;
    min-height: 500px;
  }

  .filter-panel {
    width: 200px;
    padding: 16px;
    border-left: 1px solid var(--border-color);
    background: var(--card-bg);
    overflow-y: auto;

    h4 {
      font-size: 13px;
      color: var(--text-color-secondary);
      margin: 0 0 12px;

      &:not(:first-child) {
        margin-top: 20px;
      }
    }

    .el-checkbox-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .relation-type {
      display: flex;
      align-items: center;
      gap: 6px;

      &::before {
        content: '';
        width: 12px;
        height: 3px;
        background: var(--color);
        border-radius: 2px;
      }
    }

    .stats {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .stat-item {
        display: flex;
        justify-content: space-between;
        font-size: 13px;

        .label {
          color: var(--text-color-secondary);
        }

        .value {
          font-weight: 600;
          color: var(--primary-color);
        }
      }
    }
  }
}

.character-detail {
  .detail-section {
    margin-bottom: 24px;

    h4 {
      font-size: 14px;
      color: var(--text-color-secondary);
      margin: 0 0 12px;
    }

    p {
      line-height: 1.8;
      color: var(--text-color);
    }
  }

  .related-characters {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .relation-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: var(--hover-bg);
      border-radius: var(--radius);
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background: var(--border-color);
      }

      .name {
        font-weight: 500;
      }
    }

    .no-relations {
      color: var(--text-color-placeholder);
      text-align: center;
      padding: 20px;
    }
  }
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
