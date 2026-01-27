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
                v-for="provider in providers" 
                :key="provider.id"
                class="provider-item"
                :class="{ active: activeProvider === provider.id, default: settings.defaultProvider === provider.id }"
                @click="activeProvider = provider.id"
              >
                <div class="provider-icon">{{ provider.icon }}</div>
                <div class="provider-name">{{ provider.name }}</div>
                <div v-if="settings.defaultProvider === provider.id" class="default-badge">默认</div>
              </div>
            </div>
          </div>
          
          <div class="llm-content">
            <div class="content-header">
              <h3>{{ getProviderName(activeProvider) }}</h3>
              <el-button 
                v-if="settings.defaultProvider !== activeProvider"
                size="small" 
                @click="setDefaultProvider(activeProvider)"
              >
                设为默认
              </el-button>
              <el-tag v-else type="success">当前默认</el-tag>
            </div>

            <el-form label-width="120px" class="provider-form">
              <!-- OpenAI -->
              <template v-if="activeProvider === 'openai'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.openai.apiKey" type="password" show-password placeholder="sk-..." />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input v-model="settings.openai.baseUrl" placeholder="https://api.openai.com/v1" />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.openai.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="GPT-4o" value="gpt-4o" />
                    <el-option label="GPT-4o-mini" value="gpt-4o-mini" />
                    <el-option label="GPT-4-Turbo" value="gpt-4-turbo" />
                    <el-option label="GPT-3.5-Turbo" value="gpt-3.5-turbo" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- Claude -->
              <template v-if="activeProvider === 'claude'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.claude.apiKey" type="password" show-password placeholder="sk-ant-..." />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.claude.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet-20241022" />
                    <el-option label="Claude 3.5 Haiku" value="claude-3-5-haiku-20241022" />
                    <el-option label="Claude 3 Opus" value="claude-3-opus-20240229" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- Gemini -->
              <template v-if="activeProvider === 'gemini'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.gemini.apiKey" type="password" show-password placeholder="AIza..." />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.gemini.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="Gemini 1.5 Pro" value="gemini-1.5-pro" />
                    <el-option label="Gemini 1.5 Flash" value="gemini-1.5-flash" />
                    <el-option label="Gemini Pro" value="gemini-pro" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- DeepSeek -->
              <template v-if="activeProvider === 'deepseek'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.deepseek.apiKey" type="password" show-password />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.deepseek.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="DeepSeek Chat" value="deepseek-chat" />
                    <el-option label="DeepSeek Reasoner" value="deepseek-reasoner" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- Qwen -->
              <template v-if="activeProvider === 'qwen'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.qwen.apiKey" type="password" show-password />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.qwen.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="Qwen-Max" value="qwen-max" />
                    <el-option label="Qwen-Plus" value="qwen-plus" />
                    <el-option label="Qwen-Turbo" value="qwen-turbo" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- Zhipu -->
              <template v-if="activeProvider === 'zhipu'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.zhipu.apiKey" type="password" show-password />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.zhipu.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="GLM-4" value="glm-4" />
                    <el-option label="GLM-4-Flash" value="glm-4-flash" />
                    <el-option label="GLM-3-Turbo" value="glm-3-turbo" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- Baidu -->
              <template v-if="activeProvider === 'baidu'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.baidu.apiKey" type="password" show-password placeholder="应用 API Key" />
                </el-form-item>
                <el-form-item label="Secret Key">
                  <el-input v-model="settings.baidu.secretKey" type="password" show-password placeholder="应用 Secret Key" />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.baidu.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="ERNIE 4.0" value="ernie-4.0-8k" />
                    <el-option label="ERNIE 3.5" value="ernie-3.5-8k" />
                    <el-option label="ERNIE Speed" value="ernie-speed" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- AIHubMix -->
              <template v-if="activeProvider === 'aihubmix'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.aihubmix.apiKey" type="password" show-password placeholder="sk-..." />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input v-model="settings.aihubmix.baseUrl" placeholder="https://aihubmix.com/v1" />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.aihubmix.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="GPT-4o" value="gpt-4o" />
                    <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet-20241022" />
                    <el-option label="Gemini 1.5 Pro" value="gemini-1.5-pro-latest" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- SiliconFlow -->
              <template v-if="activeProvider === 'siliconflow'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.siliconflow.apiKey" type="password" show-password placeholder="sk-..." />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input v-model="settings.siliconflow.baseUrl" placeholder="https://api.siliconflow.cn/v1" />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.siliconflow.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="DeepSeek-V3" value="deepseek-ai/DeepSeek-V3" />
                    <el-option label="DeepSeek-R1" value="deepseek-ai/DeepSeek-R1" />
                    <el-option label="Qwen2.5-72B" value="Qwen/Qwen2.5-72B-Instruct" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- OpenRouter -->
              <template v-if="activeProvider === 'openrouter'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.openrouter.apiKey" type="password" show-password placeholder="sk-or-..." />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input v-model="settings.openrouter.baseUrl" placeholder="https://openrouter.ai/api/v1" />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.openrouter.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="GPT-4o" value="openai/gpt-4o" />
                    <el-option label="Claude 3.5 Sonnet" value="anthropic/claude-3.5-sonnet" />
                    <el-option label="Gemini Pro 1.5" value="google/gemini-pro-1.5" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- Ollama -->
              <template v-if="activeProvider === 'ollama'">
                <el-form-item label="Base URL">
                  <el-input v-model="settings.ollama.baseUrl" placeholder="http://localhost:11434/v1" />
                </el-form-item>
                <el-form-item label="API Key">
                  <el-input v-model="settings.ollama.apiKey" type="password" show-password placeholder="ollama (optional)" />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.ollama.model" allow-create filterable default-first-option style="width: 100%">
                    <el-option label="Llama 3" value="llama3" />
                    <el-option label="Mistral" value="mistral" />
                    <el-option label="Qwen 2" value="qwen2" />
                  </el-select>
                </el-form-item>
              </template>

              <!-- Custom -->
              <template v-if="activeProvider === 'custom'">
                <el-form-item label="API Key">
                  <el-input v-model="settings.custom.apiKey" type="password" show-password />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input v-model="settings.custom.baseUrl" placeholder="https://your-api-endpoint.com/v1" />
                </el-form-item>
                <el-form-item label="模型">
                  <el-input v-model="settings.custom.model" placeholder="model-name" />
                </el-form-item>
              </template>

              <el-form-item>
                <el-button 
                  type="primary" 
                  :loading="testingProvider === activeProvider"
                  @click="testConnection(activeProvider)"
                >
                  测试连接
                </el-button>
                <el-tag v-if="providerStatus[activeProvider]" :type="providerStatus[activeProvider] === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                  {{ providerStatus[activeProvider] === 'success' ? '连接成功' : '连接失败' }}
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
            <p class="version">版本 1.0.0</p>
          </div>
          <p class="description">
            AI 驱动的小说剧情分析与人物关系可视化工具。
            <br>
            灵感来源于 <a href="https://github.com/666ghj/MiroFish" target="_blank">MiroFish</a> 项目。
          </p>
          <div class="links">
            <el-button text type="primary">
              <el-icon><Link /></el-icon>
              GitHub
            </el-button>
            <el-button text type="primary">
              <el-icon><Document /></el-icon>
              文档
            </el-button>
            <el-button text type="primary">
              <el-icon><ChatDotRound /></el-icon>
              反馈
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
import { Link, Document, ChatDotRound, Refresh, Delete } from '@element-plus/icons-vue'
import { settingsApi } from '@/api'

