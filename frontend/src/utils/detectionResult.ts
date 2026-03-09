import type {
  DetectionDisplayResult,
  NormalizeDetectionResultOptions,
  RawAIAudioDetectionResponse,
  RawAIImageDetectionResponse,
  RawAITextDetectionResponse,
} from '@/types/detection'

function clampPercentage(value: number) {
  return Math.min(100, Math.max(0, Math.round(value * 100) / 100))
}

function toRatio(value?: number) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 0
  if (value <= 1) return clampPercentage(value * 100)
  return clampPercentage(value)
}

function resolveLabel(rawResult: RawAITextDetectionResponse | RawAIImageDetectionResponse | RawAIAudioDetectionResponse) {
  return rawResult.label || rawResult.overall_label || '未知'
}

function resolveAIProbability(rawResult: RawAITextDetectionResponse | RawAIImageDetectionResponse | RawAIAudioDetectionResponse) {
  const details = rawResult.details
  if (details && typeof details.ai_probability === 'number') {
    return toRatio(details.ai_probability)
  }

  if (typeof rawResult.probability === 'number') {
    return toRatio(rawResult.probability)
  }

  return toRatio(rawResult.confidence)
}

function resolveConclusion(rawResult: RawAITextDetectionResponse | RawAIImageDetectionResponse | RawAIAudioDetectionResponse, aiProbability: number) {
  if (rawResult.conclusion) return rawResult.conclusion
  return aiProbability >= 50 ? '内容呈现较高风险表达特征，建议立即复核。' : '内容整体风险较低，但仍建议结合场景继续判断。'
}

function resolveSummary(rawResult: RawAITextDetectionResponse | RawAIImageDetectionResponse | RawAIAudioDetectionResponse, aiProbability: number, humanProbability: number) {
  if (rawResult.summary) return rawResult.summary
  return `高风险表达概率 ${aiProbability}%，低风险表达概率 ${humanProbability}%。`
}

export function normalizeDetectionResult({
  resultKind,
  rawResult,
  textPreview = '',
  imagePreviewUrl = '',
}: NormalizeDetectionResultOptions): DetectionDisplayResult {
  const aiProbability = resolveAIProbability(rawResult)
  const humanProbability = clampPercentage(100 - aiProbability)

  return {
    resultKind,
    label: resolveLabel(rawResult),
    confidenceRatio: aiProbability,
    aiProbability,
    humanProbability,
    conclusion: resolveConclusion(rawResult, aiProbability),
    summary: resolveSummary(rawResult, aiProbability, humanProbability),
    textPreview,
    imagePreviewUrl,
    rawResult,
  }
}
