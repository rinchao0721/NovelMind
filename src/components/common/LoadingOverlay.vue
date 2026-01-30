<template>
  <div v-if="loading" class="loading-overlay" :class="{ 'is-absolute': absolute }">
    <div class="loading-content">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span v-if="text" class="loading-text">{{ text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

withDefaults(defineProps<{
  loading: boolean
  text?: string
  absolute?: boolean
}>(), {
  text: '加载中...',
  absolute: true
})
</script>

<style lang="scss" scoped>
.loading-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--card-bg-rgb, 255, 255, 255), 0.7);
  z-index: 100;
  backdrop-filter: blur(2px);

  &.is-absolute {
    position: absolute;
    inset: 0;
  }

  &:not(.is-absolute) {
    position: fixed;
    inset: 0;
  }

  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    color: var(--primary-color);
  }

  .loading-text {
    font-size: 14px;
    font-weight: 500;
  }

  .is-loading {
    animation: rotating 2s linear infinite;
  }
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
