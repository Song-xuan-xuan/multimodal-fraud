<template>
  <el-card v-if="visualResult" class="detection-result">
    <template #header>
      <div class="detection-result__header">
        <span>风险分析结果</span>
        <el-tag :type="tagType" effect="dark">{{ visualResult.label }}</el-tag>
      </div>
    </template>

    <div class="detection-result__hero">
      <div class="detection-result__hero-main">
        <div class="detection-result__score-label">{{ scoreLabel }}</div>
        <div class="detection-result__score-value">{{ visualResult.aiProbability.toFixed(2) }}%</div>
        <div class="detection-result__summary">{{ visualResult.summary }}</div>
      </div>
      <div class="detection-result__hero-side">
        <div class="detection-result__conclusion-label">结论</div>
        <div class="detection-result__conclusion">{{ visualResult.conclusion }}</div>
      </div>
    </div>

    <div class="detection-result__content">
      <div class="detection-result__chart-card">
        <div ref="chartRef" class="detection-result__chart" />
      </div>

      <div class="detection-result__details">
        <div
          v-if="visualResult.resultKind === 'image' && visualResult.imagePreviewUrl"
          class="detection-result__image-section"
        >
          <div class="detection-result__section-title">风险截图</div>
          <img :src="visualResult.imagePreviewUrl" alt="风险截图预览" class="detection-result__image-preview" />
        </div>

        <div v-if="visualResult.resultKind === 'text' || visualResult.resultKind === 'audio'" class="detection-result__detail-card">
          <div class="detection-result__section-title">{{ visualResult.resultKind === 'audio' ? '语音转写内容' : '对话摘要' }}</div>
          <div class="detection-result__detail-text">
            {{ visualResult.textPreview || '暂无内容预览' }}
          </div>
        </div>

        <div class="detection-result__detail-grid">
          <div class="detection-result__detail-card">
            <div class="detection-result__section-title">高风险指数</div>
            <div class="detection-result__metric-value">{{ visualResult.aiProbability.toFixed(2) }}%</div>
          </div>
          <div class="detection-result__detail-card">
            <div class="detection-result__section-title">低风险概率</div>
            <div class="detection-result__metric-value">{{ visualResult.humanProbability.toFixed(2) }}%</div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { DetectionDisplayResult } from '@/types/detection'
import { chartColors } from '@/utils/chartColors'
import { normalizeDetectionResult } from '@/utils/detectionResult'

const props = defineProps<{ result: any }>()

const chartRef = ref<HTMLDivElement | null>(null)
let chart: any = null
let resizeObserver: ResizeObserver | null = null

function normalizeLegacyResult(result: any): DetectionDisplayResult | null {
  if (!result) return null

  if (result.ai_text_detection) {
    return normalizeDetectionResult({
      resultKind: result.imagePreviewUrl ? 'image' : 'text',
      rawResult: {
        ...result.ai_text_detection,
        label: result.label || result.overall_label || result.news_detection?.label || result.ai_text_detection?.label,
        summary: result.news_detection?.summary || result.ai_text_detection?.summary,
        conclusion: result.news_detection?.conclusion || result.ai_text_detection?.conclusion,
      },
      textPreview: result.content || result.text || '',
      imagePreviewUrl: result.imagePreviewUrl || '',
    })
  }

  return normalizeDetectionResult({
    resultKind: result.imagePreviewUrl ? 'image' : 'text',
    rawResult: result,
    textPreview: result.content || result.text || '',
    imagePreviewUrl: result.imagePreviewUrl || '',
  })
}

const visualResult = computed<DetectionDisplayResult | null>(() => {
  if (!props.result) return null
  if (typeof props.result?.resultKind === 'string' && typeof props.result?.aiProbability === 'number') {
    return props.result as DetectionDisplayResult
  }
  return normalizeLegacyResult(props.result)
})

const scoreLabel = computed(() => (visualResult.value?.resultKind === 'image' || visualResult.value?.resultKind === 'text' ? '高风险表达概率' : '综合概率'))

const tagType = computed(() => {
  const label = visualResult.value?.label || ''
  if (label.includes('人工') || label.includes('真') || label.includes('可信')) return 'success'
  if (label.includes('AI') || label.includes('假') || label.includes('谣')) return 'danger'
  return 'warning'
})

async function ensureChart() {
  if (chart || !chartRef.value) return

  const [{ init, use }, { PieChart }, { TooltipComponent, LegendComponent, GraphicComponent }, { CanvasRenderer }] = await Promise.all([
    import('echarts/core'),
    import('echarts/charts'),
    import('echarts/components'),
    import('echarts/renderers'),
  ])

  use([PieChart, TooltipComponent, LegendComponent, GraphicComponent, CanvasRenderer])
  chart = init(chartRef.value, undefined, { renderer: 'canvas', useDirtyRect: true })
}