const activeTab = ref('llm')
const activeProvider = ref('openai') // Default to openai, no longer collapse array
const neo4jStatus = ref('')
const saving = ref(false)
const testingProvider = ref('')
const testingNeo4j = ref(false)

const providers = [
  { id: 'openai', name: 'OpenAI', icon: '🤖' },
  { id: 'claude', name: 'Claude', icon: '🧠' },
  { id: 'gemini', name: 'Gemini', icon: '✨' },
  { id: 'deepseek', name: 'DeepSeek', icon: '🐋' },
  { id: 'qwen', name: '阿里百炼', icon: '☁️' },
  { id: 'zhipu', name: '智谱 AI', icon: '🚀' },
  { id: 'baidu', name: '百度文心', icon: '🐼' },
  { id: 'aihubmix', name: 'AIHubMix', icon: '🔄' },
  { id: 'siliconflow', name: '硅基流动', icon: '⚡' },
  { id: 'openrouter', name: 'OpenRouter', icon: '🌐' },
  { id: 'ollama', name: 'Ollama', icon: '🦙' },
  { id: 'custom', name: '自定义 API', icon: '⚙️' },
]

// Logs logic
const logs = ref<string[]>([])
const loadingLogs = ref(false)
const autoRefresh = ref(false)
const logFilter = ref('ALL')
const logContainerRef = ref<HTMLElement | null>(null)
let refreshInterval: number | null = null

