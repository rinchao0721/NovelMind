<template>
  <div class="character-detail-view">
    <PageHeader show-back @back="router.back()" />

    <div v-if="character" class="detail-content">
      <!-- 基本信息卡片 -->
      <BaseCard class="profile-card">
        <div class="profile-layout">
          <div class="avatar">
            <el-icon><User /></el-icon>
          </div>
          <div class="profile-info">
            <h2>{{ character.name }}</h2>
            <p class="aliases">{{ character.aliases?.join('、') }}</p>
            <div class="importance-info">
              <span>重要性</span>
              <el-progress 
                :percentage="character.importance_score * 100" 
                :stroke-width="12"
                style="width: 200px"
              />
            </div>
          </div>
        </div>
      </BaseCard>

      <div class="detail-grid">
        <!-- 人物描述 -->
        <BaseCard title="人物描述">
          <p>{{ character.description }}</p>
        </BaseCard>

        <!-- 性格分析 -->
        <BaseCard title="性格分析">
          <p>{{ character.personality }}</p>
        </BaseCard>

        <!-- 出场信息 -->
        <BaseCard title="出场信息">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="首次出场">
              第 {{ character.first_appearance }} 章
            </el-descriptions-item>
            <el-descriptions-item label="出场次数">
              {{ character.appearance_count }} 次
            </el-descriptions-item>
            <el-descriptions-item label="主要章节">
              第1、3、5、8、12章
            </el-descriptions-item>
          </el-descriptions>
        </BaseCard>

        <!-- 人物关系 -->
        <BaseCard title="人物关系" class="relationships-card">
          <div class="relation-grid">
            <div 
              v-for="rel in character.relationships" 
              :key="rel.id"
              class="relation-block"
              @click="navigateToCharacter(rel.target_id)"
            >
              <div class="relation-header">
                <span class="name">{{ rel.target_name }}</span>
                <StatusTag :status="rel.type" />
              </div>
              <p class="relation-desc">{{ rel.description }}</p>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { charactersApi, relationshipsApi } from '@/api'
import { getRelationType, getRelationLabel } from '@/utils/relations'
import type { Character, Relationship } from '@/types'
// 导入公共资源
import BaseCard from '@/components/common/BaseCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusTag from '@/components/common/StatusTag.vue'

const router = useRouter()
const route = useRoute()

// Extended character type for view
interface CharacterWithRelations extends Character {
  appearance_count: number
  relationships: Array<{
    id: string
    target_id: string
    target_name: string
    type: Relationship['type']
    description: string | null
  }>
}

const character = ref<CharacterWithRelations | null>(null)
const loading = ref(true)

const loadCharacter = async () => {
  const id = route.params.id as string
  if (!id) return

  loading.value = true
  try {
    // 获取人物基本信息
    const charData = await charactersApi.get(id)
    
    // 获取所有关系，筛选出与该人物相关的
    const allRelations: Relationship[] = await relationshipsApi.list(charData.novel_id)
    const related = allRelations
      .filter((r: Relationship) => r.source_id === id || r.target_id === id)
      .map((r: Relationship) => {
        const isSource = r.source_id === id
        return {
          id: r.id,
          target_id: isSource ? r.target_id : r.source_id,
          target_name: isSource ? r.target_name : r.source_name,
          type: r.type,
          description: r.description
        }
      })

    character.value = {
      ...charData,
      appearance_count: 0, // 暂无数据
      relationships: related
    }
  } catch (error) {
    console.error('Failed to load character:', error)
  } finally {
    loading.value = false
  }
}

const navigateToCharacter = (id: string) => {
  if (id) {
    router.push(`/characters/${id}`)
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    loadCharacter()
  }
})

onMounted(() => {
  loadCharacter()
})
</script>

<style lang="scss" scoped>
.character-detail-view {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 24px;
  
  .profile-layout {
    display: flex;
    gap: 24px;
    align-items: center;
  }

  .avatar {
    width: 100px;
    height: 100px;
    background: var(--hover-bg);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;

    .el-icon {
      font-size: 48px;
      color: var(--text-color-placeholder);
    }
  }

  .profile-info {
    h2 {
      margin: 0 0 8px;
      font-size: 28px;
    }

    .aliases {
      color: var(--text-color-secondary);
      margin: 0 0 16px;
    }

    .importance-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      span {
        font-size: 13px;
        color: var(--text-color-secondary);
      }
    }
  }
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;

  p {
    line-height: 1.8;
    color: var(--text-color);
    margin: 0;
  }

  .relationships-card {
    grid-column: span 2;

    .relation-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
    }

    .relation-block {
      padding: 12px;
      background: var(--hover-bg);
      border-radius: var(--radius);
      cursor: pointer;
      transition: var(--transition);

      &:hover {
        background-color: var(--border-color);
        transform: translateX(4px);
      }

      .relation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .name {
          font-weight: 600;
        }
      }

      .relation-desc {
        font-size: 13px;
        color: var(--text-color-secondary);
      }
    }
  }
}
</style>
