<template>
  <el-card class="news-detection-result">
    <template #header>
      <div class="news-detection-result__header">
        <span>检测结果</span>
        <el-tag :type="tagType" effect="dark">{{ result.label }}</el-tag>
      </div>
    </template>

    <template v-if="result.resultKind === 'aggregate'">
      <section class="news-detection-result__section">
        <div class="news-detection-result__hero">
          <div class="news-detection-result__hero-label">总体风险等级</div>
          <div class="news-detection-result__hero-value">{{ result.overallCredibility.toFixed(2) }}%</div>
          <div class="news-detection-result__hero-summary">综合内容风险检测与文本分析的整体风险评估</div>
          <span class="news-detection-result__status-pill">{{ result.label }}</span>
          <div class="news-detection-result__progress-track">
            <div class="news-detection-result__progress-bar" :style="{ width: result.overallCredibility + '%' }"></div>
          </div>
        </div>

        <div class="news-detection-result__metric-grid">
          <article class="news-detection-result__metric-card">
            <div class="news-detection-result__metric-label">总体风险等级</div>
            <div class="news-detection-result__metric-value">{{ result.overallCredibility.toFixed(2) }}%</div>
          </article>
          <article class="news-detection-result__metric-card">
            <div class="news-detection-result__metric-label">内容风险度</div>
            <div class="news-detection-result__metric-value">{{ result.newsCredibility.toFixed(2) }}%</div>
          </article>
          <article class="news-detection-result__metric-card">
            <div class="news-detection-result__metric-label">AI 文本概率</div>
            <div class="news-detection-result__metric-value">{{ result.aiProbability.toFixed(2) }}%</div>
          </article>
        </div>

        <div class="news-detection-result__analysis-grid">
          <article class="news-detection-result__analysis-card">
            <div class="news-detection-result__panel-title">新闻分析</div>
            <div class="news-detection-result__panel-text">{{ result.newsSummary || '暂无新闻摘要' }}</div>
            <div class="news-detection-result__analysis-conclusion">
              <span class="news-detection-result__metric-label">结论</span>
              <span class="news-detection-result__panel-text">{{ result.newsConclusion || '暂无新闻结论' }}</span>
            </div>
          </article>
          <article class="news-detection-result__analysis-card">
            <div class="news-detection-result__panel-title">AI 分析</div>
            <div class="news-detection-result__panel-text">{{ result.aiSummary || '暂无 AI 摘要' }}</div>
            <div class="news-detection-result__analysis-conclusion">
              <span class="news-detection-result__metric-label">结论</span>
              <span class="news-detection-result__panel-text">{{ result.aiConclusion || '暂无 AI 结论' }}</span>
            </div>
          </article>
        </div>
      </section>
    </template>

    <template v-else-if="result.resultKind === 'consistency'">
      <section class="news-detection-result__section">
        <div class="news-detection-result__hero">
          <div class="news-detection-result__hero-label">一致性状态</div>
          <div class="news-detection-result__hero-value">{{ result.titleTextSimilarity.toFixed(2) }}%</div>
          <div class="news-detection-result__hero-summary">标题与正文内容的一致性综合评估</div>
          <span class="news-detection-result__status-pill">{{ result.label }}</span>
          <div class="news-detection-result__progress-track">
            <div class="news-detection-result__progress-bar" :style="{ width: result.titleTextSimilarity + '%' }"></div>
          </div>
        </div>

        <div class="news-detection-result__metric-grid">
          <article class="news-detection-result__metric-card">
            <div class="news-detection-result__metric-label">标题-正文相似度</div>
            <div class="news-detection-result__metric-value">{{ result.titleTextSimilarity.toFixed(2) }}%</div>
            <div class="news-detection-result__progress-track news-detection-result__progress-track--inline">
              <div class="news-detection-result__progress-bar" :style="{ width: result.titleTextSimilarity + '%' }"></div>
            </div>
          </article>
          <article class="news-detection-result__metric-card">
            <div class="news-detection-result__metric-label">图文相似度</div>
            <div class="news-detection-result__metric-value">{{ result.textImageSimilarity.toFixed(2) }}%</div>
            <div class="news-detection-result__progress-track news-detection-result__progress-track--inline">
              <div class="news-detection-result__progress-bar" :style="{ width: result.textImageSimilarity + '%' }"></div>
            </div>
          </article>
          <article class="news-detection-result__status-card">
            <div class="news-detection-result__metric-label">标题一致性</div>
            <div class="news-detection-result__metric-value news-detection-result__metric-value--small">
              {{ result.titleTextMatch ? '匹配' : '不匹配' }}
            </div>
          </article>
        </div>

        <div class="news-detection-result__detail-grid">
          <article class="news-detection-result__panel">
            <div class="news-detection-result__panel-title">标题</div>
            <div class="news-detection-result__panel-text">{{ result.title || '暂无标题' }}</div>
          </article>
          <article class="news-detection-result__panel">
            <div class="news-detection-result__panel-title">一致性结果</div>
            <div class="news-detection-result__panel-text">{{ result.label || '暂无结果' }}</div>
          </article>
          <article class="news-detection-result__panel news-detection-result__panel--full">
            <div class="news-detection-result__panel-title">正文摘要</div>
            <div class="news-detection-result__panel-text">{{ result.content || '暂无正文内容' }}</div>
          </article>
          <article class="news-detection-result__panel news-detection-result__panel--full">
            <div class="news-detection-result__panel-title">详情</div>
            <div v-if="detailEntries.length" class="news-detection-result__detail-list">
              <div v-for="([key, value], index) in detailEntries" :key="`${key}-${index}`" class="news-detection-result__detail-item">
                <span class="news-detection-result__detail-key">{{ key }}</span>
                <span class="news-detection-result__detail-value">{{ stringifyValue(value) }}</span>
              </div>
            </div>
            <div v-else class="news-detection-result__panel-text">暂无详情数据</div>
          </article>
        </div>
      </section>
    </template>

    <template v-else-if="result.resultKind === 'segments'">
      <section class="news-detection-result__section">
        <div class="news-detection-result__segment-overview">
          <div class="news-detection-result__hero">
            <div class="news-detection-result__hero-label">段落风险概览</div>
            <div class="news-detection-result__hero-value">{{ result.credibilityScore.toFixed(2) }}%</div>
            <div class="news-detection-result__hero-summary">基于各段落真实与虚假概率的综合风险评估</div>
            <span class="news-detection-result__status-pill">{{ result.label }}</span>
            <div class="news-detection-result__progress-track">
              <div class="news-detection-result__progress-bar" :style="{ width: result.credibilityScore + '%' }"></div>
            </div>
          </div>

          <div class="news-detection-result__metric-grid">
            <article class="news-detection-result__metric-card">
              <div class="news-detection-result__metric-label">总体风险等级</div>
              <div class="news-detection-result__metric-value">{{ result.credibilityScore.toFixed(2) }}%</div>
            </article>
            <article class="news-detection-result__metric-card">
              <div class="news-detection-result__metric-label">标签</div>
              <div class="news-detection-result__metric-value news-detection-result__metric-value--small">{{ result.label }}</div>
            </article>
            <article class="news-detection-result__metric-card">
              <div class="news-detection-result__metric-label">段落数</div>
              <div class="news-detection-result__metric-value">{{ result.segmentCount }}</div>
            </article>
          </div>

          <div class="news-detection-result__content-grid">
            <article class="news-detection-result__panel news-detection-result__panel--full">
              <div class="news-detection-result__panel-title">结论</div>
              <div class="news-detection-result__panel-text">{{ result.conclusion || '暂无结论' }}</div>
            </article>
            <article class="news-detection-result__panel news-detection-result__panel--full">
              <div class="news-detection-result__panel-title">特征标签</div>
              <div v-if="featureTagEntries.length" class="news-detection-result__detail-list">
                <div v-for="([key, value], index) in featureTagEntries" :key="`${key}-${index}`" class="news-detection-result__detail-item">
                  <span class="news-detection-result__detail-key">{{ key }}</span>
                  <span class="news-detection-result__detail-value">{{ stringifyValue(value) }}</span>
                </div>
              </div>
              <div v-else class="news-detection-result__panel-text">暂无特征标签</div>
            </article>
          </div>
        </div>

        <div class="news-detection-result__panel-title">段落风险概览</div>
        <div class="news-detection-result__segment-list">
          <article v-for="segment in result.segments" :key="segment.segmentId" class="news-detection-result__segment-card">
            <div class="news-detection-result__segment-header">
              <span>段落 {{ segment.segmentId }}</span>
              <el-tag :type="resolveLabelTagType(segment.label)" effect="dark">{{ segment.label }}</el-tag>
            </div>
            <div class="news-detection-result__panel-text">{{ segment.text || '暂无段落内容' }}</div>
            <div class="news-detection-result__segment-bar">
              <div class="news-detection-result__segment-bar-fill" :style="{ width: segment.fakeProbability + '%' }"></div>
            </div>
            <div class="news-detection-result__segment-risk">
              虚假概率: {{ segment.fakeProbability.toFixed(2) }}%
            </div>
            <div class="news-detection-result__segment-metrics">
              <div class="news-detection-result__segment-metric">
                <span>真实概率</span>
                <strong>{{ segment.realProbability.toFixed(2) }}%</strong>
              </div>
              <div class="news-detection-result__segment-metric">
                <span>虚假概率</span>
                <strong>{{ segment.fakeProbability.toFixed(2) }}%</strong>
              </div>
            </div>
          </article>
        </div>
      </section>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type {
  AggregateDisplayResult,
  ConsistencyDisplayResult,
  SegmentsDisplayResult,
} from '@/types/newsDetection'

