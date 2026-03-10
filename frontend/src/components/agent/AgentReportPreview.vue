<template>
  <section class="agent-report-preview tech-surface">
    <div class="agent-report-preview__header">
      <div>
        <h3>安全监测报告预览</h3>
        <span>可用于导出正式报告</span>
      </div>
      <div class="agent-report-preview__actions">
        <el-button size="small" plain @click="handleExportHtml">导出 HTML</el-button>
        <el-button size="small" plain @click="handleCopyMarkdown">复制 Markdown</el-button>
        <el-button size="small" plain @click="handlePrint">打印 / 导出 PDF</el-button>
      </div>
    </div>

    <div v-if="result.guardian_action_needed" class="agent-guardian-card">
      <div class="agent-guardian-card__title">建议监护人联动</div>
      <p>{{ result.guardian_action.notice }}</p>
    </div>

    <div class="agent-report-preview__section">
      <span class="agent-report-preview__label">执行摘要</span>
      <p>{{ result.report.executive_summary || result.summary }}</p>
    </div>

    <div class="agent-report-preview__grid">
      <div class="agent-report-preview__item">
        <span class="agent-report-preview__label">风险等级</span>
        <strong>{{ result.risk_level }}</strong>
      </div>
      <div class="agent-report-preview__item">
        <span class="agent-report-preview__label">风险分数</span>
        <strong>{{ (result.risk_score * 100).toFixed(0) }}%</strong>
      </div>
      <div class="agent-report-preview__item">
        <span class="agent-report-preview__label">识别意图</span>
        <strong>{{ result.intent.label }}</strong>
      </div>
      <div class="agent-report-preview__item">
        <span class="agent-report-preview__label">处置意见</span>
        <strong>{{ result.report.disposition || result.intervention_plan.headline }}</strong>
      </div>
    </div>

    <div class="agent-report-preview__section">
      <span class="agent-report-preview__label">关键证据摘要</span>
      <ul>
        <li v-for="item in evidenceItems" :key="item">{{ item }}</li>
      </ul>
    </div>

    <div class="agent-report-preview__section">
      <span class="agent-report-preview__label">主诈骗类型</span>
      <div class="agent-report-preview__tags">
        <el-tag type="danger" effect="plain">{{ result.fraud_type.label }}</el-tag>
        <el-tag v-for="item in secondaryFraudTypes" :key="item" effect="plain">{{ item }}</el-tag>
      </div>
    </div>

    <div class="agent-report-preview__section">
      <span class="agent-report-preview__label">建议动作</span>
      <ul>
        <li v-for="item in recommendedActions" :key="item">{{ item }}</li>
      </ul>
    </div>

    <div class="agent-report-preview__section">
      <span class="agent-report-preview__label">报告发现</span>
      <ul>
        <li v-for="item in reportFindings" :key="item">{{ item }}</li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { AgentAnalyzeResponse } from '@/types/agent'
import { copyAgentReportMarkdown, downloadAgentReportHtml, printAgentReport } from '@/utils/agentReport'

const props = defineProps<{
  result: AgentAnalyzeResponse
}>()

const evidenceItems = computed(() => {
  const decisionItems = props.result.evidence?.slice(0, 5).map((item) => `${item.title}：${item.snippet}`)
  if (decisionItems?.length) return decisionItems
  const signalItems = props.result.signals.slice(0, 5).map((item) => `${item.modality}：${item.signal}`)
  if (signalItems.length) return signalItems
  return ['当前未提取到明确的证据摘要。']
})

const secondaryFraudTypes = computed(() => props.result.fraud_types.filter((item) => item !== props.result.fraud_type.label))
const reportFindings = computed(() => props.result.report.findings?.length ? props.result.report.findings : ['当前未生成结构化发现。'])
const recommendedActions = computed(() => {
  if (props.result.report.recommended_actions?.length) {
    return props.result.report.recommended_actions
  }
  if (props.result.intervention_plan.actions?.length) {
    return props.result.intervention_plan.actions.map((item) => `${item.label}：${item.description}`)
  }
  return props.result.recommendations.length ? props.result.recommendations : ['当前未生成建议动作。']
})

function handleExportHtml() {
  downloadAgentReportHtml(props.result)
  ElMessage.success('HTML 报告已导出')
}

async function handleCopyMarkdown() {
  try {
    await copyAgentReportMarkdown(props.result)
    ElMessage.success('Markdown 报告已复制')
  } catch {
    ElMessage.error('复制 Markdown 失败，请检查浏览器权限')
  }
}

function handlePrint() {
  const ok = printAgentReport(props.result)
  if (!ok) {
    ElMessage.error('无法打开打印窗口，请检查浏览器拦截设置')
  }
}
</script>

<style scoped lang="scss">
.agent-report-preview {
  margin-top: 16px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(150, 208, 255, 0.14);
}

.agent-report-preview__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 14px;
}

.agent-report-preview__header h3 {
  margin: 0;
  font-size: 18px;
}

.agent-report-preview__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.agent-report-preview__header span,
.agent-report-preview__label {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.agent-guardian-card {
  margin-bottom: 14px;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(255, 107, 107, 0.28);
  background: linear-gradient(180deg, rgba(94, 16, 24, 0.88), rgba(60, 12, 18, 0.96));
}

.agent-guardian-card__title {
  color: #ffd6d6;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 6px;
}

.agent-guardian-card p,
.agent-report-preview__section p,
.agent-report-preview__section ul {
  margin: 8px 0 0;
  color: var(--tech-theme-text-regular);
  line-height: 1.75;
}

.agent-report-preview__section {
  margin-top: 14px;
}

.agent-report-preview__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.agent-report-preview__item {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(150, 208, 255, 0.12);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 12%, transparent);
}

.agent-report-preview__item strong {
  color: var(--tech-theme-text-primary);
}

.agent-report-preview__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

@media (max-width: 720px) {
  .agent-report-preview__grid {
    grid-template-columns: 1fr;
  }

  .agent-report-preview__header {
    flex-direction: column;
  }
}
</style>
