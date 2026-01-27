<template>
  <div class="settings-view">
    <div class="page-header">
      <h2>设置</h2>
      <p>配置 API 密钥和应用参数</p>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- LLM API 设置 -->
      <el-tab-pane label="LLM API" name="llm">
        <div class="settings-section card">
          <h3>选择默认 LLM 提供商</h3>
          <el-radio-group v-model="settings.defaultProvider" @change="saveSettings">
            <el-radio value="openai">OpenAI</el-radio>
            <el-radio value="claude">Anthropic Claude</el-radio>
            <el-radio value="gemini">Google Gemini</el-radio>
            <el-radio value="deepseek">DeepSeek</el-radio>
            <el-radio value="qwen">阿里百炼 (Qwen)</el-radio>
            <el-radio value="zhipu">智谱AI</el-radio>
            <el-radio value="baidu">百度文心</el-radio>
            <el-radio value="custom">自定义 API</el-radio>
          </el-radio-group>
        </div>

        <div class="settings-section card">
          <h3>API 密钥配置</h3>
          <el-form label-width="140px">
            <el-collapse v-model="activeProvider">
              <!-- OpenAI -->
              <el-collapse-item name="openai" title="OpenAI">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.openai.apiKey" 
                    type="password"
                    show-password
                    placeholder="sk-..."
                  />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input 
                    v-model="settings.openai.baseUrl"
                    placeholder="https://api.openai.com/v1"
                  />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.openai.model" style="width: 100%">
                    <el-option label="GPT-4o" value="gpt-4o" />
                    <el-option label="GPT-4o-mini" value="gpt-4o-mini" />
                    <el-option label="GPT-4-Turbo" value="gpt-4-turbo" />
                    <el-option label="GPT-4" value="gpt-4" />
                    <el-option label="GPT-3.5-Turbo" value="gpt-3.5-turbo" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'openai'"
                    @click="testConnection('openai')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.openai" :type="providerStatus.openai === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.openai === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>

              <!-- Claude -->
              <el-collapse-item name="claude" title="Anthropic Claude">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.claude.apiKey"
                    type="password"
                    show-password
                    placeholder="sk-ant-..."
                  />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.claude.model" style="width: 100%">
                    <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet-20241022" />
                    <el-option label="Claude 3.5 Haiku" value="claude-3-5-haiku-20241022" />
                    <el-option label="Claude 3 Opus" value="claude-3-opus-20240229" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'claude'"
                    @click="testConnection('claude')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.claude" :type="providerStatus.claude === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.claude === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>

              <!-- Gemini -->
              <el-collapse-item name="gemini" title="Google Gemini">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.gemini.apiKey"
                    type="password"
                    show-password
                    placeholder="AIza..."
                  />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.gemini.model" style="width: 100%">
                    <el-option label="Gemini 1.5 Pro" value="gemini-1.5-pro" />
                    <el-option label="Gemini 1.5 Flash" value="gemini-1.5-flash" />
                    <el-option label="Gemini Pro" value="gemini-pro" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'gemini'"
                    @click="testConnection('gemini')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.gemini" :type="providerStatus.gemini === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.gemini === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>

              <!-- DeepSeek -->
              <el-collapse-item name="deepseek" title="DeepSeek">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.deepseek.apiKey"
                    type="password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.deepseek.model" style="width: 100%">
                    <el-option label="DeepSeek Chat" value="deepseek-chat" />
                    <el-option label="DeepSeek Reasoner" value="deepseek-reasoner" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'deepseek'"
                    @click="testConnection('deepseek')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.deepseek" :type="providerStatus.deepseek === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.deepseek === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>

              <!-- Qwen -->
              <el-collapse-item name="qwen" title="阿里百炼 (Qwen)">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.qwen.apiKey"
                    type="password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.qwen.model" style="width: 100%">
                    <el-option label="Qwen-Max" value="qwen-max" />
                    <el-option label="Qwen-Plus" value="qwen-plus" />
                    <el-option label="Qwen-Turbo" value="qwen-turbo" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'qwen'"
                    @click="testConnection('qwen')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.qwen" :type="providerStatus.qwen === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.qwen === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>

              <!-- Zhipu -->
              <el-collapse-item name="zhipu" title="智谱AI (GLM)">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.zhipu.apiKey"
                    type="password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.zhipu.model" style="width: 100%">
                    <el-option label="GLM-4" value="glm-4" />
                    <el-option label="GLM-4-Flash" value="glm-4-flash" />
                    <el-option label="GLM-3-Turbo" value="glm-3-turbo" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'zhipu'"
                    @click="testConnection('zhipu')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.zhipu" :type="providerStatus.zhipu === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.zhipu === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>

              <!-- Baidu -->
              <el-collapse-item name="baidu" title="百度文心">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.baidu.apiKey"
                    type="password"
                    show-password
                    placeholder="应用 API Key"
                  />
                </el-form-item>
                <el-form-item label="Secret Key">
                  <el-input 
                    v-model="settings.baidu.secretKey"
                    type="password"
                    show-password
                    placeholder="应用 Secret Key"
                  />
                </el-form-item>
                <el-form-item label="模型">
                  <el-select v-model="settings.baidu.model" style="width: 100%">
                    <el-option label="ERNIE 4.0" value="ernie-4.0-8k" />
                    <el-option label="ERNIE 3.5" value="ernie-3.5-8k" />
                    <el-option label="ERNIE Speed" value="ernie-speed" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'baidu'"
                    @click="testConnection('baidu')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.baidu" :type="providerStatus.baidu === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.baidu === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>

              <!-- 自定义 API -->
              <el-collapse-item name="custom" title="自定义 OpenAI 兼容 API">
                <el-form-item label="API Key">
                  <el-input 
                    v-model="settings.custom.apiKey"
                    type="password"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="Base URL">
                  <el-input 
                    v-model="settings.custom.baseUrl"
                    placeholder="https://your-api-endpoint.com/v1"
                  />
                </el-form-item>
                <el-form-item label="模型名称">
                  <el-input 
                    v-model="settings.custom.model"
                    placeholder="model-name"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button 
                    type="primary" 
                    :loading="testingProvider === 'custom'"
                    @click="testConnection('custom')"
                  >
                    测试连接
                  </el-button>
                  <el-tag v-if="providerStatus.custom" :type="providerStatus.custom === 'success' ? 'success' : 'danger'" style="margin-left: 12px">
                    {{ providerStatus.custom === 'success' ? '连接成功' : '连接失败' }}
                  </el-tag>
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
          </el-form>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Link, Document, ChatDotRound } from '@element-plus/icons-vue'
