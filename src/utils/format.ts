/**
 * Formatting utilities
 */

/**
 * Format number with thousand separators
 */
export const formatNumber = (num: number | undefined): string => {
  if (num === undefined) return '0'
  return num.toLocaleString()
}

/**
 * Format date string to local format
 */
export const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    return dateStr || '-'
  }
}

/**
 * Format file size in bytes to human readable string
 */
export const formatFileSize = (bytes: number | undefined): string => {
  if (bytes === undefined || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
