<template>
  <div class="graph-canvas-shell">
    <el-skeleton v-if="loading" :rows="6" animated class="graph-canvas-shell__state" />
    <template v-else>
      <div v-show="graph.nodes.length" ref="graphRef" class="graph-canvas-shell__canvas" />
      <el-empty v-if="!graph.nodes.length" description="暂无图谱数据" class="graph-canvas-shell__state" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { KnowledgeGraphResponse } from '@/types/insight'
import { buildChartCategoryPalette, chartColors } from '@/utils/chartColors'

const props = defineProps<{
  graph: KnowledgeGraphResponse
  loading?: boolean
}>()

const graphRef = ref<HTMLDivElement | null>(null)
let chart: any = null

async function ensureChart() {
  if (chart || !graphRef.value) return

  const [{ init, use }, { GraphChart }, { TooltipComponent, LegendComponent }, { CanvasRenderer }] = await Promise.all([
    import('echarts/core'),
    import('echarts/charts'),
    import('echarts/components'),
    import('echarts/renderers'),
  ])

  use([GraphChart, TooltipComponent, LegendComponent, CanvasRenderer])
  chart = init(graphRef.value, undefined, { renderer: 'canvas', useDirtyRect: true })
}

async function renderGraph() {
  await nextTick()
  if (!graphRef.value || !props.graph.nodes.length) return

  await ensureChart()
  if (!chart) return

  const categoryNames = Array.from(new Set(props.graph.nodes.map((item) => item.category)))
  const categories = categoryNames.map((name) => ({ name }))
  const categoryIndex = new Map(categories.map((c, i) => [c.name, i]))
  const categoryColors = buildChartCategoryPalette(categoryNames)

  chart.setOption({
    backgroundColor: 'transparent',
    color: categoryColors,
    tooltip: {
      trigger: 'item',
      ...chartColors.tooltip,
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          return `${params.data.source} -> ${params.data.target}<br/>关系: ${params.data.relation_type}`
        }
        return `${params.data.name}<br/>类别: ${params.data.category}`
      },
    },
    legend: {
      type: 'scroll',
      data: categories.map((item) => item.name),
      ...chartColors.legend,
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        force: {
          repulsion: 220,
          edgeLength: [50, 140],
          gravity: 0.1,
        },
        label: { show: true, position: 'right', color: chartColors.status.label },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [4, 10],
        lineStyle: { width: 1.2, opacity: 0.7, curveness: 0.15, color: chartColors.status.edge },
        emphasis: { focus: 'adjacency' },
        categories,
        data: props.graph.nodes.map((node) => ({
          id: node.id,
          name: node.name,
          value: node.value,
          category: categoryIndex.get(node.category) ?? 0,
          symbolSize: Math.max(20, Math.min(80, node.value * 2)),
        })),
        links: props.graph.edges.map((edge) => ({
          source: edge.source,
          target: edge.target,
          value: edge.weight,
          relation_type: edge.relation_type,
          label: {
            show: true,
            formatter: edge.relation_type,
            fontSize: 10,
            color: chartColors.status.secondaryLabel,
          },
        })),
      },
    ],
  }, true)
}

function handleResize() {
  chart?.resize()
}

watch(
  () => props.graph,
  () => {
    void renderGraph()
  },
  { deep: true },
)

watch(
  () => props.loading,
  (loading) => {
    if (loading) {
      // v-if will destroy the canvas DOM; dispose the stale chart instance
      chart?.dispose()
      chart = null
    } else {
      void renderGraph()
    }
  },
)

onMounted(() => {
  void renderGraph()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped lang="scss">
.graph-canvas-shell {
  min-height: 520px;
  border: 1px solid rgba(163, 206, 255, 0.16);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(15, 33, 58, 0.68), rgba(8, 16, 30, 0.96));
}

.graph-canvas-shell__canvas {
  width: 100%;
  height: 520px;
}

.graph-canvas-shell__state {
  min-height: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
</style>
