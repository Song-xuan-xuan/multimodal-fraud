import type {
  AggregateDisplayResult,
  ConsistencyDisplayResult,
  RawAggregateNewsDetectionResponse,
  RawConsistencyDetectionResponse,
  RawSegmentsDetectionResponse,
  SegmentDisplayItem,
  SegmentsDisplayResult,
} from '@/types/newsDetection'

function clampPercentage(value: number) {
  return Math.min(100, Math.max(0, Math.round(value * 100) / 100))
}

export function normalizePercentage(value?: number) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 0
  if (value <= 1) return clampPercentage(value * 100)
  return clampPercentage(value)
}

function normalizeDimensionScores(dimensions?: Record<string, number>) {
  if (!dimensions) return {}

  return Object.fromEntries(
    Object.entries(dimensions).map(([key, value]) => [key, normalizePercentage(value)]),
  )
}

function resolveAIProbability(rawResult: RawAggregateNewsDetectionResponse) {
  const aiTextDetection = rawResult.ai_text_detection
  if (!aiTextDetection) return 0

  if (typeof aiTextDetection.probability === 'number') {
    return normalizePercentage(aiTextDetection.probability)
  }

  if (typeof aiTextDetection.confidence === 'number') {
    return normalizePercentage(aiTextDetection.confidence)
  }

  return 0
}

export function normalizeAggregateNewsDetectionResult(
  rawResult: RawAggregateNewsDetectionResponse,
): AggregateDisplayResult {
  const newsDetection = rawResult.news_detection
  const aiTextDetection = rawResult.ai_text_detection

  return {
    resultKind: 'aggregate',
    label: rawResult.overall_label || newsDetection?.label || '未知',
    overallCredibility: normalizePercentage(rawResult.overall_credibility),
    newsCredibility: normalizePercentage(newsDetection?.credibility_score),
    aiProbability: resolveAIProbability(rawResult),
    newsSummary: newsDetection?.summary || '',
    newsConclusion: newsDetection?.conclusion || '',
    aiSummary: aiTextDetection?.summary || '',
    aiConclusion: aiTextDetection?.conclusion || '',
    dimensionScores: normalizeDimensionScores(newsDetection?.dimensions),
    rawResult,
  }
}

export function normalizeConsistencyDetectionResult(
  rawResult: RawConsistencyDetectionResponse,
): ConsistencyDisplayResult {
  return {
    resultKind: 'consistency',
    label: rawResult.consistency_result || '未知',
    title: rawResult.title || '',
    content: rawResult.content || '',
    url: rawResult.url || '',
    titleTextMatch: rawResult.title_txt_match ?? false,
    titleTextSimilarity: normalizePercentage(rawResult.title_txt_similarity),
    textImageSimilarity: normalizePercentage(rawResult.text_pic_similarity),
    details: rawResult.details || {},
    rawResult,
  }
}

function normalizeSegmentItem(
  segment: NonNullable<RawSegmentsDetectionResponse['segments']>[number],
  index: number,
): SegmentDisplayItem {
  return {
    segmentId: segment.segment_id ?? index,
    text: segment.text || '',
    label: segment.label || '未知',
    realProbability: normalizePercentage(segment.real_probability),
    fakeProbability: normalizePercentage(segment.fake_probability),
  }
}

export function normalizeSegmentDetectionResult(
  rawResult: RawSegmentsDetectionResponse,
): SegmentsDisplayResult {
  const normalizedSegments = (rawResult.segments || []).map(normalizeSegmentItem)

  return {
    resultKind: 'segments',
    label: rawResult.credibility_level || '未知',
    credibilityScore: normalizePercentage(rawResult.credibility_score),
    segmentCount: rawResult.segment_count ?? normalizedSegments.length,
    conclusion: rawResult.conclusion || '',
    featureTags: rawResult.feature_tags || {},
    segments: normalizedSegments,
    rawResult,
  }
}
