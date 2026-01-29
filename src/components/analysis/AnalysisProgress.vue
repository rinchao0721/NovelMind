<template>
  <div class="analysis-progress card">
    <h3>分析进度</h3>
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
  </div>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import { SuccessFilled, Loading, InfoFilled, WarningFilled } from '@element-plus/icons-vue'

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
    type: Array as PropType<Array<{ type: string; message: string; time: string }>>,
    default: () => []
  }
})
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
