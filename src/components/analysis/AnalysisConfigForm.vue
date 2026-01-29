<template>
  <div class="analysis-config card">
    <h3>分析配置</h3>
    <el-form label-width="120px">
      <el-form-item label="分析范围">
        <el-radio-group v-model="config.scope">
          <el-radio value="full">全书分析</el-radio>
          <el-radio value="partial">部分章节</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item v-if="config.scope === 'partial'" label="章节范围">
        <el-slider
          v-model="config.chapterRange"
          range
          :min="1"
          :max="totalChapters || 100"
          :marks="chapterMarks"
        />
      </el-form-item>

      <el-form-item label="分析模型">
        <div class="model-selection">
          <el-select v-model="config.provider" placeholder="选择服务商" style="width: 150px">
            <el-option
              v-for="provider in PROVIDERS"
              :key="provider.id"
              :label="provider.name"
              :value="provider.id"
            >
              <div class="provider-option">
                <ProviderAvatar :provider-id="provider.id" :size="20" style="margin-right: 8px" />
                <span>{{ provider.name }}</span>
              </div>
            </el-option>
            <template #prefix v-if="config.provider">
              <ProviderAvatar :provider-id="config.provider" :size="20" />
            </template>
          </el-select>
          <el-select 
            v-model="config.model" 
            placeholder="选择或输入模型" 
            allow-create 
            filterable 
            default-first-option
            style="flex: 1"
          >
            <el-option
              v-for="model in computedAvailableModels"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </div>
      </el-form-item>

      <el-form-item label="分析深度">
        <el-select v-model="config.depth" style="width: 200px">
          <el-option label="快速分析 (节省API调用)" value="quick" />
          <el-option label="标准分析 (推荐)" value="standard" />
          <el-option label="深度分析 (更精准)" value="deep" />
        </el-select>
      </el-form-item>

      <el-form-item label="分析项目">
        <el-checkbox-group v-model="config.features">
          <el-checkbox value="characters">人物识别</el-checkbox>
          <el-checkbox value="relationships">关系分析</el-checkbox>
          <el-checkbox value="plot">情节追踪</el-checkbox>
          <el-checkbox value="summary">章节摘要</el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item>
        <el-button 
          type="primary" 
          size="large"
          :loading="analyzing"
          :disabled="disabled || analyzing"
          @click="$emit('start', config)"
        >
          <el-icon><VideoPlay /></el-icon>
          {{ analyzing ? '分析中...' : '开始分析' }}
        </el-button>
        <el-button 
          v-if="analyzing"
          size="large"
          @click="$emit('cancel')"
        >
          取消分析
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { VideoPlay } from '@element-plus/icons-vue'
import { PROVIDERS } from '@/config/providers'
import { settingsApi } from '@/api'
import ProviderAvatar from '@/components/ProviderAvatar.vue'

const props = defineProps({
  analyzing: Boolean,
  disabled: Boolean,
  totalChapters: {
    type: Number,
    default: 100
  }
})

defineEmits(['start', 'cancel'])

const config = ref({
  scope: 'full',
  chapterRange: [1, 100],
  depth: 'standard',
  features: ['characters', 'relationships', 'plot', 'summary'],
  provider: '',
  model: ''
})

// Update config when totalChapters changes (for full range default)
watch(() => props.totalChapters, (newVal) => {
  if (config.value.scope === 'full') {
    config.value.chapterRange = [1, newVal]
  }
})

const computedAvailableModels = computed(() => {
  const provider = PROVIDERS.find(p => p.id === config.value.provider)
  return provider ? provider.defaultModels : []
})

const chapterMarks = computed(() => {
  const max = props.totalChapters || 100
  return {
    1: '第1章',
    [max]: `第${max}章`
  }
})

// Watch provider change to set default model
watch(() => config.value.provider, (newVal) => {
  const provider = PROVIDERS.find(p => p.id === newVal)
  if (provider && provider.defaultModels.length > 0) {
    if (provider.id === 'custom') {
       // Custom provider might not have default models listed
    } else if (!config.value.model || !provider.defaultModels.includes(config.value.model)) {
      config.value.model = provider.defaultModels[0]
    }
  }
})

// Load defaults
onMounted(async () => {
  try {
    const settings = await settingsApi.loadSettings()
    if (settings.defaultProvider) {
      config.value.provider = settings.defaultProvider
      if (settings[settings.defaultProvider]?.model) {
        config.value.model = settings[settings.defaultProvider].model
      }
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
})
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
.model-selection {
  display: flex;
  gap: 12px;
  width: 100%;
}
.provider-option {
  display: flex;
  align-items: center;
}
</style>
