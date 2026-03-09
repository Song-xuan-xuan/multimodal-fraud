<template>
  <div class="trend-chart-shell">
    <el-skeleton v-if="loading" :rows="5" animated class="trend-chart-shell__state" />
    <template v-else>
      <div v-show="points.length" ref="chartRef" class="trend-chart-shell__canvas" />
      <el-empty v-if="!points.length" description="暂无趋势数据" class="trend-chart-shell__state" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { HotspotTrendPoint } from '@/types/insight'
import { buildTrendSeriesPalette, chartColors } from '@/utils/chartColors'

const props = defineProps<{
  points: HotspotTrendPoint[]
  loading?: boolean
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chart: any = null
let echartsModules: any = null

async function ensureChart() {
  if (chart || !chartRef.value) return

  const [{ init, use }, { LineChart }, { GridComponent, LegendComponent, TooltipComponent }, { CanvasRenderer }] = await Promise.all([
    import('echarts/core'),
    import('echarts/charts'),
    import('echarts/components'),
    import('echarts/renderers'),
  ])

  use([LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])
  echartsModules = { init }
  chart = init(chartRef.value, undefined, { renderer: 'canvas', useDirtyRect: true })
}

async function renderChart() {
  await nextTick()
  if (!chartRef.value || !props.points.length) return

  await ensureChart()
  if (!chart) return

  const dates = props.points.map((item) => item.date)
  const fakeValues = props.points.map((item) => item.fake)
  const realValues = props.points.map((item) => item.real)
  const seriesColors = buildTrendSeriesPalette()

  chart.setOption({
    backgroundColor: 'transparent',
    color: seriesColors,
    tooltip: {
      trigger: 'axis',
      ...chartColors.tooltip,
    },
    legend: {
      data: ['谣言数', '真实数'],
      ...chartColors.legend,
    },
    grid: { left: 20, right: 24, top: 44, bottom: 24, containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: chartColors.axis.axisLine,
      axisLabel: chartColors.axis.axisLabel,
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLine: { show: false },
      splitLine: chartColors.axis.splitLine,
      axisLabel: chartColors.axis.axisLabel,
    },
    series: [
      {
        name: '谣言数',
        type: 'line',
        smooth: true,
        data: fakeValues,
        areaStyle: { opacity: 0.16 },
        lineStyle: { width: 2 },
      },
      {
        name: '真实数',
        type: 'line',
        smooth: true,
        data: realValues,
        areaStyle: { opacity: 0.1 },
        lineStyle: { width: 2 },
      },
    ],
  })
}

function handleResize() {
  chart?.resize()
}

watch(
  () => props.points,
  () => {
    void renderChart()
  },
  { deep: true },
)

watch(
  () => props.loading,
  (loading) => {
    if (!loading) {
      void renderChart()
    }
  },
)

onMounted(() => {
  void renderChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
  echartsModules = null
})
</script>

<style scoped lang="scss">
.trend-chart-shell {
  min-height: 360px;
  border: 1px solid rgba(163, 206, 255, 0.16);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(15, 33, 58, 0.68), rgba(8, 16, 30, 0.96));
}

.trend-chart-shell__canvas {
  width: 100%;
  height: 360px;
}

.trend-chart-shell__state {
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
</style>
