const semanticChartColors = {
  fake: '#56c2ff',
  real: '#78e3bd',
  warning: '#f3c969',
  danger: '#ff8da1',
  accent: '#a88bff',
} as const

const chartPalette = [
  semanticChartColors.fake,
  semanticChartColors.real,
  semanticChartColors.warning,
  semanticChartColors.danger,
  semanticChartColors.accent,
] as const

const chartTooltip = {
  backgroundColor: 'rgba(7, 17, 31, 0.94)',
  borderColor: 'rgba(86, 194, 255, 0.24)',
  textStyle: { color: '#eef6ff' },
} as const

const chartLegend = {
  textStyle: { color: '#c4d3e3' },
} as const

const chartAxis = {
  axisLine: { lineStyle: { color: 'rgba(163, 206, 255, 0.24)' } },
  axisLabel: { color: '#9db0c5' },
  splitLine: { lineStyle: { color: 'rgba(163, 206, 255, 0.12)' } },
} as const

const chartStatus = {
  label: '#eef6ff',
  secondaryLabel: '#9db0c5',
  edge: 'rgba(148, 184, 219, 0.4)',
} as const

const mapVisual = {
  areaBase: 'rgba(18, 39, 61, 0.94)',
  areaHover: '#2d8fcb',
  areaSelected: '#56c2ff',
  areaBorder: 'rgba(148, 184, 219, 0.42)',
  areaShadow: 'rgba(86, 194, 255, 0.2)',
  visualRange: ['#15283a', '#1b5378', '#2d8fcb', '#56c2ff'],
  tooltipBackground: 'rgba(7, 17, 31, 0.96)',
  tooltipBorder: 'rgba(86, 194, 255, 0.22)',
  riskLow: '#1b5378',
  riskMedium: '#f3c969',
  riskHigh: '#ff8da1',
} as const

const donutPalette = {
  aiProbability: semanticChartColors.fake,
  nonAiProbability: 'rgba(120, 227, 189, 0.28)',
} as const

const semanticCategoryColorMap = new Map<string, string>([
  ['fake', semanticChartColors.fake],
  ['rumor', semanticChartColors.fake],
  ['谣言', semanticChartColors.fake],
  ['虚假', semanticChartColors.fake],
  ['false', semanticChartColors.fake],
  ['real', semanticChartColors.real],
  ['truth', semanticChartColors.real],
  ['真实', semanticChartColors.real],
  ['事实', semanticChartColors.real],
  ['warning', semanticChartColors.warning],
  ['风险', semanticChartColors.warning],
  ['danger', semanticChartColors.danger],
  ['高风险', semanticChartColors.danger],
  ['accent', semanticChartColors.accent],
])

function normalizeSemanticKey(value: string) {
  return value.trim().toLowerCase()
}

export function resolveChartSemanticColor(value: string, fallbackIndex = 0) {
  return semanticCategoryColorMap.get(normalizeSemanticKey(value)) ?? chartPalette[fallbackIndex % chartPalette.length]
}

export function buildChartCategoryPalette(categories: string[]) {
  return categories.map((category, index) => resolveChartSemanticColor(category, index))
}

export function buildTrendSeriesPalette() {
  return [semanticChartColors.fake, semanticChartColors.real]
}

export const chartColors = {
  palette: chartPalette,
  semantic: semanticChartColors,
  tooltip: chartTooltip,
  legend: chartLegend,
  axis: chartAxis,
  status: chartStatus,
  map: mapVisual,
  donut: donutPalette,
} as const
