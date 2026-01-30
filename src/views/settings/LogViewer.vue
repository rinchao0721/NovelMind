<template>
  <div class="log-viewer-container">
    <div class="log-toolbar">
      <div class="left">
        <el-button type="primary" @click="refreshLogs" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-switch v-model="autoRefresh" active-text="自动刷新" />
        <el-select v-model="logFilter" placeholder="日志级别" style="width: 120px">
          <el-option label="全部" value="ALL" />
          <el-option label="INFO" value="INFO" />
          <el-option label="WARNING" value="WARNING" />
          <el-option label="ERROR" value="ERROR" />
        </el-select>
      </div>
      <div class="right">
        <el-button type="default" plain @click="$emit('export')" style="margin-right: 12px">
          <el-icon><FolderOpened /></el-icon> 导出日志
        </el-button>
        <el-button type="danger" plain @click="$emit('clear')">
          <el-icon><Delete /></el-icon> 清空日志
        </el-button>
      </div>
    </div>
    
    <div class="log-content" ref="logContainerRef">
      <template v-if="filteredLogs.length > 0">
        <div v-for="(line, index) in filteredLogs" :key="index" class="log-line" :class="getLogClass(line)">
          {{ line }}
        </div>
      </template>
      <div v-else class="empty-logs">暂无日志</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Refresh, Delete, FolderOpened } from '@element-plus/icons-vue'
import { settingsApi } from '@/api'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  active: boolean
}>()

defineEmits<{
  (e: 'export'): void
  (e: 'clear'): void
}>()

const logs = ref<string[]>([])
const loading = ref(false)
const autoRefresh = ref(false)
const logFilter = ref('ALL')
const logContainerRef = ref<HTMLElement | null>(null)
let refreshInterval: number | null = null

const refreshLogs = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const response = await settingsApi.getLogs(500)
    logs.value = response.logs || []
    scrollToBottom()
  } catch (error) {
    console.error('Failed to fetch logs:', error)
    if (!silent) ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

const filteredLogs = computed(() => {
  if (logFilter.value === 'ALL') return logs.value
  return logs.value.filter(line => line.includes(`[${logFilter.value}]`))
})

const getLogClass = (line: string) => {
  if (line.includes('[ERROR]')) return 'log-error'
  if (line.includes('[WARNING]')) return 'log-warning'
  return 'log-info'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (logContainerRef.value) {
      logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
    }
  })
}

const managePolling = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
  if (autoRefresh.value && props.active) {
    refreshLogs(true)
    refreshInterval = window.setInterval(() => refreshLogs(true), 3000)
  }
}

watch(() => props.active, (isActive) => {
  if (isActive) {
    refreshLogs()
    managePolling()
  } else {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }
})

watch(autoRefresh, managePolling)

onMounted(() => {
  const stored = localStorage.getItem('logAutoRefresh')
  if (stored !== null) {
    autoRefresh.value = stored === 'true'
  }
  if (props.active) {
    refreshLogs()
    managePolling()
  }
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

// Persistence
watch(autoRefresh, (newVal) => {
  localStorage.setItem('logAutoRefresh', String(newVal))
})
</script>

<style lang="scss" scoped>
.log-viewer-container {
  padding: 20px;
}

.log-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  .left {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.log-content {
  height: 450px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  border-radius: 6px;
  padding: 16px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  border: 1px solid #333;

  .log-line {
    border-bottom: 1px solid #2d2d2d;
    padding: 4px 0;
    
    &.log-error {
      color: #f56c6c;
      background-color: rgba(245, 108, 108, 0.1);
    }
    &.log-warning {
      color: #e6a23c;
      background-color: rgba(230, 162, 60, 0.1);
    }
    &.log-info {
      color: #d4d4d4;
    }
  }

  .empty-logs {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #666;
    font-style: italic;
  }
}
</style>
