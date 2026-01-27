<template>
  <div class="character-detail-view">
    <div class="page-header">
      <el-button text @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <div class="detail-content">
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
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 模拟数据
const character = ref({
  id: '1',
  name: '贾宝玉',
  aliases: ['宝二爷', '怡红公子', '绛洞花主'],
  description: '贾府荣国公贾代善之孙、荣国府贾政之子。因衔玉而诞，系贾府玉字辈嫡孙。他是贾母的心尖宝贝，从小在女儿堆中长大，对女性有着独特的尊重和怜惜态度。',
  personality: '性格叛逆、多愁善感、温柔体贴。厌恶封建仕途，不喜读书应举。对待身边的女性充满关爱，认为"女儿是水做的骨肉，男人是泥做的骨肉"。',
  first_appearance: 1,
  importance_score: 1.0,
  appearance_count: 120,
  relationships: [
    {
      id: '1',
      target_name: '林黛玉',
      type: 'lover',
      type_label: '恋人',
      description: '青梅竹马、两情相悦，但最终未能在一起。'
    },
    {
      id: '2',
      target_name: '薛宝钗',
      type: 'spouse',
      type_label: '妻子',
      description: '金玉良缘，最终成婚，但宝玉心中始终念念不忘黛玉。'
    },
    {
      id: '3',
      target_name: '贾母',
      type: 'family',
      type_label: '祖母',
      description: '贾母最疼爱的孙子，从小娇生惯养。'
    },
    {
      id: '4',
      target_name: '袭人',
      type: 'servant',
      type_label: '贴身丫鬟',
      description: '怡红院首席大丫鬟，对宝玉照顾有加。'
    }
  ]
})

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

onMounted(() => {
  const id = route.params.id
  // 实际项目中从后端加载数据
  console.log('Loading character:', id)
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
