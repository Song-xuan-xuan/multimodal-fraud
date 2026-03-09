export interface RawAITextDetectionResponse {
  is_ai_generated?: boolean
  confidence?: number
  probability?: number
  label?: string
  overall_label?: string
  summary?: string
  conclusion?: string
  details?: Record<string, unknown>
}

export interface RawAIImageDetectionResponse {
  is_ai_generated?: boolean
  confidence?: number
  probability?: number
  label?: string
  overall_label?: string
  summary?: string
  conclusion?: string
  details?: Record<string, unknown>
}

export interface RawAIAudioDetectionResponse extends RawAITextDetectionResponse {
  transcript?: string
}

export interface DetectionDisplayResult {
  resultKind: 'text' | 'image' | 'audio'
  label: string
  confidenceRatio: number
  aiProbability: number
  humanProbability: number
  conclusion: string
  summary: string
  textPreview: string
  imagePreviewUrl: string
  rawResult: RawAITextDetectionResponse | RawAIImageDetectionResponse | RawAIAudioDetectionResponse
}

export interface NormalizeDetectionResultOptions {
  resultKind: 'text' | 'image' | 'audio'
  rawResult: RawAITextDetectionResponse | RawAIImageDetectionResponse | RawAIAudioDetectionResponse
  textPreview?: string
  imagePreviewUrl?: string
}
