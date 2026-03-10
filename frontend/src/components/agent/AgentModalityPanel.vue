<template>
  <div class="agent-modality-panel">
    <div class="agent-modality-panel__header">
      <span class="agent-modality-panel__name">{{ title }}</span>
      <span class="agent-modality-panel__score">{{ scoreText }}</span>
    </div>

    <p class="agent-modality-panel__summary">{{ summary }}</p>

    <div v-if="scoreBreakdown.length" class="agent-modality-panel__metrics">
      <div v-for="item in scoreBreakdown" :key="item.label" class="agent-modality-panel__metric">
        <span class="agent-modality-panel__metric-label">{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </div>

    <div v-if="matchedKeywords.length" class="agent-modality-panel__group">
      <span class="agent-modality-panel__group-title">命中关键词</span>
      <div class="agent-modality-panel__chips">
        <el-tag v-for="item in matchedKeywords" :key="item" size="small" effect="plain">{{ item }}</el-tag>
      </div>
    </div>

    <div v-if="matchedPatterns.length" class="agent-modality-panel__group">
      <span class="agent-modality-panel__group-title">命中模式</span>
      <div class="agent-modality-panel__chips">
        <el-tag v-for="item in matchedPatterns" :key="item" size="small" type="danger" effect="plain">{{ item }}</el-tag>
      </div>
    </div>

    <div v-if="extraText" class="agent-modality-panel__extra tech-scrollbar">{{ extraText }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  score?: number
  summary?: string
  extraText?: string
  rawResult?: Record<string, any>
}>()

const scoreText = computed(() => {
  if (typeof props.score !== 'number') return '未评分'
  return `综合分 ${(props.score * 100).toFixed(0)}%`
})
const summary = computed(() => props.summary || '当前模态未返回摘要信息。')
const matchedKeywords = computed<string[]>(() => props.rawResult?.matched_keywords || [])
const matchedPatterns = computed<string[]>(() => props.rawResult?.matched_patterns || [])
const scoreBreakdown = computed(() => {
  const result = props.rawResult || {}
  const items: Array<{ label: string; value: string }> = []

  if (typeof result.base_ai_score === 'number') {
    items.push({ label: '基础AI分', value: `${(result.base_ai_score * 100).toFixed(0)}%` })
  }
  if (typeof result.base_vision_score === 'number') {
    items.push({ label: '基础视觉分', value: `${(result.base_vision_score * 100).toFixed(0)}%` })
  }
  if (typeof result.text_rule_score === 'number') {
    items.push({ label: '规则加权分', value: `${(result.text_rule_score * 100).toFixed(0)}%` })
  }
  if (typeof result.enhanced_text_score === 'number') {
    items.push({ label: '增强文本分', value: `${(result.enhanced_text_score * 100).toFixed(0)}%` })
  }
  if (typeof result.image_fused_score === 'number') {
    items.push({ label: '图片融合分', value: `${(result.image_fused_score * 100).toFixed(0)}%` })
  }

  return items
})
</script>

<style scoped lang="scss">
.agent-modality-panel {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(150, 208, 255, 0.12);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 14%, transparent);
}

.agent-modality-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.agent-modality-panel__name {
  color: var(--tech-theme-text-primary);
  font-size: 14px;
  font-weight: 600;
}

.agent-modality-panel__score {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.agent-modality-panel__summary {
  margin: 0;
  color: var(--tech-theme-text-regular);
  line-height: 1.7;
}

.agent-modality-panel__metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.agent-modality-panel__metric {
  display: grid;
  gap: 4px;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid rgba(150, 208, 255, 0.1);
  background: color-mix(in srgb, var(--tech-theme-surface-panel) 64%, transparent);
}

.agent-modality-panel__metric-label,
.agent-modality-panel__group-title {
  color: var(--tech-theme-text-secondary);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.agent-modality-panel__metric strong {
  color: var(--tech-theme-text-primary);
}

.agent-modality-panel__group {
  margin-top: 12px;
}

.agent-modality-panel__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.agent-modality-panel__extra {
  max-height: 120px;
  overflow-y: auto;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(150, 208, 255, 0.1);
  color: var(--tech-theme-text-secondary);
  line-height: 1.65;
  white-space: pre-wrap;
}

@media (max-width: 720px) {
  .agent-modality-panel__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
