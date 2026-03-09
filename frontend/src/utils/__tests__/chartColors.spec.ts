import { describe, expect, it } from 'vitest'
import { buildChartCategoryPalette, buildTrendSeriesPalette, chartColors, resolveChartSemanticColor } from '../chartColors'

describe('chartColors regression', () => {
  it('keeps semantic palette bindings stable', () => {
    expect(chartColors.semantic).toEqual({
      fake: '#56c2ff',
      real: '#78e3bd',
      warning: '#f3c969',
      danger: '#ff8da1',
      accent: '#a88bff',
    })
    expect(chartColors.palette).toEqual(['#56c2ff', '#78e3bd', '#f3c969', '#ff8da1', '#a88bff'])
  })

  it('keeps semantic category resolution for Chinese and English labels', () => {
    expect(resolveChartSemanticColor('fake')).toBe(chartColors.semantic.fake)
    expect(resolveChartSemanticColor('谣言')).toBe(chartColors.semantic.fake)
    expect(resolveChartSemanticColor('真实')).toBe(chartColors.semantic.real)
    expect(resolveChartSemanticColor('风险')).toBe(chartColors.semantic.warning)
    expect(resolveChartSemanticColor('高风险')).toBe(chartColors.semantic.danger)
    expect(resolveChartSemanticColor('accent')).toBe(chartColors.semantic.accent)
  })

  it('keeps fallback and trend palettes stable', () => {
    expect(resolveChartSemanticColor('unknown', 6)).toBe(chartColors.palette[1])
    expect(buildChartCategoryPalette(['谣言', '真实', '风险', '高风险', 'accent'])).toEqual([
      chartColors.semantic.fake,
      chartColors.semantic.real,
      chartColors.semantic.warning,
      chartColors.semantic.danger,
      chartColors.semantic.accent,
    ])
    expect(buildTrendSeriesPalette()).toEqual([chartColors.semantic.fake, chartColors.semantic.real])
  })

  it('keeps tooltip, axis, legend and map colors aligned with dark theme', () => {
    expect(chartColors.tooltip.backgroundColor).toBe('rgba(7, 17, 31, 0.94)')
    expect(chartColors.tooltip.borderColor).toBe('rgba(86, 194, 255, 0.24)')
    expect(chartColors.legend.textStyle.color).toBe('#c4d3e3')
    expect(chartColors.axis.axisLabel.color).toBe('#9db0c5')
    expect(chartColors.map.areaSelected).toBe(chartColors.semantic.fake)
    expect(chartColors.map.riskMedium).toBe(chartColors.semantic.warning)
    expect(chartColors.map.riskHigh).toBe(chartColors.semantic.danger)
  })

  it('provides a dedicated donut palette for AI detection', () => {
    expect(chartColors.donut.aiProbability).toBe(chartColors.semantic.fake)
    expect(chartColors.donut.nonAiProbability).toBe('rgba(120, 227, 189, 0.28)')
  })
})
