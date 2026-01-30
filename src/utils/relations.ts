/**
 * Relationship mapping utilities
 */

/**
 * Get Element Plus tag type for relationship type
 */
export const getRelationType = (type: string): 'success' | 'warning' | 'info' | 'primary' | 'danger' => {
  switch (type) {
    case 'family':
      return 'success'
    case 'friend':
      return 'primary'
    case 'enemy':
      return 'danger'
    case 'lover':
      return 'warning'
    case 'colleague':
      return 'info'
    default:
      return 'info'
  }
}

/**
 * Get display text for relationship type
 */
export const getRelationLabel = (type: string): string => {
  switch (type) {
    case 'family':
      return '家庭'
    case 'friend':
      return '朋友'
    case 'enemy':
      return '敌对'
    case 'lover':
      return '恋人'
    case 'colleague':
      return '同事'
    case 'other':
      return '其他'
    default:
      return type || '其他'
  }
}
