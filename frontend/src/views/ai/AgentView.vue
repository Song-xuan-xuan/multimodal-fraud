<template>
  <div class="agent-view page-shell">
    <div class="agent-view__intro">
      <h2>多模态分析</h2>
      <p>在一个入口中综合分析文本、图片截图和语音内容，输出风险判断、案例检索与个性化建议。</p>
    </div>

    <el-card class="agent-view__card">
      <div class="agent-view__grid">
        <section class="agent-panel tech-surface">
          <div class="agent-panel__header">
            <h3>输入区</h3>
            <span>支持文本、图片、语音任意组合</span>
          </div>

          <el-form label-position="top" class="agent-form">
            <el-form-item label="可疑文本 / 聊天记录">
              <el-input v-model="text" type="textarea" :rows="6" placeholder="请输入聊天记录、短信内容、转账话术或风险描述..." />
            </el-form-item>

            <el-form-item label="图片 / 截图">
              <FileUpload @select="handleImageSelect" />
              <div v-if="imageFile" class="agent-upload-chip">已选择：{{ imageFile.name }}</div>
            </el-form-item>

            <el-form-item label="语音 / 录音文件">
              <el-upload :auto-upload="false" :show-file-list="false" :limit="1" accept="audio/*" @change="handleAudioSelect">
                <el-button>选择语音文件</el-button>
              </el-upload>
              <div v-if="audioFile" class="agent-upload-chip">已选择：{{ audioFile.name }}</div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="loading" @click="analyze">开始统一分析</el-button>
            </el-form-item>
          </el-form>
        </section>

        <section class="agent-panel tech-surface">
          <div class="agent-panel__header">
            <h3>执行摘要</h3>
            <span>专业化结论输出</span>
          </div>

          <template v-if="result">
            <div class="agent-summary">
              <div class="agent-summary__badges">
                <el-tag :type="riskTagType(result.risk_level)" effect="dark">风险等级：{{ riskLevelLabel(result.risk_level) }}</el-tag>
                <el-tag effect="plain">意图：{{ result.intent.label }}</el-tag>
                <el-tag effect="plain">主剧本：{{ result.fraud_type.label }}</el-tag>
                <el-tag v-if="result.guardian_action_needed" type="danger" effect="plain">建议通知监护人</el-tag>
              </div>
              <p class="agent-summary__text">{{ result.report.executive_summary || result.summary }}</p>
            </div>

            <div class="agent-executive-grid">
              <article class="agent-executive-card">
                <span>处置意见</span>
                <strong>{{ result.report.disposition }}</strong>
              </article>
              <article class="agent-executive-card">
                <span>建议通道</span>
                <strong>{{ result.intervention_plan.recommended_channel }}</strong>
              </article>
              <article class="agent-executive-card">
                <span>识别模态</span>
                <strong>{{ formatModalities(result.modalities_received) }}</strong>
              </article>
            </div>

            <div class="agent-section">
              <h4>自动化建议</h4>
              <ul class="agent-recommendations">
                <li v-for="item in result.report.recommended_actions" :key="item">{{ item }}</li>
              </ul>
            </div>
          </template>

          <el-empty v-else description="提交至少一种模态输入后开始分析" />
        </section>
      </div>

      <AgentDecisionPanel v-if="result" :result="result" />

      <div v-if="result" class="agent-modality-grid">
        <AgentModalityPanel
          title="文本模态"
          :score="extractScore(result.text_result)"
          :summary="extractSummary(result.text_result, '当前未使用文本输入。')"
          :extra-text="text || ''"
          :raw-result="result.text_result"
        />
        <AgentModalityPanel
          title="图片模态"
          :score="extractScore(result.image_result)"
          :summary="extractSummary(result.image_result, imageFile ? '图片已上传，等待分析摘要。' : '当前未上传图片。')"
          :extra-text="String(result.image_result?.ocr_text || imageFile?.name || '')"
          :raw-result="result.image_result"
        />
        <AgentModalityPanel
          title="语音模态"
          :score="extractScore(result.audio_result)"
          :summary="extractSummary(result.audio_result, audioFile ? '语音已上传，等待分析摘要。' : '当前未上传语音。')"
          :extra-text="String(result.audio_result?.transcript || audioFile?.name || '')"
          :raw-result="result.audio_result"
        />
      </div>

      <div v-if="result" class="agent-bottom-grid">
        <section class="agent-panel tech-surface">
          <div class="agent-panel__header">
            <h3>参考案例</h3>
            <span>RAG 检索结果</span>
          </div>
          <div v-if="result.rag_sources.length">
            <RagSourceCard v-for="(source, index) in result.rag_sources" :key="index" :source="source" />
          </div>
          <el-empty v-else description="当前未检索到相似案例" />
        </section>

        <section class="agent-panel tech-surface">
          <div class="agent-panel__header">
            <h3>画像摘要</h3>
            <span>用于动态风险调整</span>
          </div>
          <div class="agent-profile-grid">
            <div class="agent-profile-item">
              <span class="agent-profile-item__label">年龄段</span>
              <span>{{ result.profile_summary.age_group || '未设置' }}</span>
            </div>
            <div class="agent-profile-item">
              <span class="agent-profile-item__label">性别</span>
              <span>{{ result.profile_summary.gender || '未设置' }}</span>
            </div>
            <div class="agent-profile-item">
              <span class="agent-profile-item__label">职业</span>
              <span>{{ result.profile_summary.occupation || '未设置' }}</span>
            </div>
            <div class="agent-profile-item">
              <span class="agent-profile-item__label">地区</span>
              <span>{{ result.profile_summary.region || '未设置' }}</span>
            </div>
          </div>
        </section>
      </div>

      <GuardianActionCard v-if="result && result.guardian_action.priority !== 'none'" :action="result.guardian_action" />

      <AgentReportPreview v-if="result" :result="result" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import FileUpload from '@/components/common/FileUpload.vue'
