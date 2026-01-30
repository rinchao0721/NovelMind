<template>
  <div class="empty-state" :style="{ padding: padding }">
    <el-icon class="empty-icon" :size="iconSize">
      <slot name="icon">
        <Document v-if="type === 'document'" />
        <Share v-else-if="type === 'graph'" />
        <Timer v-else-if="type === 'timeline'" />
        <Search v-else />
      </slot>
    </el-icon>
    <h3 v-if="title">{{ title }}</h3>
    <p v-if="description">{{ description }}</p>
    <div v-if="$slots.default" class="empty-actions">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Document, Share, Timer, Search } from '@element-plus/icons-vue'

withDefaults(defineProps<{
  title?: string
  description?: string
  type?: 'document' | 'graph' | 'timeline' | 'search'
  iconSize?: number
  padding?: string
}>(), {
  type: 'document',
  iconSize: 48,
  padding: '40px 0'
})
</script>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-color-secondary);

  .empty-icon {
    margin-bottom: 16px;
    color: var(--text-color-placeholder);
  }

  h3 {
    font-size: 18px;
    color: var(--text-color);
    margin: 0 0 8px;
  }

  p {
    margin: 0 0 24px;
    max-width: 400px;
    font-size: 14px;
  }

  .empty-actions {
    display: flex;
    gap: 12px;
  }
}
</style>
