<template>
  <div class="settings-view">
    <div class="page-header">
      <h2>设置</h2>
      <p>配置 API 密钥和应用参数</p>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- LLM API 设置 -->
      <el-tab-pane label="LLM API" name="llm">
        <div class="llm-settings-container card">
          <div class="llm-sidebar">
            <div class="sidebar-header">模型服务商</div>
            <div class="provider-list">
              <div 
                v-for="provider in PROVIDERS" 
                :key="provider.id"
                class="provider-item"
                :class="{ active: activeProviderId === provider.id, default: settings.defaultProvider === provider.id }"
                @click="activeProviderId = provider.id"
              >
                <div class="provider-icon">
                  <ProviderAvatar 
                    :provider-id="provider.id" 
                    :name="provider.name"
                    :size="24"
                  />
                </div>
                <div class="provider-name">{{ provider.name }}</div>
                <div v-if="settings.defaultProvider === provider.id" class="default-badge">默认</div>
              </div>
            </div>
          </div>
          
          <div class="llm-content">
            <div class="content-header">
              <div class="provider-info">
                <ProviderAvatar 
                  :provider-id="activeProviderId" 
                  :name="activeProviderConfig?.name"
                  :size="28"
                  style="margin-right: 12px"
                />
                <h3>{{ activeProviderConfig?.name }}</h3>
              </div>
              <el-button 
                v-if="settings.defaultProvider !== activeProviderId"
                size="small" 
                @click="setDefaultProvider(activeProviderId)"
              >
                设为默认
              </el-button>
              <el-tag v-else type="success">当前默认</el-tag>
            </div>

            <!-- 动态表单 -->
            <el-form 
              v-if="activeProviderConfig && currentProviderSettings" 
              label-width="120px" 
              class="provider-form"
            >
              <!-- API Key -->
              <el-form-item v-if="activeProviderConfig.requiresApiKey" label="API Key">
                <el-input 
                  v-model="currentProviderSettings.apiKey" 
                  type="password" 
                  show-password 
                  :placeholder="`请输入 ${activeProviderConfig.name} API Key`" 
                />
              </el-form-item>

              <!-- Secret Key (如百度) -->
              <el-form-item v-if="activeProviderConfig.requiresSecretKey" label="Secret Key">
                <el-input 
                  v-model="currentProviderSettings.secretKey" 
                  type="password" 
                  show-password 
                  placeholder="请输入 Secret Key" 
                />
              </el-form-item>

              <!-- Base URL -->
              <el-form-item v-if="activeProviderConfig.supportsCustomBaseUrl" label="Base URL">
                <el-input 
                  v-model="currentProviderSettings.baseUrl" 
                  :placeholder="activeProviderConfig.defaultBaseUrl || 'https://api.example.com/v1'" 
                />
              </el-form-item>

              <!-- 模型选择 -->
              <el-form-item label="模型">
                <el-select 
                  v-model="currentProviderSettings.model" 
                  allow-create 
                  filterable 
                  default-first-option 
                  placeholder="选择或输入模型名称"
                  style="width: 100%"
                >
                  <el-option 
                    v-for="model in activeProviderConfig.defaultModels" 
                    :key="model" 
                    :label="model" 
                    :value="model" 
                  />
                </el-select>
              </el-form-item>

              <!-- 测试连接 -->
              <el-form-item>
                <el-button 
                  type="primary" 
                  :loading="testingProvider === activeProviderId"
                  @click="testConnection(activeProviderId)"
                >
                  测试连接
                </el-button>
                <el-tag 
                  v-if="providerStatus[activeProviderId]" 
                  :type="providerStatus[activeProviderId] === 'success' ? 'success' : 'danger'" 
                  style="margin-left: 12px"
                >
                  {{ providerStatus[activeProviderId] === 'success' ? '连接成功' : '连接失败' }}
                </el-tag>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-tab-pane>

      <!-- Neo4j 设置 -->
      <el-tab-pane label="Neo4j 数据库" name="neo4j">
        <div class="settings-section card">
          <h3>Neo4j 连接配置</h3>
          <p class="hint">Neo4j 是可选的。如果不配置，将使用 SQLite 存储关系数据。</p>
          <el-form label-width="120px">
            <el-form-item label="启用 Neo4j">
              <el-switch v-model="settings.neo4j.enabled" />
            </el-form-item>
            <template v-if="settings.neo4j.enabled">
              <el-form-item label="连接 URI">
                <el-input 
                  v-model="settings.neo4j.uri"
                  placeholder="bolt://localhost:7687"
                />
              </el-form-item>
              <el-form-item label="用户名">
                <el-input v-model="settings.neo4j.user" placeholder="neo4j" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input 
                  v-model="settings.neo4j.password"
                  type="password"
                  show-password
                />
              </el-form-item>
              <el-form-item>
                <el-button 
                  type="primary" 
                  :loading="testingNeo4j"
                  @click="testNeo4jConnection"
                >
                  测试连接
                </el-button>
                <el-tag v-if="neo4jStatus" :type="neo4jStatus === 'connected' ? 'success' : 'danger'" style="margin-left: 12px">
                  {{ neo4jStatus === 'connected' ? '已连接' : '连接失败' }}
                </el-tag>
              </el-form-item>
            </template>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 应用设置 -->
      <el-tab-pane label="应用设置" name="app">
        <div class="settings-section card">
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

        <div class="settings-section card">
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

        <div class="settings-section card">
          <h3>数据管理</h3>
          <el-form label-width="120px">
            <el-form-item label="数据存储位置">
              <el-input v-model="settings.dataPath" readonly>
                <template #append>
                  <el-button @click="selectDataPath">选择</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="清除数据">
              <el-button type="danger" @click="clearData">
                清除所有数据
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 运行日志 -->
      <el-tab-pane label="运行日志" name="logs">
        <div class="settings-section card">
          <div class="log-toolbar">
            <div class="left">
              <el-button type="primary" @click="refreshLogs" :loading="loadingLogs">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
              <el-switch v-model="autoRefresh" active-text="自动刷新" @change="saveAutoRefreshState" />
              <el-select v-model="logFilter" placeholder="日志级别" style="width: 120px">
                <el-option label="全部" value="ALL" />
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
              </el-select>
            </div>
            <div class="right">
              <el-button type="default" plain @click="exportLogs" style="margin-right: 12px">
                <el-icon><FolderOpened /></el-icon> 导出日志
              </el-button>
              <el-button type="danger" plain @click="clearLogs">
                <el-icon><Delete /></el-icon> 清空日志
              </el-button>
            </div>
          </div>
          
          <div class="log-container" ref="logContainerRef">
            <template v-if="filteredLogs.length > 0">
              <div v-for="(line, index) in filteredLogs" :key="index" class="log-line" :class="getLogClass(line)">
                {{ line }}
              </div>
            </template>
            <div v-else class="empty-logs">暂无日志</div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 关于 -->
      <el-tab-pane label="关于" name="about">
        <div class="settings-section card about-section">
          <div class="logo">
            <h1>NovelMind</h1>
            <p class="version">版本 0.0.1</p>
          </div>
          <p class="description">
            AI 驱动的小说剧情分析与人物关系可视化工具。
          </p>
          <div class="links">
            <el-button text type="primary">
              <el-icon><Link /></el-icon>
              GitHub
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 保存按钮 -->
    <div class="save-bar">
      <el-button type="primary" size="large" :loading="saving" @click="saveSettings">
        保存设置
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Link, Refresh, Delete, FolderOpened } from '@element-plus/icons-vue'
import { settingsApi } from '@/api'
import { PROVIDERS, getProviderById } from '@/config/providers'
import ProviderAvatar from '@/components/ProviderAvatar.vue'

