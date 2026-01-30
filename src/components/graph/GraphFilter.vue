<template>
  <div class="filter-panel">
    <h4>关系类型筛选</h4>
    <el-checkbox-group 
      :model-value="visibleRelationTypes" 
      @update:model-value="$emit('update:visibleRelationTypes', $event)"
      @change="$emit('change')"
    >
      <el-checkbox 
        v-for="type in relationTypes" 
        :key="type.value" 
        :value="type.value"
      >
        <span class="relation-type-item" :style="{ '--color': type.color }">
          {{ type.label }}
        </span>
      </el-checkbox>
    </el-checkbox-group>

    <h4>重要性筛选</h4>
    <el-slider
      :model-value="importanceThreshold"
      @update:model-value="$emit('update:importanceThreshold', $event)"
      :min="0"
      :max="100"
      :format-tooltip="(val: number) => `重要性 >= ${val}%`"
      @change="$emit('change')"
    />

    <h4>统计信息</h4>
    <div class="stats-info">
      <div class="stat-row">
        <span class="label">人物数量</span>
        <span class="value">{{ nodeCount }}</span>
      </div>
      <div class="stat-row">
        <span class="label">关系数量</span>
        <span class="value">{{ linkCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface RelationTypeOption {
  label: string
  value: string
  color: string
}

defineProps<{
  visibleRelationTypes: string[]
  importanceThreshold: number
  relationTypes: RelationTypeOption[]
  nodeCount: number
  linkCount: number
}>()

defineEmits<{
  (e: 'update:visibleRelationTypes', value: string[]): void
  (e: 'update:importanceThreshold', value: number): void
  (e: 'change'): void
}>()
</script>

<style lang="scss" scoped>
.filter-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 100%;
  padding: 16px;
  border-left: 1px solid var(--border-color);
  background: var(--card-bg);
  overflow-y: auto;
  z-index: 10;

  h4 {
    font-size: 13px;
    color: var(--text-color-secondary);
    margin: 0 0 12px;

    &:not(:first-child) {
      margin-top: 20px;
    }
  }

  .el-checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .relation-type-item {
    display: flex;
    align-items: center;
    gap: 6px;

    &::before {
      content: '';
      width: 12px;
      height: 3px;
      background: var(--color);
      border-radius: 2px;
    }
  }

  .stats-info {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .stat-row {
      display: flex;
      justify-content: space-between;
      font-size: 13px;

      .label {
        color: var(--text-color-secondary);
      }

      .value {
        font-weight: 600;
        color: var(--primary-color);
      }
    }
  }
}
</style>
