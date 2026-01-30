/**
 * Status mapping utilities
 */

export type StatusTagType = 'success' | 'warning' | 'info' | 'primary' | 'danger'

/**
 * Get Element Plus tag type for analysis status
 */
export const getStatusType = (status: string | undefined): StatusTagType => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'analyzing':
      return 'primary'
    case 'failed':
      return 'danger'
    case 'pending':
      return 'warning'
    default:
      return 'info'
  }
}

/**
 * Get display text for analysis status
 */
export const getStatusText = (status: string | undefined): string => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'analyzing':
      return '分析中'
    case 'failed':
      return '失败'
    case 'pending':
      return '待处理'
    default:
      return '未开始'
  }
}
