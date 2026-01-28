<template>
  <div class="timeline-view">
    <div class="page-header">
      <h2>情节时间线</h2>
      <p>按章节展示小说情节发展与人物出场</p>
    </div>

    <div class="timeline-toolbar card">
      <el-select v-model="selectedNovelId" placeholder="选择小说">
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
    </div>

    <div v-if="chapters.length > 0" class="timeline-content card">
      <div ref="timelineChartRef" class="timeline-chart"></div>
    </div>

    <!-- 章节详情 -->
    <div v-if="chapters.length > 0" class="chapter-list">
      <div 
        v-for="chapter in chapters" 
        :key="chapter.id" 
        class="chapter-item card"
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
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!selectedNovelId || chapters.length === 0" class="empty-state">
      <el-icon><Timer /></el-icon>
      <template v-if="!selectedNovelId">
        <h3>请选择小说</h3>
        <p>选择上方小说以查看情节时间线</p>
      </template>
      <template v-else-if="currentNovel && currentNovel.analysis_status !== 'completed'">
        <h3>尚未进行分析</h3>
        <p>该小说还未进行情节分析</p>
        <el-button type="primary" @click="goToAnalysis">前往分析</el-button>
      </template>
      <template v-else>
        <h3>暂无时间线数据</h3>
        <p>分析已完成，但未能提取到情节数据</p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { useNovelStore } from '@/stores/novel'
import { Timer } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const novelStore = useNovelStore()
const timelineChartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const novels = ref<any[]>([])
const selectedNovelId = ref('')
const viewMode = ref('plot')

// 使用 store 中的章节数据
const chapters = computed(() => novelStore.chapters)
const currentNovel = computed(() => novelStore.currentNovel)

const initChart = async () => {
  await nextTick() // Ensure DOM is present
  if (!timelineChartRef.value || chapters.value.length === 0) return

  if (chart) {
      chart.dispose()
  }
  chart = echarts.init(timelineChartRef.value)

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
        // 这里的固定数据之后需要替换为真实情节事件计数
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

  chart.setOption(option)
}

const handleResize = () => {
  chart?.resize()
}

const goToAnalysis = () => {
  router.push(`/analysis?id=${selectedNovelId.value}`)
}

// 监听小说选择变化
watch(selectedNovelId, async (newId) => {
  if (newId) {
    await novelStore.fetchNovel(newId)
    await novelStore.fetchChapters(newId)
    initChart()
  }
})

// 监听章节数据变化
watch(chapters, () => {
  initChart()
}, { deep: true })

onMounted(async () => {
  novels.value = await novelStore.fetchNovels()
  window.addEventListener('resize', handleResize)
  
  const id = route.query.id as string
  if (id) {
    selectedNovelId.value = id
  }
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', handleResize)
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
  padding: 12px 16px !important;
  margin-bottom: 16px;
}

.timeline-content {
  margin-bottom: 24px;

  .timeline-chart {
    height: 300px;
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
    color: var(--text-color-secondary);
    line-height: 1.8;
    margin-bottom: 12px;
  }

  .chapter-characters {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;

    .label {
      color: var(--text-color-secondary);
      font-size: 13px;
    }
  }
}
</style>
