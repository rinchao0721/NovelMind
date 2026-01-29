<template>
  <div class="home-view">
    <div class="page-header">
      <h2>欢迎使用 NovelMind</h2>
      <p>AI 驱动的小说剧情分析与人物关系可视化工具</p>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <div class="action-card" @click="handleImport">
        <el-icon class="action-icon"><Upload /></el-icon>
        <h3>导入小说</h3>
        <p>支持 TXT、DOCX、EPUB、MOBI 格式</p>
      </div>
      <div class="action-card" @click="router.push('/analysis')">
        <el-icon class="action-icon"><DataAnalysis /></el-icon>
        <h3>开始分析</h3>
        <p>AI 自动识别人物与关系</p>
      </div>
      <div class="action-card" @click="router.push('/graph')">
        <el-icon class="action-icon"><Share /></el-icon>
        <h3>查看图谱</h3>
        <p>交互式人物关系网络</p>
      </div>
    </div>

    <!-- 最近项目与文件管理 -->
    <div class="recent-section">
      <el-tabs v-model="activeTab" class="project-tabs">
        <!-- 标签页 1: 项目视图 (网格卡片) -->
        <el-tab-pane label="项目视图" name="grid">
          <div v-if="recentNovels.length === 0" class="empty-state">
            <el-icon><Document /></el-icon>
            <h3>暂无项目</h3>
            <p>导入一本小说开始分析吧</p>
            <el-button type="primary" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入小说
            </el-button>
          </div>

          <div v-else class="novel-grid">
            <div 
              v-for="novel in recentNovels" 
              :key="novel.id" 
              class="novel-card"
              @click="openNovel(novel.id)"
            >
              <div class="novel-cover">
                <el-icon><Notebook /></el-icon>
              </div>
              <div class="novel-info">
                <h4>{{ novel.title }}</h4>
                <p class="novel-meta">
                  <span>{{ novel.author || '未知作者' }}</span>
                  <span>{{ novel.total_chapters }} 章</span>
                </p>
                <el-tag 
                  :type="getStatusType(novel.analysis_status)" 
                  size="small"
                >
                  {{ getStatusText(novel.analysis_status) }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 标签页 2: 文件列表 (详细表格) -->
        <el-tab-pane label="文件列表" name="list">
          <el-table :data="recentNovels" style="width: 100%" stripe>
            <el-table-column prop="title" label="书名" min-width="180">
              <template #default="{ row }">
                <span class="novel-title-cell" @click="openNovel(row.id)">
                  <el-icon><Document /></el-icon>
                  {{ row.title }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="author" label="作者" width="120">
              <template #default="{ row }">
                {{ row.author || '未知' }}
              </template>
            </el-table-column>
            <el-table-column label="统计信息" width="180">
              <template #default="{ row }">
                <div class="stats-cell">
                  <span>{{ row.total_chapters }} 章</span>
                  <span class="divider">|</span>
                  <span>{{ formatNumber(row.total_words) }} 字</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.analysis_status)" size="small">
                  {{ getStatusText(row.analysis_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="导入时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="openNovel(row.id)">
                  分析
                </el-button>
                <el-button link type="primary" size="small" @click="router.push(`/graph?id=${row.id}`)">
                  图谱
                </el-button>
                <el-popconfirm 
                  title="确定删除这本书吗？" 
                  confirm-button-text="删除" 
                  cancel-button-text="取消"
                  @confirm="handleDelete(row.id)"
                >
                  <template #reference>
                    <el-button link type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- 标签栏右侧操作按钮 -->
      <div class="tabs-extra">
        <el-button type="primary" text @click="handleImport">
          <el-icon><Plus /></el-icon>
          导入新小说
        </el-button>
      </div>
    </div>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入小说"
      width="500px"
    >
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".txt,.docx,.epub,.mobi"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或 <em>点击选择</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 TXT、DOCX、EPUB、MOBI 格式，文件大小不超过 50MB
          </div>
        </template>
      </el-upload>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="importing"
          :disabled="!selectedFile"
          @click="confirmImport"
        >
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadInstance } from 'element-plus'
import { useNovelStore } from '@/stores/novel'

const router = useRouter()
const novelStore = useNovelStore()

const uploadRef = ref<UploadInstance>()
const { novels: recentNovels } = storeToRefs(novelStore)
const activeTab = ref('grid') // Default active tab
const importDialogVisible = ref(false)
const selectedFile = ref<File | null>(null)
const importing = ref(false)

const handleImport = () => {
  importDialogVisible.value = true
}

const handleDelete = async (id: string) => {
  try {
    await novelStore.deleteNovel(id)
    ElMessage.success('删除成功')
    await loadRecentNovels()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

const formatNumber = (num: number) => {
  return num ? num.toLocaleString() : '0'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file.raw || null
}

const confirmImport = async () => {
  if (!selectedFile.value) return

  importing.value = true
  try {
    await novelStore.importNovel(selectedFile.value)
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    selectedFile.value = null
    await loadRecentNovels()
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

const openNovel = (id: string) => {
  router.push(`/analysis?id=${id}`)
}

const getStatusType = (status: string): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  const map: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
    pending: 'info',
    analyzing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待分析',
    analyzing: '分析中',
    completed: '已完成',
    failed: '分析失败'
  }
  return map[status] || status
}

const loadRecentNovels = async () => {
  try {
    await novelStore.fetchNovels()
  } catch (error) {
    console.error('Failed to load novels:', error)
  }
}

onMounted(() => {
  loadRecentNovels()
})
</script>

<style lang="scss" scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.action-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: var(--transition);

  &:hover {
    border-color: var(--primary-color);
    box-shadow: var(--shadow);
    transform: translateY(-2px);
  }

  .action-icon {
    font-size: 48px;
    color: var(--primary-color);
    margin-bottom: 16px;
  }

  h3 {
    font-size: 18px;
    margin-bottom: 8px;
    color: var(--text-color);
  }

  p {
    color: var(--text-color-secondary);
    font-size: 13px;
  }
}

.recent-section {
  position: relative; // For tabs-extra positioning

  .project-tabs {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 16px;
    min-height: 400px; // Ensure height consistency

    :deep(.el-tabs__nav-wrap::after) {
      height: 1px;
      background-color: var(--border-color);
    }
    
    :deep(.el-tabs__header) {
      margin-bottom: 24px;
    }
  }

  .tabs-extra {
    position: absolute;
    top: 12px;
    right: 16px;
    z-index: 10;
  }
}

.novel-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--primary-color);
  font-weight: 500;
  
  &:hover {
    text-decoration: underline;
  }
}

.stats-cell {
  color: var(--text-color-secondary);
  font-size: 13px;
  
  .divider {
    margin: 0 6px;
    color: var(--border-color);
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--text-color-secondary);

  .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
    color: var(--text-color-placeholder);
  }

  h3 {
    font-size: 18px;
    color: var(--text-color);
    margin: 0 0 8px;
  }

  p {
    margin: 0 0 24px;
  }

  .el-button {
    .el-icon {
      font-size: 16px;
      margin-bottom: 0;
      margin-right: 6px;
      color: inherit;
      
      svg {
        width: 1em;
        height: 1em;
        vertical-align: middle;
      }
    }
  }
}

.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.novel-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  gap: 16px;
  cursor: pointer;
  transition: var(--transition);

  &:hover {
    border-color: var(--primary-color);
    box-shadow: var(--shadow);
  }

  .novel-cover {
    width: 60px;
    height: 80px;
    background: var(--hover-bg);
    border-radius: var(--radius);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .el-icon {
      font-size: 32px;
      color: var(--text-color-placeholder);
    }
  }

  .novel-info {
    flex: 1;
    min-width: 0;

    h4 {
      font-size: 16px;
      margin: 0 0 8px;
      color: var(--text-color);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .novel-meta {
      display: flex;
      gap: 12px;
      font-size: 12px;
      color: var(--text-color-secondary);
      margin-bottom: 8px;
    }
  }
}

.upload-area {
  width: 100%;

  :deep(.el-upload-dragger) {
    padding: 40px 20px;
  }
}
</style>
