<template>
  <BaseCard title="分析进度" class="analysis-progress">
    <el-progress 
      :percentage="progress" 
      :status="progress === 100 ? 'success' : ''"
      :stroke-width="20"
    />
    <p class="progress-text">{{ progressText }}</p>

    <div v-if="logs.length > 0" class="analysis-logs">
      <div 
        v-for="(log, index) in logs" 
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
  </BaseCard>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import { SuccessFilled, Loading, InfoFilled, WarningFilled } from '@element-plus/icons-vue'
import BaseCard from '@/components/common/BaseCard.vue'
import type { AnalysisLog } from '@/types'

defineProps({
  progress: {
    type: Number,
    default: 0
  },
  progressText: {
    type: String,
    default: ''
  },
  logs: {
    type: Array as PropType<AnalysisLog[]>,
    default: () => []
  }
})
</script>

<style lang="scss" scoped>
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

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