const props = defineProps<{
  result: AggregateDisplayResult | ConsistencyDisplayResult | SegmentsDisplayResult
}>()

function resolveLabelTagType(label: string) {
  if (label.includes('真实') || label.includes('可信') || label.includes('匹配') || label.includes('real')) {
    return 'success'
  }
  if (label.includes('虚假') || label.includes('假') || label.includes('谣') || label.includes('fake')) {
    return 'danger'
  }
  return 'warning'
}

const tagType = computed(() => resolveLabelTagType(props.result.label))

const detailEntries = computed(() => {
  if (props.result.resultKind !== 'consistency') return []
  return Object.entries(props.result.details)
})

const featureTagEntries = computed(() => {
  if (props.result.resultKind !== 'segments') return []
  return Object.entries(props.result.featureTags)
})

function stringifyValue(value: unknown) {
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  if (value == null) return '-'
  return JSON.stringify(value)
}
</script>

<style scoped lang="scss">
.news-detection-result {
  border: 1px solid var(--app-border-default);
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
}

.news-detection-result :deep(.el-card__header) {
  border-bottom-color: color-mix(in srgb, var(--app-border-default) 76%, transparent);
}

.news-detection-result__header,
.news-detection-result__segment-header,
.news-detection-result__detail-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.news-detection-result__section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.news-detection-result__metric-grid,
.news-detection-result__content-grid,
.news-detection-result__analysis-grid,
.news-detection-result__detail-grid,
.news-detection-result__segment-list,
.news-detection-result__segment-metrics {
  display: grid;
  gap: 16px;
}

