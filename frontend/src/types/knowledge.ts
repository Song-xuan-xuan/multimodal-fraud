export type KnowledgeStatus = 'pending' | 'approved' | 'rejected'
export type KnowledgeType = 'case' | 'law' | 'guideline' | 'notice'

export interface KnowledgeItem {
  id: number
  item_id: string
  item_type: string
  title: string
  content: string
  conclusion: string
  fraud_type: string
  risk_level: string
  source: string
  tags: string[]
  target_groups: string[]
  signals: string[]
  advice: string[]
  status: KnowledgeStatus
  submitted_by: string
  reviewed_by: string
  reviewed_reason: string
  created_at: string
  updated_at: string
}

export interface KnowledgeItemListResponse {
  items: KnowledgeItem[]
  total: number
}

export interface KnowledgeItemCreatePayload {
  item_id: string
  item_type: KnowledgeType
  title: string
  content: string
  conclusion?: string
  fraud_type?: string
  risk_level?: string
  source?: string
  tags?: string[]
  target_groups?: string[]
  signals?: string[]
  advice?: string[]
}

export interface KnowledgeItemReviewPayload {
  status: 'approved' | 'rejected'
  reason?: string
}

export interface KnowledgeItemResponse extends KnowledgeItem {}

export interface KnowledgeRebuildResponse {
  message: string
  item_count: number
  storage_path: string
  status: string
}

export interface KnowledgeIndexStatus {
  ready: boolean
  data_path: string
  storage_path: string
  index_exists: boolean
}
