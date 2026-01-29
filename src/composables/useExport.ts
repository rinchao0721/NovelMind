import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { exportApi } from '@/api'
import type { Novel } from '@/types'

export function useExport() {
  const exportDialogVisible = ref(false)
  const exportFormat = ref<'json' | 'markdown'>('json')
  const exporting = ref(false)

  const openExportDialog = () => {
    exportDialogVisible.value = true
  }

  const handleExportConfirm = async (novelId: string, currentNovel: Novel | null) => {
    if (!novelId) return

    exporting.value = true
    try {
      const format = exportFormat.value
      let data: Blob
      let extension: string

      if (format === 'json') {
        data = await exportApi.exportJson(novelId)
        extension = 'json'
      } else {
        data = await exportApi.exportMarkdown(novelId)
        extension = 'md'
      }

      // Create download link
      const url = window.URL.createObjectURL(data)
      const link = document.createElement('a')
      link.href = url
      link.download = `${currentNovel?.title || 'novel'}_analysis.${extension}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('导出成功')
      exportDialogVisible.value = false
    } catch (error) {
      console.error('Export failed:', error)
      ElMessage.error('导出失败')
    } finally {
      exporting.value = false
    }
  }

  return {
    exportDialogVisible,
    exportFormat,
    exporting,
    openExportDialog,
    handleExportConfirm
  }
}
