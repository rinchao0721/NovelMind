// 小说类型
export interface Novel {
  id: string
  title: string
  author: string | null
  file_path: string | null
  created_at: string
  updated_at: string
  analysis_status: 'pending' | 'analyzing' | 'completed' | 'failed'
  total_chapters: number
  total_words: number
}

// 章节类型
export interface Chapter {
  id: string
  novel_id: string
  chapter_num: number
  title: string | null
  content: string
  word_count: number
  summary: string | null
}

// 人物类型
export interface Character {
  id: string
  novel_id: string
  name: string
  aliases: string[]
  description: string | null
  personality: string | null
  first_appearance: number
  importance_score: number
}

// 关系类型
export interface Relationship {
  id: string
  source_id: string
  target_id: string
  source_name: string
  target_name: string
  type: 'family' | 'friend' | 'enemy' | 'lover' | 'colleague' | 'other'
  subtype: string | null
  strength: number
  first_chapter: number
  description: string | null
}

// 分析任务类型
export interface AnalysisTask {
  id: string
  novel_id: string
  status: 'pending' | 'analyzing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  started_at: string | null
  completed_at: string | null
  error_message: string | null
}

// 分析结果类型
export interface AnalysisResult {
  task_id: string
  novel_id: string
  character_count: number
  relationship_count: number
  plot_count: number
  chapter_count: number
  characters: Character[]
  relationships: Relationship[]
}

// 图谱节点类型
export interface GraphNode {
  id: string
  name: string
  importance: number
  category: number
}

// 图谱边类型
export interface GraphLink {
  source: string
  target: string
  type: string
  value: number
}

// 图谱数据类型
export interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
}

// API 响应类型
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}