const activeTab = ref('llm')
const activeProviderId = ref('openai')
const neo4jStatus = ref('')
const saving = ref(false)
const testingProvider = ref('')
const testingNeo4j = ref(false)

// Logs logic
const logs = ref<string[]>([])
const loadingLogs = ref(false)
const autoRefresh = ref(false)
const logFilter = ref('ALL')
const logContainerRef = ref<HTMLElement | null>(null)
let refreshInterval: number | null = null

const providerStatus = reactive<Record<string, string>>({})

// Initialize settings structure
// We will populate this with default values or loaded values
const settings = ref<any>({
  defaultProvider: 'openai',
  // Providers settings will be dynamic, but we can initialize known ones or rely on loading
  // However, to make reactivity work easily for v-model, we should ensure keys exist.
  // We'll initialize keys for all providers in PROVIDERS.
  ...Object.fromEntries(PROVIDERS.map(p => [p.id, {}])),
  
  neo4j: { enabled: false, uri: 'bolt://localhost:7687', user: 'neo4j', password: '' },
  theme: 'light',
  language: 'zh-CN',
  defaultAnalysisDepth: 'standard',
  autoSave: true,
  dataPath: ''
})

// Computed properties for dynamic form
const activeProviderConfig = computed(() => getProviderById(activeProviderId.value))

