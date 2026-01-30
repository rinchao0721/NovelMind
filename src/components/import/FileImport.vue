<template>
  <div class="file-import">
    <el-upload
      ref="uploadRef"
      class="upload-dragger"
      drag
      :auto-upload="false"
      :show-file-list="false"
      :on-change="handleFileChange"
      :accept="acceptFormats"
    >
      <div class="upload-content">
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          <p class="main-text">拖拽文件到此处，或 <em>点击选择</em></p>
          <p class="sub-text">支持 TXT、DOCX、EPUB、MOBI 格式</p>
        </div>
      </div>
    </el-upload>
    
    <div v-if="selectedFile" class="file-preview">
      <div class="file-info">
        <el-icon class="file-icon"><Document /></el-icon>
        <div class="file-details">
          <span class="file-name">{{ selectedFile.name }}</span>
          <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
        </div>
        <el-button type="danger" text @click="clearFile">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      
      <el-button 
        type="primary" 
        size="large"
        :loading="importing"
        @click="startImport"
        class="import-btn"
      >
        <el-icon><Upload /></el-icon>
        开始导入
      </el-button>
    </div>
    
    <div v-if="importing" class="import-progress">
      <el-progress 
        :percentage="progress" 
        :status="progress === 100 ? 'success' : ''"
      />
      <p class="progress-text">{{ progressText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { UploadFile } from 'element-plus'
import { formatFileSize } from '@/utils/format'
import type { Novel } from '@/types'

defineProps<{
  acceptFormats?: string
}>()

const emit = defineEmits<{
  (e: 'import', file: File): void
  (e: 'success', novel: Partial<Novel>): void
  (e: 'error', error: Error): void
}>()

const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const progress = ref(0)
const progressText = ref('')

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

const clearFile = () => {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

const startImport = async () => {
  if (!selectedFile.value) return
  
  importing.value = true
  progress.value = 0
  progressText.value = '正在读取文件...'
  
  try {
    emit('import', selectedFile.value)
    
    // Simulate progress
    const steps = [
      { p: 30, t: '正在解析内容...' },
      { p: 60, t: '正在识别章节...' },
      { p: 90, t: '正在保存数据...' },
      { p: 100, t: '导入完成!' }
    ]
    
    for (const step of steps) {
      await new Promise(r => setTimeout(r, 500))
      progress.value = step.p
      progressText.value = step.t
    }
    
    emit('success', { title: selectedFile.value.name })
    
  } catch (error: unknown) {
    emit('error', error instanceof Error ? error : new Error(String(error)))
  } finally {
    importing.value = false
    selectedFile.value = null
  }
}
</script>

<style lang="scss" scoped>
.file-import {
  .upload-dragger {
    width: 100%;
    
    :deep(.el-upload-dragger) {
      padding: 40px 20px;
      border-radius: var(--radius-lg);
      transition: var(--transition);
      
      &:hover {
        border-color: var(--primary-color);
      }
    }
  }
  
  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    
    .upload-icon {
      font-size: 48px;
      color: var(--primary-color);
    }
    
    .upload-text {
      text-align: center;
      
      .main-text {
        font-size: 16px;
        color: var(--text-color);
        margin: 0 0 8px;
        
        em {
          color: var(--primary-color);
          font-style: normal;
        }
      }
      
      .sub-text {
        font-size: 13px;
        color: var(--text-color-secondary);
        margin: 0;
      }
    }
  }
  
  .file-preview {
    margin-top: 20px;
    padding: 16px;
    background: var(--hover-bg);
    border-radius: var(--radius);
    
    .file-info {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      
      .file-icon {
        font-size: 32px;
        color: var(--primary-color);
      }
      
      .file-details {
        flex: 1;
        
        .file-name {
          display: block;
          font-weight: 500;
          margin-bottom: 4px;
        }
        
        .file-size {
          font-size: 12px;
          color: var(--text-color-secondary);
        }
      }
    }
    
    .import-btn {
      width: 100%;
    }
  }
  
  .import-progress {
    margin-top: 20px;
    
    .progress-text {
      text-align: center;
      margin-top: 8px;
      font-size: 13px;
      color: var(--text-color-secondary);
    }
  }
}
</style>
