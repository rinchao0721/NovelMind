<template>
  <div class="analysis-result card">
    <h3>分析结果</h3>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-statistic title="识别人物" :value="result.characterCount">
          <template #suffix>
            <span class="stat-suffix">人</span>
          </template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="人物关系" :value="result.relationshipCount">
          <template #suffix>
            <span class="stat-suffix">条</span>
          </template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="主要情节" :value="result.plotCount">
          <template #suffix>
            <span class="stat-suffix">个</span>
          </template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="分析章节" :value="result.chapterCount">
          <template #suffix>
            <span class="stat-suffix">章</span>
          </template>
        </el-statistic>
      </el-col>
    </el-row>

    <div class="result-actions">
      <el-button type="primary" @click="$emit('view-graph')">
        <el-icon><Share /></el-icon>
        查看关系图谱
      </el-button>
      <el-button @click="$emit('view-characters')">
        <el-icon><User /></el-icon>
        查看人物列表
      </el-button>
      <el-button @click="$emit('view-timeline')">
        <el-icon><Timer /></el-icon>
        查看时间线
      </el-button>
      <el-button @click="$emit('export')">
        <el-icon><Download /></el-icon>
        导出结果
      </el-button>
      
      <el-button type="warning" plain @click="$emit('reanalyze')">
        <el-icon><RefreshRight /></el-icon>
        重新分析
      </el-button>
      
      <el-popconfirm 
        title="确定要删除所有分析结果吗？此操作不可恢复。" 
        confirm-button-text="删除" 
        cancel-button-text="取消"
        confirm-button-type="danger"
        @confirm="$emit('delete')"
      >
        <template #reference>
          <el-button type="danger" plain>
            <el-icon><Delete /></el-icon>
            删除结果
          </el-button>
        </template>
      </el-popconfirm>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import { Share, User, Timer, Download, Delete, RefreshRight } from '@element-plus/icons-vue'

defineProps({
  result: {
    type: Object as PropType<{
      characterCount: number;
      relationshipCount: number;
      plotCount: number;
      chapterCount: number;
    }>,
    required: true
  }
})

defineEmits(['view-graph', 'view-characters', 'view-timeline', 'export', 'delete', 'reanalyze'])
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
.analysis-result {
  .stat-suffix {
    font-size: 14px;
    color: var(--text-color-secondary);
  }

  .result-actions {
    margin-top: 24px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
}
</style>
