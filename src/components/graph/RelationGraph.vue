<template>
  <div ref="containerRef" class="relation-graph" :style="{ height: height }">
    <div v-if="loading" class="loading-overlay">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { GraphData, GraphNode, GraphLink } from '@/types'
import { getRelationLabel } from '@/utils/relations'

const props = withDefaults(defineProps<{
  data: GraphData | null
  height?: string
  loading?: boolean
  layout?: 'force' | 'circular'
  categories?: Array<{ name: string; color?: string }>
}>(), {
  height: '600px',
  loading: false,
  layout: 'force',
  categories: () => [
    { name: '主角', color: '#409EFF' },
    { name: '重要角色', color: '#67C23A' },
    { name: '配角', color: '#E6A23C' },
    { name: '其他', color: '#909399' }
  ]
})

const emit = defineEmits<{
  (e: 'node-click', node: GraphNode): void
  (e: 'link-click', link: GraphLink): void
}>()

const containerRef = ref<HTMLElement>()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

// Relation type colors
const relationColors: Record<string, string> = {
  family: '#F56C6C',
  friend: '#67C23A',
  enemy: '#909399',
  lover: '#E6A23C',
  colleague: '#409EFF',
  other: '#C0C4CC'
}

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  // Set initial empty option
  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: unknown) => {
        const item = params as echarts.DefaultLabelFormatterCallbackParams
        if (item.dataType === 'node') {
          const node = item.data as GraphNode
          return `
            <strong>${node.name}</strong><br/>
            重要性: ${((node.importance || 0.5) * 100).toFixed(0)}%
          `
        } else if (item.dataType === 'edge') {
          const link = item.data as GraphLink
          return `
            <strong>${link.source} → ${link.target}</strong><br/>
            关系: ${getRelationLabel(link.type)}<br/>
            强度: ${((link.value || 0.5) * 100).toFixed(0)}%
          `
        }
        return ''
      }
    },
    legend: {
      data: props.categories.map(c => c.name),
      orient: 'vertical',
      right: 10,
      top: 20,
      textStyle: {
        color: 'var(--text-color)'
      }
    },
    series: [{
      type: 'graph',
      layout: props.layout,
      data: [],
      links: [],
      categories: props.categories,
      roam: true,
      draggable: true,
      label: {
        show: true,
        position: 'right',
        fontSize: 12
      },
      force: {
        repulsion: 300,
        edgeLength: [100, 200],
        gravity: 0.1
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 5
        }
      }
    }]
  })
  
  // Event handlers
  chart.on('click', (params: echarts.ECElementEvent) => {
    if (params.dataType === 'node') {
      emit('node-click', params.data)
    } else if (params.dataType === 'edge') {
      emit('link-click', params.data)
    }
  })
}

const updateChart = () => {
  if (!chart || !props.data) return
  
  const { nodes, links } = props.data
  
  // Process nodes
  const processedNodes = nodes.map(node => ({
    ...node,
    symbolSize: Math.max(20, (node.importance || 0.5) * 60 + 20),
    category: getCategoryIndex(node.importance || 0.5),
    label: {
      show: true,
      fontSize: 12
    },
    itemStyle: {
      borderWidth: 2,
      borderColor: '#fff'
    }
  }))
  
  // Process links
  const processedLinks = links.map(link => ({
    ...link,
    lineStyle: {
      color: relationColors[link.type] || relationColors.other,
      width: Math.max(1, (link.value || 0.5) * 5),
      curveness: 0.2
    }
  }))
  
  chart.setOption({
    series: [{
      data: processedNodes,
      links: processedLinks
    }]
  })
}

const getCategoryIndex = (importance: number): number => {
  if (importance >= 0.8) return 0  // 主角
  if (importance >= 0.6) return 1  // 重要角色
  if (importance >= 0.4) return 2  // 配角
  return 3  // 其他
}

const resize = () => {
  chart?.resize()
}

// Expose methods
defineExpose({
  resize,
  getChart: () => chart
})

// Watch for data changes
watch(() => props.data, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

watch(() => props.layout, (newLayout) => {
  if (chart) {
    chart.setOption({
      series: [{
        layout: newLayout
      }]
    })
  }
})

onMounted(() => {
  initChart()
  if (props.data) {
    updateChart()
  }
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', resize)
})
</script>

<style lang="scss" scoped>
.relation-graph {
  position: relative;
  width: 100%;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
  
  .chart-container {
    width: 100%;
    height: 100%;
  }
  
  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(var(--card-bg), 0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    z-index: 10;
    
    .el-icon {
      font-size: 32px;
      color: var(--primary-color);
      
      &.is-loading {
        animation: rotating 2s linear infinite;
      }
    }
  }
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
