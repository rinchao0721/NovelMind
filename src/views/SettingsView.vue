<template>
  <div class="settings-view">
    <PageHeader title="应用设置" subtitle="配置 AI 模型、应用偏好与查看运行日志" />

    <BaseCard no-padding class="settings-container">
      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 标签页 1: LLM API 设置 -->
        <el-tab-pane label="模型配置" name="llm">
          <LLMConfig 
            v-if="settings" 
            :settings="settings" 
            :provider-status="providerStatus"
            :testing-provider="testingProvider"
            @set-default="setDefaultProvider"
            @test-connection="testConnection"
          />
        </el-tab-pane>

        <!-- 标签页 2: 应用设置 -->
        <el-tab-pane label="基本设置" name="app">
          <AppConfig 
            v-if="settings" 
            :settings="settings" 
            @select-path="selectDataPath"
            @clear-data="clearData"
          />
        </el-tab-pane>

        <!-- 标签页 3: 运行日志 -->
        <el-tab-pane label="运行日志" name="logs">
          <LogViewer
            ref="logViewerRef"
            :active="activeTab === 'logs'"
            @export="exportLogs"
            @clear="clearLogs"
          />
        </el-tab-pane>

        <!-- 标签页 4: 关于 -->
        <el-tab-pane label="关于" name="about">
          <div class="about-section">
            <div class="logo">
              <h1>NovelMind</h1>
              <p class="version">版本 0.1.0</p>
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
    </BaseCard>

    <!-- 保存按钮 -->
    <div class="save-bar">
      <el-button type="primary" size="large" :loading="saving" @click="saveSettings">
        保存所有设置
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Link } from '@element-plus/icons-vue'
import { settingsApi } from '@/api'
import { PROVIDERS } from '@/config/providers'
import type { Settings, ProviderConfig } from '@/types'
// 导入公共资源
import BaseCard from '@/components/common/BaseCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
// 导入子组件
import LLMConfig from './settings/LLMConfig.vue'
import AppConfig from './settings/AppConfig.vue'
import LogViewer from './settings/LogViewer.vue'

const logViewerRef = ref<InstanceType<typeof LogViewer> | null>(null)

const activeTab = ref('llm')
const saving = ref(false)
const testingProvider = ref('')
const providerStatus = reactive<Record<string, string>>({})

const settings = ref<Settings>({
  defaultProvider: 'openai',
  ...Object.fromEntries(PROVIDERS.map(p => [p.id, {}])),
  theme: 'light',
  language: 'zh-CN',
  defaultAnalysisDepth: 'standard',
  autoSave: true,
  dataPath: '',
  openai: {},
  claude: {},
  gemini: {},
  deepseek: {},
  qwen: {},
  zhipu: {},
  baidu: {},
  custom: {}
})

const setDefaultProvider = async (id: string) => {
  settings.value.defaultProvider = id
  await saveSettings()
}

const testConnection = async (providerId: string, providerConfig: ProviderConfig) => {
  testingProvider.value = providerId
  providerStatus[providerId] = ''
  
  try {
    const result = await settingsApi.testProvider(providerId, providerConfig)
    if (result.success) {
      providerStatus[providerId] = 'success'
      ElMessage.success('连接成功')
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

const exportLogs = async () => {
  try {
    if (window.electronAPI?.openLogFolder) {
      await window.electronAPI.openLogFolder()
      ElMessage.success('已打开日志文件夹')
    } else {
      ElMessage.warning('此功能仅在桌面版可用')
    }
  } catch (error) {
    console.error('Failed to export logs:', error)
  }
}

const clearLogs = async () => {
  try {
    await settingsApi.clearLogs()
    ElMessage.success('日志已清空')
    // 刷新日志显示
    if (logViewerRef.value) {
      await logViewerRef.value.refreshLogs?.()
    }
  } catch (error) {
    ElMessage.error('清空日志失败')
  }
}

onMounted(async () => {
  try {
    const savedSettings = await settingsApi.loadSettings()
    if (savedSettings) {
      Object.keys(savedSettings).forEach(k => {
        const key = k as keyof Settings
        if (typeof savedSettings[key] === 'object' && savedSettings[key] !== null && !Array.isArray(savedSettings[key])) {
          if (!settings.value[key]) (settings.value as any)[key] = {}
          settings.value[key] = { ...(settings.value[key] as any), ...(savedSettings[key] as any) }
        } else {
          (settings.value as any)[key] = savedSettings[key]
        }
      })
    }
    
    if (window.electronAPI?.getPath && !settings.value.dataPath) {
      const path = await window.electronAPI.getPath('userData')
      settings.value.dataPath = path
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
})
</script>

<style lang="scss" scoped>
.settings-view {
  max-width: 1000px;
  margin: 0 auto;
}

.settings-container {
  min-height: 600px;
  margin-bottom: 80px;
  
  :deep(.card-body) {
    padding: 0;
  }

  :deep(.settings-tabs) {
    .el-tabs__header {
      margin: 0;
      padding: 0 20px;
      background-color: var(--card-bg);
      border-bottom: 1px solid var(--border-color);
    }

    .el-tabs__nav-wrap {
      padding: 0;
    }

    .el-tabs__item {
      padding: 0 20px;
      height: 48px;
      line-height: 48px;
      font-size: 14px;
    }

    .el-tabs__content {
      padding: 0;
    }
  }
}

.about-section {
  text-align: center;
  padding: 60px 40px;

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
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
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
  padding: 12px 24px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-color);
}
</style>
