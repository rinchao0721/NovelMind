<template>
  <el-dialog 
    :model-value="visible" 
    title="导出分析结果" 
    width="400px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <div class="export-options">
      <el-radio-group 
        :model-value="format" 
        class="export-format"
        @update:model-value="$emit('update:format', $event)"
      >
        <el-radio-button value="json">JSON</el-radio-button>
        <el-radio-button value="markdown">Markdown</el-radio-button>
      </el-radio-group>
      <p class="export-hint">
        {{ format === 'json' ? 'JSON 格式包含完整数据，适合导入其他工具' : 'Markdown 格式便于阅读和分享' }}
      </p>
    </div>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="$emit('confirm')">
        导出
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
defineProps({
  visible: Boolean,
  format: {
    type: String,
    default: 'json'
  },
  loading: Boolean
})

defineEmits(['update:visible', 'update:format', 'confirm'])
</script>

<style lang="scss" scoped>
.export-options {
  text-align: center;

  .export-format {
    margin-bottom: 16px;
  }

  .export-hint {
    color: var(--text-color-secondary);
    font-size: 13px;
  }
}
</style>
