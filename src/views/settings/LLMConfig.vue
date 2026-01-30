<template>
  <div class="llm-settings-container">
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
      <div class="content-header" v-if="activeProviderConfig">
        <div class="provider-info">
          <ProviderAvatar 
            :provider-id="activeProviderId" 
            :name="activeProviderConfig.name"
            :size="28"
            style="margin-right: 12px"
          />
          <h3>{{ activeProviderConfig.name }}</h3>
        </div>
        <el-button 
          v-if="settings.defaultProvider !== activeProviderId"
          size="small" 
          @click="$emit('set-default', activeProviderId)"
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
            @click="handleTestConnection"
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
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { PROVIDERS, getProviderById } from '@/config/providers'
import ProviderAvatar from '@/components/ProviderAvatar.vue'
import type { Settings, ProviderConfig } from '@/types'

const props = defineProps<{
  settings: Settings
  providerStatus: Record<string, string>
  testingProvider: string
}>()

const emit = defineEmits<{
  (e: 'set-default', providerId: string): void
  (e: 'test-connection', providerId: string, config: ProviderConfig): void
}>()

const activeProviderId = ref('openai')
const activeProviderConfig = computed(() => getProviderById(activeProviderId.value))

const currentProviderSettings = computed(() => {
  const providerId = activeProviderId.value
  if (!providerId || !props.settings) return null
  
  // Dynamic access
  return props.settings[providerId] as ProviderConfig | undefined
})

const handleTestConnection = () => {
  if (currentProviderSettings.value) {
    emit('test-connection', activeProviderId.value, currentProviderSettings.value)
  }
}
</script>

<style lang="scss" scoped>
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
    background-color: var(--card-bg);

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
        background-color: var(--card-bg);
      }

      &.active {
        background-color: var(--el-color-primary-light-9);
        color: var(--el-color-primary);
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
</style>
