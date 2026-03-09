import { describe, expect, it } from 'vitest'
import { normalizeDetectionResult } from '../detectionResult'

describe('detectionResult normalization', () => {
  it('prefers probability for AI text results and preserves text preview', () => {
    const result = normalizeDetectionResult({
      resultKind: 'text',
      rawResult: {
        label: 'AI生成',
        confidence: 0.31,
        probability: 0.84,
        summary: 'summary',
        conclusion: 'conclusion',
        details: {
          ai_probability: 0.84,
          human_probability: 0.16,
        },
      },
      textPreview: '待检测文本片段',
    })

    expect(result.aiProbability).toBe(84)
    expect(result.humanProbability).toBe(16)
    expect(result.confidenceRatio).toBe(84)
    expect(result.label).toBe('AI生成')
    expect(result.textPreview).toBe('待检测文本片段')
    expect(result.resultKind).toBe('text')
  })

  it('falls back to confidence for image results and keeps preview url', () => {
    const result = normalizeDetectionResult({
      resultKind: 'image',
      rawResult: {
        label: '人工创作',
        confidence: 0.22,
      },
      imagePreviewUrl: 'blob:test-preview',
    })

    expect(result.aiProbability).toBe(22)
    expect(result.humanProbability).toBe(78)
    expect(result.imagePreviewUrl).toBe('blob:test-preview')
    expect(result.resultKind).toBe('image')
  })
})
