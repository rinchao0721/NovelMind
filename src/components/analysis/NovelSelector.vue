<template>
  <div class="novel-selector card">
    <h3>选择小说</h3>
    <el-select 
      :model-value="modelValue" 
      placeholder="请选择要分析的小说"
      size="large"
      style="width: 100%"
      @update:model-value="$emit('update:modelValue', $event)"
      @change="$emit('change', $event)"
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
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import type { Novel } from '@/types'

defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  novels: {
    type: Array as PropType<Novel[]>,
    default: () => []
  },
  currentNovel: {
    type: Object as PropType<Novel | null>,
    default: null
  }
})

defineEmits(['update:modelValue', 'change'])

const formatNumber = (num: number | undefined) => {
  return num ? num.toLocaleString() : '0'
}

const getStatusType = (status: string | undefined) => {
  switch (status) {
    case 'completed': return 'success'
    case 'analyzing': return 'primary'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string | undefined) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'analyzing': return '分析中'
    case 'failed': return '失败'
    case 'pending': return '待分析'
    default: return '未知'
  }
}
</script>

<style lang="scss" scoped>
.card {
  h3 {
    font-size: 16px;
    margin: 0 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
  }
}
.novel-info {
  margin-top: 16px;
}
</style>