async function renderChart() {
  await nextTick()
  await new Promise<void>((resolve) => {
    requestAnimationFrame(() => resolve())
  })

  if (!chartRef.value || !visualResult.value) return
  if (!chartRef.value.clientWidth || !chartRef.value.clientHeight) return

  await ensureChart()
  if (!chart) return

  chart.setOption({
    backgroundColor: 'transparent',
    color: [chartColors.donut.aiProbability, chartColors.donut.nonAiProbability],
    tooltip: {
      trigger: 'item',
      ...chartColors.tooltip,
      formatter: (params: any) => `${params.name}: ${Number(params.value).toFixed(2)}%`,
    },
    legend: {
      bottom: 0,
      left: 'center',
      icon: 'circle',
      data: ['高风险', '非高风险'],
      ...chartColors.legend,
    },
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '42%',
        style: {
          text: '高风险表达概率',
          textAlign: 'center',
          fill: chartColors.status.secondaryLabel,
          fontSize: 14,
          fontWeight: 500,
        },
      },
      {
        type: 'text',
        left: 'center',
        top: '50%',
        style: {
          text: `${visualResult.value.aiProbability.toFixed(2)}%`,
          textAlign: 'center',
          fill: chartColors.status.label,
          fontSize: 28,
          fontWeight: 700,
        },
      },
    ],
    series: [
      {
        name: '风险识别结果',
        type: 'pie',
        radius: ['60%', '82%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderColor: 'rgba(7, 17, 31, 0.92)',
          borderWidth: 3,
        },
        label: { show: false },
        emphasis: { scale: false },
        data: [
          { value: visualResult.value.aiProbability, name: '高风险' },
          { value: visualResult.value.humanProbability, name: '非高风险' },
        ],
      },
    ],
  })
}

function handleResize() {
  chart?.resize()
}

watch(
  () => visualResult.value,
  () => {
    void renderChart()
  },
  { deep: true },
)

onMounted(() => {
  void renderChart()
  window.addEventListener('resize', handleResize)

  if (typeof ResizeObserver !== 'undefined' && chartRef.value) {
    resizeObserver = new ResizeObserver(() => {
      chart?.resize()
      void renderChart()
    })
    resizeObserver.observe(chartRef.value)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  resizeObserver?.disconnect()
  resizeObserver = null
  chart?.dispose()
  chart = null
})
</script>

<style scoped lang="scss">
.detection-result {
  border: 1px solid rgba(163, 206, 255, 0.16);
  background: linear-gradient(180deg, rgba(15, 33, 58, 0.68), rgba(8, 16, 30, 0.96));
  box-shadow: 0 18px 40px rgba(4, 10, 20, 0.26);
}

.detection-result :deep(.el-card__header) {
  border-bottom-color: rgba(163, 206, 255, 0.12);
}

.detection-result__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detection-result__hero {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(240px, 0.9fr);
  gap: 20px;
  margin-bottom: 20px;
}

.detection-result__hero-main,
.detection-result__hero-side,
.detection-result__chart-card,
.detection-result__detail-card,
.detection-result__image-section {
  border: 1px solid rgba(163, 206, 255, 0.14);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(14, 28, 44, 0.72), rgba(7, 15, 28, 0.94));
}

.detection-result__hero-main,
.detection-result__hero-side {
  padding: 24px;
}

.detection-result__score-label,
.detection-result__conclusion-label,
.detection-result__section-title {
  color: #9db0c5;
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detection-result__score-value {
  margin-top: 10px;
  color: #eef6ff;
  font-size: 42px;
  font-weight: 700;
  line-height: 1;
}

.detection-result__summary,
.detection-result__conclusion,
.detection-result__detail-text {
  margin-top: 14px;
  color: #c4d3e3;
  line-height: 1.7;
}

.detection-result__content {
  display: grid;
  grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
  gap: 20px;
}

.detection-result__chart-card {
  padding: 20px 16px 10px;
}

.detection-result__chart {
  width: 100%;
  height: 320px;
}

.detection-result__details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detection-result__image-section,
.detection-result__detail-card {
  padding: 18px;
}

.detection-result__image-preview {
  display: block;
  width: 100%;
  margin-top: 12px;
  border-radius: 16px;
  object-fit: cover;
}

.detection-result__detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.detection-result__metric-value {
  margin-top: 12px;
  color: #eef6ff;
  font-size: 28px;
  font-weight: 700;
}

@media (max-width: 960px) {
  .detection-result__hero,
  .detection-result__content,
  .detection-result__detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>

