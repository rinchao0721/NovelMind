<template>
  <div class="character-detail-view">
    <div class="page-header">
      <el-button text @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <div v-if="character" class="detail-content">
      <!-- 基本信息卡片 -->
      <div class="profile-card card">
        <div class="avatar">
          <el-icon><User /></el-icon>
        </div>
        <div class="profile-info">
          <h2>{{ character.name }}</h2>
          <p class="aliases">{{ character.aliases?.join('、') }}</p>
          <div class="importance">
            <span>重要性</span>
            <el-progress 
              :percentage="character.importance_score * 100" 
              :stroke-width="12"
              style="width: 200px"
            />
          </div>
        </div>
      </div>

      <div class="detail-grid">
        <!-- 人物描述 -->
        <div class="card">
          <h3>人物描述</h3>
          <p>{{ character.description }}</p>
        </div>

        <!-- 性格分析 -->
        <div class="card">
          <h3>性格分析</h3>
          <p>{{ character.personality }}</p>
        </div>

        <!-- 出场信息 -->
        <div class="card">
          <h3>出场信息</h3>
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
        </div>

        <!-- 人物关系 -->
        <div class="card relationships">
          <h3>人物关系</h3>
          <div class="relation-list">
            <div 
              v-for="rel in character.relationships" 
              :key="rel.id"
              class="relation-item"
              @click="navigateToCharacter(rel.target_id)"
            >
              <span class="name">{{ rel.target_name }}</span>
              <el-tag :type="getRelationType(rel.type)" size="small">
                {{ rel.type_label }}
              </el-tag>
              <p class="desc">{{ rel.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { charactersApi, relationshipsApi } from '@/api'

const router = useRouter()
const route = useRoute()

const character = ref<any>(null)
const loading = ref(true)

const getRelationType = (type: string): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
    lover: 'danger',
    spouse: 'warning',
    family: 'success',
    friend: 'primary',
    servant: 'info',
    enemy: 'info'
  }
  return map[type] || 'info'
}

const loadCharacter = async () => {
  const id = route.params.id as string
  if (!id) return

  loading.value = true
  try {
    // 获取人物基本信息
    const charData = await charactersApi.get(id)
    
    // 获取所有关系，筛选出与该人物相关的
    const allRelations = await relationshipsApi.list(charData.novel_id)
    const related = allRelations
      .filter((r: any) => r.source_id === id || r.target_id === id)
      .map((r: any) => {
        const isSource = r.source_id === id
        return {
          id: r.id,
          target_id: isSource ? r.target_id : r.source_id,
          target_name: isSource ? r.target_name : r.source_name,
          type: r.type,
          type_label: r.type, // 后端若未返回中文标签，可在此映射
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
  display: flex;
  gap: 24px;
  align-items: center;
  margin-bottom: 24px;

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

    .importance {
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

  .card {
    h3 {
      font-size: 16px;
      margin: 0 0 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border-color);
    }

    p {
      line-height: 1.8;
      color: var(--text-color);
      margin: 0;
    }
  }

  .relationships {
    grid-column: span 2;

    .relation-list {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
    }

    .relation-item {
      padding: 12px;
      background: var(--hover-bg);
      border-radius: var(--radius);
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background-color: var(--border-color);
      }

      .name {
        font-weight: 600;
        margin-right: 8px;
      }

      .desc {
        margin: 8px 0 0;
        font-size: 13px;
        color: var(--text-color-secondary);
      }
    }
  }
}
</style>
