<template>
  <div class="provider-avatar" :style="avatarStyle">
    <img 
      v-if="!imageError && logoSrc" 
      :src="logoSrc" 
      :alt="name"
      @error="handleImageError"
      class="provider-logo"
    />
    <span v-else class="provider-fallback">{{ fallbackText }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { PROVIDER_LOGO_MAP } from '@/config/providers'

interface Props {
  /** Provider ID */
  providerId: string
  /** Provider 名称 (用于生成首字母) */
  name?: string
  /** 尺寸 (px) */
  size?: number
  /** 是否使用圆形 */
  round?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  name: '',
  size: 24,
  round: false,
})

const imageError = ref(false)

const logoSrc = computed(() => {
  return PROVIDER_LOGO_MAP[props.providerId] || ''
})

const fallbackText = computed(() => {
  // 仅使用首字母作为备用，不使用 Emoji
  if (props.name) {
    return props.name.charAt(0).toUpperCase()
  }
  return props.providerId.charAt(0).toUpperCase()
})

const avatarStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  borderRadius: props.round ? '50%' : '4px',
  fontSize: `${props.size * 0.6}px`,
}))

const handleImageError = () => {
  imageError.value = true
}
</script>

<style lang="scss" scoped>
.provider-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  background-color: var(--bg-color-secondary, #f5f5f5);
  
  .provider-logo {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  .provider-fallback {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    font-weight: 500;
    color: var(--text-color-primary, #333);
  }
}
</style>
