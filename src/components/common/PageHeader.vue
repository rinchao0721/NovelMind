<template>
  <div class="page-header" :class="{ 'has-back': showBack }">
    <div class="header-main">
      <div v-if="showBack" class="back-btn" @click="$emit('back')">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回</span>
      </div>
      <div class="header-content">
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      </div>
    </div>
    <div v-if="$slots.extra" class="header-extra">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from '@element-plus/icons-vue'

defineProps<{
  title?: string
  subtitle?: string
  showBack?: boolean
}>()

defineEmits(['back'])
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .header-main {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .back-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    color: var(--primary-color);
    cursor: pointer;
    width: fit-content;
    transition: var(--transition);

    &:hover {
      opacity: 0.8;
    }
  }

  .header-content {
    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-color);
    }

    .subtitle {
      margin: 4px 0 0;
      color: var(--text-color-secondary);
      font-size: 14px;
    }
  }

  .header-extra {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}
</style>
