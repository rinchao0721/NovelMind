<template>
  <div class="character-view">
    <div class="page-header">
      <h2>人物列表</h2>
      <p>查看小说中识别的所有人物及其详细信息</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="toolbar card">
      <el-input
        v-model="searchQuery"
        placeholder="搜索人物名称..."
        :prefix-icon="Search"
        clearable
        style="width: 300px"
      />

      <el-select v-model="selectedNovelId" placeholder="选择小说">
        <el-option
          v-for="novel in novels"
          :key="novel.id"
          :label="novel.title"
          :value="novel.id"
        />
      </el-select>

      <el-select v-model="sortBy" placeholder="排序方式">
        <el-option label="按重要性" value="importance" />
        <el-option label="按出场顺序" value="appearance" />
        <el-option label="按名称" value="name" />
      </el-select>
    </div>

    <!-- 人物列表 -->
    <div class="character-grid">
      <div 
        v-for="character in filteredCharacters" 
        :key="character.id"
        class="character-card card"
        @click="router.push(`/characters/${character.id}`)"
      >
        <div class="avatar">
          <el-icon><User /></el-icon>
        </div>
        <div class="info">
          <h4>{{ character.name }}</h4>
          <p class="aliases" v-if="character.aliases?.length">
            {{ character.aliases.join('、') }}
          </p>
          <p class="description">{{ character.description }}</p>
          <div class="meta">
            <el-tag size="small" type="info">
              第 {{ character.first_appearance }} 章出场
            </el-tag>
            <el-progress
              :percentage="character.importance_score * 100"
              :stroke-width="6"
              :show-text="false"
              style="width: 80px"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredCharacters.length === 0" class="empty-state">
      <el-icon><User /></el-icon>
      <template v-if="!selectedNovelId">
        <h3>请选择小说</h3>
        <p>选择上方小说以查看人物列表</p>
      </template>
      <template v-else-if="currentNovel && currentNovel.analysis_status !== 'completed'">
        <h3>尚未进行分析</h3>
        <p>该小说还未进行人物分析</p>
        <el-button type="primary" @click="goToAnalysis">前往分析</el-button>
      </template>
      <template v-else>
        <h3>暂无人物数据</h3>
        <p>分析完成，但未找到匹配的人物</p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useNovelStore } from '@/stores/novel'
import { User, Search } from '@element-plus/icons-vue' // Added Search icon

const router = useRouter()
const route = useRoute()
const novelStore = useNovelStore()

const { novels } = storeToRefs(novelStore)
const selectedNovelId = ref('')
const searchQuery = ref('')
const sortBy = ref('importance')

// 使用 store 中的数据
const characters = computed(() => novelStore.characters)
const currentNovel = computed(() => novelStore.currentNovel)

const filteredCharacters = computed(() => {
  let result = [...characters.value]

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(c => 
      c.name.toLowerCase().includes(query) ||
      c.aliases?.some((a: string) => a.toLowerCase().includes(query))
    )
  }

  // 排序
  switch (sortBy.value) {
    case 'importance':
      result.sort((a, b) => b.importance_score - a.importance_score)
      break
    case 'appearance':
      result.sort((a, b) => a.first_appearance - b.first_appearance)
      break
    case 'name':
      result.sort((a, b) => a.name.localeCompare(b.name, 'zh'))
      break
  }

  return result
})

// 监听小说选择变化
watch(selectedNovelId, async (newId) => {
  if (newId) {
    loadCharacterData(newId)
  }
})

const loadCharacterData = async (id: string) => {
    try {
        await novelStore.fetchNovel(id) // Sync status
        await novelStore.fetchCharacters(id) // Force fetch characters
    } catch (e) {
        console.error("Failed to load character data", e)
    }
}

const goToAnalysis = () => {
  router.push(`/analysis?id=${selectedNovelId.value}`)
}

onMounted(async () => {
  await novelStore.fetchNovels()
  
  const id = route.query.id as string
  if (id) {
    selectedNovelId.value = id
    // Explicitly load data on mount, don't rely solely on watch
    await loadCharacterData(id)
  }
})
</script>

<style lang="scss" scoped>
.character-view {
  max-width: 1200px;
  margin: 0 auto;
}

.toolbar {
  display: flex;
  gap: 16px;
  padding: 12px 16px !important;
  margin-bottom: 24px;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.character-card {
  display: flex;
  gap: 16px;
  cursor: pointer;
  transition: var(--transition);

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
  }

  .avatar {
    width: 64px;
    height: 64px;
    background: var(--hover-bg);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .el-icon {
      font-size: 32px;
      color: var(--text-color-placeholder);
    }
  }

  .info {
    flex: 1;
    min-width: 0;

    h4 {
      margin: 0 0 4px;
      font-size: 16px;
    }

    .aliases {
      font-size: 12px;
      color: var(--text-color-secondary);
      margin: 0 0 8px;
    }

    .description {
      font-size: 13px;
      color: var(--text-color-secondary);
      margin: 0 0 12px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .meta {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }
}
</style>
