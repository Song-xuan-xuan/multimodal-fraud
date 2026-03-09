import type {
  NewsDetailResponse,
  NewsCredibilityDimensionScores,
  NewsCredibilityInfo,
  PropagationPlatformItem,
  PropagationRegionItem,
  PropagationTrendPoint,
  RelatedNewsItem,
  RelationNode,
  RelationEdge,
} from '@/api/news'

export type NewsDetailModuleKey =
  | 'baseInfo'
  | 'credibility'
  | 'propagationTrend'
  | 'propagationPlatforms'
  | 'propagationRegions'
  | 'relationsRelatedNews'
  | 'relationsKnowledgeNodes'
  | 'relationsEdges'

export type NewsDetailModuleVisibility = Record<NewsDetailModuleKey, boolean>

export interface NewsDetailAnchorItem {
  key: NewsDetailModuleKey
  target: string
  label: string
}

export interface NewsDetailBaseInfoVM {
  newsId: string
  title: string
  content: string
  summary: string
  conclusion: string
  label: string
  platform: string
  location: string
  publishTime: string
  checkTime: string
  hashtag: string
  url: string
  picUrl: string
  isCredit: boolean
}

export interface NewsDetailCredibilityVM {
  score: number
  scorePercentText: string
  verificationProgress: number
  verified: boolean
  dimensions: NewsCredibilityDimensionScores
}

export interface NewsDetailPropagationVM {
  totalMentions: number
  peakTimestamp: string
  trend: PropagationTrendPoint[]
  platformDistribution: PropagationPlatformItem[]
  regionDistribution: PropagationRegionItem[]
  emptyReason: string
}

export interface NewsDetailRelationsVM {
  relatedNews: RelatedNewsItem[]
  knowledgeNodes: RelationNode[]
  edges: RelationEdge[]
  emptyReason: string
}

export interface NewsDetailVM {
  baseInfo: NewsDetailBaseInfoVM
  credibility: NewsDetailCredibilityVM
  propagation: NewsDetailPropagationVM
  relations: NewsDetailRelationsVM
  raw: NewsDetailResponse
}

export interface UseNewsDetailPageState {
  detail: NewsDetailVM | null
  raw: NewsDetailResponse | null
  moduleVisibility: NewsDetailModuleVisibility
  anchors: NewsDetailAnchorItem[]
  loading: boolean
  errorMessage: string
}

export interface NewsDetailNormalizerInput extends NewsDetailResponse {
  credibility: NewsCredibilityInfo
}
