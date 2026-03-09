export interface RawNewsDetectionResponse {
  label?: string
  confidence?: number
  credibility_score?: number
  dimensions?: Record<string, number>
  summary?: string
  conclusion?: string
}

export interface RawAggregateNewsDetectionResponse {
  news_detection?: RawNewsDetectionResponse
  ai_text_detection?: {
    label?: string
    confidence?: number
    probability?: number
    overall_label?: string
    summary?: string
    conclusion?: string
    details?: Record<string, unknown>
  }
  overall_credibility?: number
  overall_label?: string
}

export interface RawConsistencyDetectionResponse {
  title?: string
  content?: string
  url?: string
  title_txt_match?: boolean
  title_txt_similarity?: number
  text_pic_similarity?: number
  consistency_result?: string
  details?: Record<string, unknown>
}

export interface RawSegmentItem {
  segment_id?: number
  text?: string
  label?: string
  real_probability?: number
  fake_probability?: number
}

export interface RawSegmentsDetectionResponse {
  credibility_score?: number
  credibility_level?: string
  segment_count?: number
  conclusion?: string
  segments?: RawSegmentItem[]
  feature_tags?: Record<string, unknown>
}

export interface AggregateDisplayResult {
  resultKind: 'aggregate'
  label: string
  overallCredibility: number
  newsCredibility: number
  aiProbability: number
  newsSummary: string
  newsConclusion: string
  aiSummary: string
  aiConclusion: string
  dimensionScores: Record<string, number>
  rawResult: RawAggregateNewsDetectionResponse
}

export interface ConsistencyDisplayResult {
  resultKind: 'consistency'
  label: string
  title: string
  content: string
  url: string
  titleTextMatch: boolean
  titleTextSimilarity: number
  textImageSimilarity: number
  details: Record<string, unknown>
  rawResult: RawConsistencyDetectionResponse
}

export interface SegmentDisplayItem {
  segmentId: number
  text: string
  label: string
  realProbability: number
  fakeProbability: number
}

export interface SegmentsDisplayResult {
  resultKind: 'segments'
  label: string
  credibilityScore: number
  segmentCount: number
  conclusion: string
  featureTags: Record<string, unknown>
  segments: SegmentDisplayItem[]
  rawResult: RawSegmentsDetectionResponse
}
