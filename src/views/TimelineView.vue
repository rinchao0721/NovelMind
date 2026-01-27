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

    <div class="timeline-content card">
      <div ref="timelineChartRef" class="timeline-chart"></div>
    </div>

    <!-- 章节详情 -->
    <div class="chapter-list">
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
        <div class="chapter-characters">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { useNovelStore } from '@/stores/novel'

const novelStore = useNovelStore()
const timelineChartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const novels = ref<any[]>([])
const selectedNovelId = ref('')
const viewMode = ref('plot')

// 模拟数据
const chapters = ref([
  {
    id: '1',
    chapter_num: 1,
    title: '贾雨村夤缘复旧职',
    word_count: 8500,
    summary: '甄士隐梦幻识通灵，贾雨村风尘怀闺秀。开篇交代了通灵宝玉的来历，以及贾雨村与甄士隐的故事。',
    characters: ['贾雨村', '甄士隐', '甄英莲']
  },
  {
    id: '2',
    chapter_num: 2,
    title: '贾夫人仙逝扬州城',
    word_count: 7200,
    summary: '林黛玉丧母后被贾母接入贾府，初次见到贾宝玉，两人一见如故。',
    characters: ['林黛玉', '贾母', '贾宝玉', '王熙凤']
  },
  {
    id: '3',
    chapter_num: 3,
    title: '托内兄如海酬训教',
    word_count: 9100,
    summary: '黛玉进贾府，见到了贾府众人。宝玉见黛玉，觉得面善，似曾相识。',
    characters: ['林黛玉', '贾宝玉', '贾母', '王夫人', '薛宝钗']
  }
])

const initChart = () => {
  if (!timelineChartRef.value) return

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
        data: chapters.value.map(c => c.characters.length),
        itemStyle: { color: '#409eff' }
      },
      {
        name: '情节事件数',
        type: 'bar',
        data: [3, 5, 4],
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

onMounted(async () => {
  novels.value = await novelStore.fetchNovels()
  initChart()
  window.addEventListener('resize', handleResize)
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
