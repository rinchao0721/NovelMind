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
        prefix-icon="Search"
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
      <h3>暂无人物数据</h3>
      <p>请先选择小说并完成分析</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNovelStore } from '@/stores/novel'

const router = useRouter()
const novelStore = useNovelStore()

const novels = ref<any[]>([])
const selectedNovelId = ref('')
const searchQuery = ref('')
const sortBy = ref('importance')

// 模拟数据
const characters = ref([
  {
    id: '1',
    name: '贾宝玉',
    aliases: ['宝二爷', '怡红公子'],
    description: '贾府荣国公贾代善之孙，荣国府贾政之子，因衔玉而诞。',
    first_appearance: 1,
    importance_score: 1.0
  },
  {
    id: '2',
    name: '林黛玉',
    aliases: ['林妹妹', '潇湘妃子'],
    description: '林如海与贾敏之女，贾母的外孙女，宝玉的表妹。',
    first_appearance: 2,
    importance_score: 0.9
  },
  {
    id: '3',
    name: '薛宝钗',
    aliases: ['宝姐姐', '蘅芜君'],
    description: '薛姨妈之女，王夫人的外甥女，金陵十二钗之首。',
    first_appearance: 3,
    importance_score: 0.85
  },
  {
    id: '4',
    name: '王熙凤',
    aliases: ['凤姐', '凤辣子'],
    description: '贾琏之妻，王夫人的内侄女，贾府的实际管家人。',
    first_appearance: 2,
    importance_score: 0.8
  },
  {
    id: '5',
    name: '贾母',
    aliases: ['老太太', '史太君'],
    description: '贾府辈分最高的长辈，宝玉的祖母。',
    first_appearance: 2,
    importance_score: 0.75
  },
  {
    id: '6',
    name: '史湘云',
    aliases: ['云妹妹', '枕霞旧友'],
    description: '史家大小姐，贾母的侄孙女，性格豪爽开朗。',
    first_appearance: 5,
    importance_score: 0.6
  }
])

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

onMounted(async () => {
  novels.value = await novelStore.fetchNovels()
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
