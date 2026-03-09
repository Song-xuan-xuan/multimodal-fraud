export interface HotspotProvinceItem {
  province: string
  total: number
  fake_count: number
  real_count: number
  unknown_count: number
  fake_ratio: number
}

export interface HotspotSummaryResponse {
  provinces: HotspotProvinceItem[]
  total_news: number
  total_fake: number
  updated_at: string
}

export interface HotspotTrendPoint {
  date: string
  fake: number
  real: number
  total: number
}

export interface HotspotTrendResponse {
  points: HotspotTrendPoint[]
}

export interface KnowledgeGraphNode {
  id: string
  name: string
  category: string
  value: number
}

export interface KnowledgeGraphEdge {
  source: string
  target: string
  relation_type: string
  weight: number
}

export interface KnowledgeGraphResponse {
  seed_news_id: string
  seed_title: string
  nodes: KnowledgeGraphNode[]
  edges: KnowledgeGraphEdge[]
}

export interface EvidenceBoardItem {
  id: number
  news_id: string
  title: string
  platform: string
  label: string
  submitted_at: string
  status: 'pending' | 'approved' | 'rejected'
  source: string
}

export interface EvidenceBoardListResponse {
  items: EvidenceBoardItem[]
  total: number
}

export interface EvidenceBoardStats {
  total: number
  pending: number
  approved: number
  rejected: number
}

export interface CrowdBoardProgressItem {
  news_id: string
  title: string
  platform: string
  label: string
  verification_progress: number
}

export interface CrowdBoardProgressResponse {
  items: CrowdBoardProgressItem[]
  total: number
  page: number
  page_size: number
}