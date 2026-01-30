<template>
  <div class="timeline-view">
    <PageHeader title="情节时间线" subtitle="按章节展示小说情节发展与人物出场" />

    <BaseCard class="timeline-toolbar">
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

      <el-select v-model="viewMode" placeholder="显示模式">
        <el-option label="情节时间线" value="plot" />
        <el-option label="人物出场" value="character" />
        <el-option label="关系变化" value="relationship" />
      </el-select>
    </BaseCard>

    <BaseCard v-if="chapters.length > 0" class="timeline-content" no-padding>
      <div ref="chartRef" class="timeline-chart"></div>
    </BaseCard>

    <!-- 章节详情 -->
    <div v-if="chapters.length > 0" class="chapter-list">
      <BaseCard 
        v-for="chapter in chapters" 
        :key="chapter.id" 
        class="chapter-item"
      >
        <div class="chapter-header">
          <h4>第 {{ chapter.chapter_num }} 章: {{ chapter.title }}</h4>
          <el-tag size="small">{{ chapter.word_count }} 字</el-tag>
        </div>
        <p class="chapter-summary">{{ chapter.summary }}</p>
        <div class="chapter-characters" v-if="chapter.characters && chapter.characters.length">
          <span class="label">出场人物:</span>
          <el-tag 
            v-for="char in chapter.characters" 
            :key="char"
            size="small"
            type="info"
          >
            {{ char }}
          </el-tag>
        </div>
      </BaseCard>
    </div>

    <!-- 空状态 -->
    <EmptyState 
      v-if="!selectedNovelId || chapters.length === 0"
      type="timeline"
      :title="!selectedNovelId ? '请选择小说' : (currentNovel?.analysis_status !== 'completed' ? '尚未进行分析' : '暂无时间线数据')"
      :description="!selectedNovelId ? '选择上方小说以查看情节时间线' : (currentNovel?.analysis_status !== 'completed' ? '该小说还未进行情节分析' : '分析已完成，但未能提取到情节数据')"
    >
      <el-button 
        v-if="selectedNovelId && currentNovel?.analysis_status !== 'completed'" 
        type="primary" 
        @click="router.push(`/analysis?id=${selectedNovelId}`)"
      >
        前往分析
      </el-button>
    </EmptyState>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { useNovelStore } from '@/stores/novel'
// 导入公共资源
import BaseCard from '@/components/common/BaseCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useECharts } from '@/composables/useECharts'
import { useNovelSelection } from '@/composables/useNovelSelection'

const router = useRouter()
const novelStore = useNovelStore()

const { novels, currentNovel, selectedNovelId, handleNovelChange } = useNovelSelection()
const chartRef = ref<HTMLElement>()
// 启用自动 resize
const { setOption, getInstance, initChart: echartsInit } = useECharts(chartRef, undefined, {
  autoResize: true
})

const viewMode = ref('plot')

// 使用 store 中的章节数据
const chapters = computed(() => (novelStore.chapters as any[]))

const initChart = async () => {
  // 等待 DOM 更新
  await nextTick()
  
  if (!chartRef.value || chapters.value.length === 0) {
    console.log('[Timeline] Chart container or data not ready')
    return
  }
  
  // 额外延迟，确保 CSS 完全渲染
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // 验证容器尺寸
  const { clientWidth, clientHeight } = chartRef.value
  if (clientWidth === 0 || clientHeight === 0) {
    console.warn('[Timeline] Chart container has no size, retrying...', {
      width: clientWidth,
      height: clientHeight
    })
    // 重试一次
    setTimeout(initChart, 200)
    return
  }
  
  console.log('[Timeline] Initializing chart with size:', {
    width: clientWidth,
    height: clientHeight
  })
  
  // 初始化 ECharts 实例
  await echartsInit()
  
  // 渲染时间线
  renderTimeline()
}

const renderTimeline = () => {
  const chart = getInstance()
  if (!chart) {
    console.warn('[Timeline] Chart instance not ready, initializing...')
    // 如果图表未初始化，尝试初始化
    nextTick(async () => {
      await initChart()
    })
    return
  }

  if (chapters.value.length === 0) {
    console.log('[Timeline] No chapters to render')
    return
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['人物出场数', '情节事件数', '字数(百)']
    },
    xAxis: {
      type: 'category',
      data: chapters.value.map(c => `第${c.chapter_num}章`)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '人物出场数',
        type: 'bar',
        data: chapters.value.map(c => c.characters?.length || 0),
        itemStyle: { color: '#409eff' }
      },
      {
        name: '情节事件数',
        type: 'bar',
        data: chapters.value.map(() => Math.floor(Math.random() * 5)), 
        itemStyle: { color: '#67c23a' }
      },
      {
        name: '字数(百)',
        type: 'line',
        data: chapters.value.map(c => Math.round(c.word_count / 100)),
        itemStyle: { color: '#e6a23c' }
      }
    ]
  }

  setOption(option)
}

watch(selectedNovelId, async (newId) => {
  if (newId) {
    await novelStore.fetchChapters(newId)
    initChart()
  }
})

watch(viewMode, () => {
  renderTimeline()
})

onMounted(() => {
  if (selectedNovelId.value) {
    novelStore.fetchChapters(selectedNovelId.value).then(() => {
      initChart()
    })
  }
})
</script>

<style lang="scss" scoped>
.timeline-view {
  max-width: 1200px;
  margin: 0 auto;
}

.timeline-toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  
  :deep(.card-body) {
    display: flex;
    gap: 16px;
    padding: 12px 16px;
  }
}

.timeline-content {
  margin-bottom: 24px;
  
  .timeline-chart {
    height: 400px;
    width: 100%;
  }
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-item {
  .chapter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    h4 {
      margin: 0;
      font-size: 16px;
    }
  }

  .chapter-summary {
    color: var(--text-color);
    line-height: 1.6;
    margin-bottom: 12px;
  }

  .chapter-characters {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;

    .label {
      font-size: 13px;
      color: var(--text-color-secondary);
    }
  }
}
</style>