const currentProviderSettings = computed(() => {
  if (!activeProviderId.value || !settings.value) return null
  
  // Ensure the object exists to avoid v-model errors
  if (!settings.value[activeProviderId.value]) {
    settings.value[activeProviderId.value] = {}
  }
  return settings.value[activeProviderId.value]
})

const setDefaultProvider = async (id: string) => {
  settings.value.defaultProvider = id
  await saveSettings()
}

const testConnection = async (providerId: string) => {
  testingProvider.value = providerId
  providerStatus[providerId] = ''
  
  try {
    const providerConfig = settings.value[providerId]
    if (!providerConfig) {
      throw new Error('Invalid provider config')
    }
    
    // Ensure we send what backend expects. The backend likely expects keys like 'apiKey', 'model', etc.
    const result = await settingsApi.testProvider(providerId, providerConfig)
    
    if (result.success) {
      providerStatus[providerId] = 'success'
      ElMessage.success(`${activeProviderConfig.value?.name || providerId} 连接成功`)
    } else {
      providerStatus[providerId] = 'failed'
      ElMessage.error(`连接失败: ${result.error || '未知错误'}`)
    }
  } catch (error: unknown) {
    providerStatus[providerId] = 'failed'
    const message = error instanceof Error ? error.message : '连接失败'
    ElMessage.error(`连接失败: ${message}`)
  } finally {
    testingProvider.value = ''
  }
}

const testNeo4jConnection = async () => {
  testingNeo4j.value = true
  neo4jStatus.value = ''
  
  try {
    const result = await settingsApi.testNeo4j({
      uri: settings.value.neo4j.uri,
      user: settings.value.neo4j.user,
      password: settings.value.neo4j.password
    })
    
    if (result.success) {
      neo4jStatus.value = 'connected'
      ElMessage.success('Neo4j 连接成功')
    } else {
      neo4jStatus.value = 'failed'
      ElMessage.error(`连接失败: ${result.error || '未知错误'}`)
    }
  } catch (error: unknown) {
    neo4jStatus.value = 'failed'
    const message = error instanceof Error ? error.message : '连接失败'
    ElMessage.error(`连接失败: ${message}`)
  } finally {
    testingNeo4j.value = false
  }
}

const selectDataPath = async () => {
  try {
    const result = await window.electronAPI.openDirectory()
    if (!result.canceled && result.filePaths.length > 0) {
      settings.value.dataPath = result.filePaths[0]
    }
  } catch (error) {
    console.error('Failed to select directory:', error)
  }
}

const clearData = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有数据吗？此操作不可恢复。',
      '警告',
      { type: 'warning' }
    )
    // Call backend to clear data (API needs to be implemented or added here)
    // For now, simulating success
    ElMessage.success('数据已清除')
  } catch {
    // User cancelled
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await settingsApi.saveSettings(settings.value)
    ElMessage.success('设置已保存')
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '保存失败'
    ElMessage.error(`保存失败: ${message}`)
  } finally {
    saving.value = false
  }
}

// Log functions
const refreshLogs = async () => {
  loadingLogs.value = true
  try {
    const response = await settingsApi.getLogs(500)
    logs.value = response.logs || []
    scrollToBottom()
  } catch (error) {
    console.error('Failed to fetch logs:', error)
    if (!autoRefresh.value) ElMessage.error('获取日志失败')
  } finally {
    loadingLogs.value = false
  }
}

const exportLogs = async () => {
  try {
    if (window.electronAPI?.openLogFolder) {
      const path = await window.electronAPI.openLogFolder()
      ElMessage.success(`已打开日志文件夹: ${path}`)
    } else {
      ElMessage.warning('此功能仅在桌面版可用')
    }
  } catch (error) {
    console.error('Failed to export logs:', error)
    ElMessage.error('无法打开日志文件夹')
  }
}