.news-detection-result__metric-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.news-detection-result__content-grid,
.news-detection-result__analysis-grid,
.news-detection-result__detail-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.news-detection-result__segment-list {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.news-detection-result__metric-card,
.news-detection-result__panel,
.news-detection-result__analysis-card,
.news-detection-result__status-card,
.news-detection-result__segment-card {
  border: 1px solid var(--app-border-default);
  border-radius: 20px;
  background: color-mix(in srgb, var(--app-surface-card) 92%, white 8%);
  padding: 20px;
}

.news-detection-result__panel--full {
  grid-column: 1 / -1;
}

.news-detection-result__metric-label,
.news-detection-result__panel-title,
.news-detection-result__detail-key,
.news-detection-result__segment-metric span {
  color: var(--app-text-secondary);
  font-size: 13px;
  letter-spacing: 0.08em;
}

.news-detection-result__metric-value {
  margin-top: 12px;
  color: var(--app-text-primary);
  font-size: 34px;
  font-weight: 700;
  line-height: 1.1;
}

.news-detection-result__metric-value--small {
  font-size: 24px;
}

.news-detection-result__panel-text,
.news-detection-result__detail-value {
  margin-top: 12px;
  color: var(--app-text-secondary);
  line-height: 1.7;
  word-break: break-word;
}

.news-detection-result__detail-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.news-detection-result__detail-item {
  padding: 10px 12px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--app-surface-note) 76%, white 24%);
  align-items: flex-start;
}

.news-detection-result__segment-metrics {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 16px;
}

.news-detection-result__segment-metric {
  padding: 12px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--app-surface-note) 76%, white 24%);
}

.news-detection-result__segment-metric strong {
  display: block;
  margin-top: 8px;
  color: var(--app-text-primary);
  font-size: 22px;
}

.news-detection-result__hero {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px 0;
}

.news-detection-result__hero-value {
  color: var(--app-text-primary);
  font-size: 48px;
  font-weight: 700;
  line-height: 1.1;
}

.news-detection-result__status-pill {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  background: color-mix(in srgb, var(--app-accent-primary-soft) 100%, white 0%);
  color: var(--tech-color-primary-strong);
  font-size: 13px;
  font-weight: 500;
}

.news-detection-result__progress-track {
  height: 6px;
  margin-top: 8px;
  border-radius: 3px;
  background: color-mix(in srgb, var(--app-accent-primary-soft) 36%, white 64%);
  overflow: hidden;
}

.news-detection-result__progress-bar {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #56c2ff, #3a8fd4);
  transition: width 0.4s ease;
}

.news-detection-result__hero-label {
  color: var(--app-text-secondary);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.news-detection-result__hero-summary {
  margin-top: 4px;
  color: var(--app-text-tertiary);
  font-size: 13px;
  line-height: 1.5;
}

.news-detection-result__analysis-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-detection-result__analysis-conclusion {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid color-mix(in srgb, var(--app-border-default) 72%, transparent);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.news-detection-result__status-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.news-detection-result__progress-track--inline {
  margin-top: 10px;
}

.news-detection-result__segment-overview {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  border: 1px solid var(--app-border-default);
  border-radius: 20px;
  background: color-mix(in srgb, var(--app-surface-card) 92%, white 8%);
}

.news-detection-result__segment-bar {
  height: 8px;
  margin-top: 12px;
  border-radius: 4px;
  background: color-mix(in srgb, var(--app-accent-primary-soft) 36%, white 64%);
  overflow: hidden;
}

.news-detection-result__segment-bar-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #f56c6c, #e63946);
  transition: width 0.4s ease;
}

.news-detection-result__segment-risk {
  margin-top: 8px;
  color: var(--app-text-danger);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.04em;
}

@media (max-width: 960px) {
  .news-detection-result__metric-grid,
  .news-detection-result__content-grid,
  .news-detection-result__analysis-grid,
  .news-detection-result__detail-grid,
  .news-detection-result__segment-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
