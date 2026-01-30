<template>
  <div class="app-settings-container">
    <div class="settings-section">
      <h3>界面设置</h3>
      <el-form label-width="120px">
        <el-form-item label="默认主题">
          <el-radio-group v-model="settings.theme">
            <el-radio value="light">浅色</el-radio>
            <el-radio value="dark">深色</el-radio>
            <el-radio value="auto">跟随系统</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="settings.language" style="width: 200px">
            <el-option label="简体中文" value="zh-CN" />
            <el-option label="English" value="en-US" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-section">
      <h3>分析设置</h3>
      <el-form label-width="120px">
        <el-form-item label="默认分析深度">
          <el-select v-model="settings.defaultAnalysisDepth" style="width: 200px">
            <el-option label="快速分析" value="quick" />
            <el-option label="标准分析" value="standard" />
            <el-option label="深度分析" value="deep" />
          </el-select>
        </el-form-item>
        <el-form-item label="自动保存">
          <el-switch v-model="settings.autoSave" />
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-section">
      <h3>数据管理</h3>
      <el-form label-width="120px">
        <el-form-item label="数据存储位置">
          <el-input v-model="settings.dataPath" readonly>
            <template #append>
              <el-button @click="$emit('select-path')">选择</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="清除数据">
          <el-button type="danger" @click="$emit('clear-data')">
            清除所有数据
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Settings } from '@/types'

defineProps<{
  settings: Settings
}>()

defineEmits<{
  (e: 'select-path'): void
  (e: 'clear-data'): void
}>()
</script>

<style lang="scss" scoped>
.app-settings-container {
  padding: 24px;
}

.settings-section {
  margin-bottom: 32px;

  h3 {
    font-size: 16px;
    margin: 0 0 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
  }
}
</style>
