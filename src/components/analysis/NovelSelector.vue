<template>
  <BaseCard title="选择小说" class="novel-selector">
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
          <StatusTag :status="currentNovel.analysis_status" />
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import type { Novel } from '@/types'
import { formatNumber } from '@/utils/format'
// 导入公共资源
import BaseCard from '@/components/common/BaseCard.vue'
import StatusTag from '@/components/common/StatusTag.vue'

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
</script>

<style lang="scss" scoped>
.novel-info {
  margin-top: 16px;
}
</style>
