<template>
  <el-drawer
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="character?.name"
    direction="rtl"
    size="400px"
  >
    <template v-if="character">
      <div class="character-detail">
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="别名">
              {{ character.aliases?.join('、') || '无' }}
            </el-descriptions-item>
            <el-descriptions-item label="首次出现">
              第 {{ character.first_appearance }} 章
            </el-descriptions-item>
            <el-descriptions-item label="重要性">
              <el-progress 
                :percentage="Math.round(character.importance * 100)" 
                :stroke-width="12"
              />
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h4>人物描述</h4>
          <p>{{ character.description || '暂无描述' }}</p>
        </div>

        <div class="detail-section">
          <h4>性格特点</h4>
          <p>{{ character.personality || '暂无分析' }}</p>
        </div>

        <div class="detail-section">
          <h4>相关人物 ({{ relations.length }})</h4>
          <div class="related-characters">
            <div 
              v-for="rel in relations" 
              :key="rel.id"
              class="relation-item"
              @click="$emit('select-character', rel.targetId)"
            >
              <span class="name">{{ rel.targetName }}</span>
              <StatusTag :status="rel.type" />
            </div>
            <div v-if="relations.length === 0" class="no-relations">
              暂无关联人物
            </div>
          </div>
        </div>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import StatusTag from '@/components/common/StatusTag.vue'
import type { GraphNode, Relationship } from '@/types'

export interface DrawerCharacter extends GraphNode {
  aliases: string[]
  first_appearance: number
  description: string
  personality: string
}

export interface CharacterRelation {
  id: string
  targetId: string
  targetName: string
  type: Relationship['type']
}

defineProps<{
  visible: boolean
  character: DrawerCharacter | null
  relations: CharacterRelation[]
}>()

defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'select-character', id: string): void
}>()
</script>

<style lang="scss" scoped>
.character-detail {
  .detail-section {
    margin-bottom: 24px;

    h4 {
      font-size: 14px;
      color: var(--text-color-secondary);
      margin: 0 0 12px;
    }

    p {
      line-height: 1.8;
      color: var(--text-color);
    }
  }

  .related-characters {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .relation-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: var(--hover-bg);
      border-radius: var(--radius);
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background: var(--border-color);
      }

      .name {
        font-weight: 500;
      }
    }

    .no-relations {
      color: var(--text-color-placeholder);
      text-align: center;
      padding: 20px;
    }
  }
}
</style>
