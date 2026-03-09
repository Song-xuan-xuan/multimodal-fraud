import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const componentPath = path.resolve(__dirname, '../DetectionResult.vue')
const source = fs.readFileSync(componentPath, 'utf-8')

describe('DetectionResult visualization regression', () => {
  it('renders donut chart contract and adaptive text/image sections', () => {
    expect(source).toContain("import('echarts/core')")
    expect(source).toContain('PieChart')
    expect(source).toContain('AI生成概率')
    expect(source).toContain('detection-result__chart')
    expect(source).toContain('detection-result__image-preview')
    expect(source).toContain('textPreview')
    expect(source).toContain('chartColors')
    expect(source).toContain('chartColors.donut')
    expect(source).toContain('requestAnimationFrame')
    expect(source).toContain('ResizeObserver')
  })
})