const providerStatus = reactive<Record<string, string>>({
  openai: '',
  claude: '',
  gemini: '',
  deepseek: '',
  qwen: '',
  zhipu: '',
  baidu: '',
  custom: '',
  aihubmix: '',
  siliconflow: '',
  openrouter: '',
  ollama: '',
})

const settings = ref({
  defaultProvider: 'openai',
  openai: { apiKey: '', baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o' },
  claude: { apiKey: '', model: 'claude-3-5-sonnet-20241022' },
  gemini: { apiKey: '', model: 'gemini-1.5-flash' },
  deepseek: { apiKey: '', model: 'deepseek-chat' },
  qwen: { apiKey: '', model: 'qwen-plus' },
  zhipu: { apiKey: '', model: 'glm-4' },
  baidu: { apiKey: '', secretKey: '', model: 'ernie-4.0-8k' },
  custom: { apiKey: '', baseUrl: '', model: '' },
  aihubmix: { apiKey: '', baseUrl: 'https://aihubmix.com/v1', model: 'gpt-4o' },
  siliconflow: { apiKey: '', baseUrl: 'https://api.siliconflow.cn/v1', model: 'deepseek-ai/DeepSeek-V3' },
  openrouter: { apiKey: '', baseUrl: 'https://openrouter.ai/api/v1', model: 'openai/gpt-4o' },
  ollama: { apiKey: 'ollama', baseUrl: 'http://localhost:11434/v1', model: 'llama3' },
  neo4j: { enabled: false, uri: 'bolt://localhost:7687', user: 'neo4j', password: '' },
  theme: 'light',
  language: 'zh-CN',
  defaultAnalysisDepth: 'standard',
  autoSave: true,
  dataPath: ''
})

const getProviderName = (id: string) => providers.find(p => p.id === id)?.name || id

const setDefaultProvider = async (id: string) => {
  settings.value.defaultProvider = id
  await saveSettings()
}

const testConnection = async (provider: string) => {
  testingProvider.value = provider
  providerStatus[provider] = ''
  
  try {
    const providerConfig = settings.value[provider as keyof typeof settings.value]
    if (typeof providerConfig !== 'object' || providerConfig === null) {
      throw new Error('Invalid provider config')
    }
    
    const result = await settingsApi.testProvider(provider, providerConfig as Record<string, unknown>)
    
    if (result.success) {
      providerStatus[provider] = 'success'
      ElMessage.success(`${getProviderName(provider)} 连接成功`)
    } else {
      providerStatus[provider] = 'failed'
      ElMessage.error(`连接失败: ${result.error || '未知错误'}`)
    }
  } catch (error: unknown) {
    providerStatus[provider] = 'failed'
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
    // 调用后端清除数据
    ElMessage.success('数据已清除')
  } catch {
    // 用户取消
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
    // Don't show error message for polling to avoid spam
    if (!autoRefresh.value) ElMessage.error('获取日志失败')
  } finally {
    loadingLogs.value = false
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
  // Clear existing interval
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }

  // Start interval only if auto refresh is enabled AND we are on the logs tab
  if (autoRefresh.value && activeTab.value === 'logs') {
    refreshLogs() // Immediate fetch
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
      // Deep merge settings
      settings.value = {
        ...settings.value,
        ...savedSettings,
        openai: { ...settings.value.openai, ...savedSettings.openai },
        claude: { ...settings.value.claude, ...savedSettings.claude },
        gemini: { ...settings.value.gemini, ...savedSettings.gemini },
        deepseek: { ...settings.value.deepseek, ...savedSettings.deepseek },
        qwen: { ...settings.value.qwen, ...savedSettings.qwen },
        zhipu: { ...settings.value.zhipu, ...savedSettings.zhipu },
        baidu: { ...settings.value.baidu, ...savedSettings.baidu },
        custom: { ...settings.value.custom, ...savedSettings.custom },
        aihubmix: { ...settings.value.aihubmix, ...savedSettings.aihubmix },
        siliconflow: { ...settings.value.siliconflow, ...savedSettings.siliconflow },
        openrouter: { ...settings.value.openrouter, ...savedSettings.openrouter },
        ollama: { ...settings.value.ollama, ...savedSettings.ollama },
        neo4j: { ...settings.value.neo4j, ...savedSettings.neo4j }
      }
    }
    
    // Get data path from Electron
    if (window.electronAPI?.getPath) {
      settings.value.dataPath = await window.electronAPI.getPath('userData')
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

      h3 {
        margin: 0;
        font-size: 18px;
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