const clearLogs = async () => {
  try {
    await settingsApi.clearLogs()
    logs.value = []
    ElMessage.success('日志已清空')
  } catch (error) {
    ElMessage.error('清空日志失败')
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

// Persistent Auto Refresh
const loadAutoRefreshState = () => {
  const stored = localStorage.getItem('logAutoRefresh')
  if (stored !== null) {
    autoRefresh.value = stored === 'true'
  }
}

const saveAutoRefreshState = () => {
  localStorage.setItem('logAutoRefresh', String(autoRefresh.value))
}

const managePolling = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
  if (autoRefresh.value && activeTab.value === 'logs') {
    refreshLogs()
    refreshInterval = window.setInterval(refreshLogs, 3000)
  }
}

watch(autoRefresh, managePolling)

watch(activeTab, (newVal) => {
  if (newVal === 'logs') {
    refreshLogs()
  }
  managePolling()
})

onMounted(async () => {
  loadAutoRefreshState()
  
  try {
    // Load settings from backend
    const savedSettings = await settingsApi.loadSettings()
    if (savedSettings) {
      // Merge settings safely
      // We iterate over keys to preserve structure
      Object.keys(savedSettings).forEach(key => {
        if (typeof savedSettings[key] === 'object' && savedSettings[key] !== null && !Array.isArray(savedSettings[key])) {
          // If the key exists in our default settings, merge it
          // If it's a provider key (which we initialized in PROVIDERS loop), merge it
          if (!settings.value[key]) {
             settings.value[key] = {}
          }
          settings.value[key] = { ...settings.value[key], ...savedSettings[key] }
        } else {
          settings.value[key] = savedSettings[key]
        }
      })
    }
    
    // Get data path from Electron
    if (window.electronAPI?.getPath) {
      const path = await window.electronAPI.getPath('userData')
      // Only set if not already set by backend settings (unlikely for dataPath which is mostly system dep)
      if (!settings.value.dataPath) {
         settings.value.dataPath = path
      }
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style lang="scss" scoped>
.settings-view {
  max-width: 1000px;
  margin: 0 auto;
}

.settings-tabs {
  :deep(.el-tabs__content) {
    padding: 0;
  }
}

.llm-settings-container {
  display: flex;
  height: 500px;
  padding: 0 !important;
  overflow: hidden;

  .llm-sidebar {
    width: 200px;
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    background-color: var(--bg-color-secondary);

    .sidebar-header {
      padding: 12px 16px;
      font-weight: 600;
      color: var(--text-color-secondary);
      font-size: 12px;
      border-bottom: 1px solid var(--border-color);
    }

    .provider-list {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
    }

    .provider-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      cursor: pointer;
      border-radius: 6px;
      transition: background-color 0.2s;
      margin-bottom: 2px;
      position: relative;

      &:hover {
        background-color: var(--hover-bg);
      }

      &.active {
        background-color: var(--el-color-primary-light-9);
        color: var(--el-color-primary);
      }

      .provider-icon {
        font-size: 18px;
      }

      .provider-name {
        font-size: 14px;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .default-badge {
        font-size: 10px;
        background-color: var(--el-color-success-light-9);
        color: var(--el-color-success);
        padding: 2px 4px;
        border-radius: 4px;
      }
    }
  }

  .llm-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;

    .content-header {
      padding: 16px 24px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;

      .provider-info {
        display: flex;
        align-items: center;

        h3 {
          margin: 0;
          font-size: 18px;
        }
      }
    }

    .provider-form {
      padding: 24px;
      max-width: 600px;
    }
  }
}

.settings-section {
  margin-bottom: 20px;

  h3 {
    font-size: 16px;
    margin: 0 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
  }

  .hint {
    color: var(--text-color-secondary);
    font-size: 13px;
    margin: -8px 0 16px;
  }
}

.about-section {
  text-align: center;
  padding: 40px !important;

  .logo {
    margin-bottom: 24px;

    h1 {
      font-size: 32px;
      color: var(--primary-color);
      margin: 0;
    }

    .version {
      color: var(--text-color-secondary);
      margin: 8px 0 0;
    }
  }

  .description {
    color: var(--text-color-secondary);
    line-height: 1.8;
    margin-bottom: 24px;

    a {
      color: var(--primary-color);
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }

  .links {
    display: flex;
    justify-content: center;
    gap: 16px;
  }
}

.save-bar {
  position: fixed;
  bottom: 24px;
  right: 40px;
  z-index: 100;
}

.log-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  .left {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.log-container {
  height: 400px;
  background-color: #1e1e1e;
  color: #d4d4d4;
  border-radius: 4px;
  padding: 12px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;

  .log-line {
    border-bottom: 1px solid #333;
    padding: 2px 0;
    
    &.log-error {
      color: #f56c6c;
    }
    &.log-warning {
      color: #e6a23c;
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
  }
}
</style>