import AgentDecisionPanel from '@/components/agent/AgentDecisionPanel.vue'
import RagSourceCard from '@/components/rag/RagSourceCard.vue'
import AgentModalityPanel from '@/components/agent/AgentModalityPanel.vue'
import AgentReportPreview from '@/components/agent/AgentReportPreview.vue'
import GuardianActionCard from '@/components/agent/GuardianActionCard.vue'
import { agentApi } from '@/api/agent'
import type { AgentAnalyzeResponse } from '@/types/agent'

const text = ref('')
const imageFile = ref<File | null>(null)
const audioFile = ref<File | null>(null)
const loading = ref(false)
const result = ref<AgentAnalyzeResponse | null>(null)

function handleImageSelect(file: File) {
  imageFile.value = file
}

function handleAudioSelect(uploadFile: any) {
  if (uploadFile?.raw) {
    audioFile.value = uploadFile.raw as File
  }
}

function riskTagType(level: string) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'success'
}

function riskLevelLabel(level: string) {
  if (level === 'high') return '高'
  if (level === 'medium') return '中'
  return '低'
}

function formatModalities(modalities: string[]) {
  const labels: Record<string, string> = {
    text: '文本',
    image: '图片',
    audio: '语音',
  }
  return modalities.map((item) => labels[item] || item).join(' / ') || '无'
}

function extractScore(payload: Record<string, any>) {
  const value = payload?.confidence ?? payload?.probability
  return typeof value === 'number' ? value : undefined
}

function extractSummary(payload: Record<string, any>, fallback: string) {
  return payload?.summary || payload?.label || fallback
}

async function analyze() {
  if (!text.value.trim() && !imageFile.value && !audioFile.value) {
    ElMessage.warning('请至少提供一种输入模态')
    return
  }

  loading.value = true
  try {
    result.value = await agentApi.analyze({
      text: text.value,
      image: imageFile.value,
      audio: audioFile.value,
    })
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '统一分析失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.agent-view__intro p {
  margin: 12px 0 0;
  color: var(--tech-theme-text-secondary);
}

.agent-view__card {
  margin-top: 16px;
}

.agent-view__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  gap: 16px;
}

.agent-modality-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.agent-bottom-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
  gap: 16px;
  margin-top: 16px;
}

.agent-panel {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(150, 208, 255, 0.14);
}

.agent-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 14px;
}

.agent-panel__header h3 {
  margin: 0;
  font-size: 18px;
}

.agent-panel__header span {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.agent-upload-chip {
  margin-top: 10px;
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.agent-summary {
  display: grid;
  gap: 10px;
}

.agent-summary__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.agent-summary__text {
  margin: 0;
  color: var(--tech-theme-text-primary);
  line-height: 1.7;
}

.agent-executive-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.agent-executive-card {
  display: grid;
  gap: 6px;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(150, 208, 255, 0.12);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 14%, transparent);
}

.agent-executive-card span {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.agent-executive-card strong {
  color: var(--tech-theme-text-primary);
  line-height: 1.6;
}

.agent-guardian-inline {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 107, 107, 0.24);
  background: color-mix(in srgb, #ff6b6b 12%, var(--tech-theme-surface-panel));
  color: var(--tech-theme-text-primary);
  line-height: 1.65;
}

.agent-section {
  margin-top: 18px;
}

.agent-section h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--tech-theme-text-primary);
}

.agent-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.agent-signals {
  display: grid;
  gap: 10px;
}

.agent-signal-card {
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(150, 208, 255, 0.12);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 16%, transparent);
}

.agent-signal-card__meta {
  display: inline-block;
  margin-bottom: 6px;
  font-size: 11px;
  color: var(--tech-theme-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.agent-signal-card p {
  margin: 0;
  color: var(--tech-theme-text-regular);
  line-height: 1.65;
}

.agent-recommendations {
  margin: 0;
  padding-left: 18px;
  color: var(--tech-theme-text-regular);
  line-height: 1.8;
}

.agent-profile-grid {
  display: grid;
  gap: 10px;
}

.agent-profile-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(150, 208, 255, 0.12);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 14%, transparent);
  color: var(--tech-theme-text-regular);
}

.agent-profile-item__label {
  color: var(--tech-theme-text-secondary);
}

@media (max-width: 1100px) {
  .agent-view__grid,
  .agent-bottom-grid,
  .agent-modality-grid {
    grid-template-columns: 1fr;
  }

  .agent-executive-grid {
    grid-template-columns: 1fr;
  }
}
</style>
