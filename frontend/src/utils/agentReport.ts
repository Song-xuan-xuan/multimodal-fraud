import type { AgentAnalyzeResponse } from '@/types/agent'

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function buildEvidenceItems(result: AgentAnalyzeResponse) {
  const decisionItems = result.evidence?.slice(0, 5).map((item) => `${item.title}：${item.snippet}`)
  if (decisionItems?.length) return decisionItems
  const signalItems = result.signals.slice(0, 5).map((item) => `${item.modality}：${item.signal}`)
  return signalItems.length ? signalItems : ['当前未提取到明确的证据摘要。']
}

function formatTimestamp() {
  const now = new Date()
  const date = now.toISOString().slice(0, 10).replace(/-/g, '')
  const time = now.toTimeString().slice(0, 8).replace(/:/g, '')
  return { label: now.toLocaleString('zh-CN'), file: `${date}-${time}` }
}

function buildRecommendedActions(result: AgentAnalyzeResponse) {
  if (result.report?.recommended_actions?.length) {
    return result.report.recommended_actions
  }

  if (result.intervention_plan?.actions?.length) {
    return result.intervention_plan.actions.map((item) => `${item.label}：${item.description}`)
  }

  return result.recommendations.length ? result.recommendations : ['暂无建议']
}

export function buildAgentReportMarkdown(result: AgentAnalyzeResponse) {
  const ts = formatTimestamp()
  const evidenceItems = buildEvidenceItems(result)
  const recommendedActions = buildRecommendedActions(result)
  const findings = result.report?.findings?.length ? result.report.findings : ['当前未生成结构化发现。']

  return [
    `# ${result.report?.title || '安全监测报告'}`,
    '',
    `生成时间：${ts.label}`,
    `风险等级：${result.risk_level}`,
    `风险分数：${(result.risk_score * 100).toFixed(0)}%`,
    `识别意图：${result.intent.label}`,
    `主诈骗类型：${result.fraud_type.label}`,
    `建议通道：${result.intervention_plan.recommended_channel || '无'}`,
    '',
    '## 执行摘要',
    result.report?.executive_summary || result.summary,
    '',
    '## 主诈骗类型',
    `- ${result.fraud_type.label}（置信度 ${((result.fraud_type.confidence || 0) * 100).toFixed(0)}%）`,
    ...(result.fraud_types.length ? result.fraud_types.filter((item) => item !== result.fraud_type.label).map((item) => `- ${item}`) : []),
    '',
    '## 关键证据摘要',
    ...evidenceItems.map((item) => `- ${item}`),
    '',
    '## 报告发现',
    ...findings.map((item) => `- ${item}`),
    '',
    '## 用户画像摘要',
    `- 年龄段：${result.profile_summary.age_group || '未设置'}`,
    `- 性别：${result.profile_summary.gender || '未设置'}`,
    `- 职业：${result.profile_summary.occupation || '未设置'}`,
    `- 地区：${result.profile_summary.region || '未设置'}`,
    '',
    '## 干预策略',
    `- 处置意见：${result.report?.disposition || result.intervention_plan.headline || '暂无'}`,
    `- 干预摘要：${result.intervention_plan.summary || '暂无'}`,
    ...((result.intervention_plan?.actions || []).length
      ? result.intervention_plan.actions.map((item) => `  - [${item.priority}] ${item.label}：${item.description}`)
      : ['  - 暂无干预动作']),
    '',
    '## 监护人联动建议',
    `- 是否建议联动：${result.guardian_action_needed ? '是' : '否'}`,
    `- 联动优先级：${result.guardian_action?.priority || 'none'}`,
    `- 联动说明：${result.guardian_action?.notice || '暂无'}`,
    `- 联动对象：${result.guardian_action?.target_role || '监护人/家属'}`,
    `- 建议通知模板：${result.guardian_action?.message_template || '暂无'}`,
    ...(result.guardian_action?.checklist?.length ? result.guardian_action.checklist.map((item) => `  - ${item}`) : ['  - 暂无处置清单']),
    '',
    '## 建议动作',
    ...recommendedActions.map((item) => `- ${item}`),
  ].join('\n')
}

