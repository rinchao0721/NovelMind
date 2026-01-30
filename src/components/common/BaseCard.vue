<template>
  <div class="base-card" :class="{ 'is-hoverable': hoverable, 'no-padding': noPadding }">
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <h3 v-if="title">{{ title }}</h3>
        <div v-if="$slots.extra" class="card-extra">
          <slot name="extra"></slot>
        </div>
      </slot>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  hoverable?: boolean
  noPadding?: boolean
}>()
</script>

<style lang="scss" scoped>
.base-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: var(--transition);

  &.is-hoverable:hover {
    border-color: var(--primary-color);
    box-shadow: var(--shadow);
    transform: translateY(-2px);
  }

  &.no-padding {
    .card-body {
      padding: 0;
    }
  }

  .card-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-color);
    }
  }

  .card-body {
    padding: 20px;
  }

  .card-footer {
    padding: 12px 20px;
    background: var(--hover-bg);
    border-top: 1px solid var(--border-color);
  }
}
</style>