import { settingsApi } from '@/api'

const activeTab = ref('llm')
const activeProvider = ref(['openai'])
const neo4jStatus = ref('')
const saving = ref(false)
const testingProvider = ref('')
const testingNeo4j = ref(false)

const providerStatus = reactive<Record<string, string>>({
  openai: '',
  claude: '',
  gemini: '',
  deepseek: '',
  qwen: '',
  zhipu: '',
  baidu: '',
  custom: ''
})

const settings = ref({
  defaultProvider: 'openai',
  openai: {
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o'
  },
  claude: {
    apiKey: '',
    model: 'claude-3-5-sonnet-20241022'
  },
  gemini: {
    apiKey: '',
    model: 'gemini-1.5-flash'
  },
  deepseek: {
    apiKey: '',
    model: 'deepseek-chat'
  },
  qwen: {
    apiKey: '',
    model: 'qwen-plus'
  },
  zhipu: {
    apiKey: '',
    model: 'glm-4'
  },
  baidu: {
    apiKey: '',
    secretKey: '',
    model: 'ernie-4.0-8k'
  },
  custom: {
    apiKey: '',
    baseUrl: '',
    model: ''
  },
  neo4j: {
    enabled: false,
    uri: 'bolt://localhost:7687',
    user: 'neo4j',
    password: ''
  },
  theme: 'light',
  language: 'zh-CN',
  defaultAnalysisDepth: 'standard',
  autoSave: true,
  dataPath: ''
})

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
      ElMessage.success(`${provider} 连接成功`)
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

onMounted(async () => {
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
</script>

<style lang="scss" scoped>
.settings-view {
  max-width: 900px;
  margin: 0 auto;
}

.settings-tabs {
  :deep(.el-tabs__content) {
    padding: 0;
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

  .el-collapse {
    border: none;
  }

  :deep(.el-collapse-item__header) {
    background: transparent;
    font-weight: 500;
  }

  :deep(.el-collapse-item__wrap) {
    background: transparent;
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
</style>
