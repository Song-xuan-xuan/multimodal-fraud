<template>
  <section class="agent-decision-panel tech-surface">
    <div class="agent-decision-panel__header">
      <div>
        <h3>智能体决策总览</h3>
        <span>Intent -> Risk -> Intervention</span>
      </div>
      <div class="agent-decision-panel__badges">
        <el-tag :type="riskTagType(result.risk_level)" effect="dark">风险等级 {{ levelLabel }}</el-tag>
        <el-tag effect="plain">风险分数 {{ scoreText }}</el-tag>
        <el-tag effect="plain">主剧本 {{ result.fraud_type.label }}</el-tag>
      </div>
    </div>

    <div class="agent-decision-panel__overview">
      <article class="agent-decision-panel__card">
        <span class="agent-decision-panel__label">意图识别</span>
        <strong>{{ result.intent.label }}</strong>
        <small>置信度 {{ intentConfidence }}</small>
        <p>{{ result.intent.reason }}</p>
      </article>

      <article class="agent-decision-panel__card">
        <span class="agent-decision-panel__label">主诈骗类型</span>
        <strong>{{ result.fraud_type.label }}</strong>
        <small>置信度 {{ fraudConfidence }}</small>
        <p>{{ result.fraud_type.rationale }}</p>
      </article>

      <article class="agent-decision-panel__card">
        <span class="agent-decision-panel__label">干预策略</span>
        <strong>{{ result.intervention_plan.headline }}</strong>
        <small>{{ result.intervention_plan.recommended_channel }}</small>
        <p>{{ result.intervention_plan.summary }}</p>
      </article>
    </div>

    <div class="agent-decision-panel__section">
      <div class="agent-decision-panel__section-head">
        <h4>证据链</h4>
        <span>系统按风险强度排序展示关键依据</span>
      </div>
      <div class="agent-decision-panel__evidence-list">
        <article
          v-for="(item, index) in evidenceItems"
          :key="`${item.kind}-${index}`"
          class="agent-decision-panel__evidence-item"
        >
          <div class="agent-decision-panel__evidence-meta">
            <span>{{ item.title }}</span>
            <strong>{{ formatPercent(item.score) }}</strong>
          </div>
          <small>{{ formatEvidenceTag(item) }}</small>
          <p>{{ item.snippet }}</p>
        </article>
      </div>
    </div>

    <div class="agent-decision-panel__section">
      <div class="agent-decision-panel__section-head">
        <h4>建议动作</h4>
        <span>{{ result.intervention_plan.actions.length }} 项处置建议</span>
      </div>
      <div class="agent-decision-panel__actions">
        <article
          v-for="item in result.intervention_plan.actions"
          :key="item.label"
          class="agent-decision-panel__action"
          :class="`agent-decision-panel__action--${item.priority}`"
        >
          <div>
            <strong>{{ item.label }}</strong>
            <p>{{ item.description }}</p>
          </div>
          <span>{{ priorityLabel(item.priority) }}</span>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentAnalyzeResponse, AgentEvidenceItem } from '@/types/agent'

const props = defineProps<{
  result: AgentAnalyzeResponse
}>()

const evidenceItems = computed<AgentEvidenceItem[]>(() => {
  if (props.result.evidence?.length) {
    return props.result.evidence
  }

  return props.result.signals.slice(0, 4).map((item) => ({
    title: `${item.modality} 风险信号`,
    source: '多模态判别引擎',
    snippet: item.signal,
    score: item.score,
    modality: item.modality,
    kind: 'model_signal',
  }))
})

const scoreText = computed(() => formatPercent(props.result.risk_score))
const intentConfidence = computed(() => formatPercent(props.result.intent.confidence))
const fraudConfidence = computed(() => formatPercent(props.result.fraud_type.confidence))
const levelLabel = computed(() => {
  if (props.result.risk_level === 'high') return '高'
  if (props.result.risk_level === 'medium') return '中'
  return '低'
})

function formatPercent(value: number) {
  return `${((value || 0) * 100).toFixed(0)}%`
}

function riskTagType(level: string) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'success'
}

function priorityLabel(priority: string) {
  if (priority === 'critical') return '立即执行'
  if (priority === 'high') return '高优先级'
  if (priority === 'medium') return '建议执行'
  return '观察'
}

function formatEvidenceTag(item: AgentEvidenceItem) {
  const parts = [item.source]
  if (item.modality) parts.push(item.modality)
  return parts.join(' · ')
}
</script>

<style scoped lang="scss">
.agent-decision-panel {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(150, 208, 255, 0.14);
}

.agent-decision-panel__header,
.agent-decision-panel__section-head,
.agent-decision-panel__evidence-meta,
.agent-decision-panel__action {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.agent-decision-panel__header {
  align-items: flex-start;
}

.agent-decision-panel__header h3,
.agent-decision-panel__section-head h4 {
  margin: 0;
}

.agent-decision-panel__header span,
.agent-decision-panel__section-head span,
.agent-decision-panel__label,
.agent-decision-panel__evidence-item small {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.agent-decision-panel__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.agent-decision-panel__overview {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.agent-decision-panel__card,
.agent-decision-panel__evidence-item,
.agent-decision-panel__action {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(150, 208, 255, 0.12);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 14%, transparent);
}

.agent-decision-panel__card {
  display: grid;
  gap: 6px;
}

.agent-decision-panel__card strong,
.agent-decision-panel__evidence-meta span,
.agent-decision-panel__action strong {
  color: var(--tech-theme-text-primary);
}

.agent-decision-panel__card p,
.agent-decision-panel__evidence-item p,
.agent-decision-panel__action p {
  margin: 0;
  color: var(--tech-theme-text-regular);
  line-height: 1.7;
}

.agent-decision-panel__section {
  margin-top: 18px;
}

.agent-decision-panel__evidence-list,
.agent-decision-panel__actions {
  display: grid;
  gap: 10px;
  margin-top: 10px;
}

.agent-decision-panel__evidence-item {
  display: grid;
  gap: 6px;
}

.agent-decision-panel__evidence-meta strong {
  color: var(--tech-theme-text-primary);
}

.agent-decision-panel__action {
  align-items: flex-start;
}

.agent-decision-panel__action span {
  flex-shrink: 0;
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.agent-decision-panel__action--critical {
  border-color: rgba(255, 107, 107, 0.24);
}

.agent-decision-panel__action--high {
  border-color: rgba(255, 195, 75, 0.24);
}

@media (max-width: 1100px) {
  .agent-decision-panel__overview {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .agent-decision-panel__header,
  .agent-decision-panel__section-head,
  .agent-decision-panel__action {
    flex-direction: column;
  }
}
</style>
