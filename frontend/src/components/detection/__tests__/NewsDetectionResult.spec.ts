import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const componentPath = path.resolve(__dirname, '../NewsDetectionResult.vue')
const source = fs.readFileSync(componentPath, 'utf-8')

describe('NewsDetectionResult multi-mode regression', () => {
  it('keeps aggregate, consistency, and segments rendering branches', () => {
    expect(source).toContain("result.resultKind === 'aggregate'")
    expect(source).toContain("result.resultKind === 'consistency'")
    expect(source).toContain("result.resultKind === 'segments'")
  })

  it('renders key metrics and cards for all news detection modes', () => {
    expect(source).toContain('overallCredibility')
    expect(source).toContain('titleTextSimilarity')
    expect(source).toContain('segmentCount')
    expect(source).toContain('news-detection-result__metric-card')
    expect(source).toContain('news-detection-result__segment-card')
  })
})

describe('NewsDetectionResult hero / status / progress contract', () => {
  it('has a hero block with hero-value for the primary score', () => {
    expect(source).toContain('news-detection-result__hero')
    expect(source).toContain('news-detection-result__hero-value')
  })

  it('has a status pill for label display', () => {
    expect(source).toContain('news-detection-result__status-pill')
  })

  it('has a progress track with an inner progress bar', () => {
    expect(source).toContain('news-detection-result__progress-track')
    expect(source).toContain('news-detection-result__progress-bar')
  })
})

describe('NewsDetectionResult segment risk bar contract', () => {
  it('has segment-bar with fill and risk label for each segment', () => {
    expect(source).toContain('news-detection-result__segment-bar')
    expect(source).toContain('news-detection-result__segment-bar-fill')
    expect(source).toContain('news-detection-result__segment-risk')
  })

  it('displays realProbability inside each segment card', () => {
    expect(source).toContain('realProbability')
  })
})

describe('NewsDetectionResult segment-overview structure contract', () => {
  it('wraps the overview in a dedicated segment-overview element', () => {
    expect(source).toContain('news-detection-result__segment-overview')
  })

  it('segment-overview contains credibilityScore, label, segmentCount, and conclusion', () => {
    // Extract the segment-overview block to verify all four fields are inside it
    const overviewStart = source.indexOf('segment-overview')
    expect(overviewStart).toBeGreaterThan(-1)
    const overviewBlock = source.slice(overviewStart, overviewStart + 2000)
    expect(overviewBlock).toContain('credibilityScore')
    expect(overviewBlock).toContain('result.label')
    expect(overviewBlock).toContain('segmentCount')
    expect(overviewBlock).toContain('result.conclusion')
  })

  it('segment-overview has hero-summary describing segment risk', () => {
    const overviewStart = source.indexOf('segment-overview')
    const overviewBlock = source.slice(overviewStart, overviewStart + 1500)
    expect(overviewBlock).toContain('news-detection-result__hero-summary')
  })
})

describe('NewsDetectionResult segment SCSS contract', () => {
  it('has SCSS rules for segment-bar with height and background', () => {
    expect(source).toMatch(/\.news-detection-result__segment-bar\s*\{[^}]*height/s)
    expect(source).toMatch(/\.news-detection-result__segment-bar\s*\{[^}]*background/s)
  })

  it('has SCSS rules for segment-bar-fill with height and transition', () => {
    expect(source).toMatch(/\.news-detection-result__segment-bar-fill\s*\{[^}]*height/s)
    expect(source).toMatch(/\.news-detection-result__segment-bar-fill\s*\{[^}]*background/s)
  })

  it('has SCSS rules for segment-risk with color', () => {
    expect(source).toMatch(/\.news-detection-result__segment-risk\s*\{[^}]*color/s)
  })

  it('has SCSS rules for segment-overview with border and background', () => {
    expect(source).toMatch(/\.news-detection-result__segment-overview\s*\{[^}]*border/s)
    expect(source).toMatch(/\.news-detection-result__segment-overview\s*\{[^}]*background/s)
  })
})

describe('NewsDetectionResult key copy text', () => {
  it('contains aggregate-branch copy', () => {
    expect(source).toContain('总体可信度')
    expect(source).toContain('AI 文本概率')
  })

  it('contains consistency-branch copy', () => {
    expect(source).toContain('一致性状态')
    expect(source).toContain('标题-正文相似度')
  })

  it('contains segments-branch copy', () => {
    expect(source).toContain('段落风险概览')
    expect(source).toContain('虚假概率')
  })
})

describe('NewsDetectionResult aggregate hero + analysis-grid contract', () => {
  it('has hero-label and hero-summary in the aggregate branch', () => {
    expect(source).toContain('news-detection-result__hero-label')
    expect(source).toContain('news-detection-result__hero-summary')
  })

  it('has an analysis-grid with analysis-card entries', () => {
    expect(source).toContain('news-detection-result__analysis-grid')
    expect(source).toContain('news-detection-result__analysis-card')
  })

  it('contains analysis card titles for news and AI', () => {
    expect(source).toContain('新闻分析')
    expect(source).toContain('AI 分析')
  })
})

describe('NewsDetectionResult hero / status / progress SCSS contract', () => {
  it('has SCSS rule for hero with display or padding', () => {
    expect(source).toMatch(/\.news-detection-result__hero\s*\{[^}]*display/s)
  })

  it('has SCSS rule for hero-value with color and font-size', () => {
    expect(source).toMatch(/\.news-detection-result__hero-value\s*\{[^}]*color/s)
    expect(source).toMatch(/\.news-detection-result__hero-value\s*\{[^}]*font-size/s)
  })

  it('has SCSS rule for status-pill with padding and border-radius', () => {
    expect(source).toMatch(/\.news-detection-result__status-pill\s*\{[^}]*padding/s)
    expect(source).toMatch(/\.news-detection-result__status-pill\s*\{[^}]*border-radius/s)
  })

  it('has SCSS rule for progress-track with height, background, and overflow', () => {
    expect(source).toMatch(/\.news-detection-result__progress-track\s*\{[^}]*height/s)
    expect(source).toMatch(/\.news-detection-result__progress-track\s*\{[^}]*background/s)
    expect(source).toMatch(/\.news-detection-result__progress-track\s*\{[^}]*overflow/s)
  })

  it('has SCSS rule for progress-bar with height and background', () => {
    expect(source).toMatch(/\.news-detection-result__progress-bar\s*\{[^}]*height/s)
    expect(source).toMatch(/\.news-detection-result__progress-bar\s*\{[^}]*background/s)
  })
})

describe('NewsDetectionResult consistency hero + detail-grid contract', () => {
  it('highlights consistency status in the hero', () => {
    expect(source).toContain('一致性状态')
  })

  it('has status-card for the consistency match indicator', () => {
    expect(source).toContain('news-detection-result__status-card')
  })

  it('has a detail-grid for reorganized consistency details', () => {
    expect(source).toContain('news-detection-result__detail-grid')
  })
})
