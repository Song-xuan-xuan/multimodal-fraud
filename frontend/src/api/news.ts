import api from './index'

export interface NewsCredibilityDimensionScores {
  source: number
  content: number
  logic: number
  propagation: number
  AI: number
  content1: string
  content2: string
}

export interface NewsCredibilityInfo {
  score: number
  dimension_scores: NewsCredibilityDimensionScores
  verification_progress: number
  verified: boolean
}

export interface NewsItem {
  news_id: string
  title: string
  content: string
  label: string
  platform: string
  summary: string
  location: string
  conclusion: string
  publish_time: string
  check_time: string
  iscredit: boolean
  credibility: NewsCredibilityInfo
  propagation_data: Record<string, any>
  relations_data: Record<string, any>
}

export interface PropagationTrendPoint {
  timestamp: string
  value: number
}

export interface PropagationPlatformItem {
  platform: string
  count: number
  ratio: number
}

export interface PropagationRegionItem {
  region: string
  count: number
}

export interface NewsPropagationInfo {
  total_mentions: number
  peak_timestamp: string
  trend: PropagationTrendPoint[]
  platform_distribution: PropagationPlatformItem[]
  region_distribution: PropagationRegionItem[]
}

export interface RelatedNewsItem {
  news_id: string
  title: string
  similarity: number
  platform: string
  publish_time: string
  url: string
}

export interface RelationNode {
  node_id: string
  name: string
  category: string
  value: number
}

export interface RelationEdge {
  source: string
  target: string
  relation_type: string
  weight: number
}

export interface NewsRelationsInfo {
  related_news: RelatedNewsItem[]
  nodes: RelationNode[]
  edges: RelationEdge[]
}

export interface NewsDetailUIFallbacks {
  summary: string
  conclusion: string
  propagation_empty_reason: string
  relations_empty_reason: string
}

export interface NewsDetailResponse extends NewsItem {
  url: string
  pic_url: string
  hashtag: string
  propagation: NewsPropagationInfo
  relations: NewsRelationsInfo
  ui_fallbacks: NewsDetailUIFallbacks
}

export interface NewsListResult {
  items: NewsItem[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface NewsListParams {
  page?: number
  perPage?: number
  keyword?: string
  province?: string
  label?: string
  platform?: string
}

function normalizeListParams(pageOrParams: number | NewsListParams = {}, perPage?: number, keyword?: string): NewsListParams {
  if (typeof pageOrParams === 'number') {
    return {
      page: pageOrParams,
      perPage,
      keyword,
    }
  }
  return pageOrParams
}

export const newsApi = {
  async list(pageOrParams: number | NewsListParams = {}, perPage?: number, keyword?: string) {
    const params = normalizeListParams(pageOrParams, perPage, keyword)
    const query: Record<string, any> = {
      page: params.page ?? 1,
      per_page: params.perPage ?? 10,
    }
    if (params.keyword) query.keyword = params.keyword
    if (params.province) query.province = params.province
    if (params.label) query.label = params.label
    if (params.platform) query.platform = params.platform

    const endpoint = params.platform ? '/news/aggregate' : '/news/'
    const { data } = await api.get(endpoint, { params: query })
    return data as NewsListResult
  },
  async get(id: string) {
    const { data } = await api.get(`/news/${id}`)
    return data as NewsItem
  },
  async getDetail(id: string) {
    const { data } = await api.get(`/news/${id}/detail`)
    return data as NewsDetailResponse
  },
}
