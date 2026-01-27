<template>
  <div class="character-card" @click="$emit('click')">
    <div class="avatar" :style="{ backgroundColor: avatarColor }">
      <span>{{ initials }}</span>
    </div>
    <div class="info">
      <h4 class="name">{{ character.name }}</h4>
      <p class="aliases" v-if="character.aliases?.length">
        {{ character.aliases.slice(0, 2).join('、') }}
        <span v-if="character.aliases.length > 2">等</span>
      </p>
      <div class="importance-bar">
        <div 
          class="importance-fill" 
          :style="{ width: `${character.importance_score * 100}%` }"
        ></div>
      </div>
    </div>
    <el-tag 
      v-if="showTag" 
      :type="tagType" 
      size="small"
      class="role-tag"
    >
      {{ roleLabel }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Character } from '@/types'

const props = withDefaults(defineProps<{
  character: Character
  showTag?: boolean
}>(), {
  showTag: true
})

defineEmits<{
  (e: 'click'): void
}>()

const initials = computed(() => {
  const name = props.character.name
  // For Chinese names, take first 1-2 characters
  if (/[\u4e00-\u9fff]/.test(name)) {
    return name.slice(0, name.length > 2 ? 2 : 1)
  }
  // For English names, take initials
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
})

const avatarColor = computed(() => {
  // Generate color based on name hash
  const hash = props.character.name.split('').reduce((a, c) => a + c.charCodeAt(0), 0)
  const colors = [
    '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', 
    '#909399', '#00D1B2', '#7957D5', '#3273DC'
  ]
  return colors[hash % colors.length]
})

const roleLabel = computed(() => {
  const score = props.character.importance_score
  if (score >= 0.8) return '主角'
  if (score >= 0.6) return '重要'
  if (score >= 0.4) return '配角'
  return '路人'
})

const tagType = computed(() => {
  const score = props.character.importance_score
  if (score >= 0.8) return 'danger'
  if (score >= 0.6) return 'warning'
  if (score >= 0.4) return 'success'
  return 'info'
})
</script>

<style lang="scss" scoped>
.character-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  
  &:hover {
    border-color: var(--primary-color);
    box-shadow: var(--shadow);
  }
  
  .avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    
    span {
      color: #fff;
      font-weight: 600;
      font-size: 16px;
    }
  }
  
  .info {
    flex: 1;
    min-width: 0;
    
    .name {
      margin: 0 0 4px;
      font-size: 14px;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .aliases {
      margin: 0 0 6px;
      font-size: 12px;
      color: var(--text-color-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .importance-bar {
      height: 4px;
      background: var(--border-color);
      border-radius: 2px;
      overflow: hidden;
      
      .importance-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--success-color));
        border-radius: 2px;
        transition: width 0.3s ease;
      }
    }
  }
  
  .role-tag {
    flex-shrink: 0;
  }
}
</style>
