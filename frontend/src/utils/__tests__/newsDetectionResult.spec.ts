import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  normalizeAggregateNewsDetectionResult,
  normalizeConsistencyDetectionResult,
  normalizePercentage,
  normalizeSegmentDetectionResult,
} from '../newsDetectionResult'

describe('newsDetectionResult normalization', () => {
  it('normalizes aggregate raw result into AggregateDisplayResult', () => {
    const result = normalizeAggregateNewsDetectionResult({
      news_detection: {
        label: '可疑',
        confidence: 0.91,
        credibility_score: 0.32,
        summary: 'summary',
        conclusion: 'conclusion',
        dimensions: {
          source: 0.2,
          evidence: 65,
        },
      },
      ai_text_detection: {
        label: 'AI生成',
        confidence: 0.76,
        probability: 0.76,
        summary: 'ai summary',
        conclusion: 'ai conclusion',
      },
      overall_credibility: 0.28,
      overall_label: '高风险',
    })

    expect(result.resultKind).toBe('aggregate')
    expect(result.label).toBe('高风险')
    expect(result.overallCredibility).toBe(28)
    expect(result.newsCredibility).toBe(32)
    expect(result.aiProbability).toBe(76)
    expect(result.newsSummary).toBe('summary')
    expect(result.newsConclusion).toBe('conclusion')
    expect(result.aiSummary).toBe('ai summary')
    expect(result.aiConclusion).toBe('ai conclusion')
    expect(result.dimensionScores).toEqual({
      source: 20,
      evidence: 65,
    })
  })

  it('normalizes consistency raw result into ConsistencyDisplayResult', () => {
    const result = normalizeConsistencyDetectionResult({
      title: '新闻标题',
      content: '正文内容',
      url: 'https://example.com/news',
      title_txt_match: false,
      title_txt_similarity: 0.61,
      text_pic_similarity: 82,
      consistency_result: '不一致',
      details: {
        reason: '图片与正文不一致',
      },
    })

    expect(result.resultKind).toBe('consistency')
    expect(result.label).toBe('不一致')
    expect(result.title).toBe('新闻标题')
    expect(result.content).toBe('正文内容')
    expect(result.url).toBe('https://example.com/news')
    expect(result.titleTextMatch).toBe(false)
    expect(result.titleTextSimilarity).toBe(61)
    expect(result.textImageSimilarity).toBe(82)
    expect(result.details).toEqual({
      reason: '图片与正文不一致',
    })
  })

  it('normalizes segments raw result into SegmentsDisplayResult', () => {
    const result = normalizeSegmentDetectionResult({
      credibility_score: 0.66,
      credibility_level: '中',
      segment_count: 2,
      conclusion: '存在风险片段',
      feature_tags: {
        emotion: ['strong'],
      },
      segments: [
        {
          segment_id: 1,
          text: '第一段',
          label: '真实',
          real_probability: 0.91,
          fake_probability: 0.09,
        },
        {
          segment_id: 2,
          text: '第二段',
          label: '虚假',
          real_probability: 20,
          fake_probability: 80,
        },
      ],
    })

    expect(result.resultKind).toBe('segments')
    expect(result.label).toBe('中')
    expect(result.credibilityScore).toBe(66)
    expect(result.segmentCount).toBe(2)
    expect(result.conclusion).toBe('存在风险片段')
    expect(result.featureTags).toEqual({
      emotion: ['strong'],
    })
    expect(result.segments).toEqual([
      {
        segmentId: 1,
        text: '第一段',
        label: '真实',
        realProbability: 91,
        fakeProbability: 9,
      },
      {
        segmentId: 2,
        text: '第二段',
        label: '虚假',
        realProbability: 20,
        fakeProbability: 80,
      },
    ])
  })

  it('normalizes percentages and applies defaults for missing values', () => {
    expect(normalizePercentage(0.126)).toBe(12.6)
    expect(normalizePercentage(37)).toBe(37)
    expect(normalizePercentage(undefined)).toBe(0)
    expect(normalizePercentage(NaN)).toBe(0)
    expect(normalizePercentage(120)).toBe(100)

    const aggregate = normalizeAggregateNewsDetectionResult({})
    expect(aggregate.label).toBe('未知')
    expect(aggregate.overallCredibility).toBe(0)
    expect(aggregate.newsCredibility).toBe(0)
    expect(aggregate.aiProbability).toBe(0)
    expect(aggregate.dimensionScores).toEqual({})

    const consistency = normalizeConsistencyDetectionResult({})
    expect(consistency.label).toBe('未知')
    expect(consistency.title).toBe('')
    expect(consistency.content).toBe('')
    expect(consistency.url).toBe('')
    expect(consistency.titleTextMatch).toBe(false)
    expect(consistency.titleTextSimilarity).toBe(0)
    expect(consistency.textImageSimilarity).toBe(0)
    expect(consistency.details).toEqual({})

    const segments = normalizeSegmentDetectionResult({})
    expect(segments.label).toBe('未知')
    expect(segments.credibilityScore).toBe(0)
    expect(segments.segmentCount).toBe(0)
    expect(segments.conclusion).toBe('')
    expect(segments.featureTags).toEqual({})
    expect(segments.segments).toEqual([])
  })

  it('falls back safely when consistency match flag is missing', () => {
    const result = normalizeConsistencyDetectionResult({
      consistency_result: '未知',
    })

    expect(result.titleTextMatch).toBe(false)
  })

  it('falls back segment count to normalized segments length and uses index for missing segment ids', () => {
    const result = normalizeSegmentDetectionResult({
      credibility_level: '低',
      segments: [
        {
          text: '第一段',
          label: '真实',
          real_probability: 0.7,
          fake_probability: 0.3,
        },
        {
          segment_id: 5,
          text: '第二段',
          label: '虚假',
          real_probability: 0.2,
          fake_probability: 0.8,
        },
      ],
    })

    expect(result.segmentCount).toBe(2)
    expect(result.segments[0]).toMatchObject({
      segmentId: 0,
      text: '第一段',
    })
    expect(result.segments[1]).toMatchObject({
      segmentId: 5,
      text: '第二段',
    })
  })

  it('detectAggregate omits url from payload when not provided', () => {
    const apiSource = readFileSync(resolve(__dirname, '../../api/detection.ts'), 'utf8')

    expect(apiSource).not.toContain("detectAggregate(title: string, content: string, url = '')")
    expect(apiSource).toContain('async detectAggregate(title: string, content: string, url?: string)')
    expect(apiSource).toContain('...(url ? { url } : {})')
  })
})