export function buildAgentReportHtml(result: AgentAnalyzeResponse) {
  const ts = formatTimestamp()
  const evidenceItems = buildEvidenceItems(result)
  const recommendedActions = buildRecommendedActions(result)
  const findings = result.report?.findings?.length ? result.report.findings : ['当前未生成结构化发现。']
  const fraudTags = result.fraud_types.length
    ? result.fraud_types.map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join('')
    : `<span class="tag">${escapeHtml(result.fraud_type.label)}</span>`
  const recommendationItems = recommendedActions.length
    ? recommendedActions.map((item) => `<li>${escapeHtml(item)}</li>`).join('')
    : '<li>暂无建议</li>'
  const evidenceList = evidenceItems.map((item) => `<li>${escapeHtml(item)}</li>`).join('')
  const findingsList = findings.map((item) => `<li>${escapeHtml(item)}</li>`).join('')
  const guardianList = (result.guardian_action?.checklist?.length
    ? result.guardian_action.checklist
    : ['暂无处置清单']
  ).map((item) => `<li>${escapeHtml(item)}</li>`).join('')

  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>安全监测报告</title>
  <style>
    body { font-family: "Microsoft YaHei", sans-serif; background: #07152b; color: #eaf4ff; margin: 0; padding: 32px; }
    .shell { max-width: 980px; margin: 0 auto; }
    .card { background: linear-gradient(180deg, rgba(16,34,61,.95), rgba(7,20,39,.98)); border: 1px solid rgba(150,208,255,.16); border-radius: 18px; padding: 24px; margin-bottom: 18px; }
    h1,h2 { margin: 0 0 12px; }
    .meta { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; margin-top: 16px; }
    .meta-item { background: rgba(255,255,255,.03); border-radius: 14px; padding: 12px 14px; }
    .label { font-size: 12px; color: #93a7c2; display: block; margin-bottom: 6px; }
    .tag { display: inline-block; margin: 0 8px 8px 0; padding: 6px 10px; border-radius: 999px; border: 1px solid rgba(255,107,107,.3); color: #ffd9d9; }
    ul { margin: 10px 0 0; padding-left: 20px; line-height: 1.8; }
    .guardian { border-color: rgba(255,107,107,.32); background: linear-gradient(180deg, rgba(94,16,24,.95), rgba(60,12,18,.98)); }
  </style>
</head>
<body>
  <div class="shell">
    <section class="card">
      <h1>${escapeHtml(result.report?.title || '安全监测报告')}</h1>
      <p>生成时间：${escapeHtml(ts.label)}</p>
      <div class="meta">
        <div class="meta-item"><span class="label">风险等级</span><strong>${escapeHtml(result.risk_level)}</strong></div>
        <div class="meta-item"><span class="label">风险分数</span><strong>${(result.risk_score * 100).toFixed(0)}%</strong></div>
        <div class="meta-item"><span class="label">识别意图</span><strong>${escapeHtml(result.intent.label)}</strong></div>
        <div class="meta-item"><span class="label">处置意见</span><strong>${escapeHtml(result.report?.disposition || result.intervention_plan.headline || '暂无')}</strong></div>
      </div>
    </section>

    <section class="card">
      <h2>执行摘要</h2>
      <p>${escapeHtml(result.report?.executive_summary || result.summary)}</p>
    </section>

    <section class="card">
      <h2>主诈骗类型</h2>
      <div>${fraudTags}</div>
    </section>

    <section class="card">
      <h2>关键证据摘要</h2>
      <ul>${evidenceList}</ul>
    </section>

    <section class="card">
      <h2>报告发现</h2>
      <ul>${findingsList}</ul>
    </section>

    <section class="card">
      <h2>用户画像摘要</h2>
      <ul>
        <li>年龄段：${escapeHtml(result.profile_summary.age_group || '未设置')}</li>
        <li>性别：${escapeHtml(result.profile_summary.gender || '未设置')}</li>
        <li>职业：${escapeHtml(result.profile_summary.occupation || '未设置')}</li>
        <li>地区：${escapeHtml(result.profile_summary.region || '未设置')}</li>
      </ul>
    </section>

    <section class="card">
      <h2>干预策略</h2>
      <p>${escapeHtml(result.intervention_plan.summary || '暂无')}</p>
      <ul>${(result.intervention_plan.actions || []).map((item) => `<li>${escapeHtml(`${item.label}：${item.description}`)}</li>`).join('') || '<li>暂无干预动作</li>'}</ul>
    </section>

    <section class="card guardian">
      <h2>监护人联动建议</h2>
      <p>${escapeHtml(result.guardian_action?.notice || '暂无监护人联动建议。')}</p>
      <p>联动对象：${escapeHtml(result.guardian_action?.target_role || '监护人/家属')}</p>
      <p>建议通知模板：${escapeHtml(result.guardian_action?.message_template || '暂无')}</p>
      <ul>${guardianList}</ul>
    </section>

    <section class="card">
      <h2>建议动作</h2>
      <ul>${recommendationItems}</ul>
    </section>
  </div>
</body>
</html>`
}

export function downloadAgentReportHtml(result: AgentAnalyzeResponse) {
  const html = buildAgentReportHtml(result)
  const ts = formatTimestamp()
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `anti-fraud-report-${result.risk_level}-${ts.file}.html`
  anchor.click()
  URL.revokeObjectURL(url)
}

export async function copyAgentReportMarkdown(result: AgentAnalyzeResponse) {
  const markdown = buildAgentReportMarkdown(result)
  await navigator.clipboard.writeText(markdown)
}

export function printAgentReport(result: AgentAnalyzeResponse) {
  const html = buildAgentReportHtml(result)
  const popup = window.open('', '_blank', 'width=1200,height=900')
  if (!popup) return false
  popup.document.open()
  popup.document.write(html)
  popup.document.close()
  popup.focus()
  popup.print()
  return true
}
