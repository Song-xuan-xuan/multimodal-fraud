<template>
  <div class="ai-detect-view page-shell">
    <section class="ai-detect-view__hero">
      <div class="ai-detect-view__hero-copy">
        <p class="ai-detect-view__eyebrow">专项分析工作台</p>
        <h2>风险分析能力</h2>
      </div>
      <div class="ai-detect-view__hero-badges">
        <span>文本 / 图片 / 语音</span>
        <span>内容核验</span>
        <span>诈骗话术分类</span>
        <span>外部证据检索</span>
      </div>
    </section>

    <el-tabs v-model="activeWorkspace" class="ai-detect-view__workspace-tabs">
      <el-tab-pane label="专项风险检测" name="multimodal">
        <section class="ai-detect-view__workspace-panel">
          <div class="ai-detect-view__panel-header">
            <div>
              <h3>风控分析</h3>
              <p>保留原有文本、截图和语音检测能力，作为专项分析里的第一类核心工具。</p>
            </div>
          </div>

          <el-tabs v-model="activeTab" class="ai-detect-view__tool-tabs">
            <el-tab-pane label="文本风险分析" name="text">
              <el-input
                v-model="textInput"
                type="textarea"
                :rows="6"
                placeholder="请输入聊天记录、短信内容或可疑话术..."
              />
              <el-button type="primary" @click="detectText" :loading="loading" class="ai-detect-view__action">分析</el-button>
            </el-tab-pane>
            <el-tab-pane label="截图风险分析" name="image">
              <FileUpload @select="handleFileSelect" />
              <div v-if="imagePreviewUrl" class="ai-detect-view__preview-card">
                <div class="ai-detect-view__preview-label">待分析截图预览</div>
                <img :src="imagePreviewUrl" alt="待分析截图预览" class="ai-detect-view__preview-image" />
              </div>
              <el-button type="primary" @click="detectImage" :loading="loading" :disabled="!selectedFile" class="ai-detect-view__action">分析</el-button>
            </el-tab-pane>
            <el-tab-pane label="语音风险分析" name="audio">
              <el-upload :auto-upload="false" :show-file-list="false" :limit="1" accept="audio/*" @change="handleAudioSelect">
                <el-button>选择音频文件</el-button>
              </el-upload>
              <div v-if="audioFile" class="ai-detect-view__preview-card">
                <div class="ai-detect-view__preview-label">待分析语音文件</div>
                <div class="ai-detect-view__audio-name">{{ audioFile.name }}</div>
              </div>
              <el-button type="primary" @click="detectAudio" :loading="loading" :disabled="!audioFile" class="ai-detect-view__action">分析</el-button>
            </el-tab-pane>
            <el-tab-pane label="链接检测" name="url">
              <el-input v-model="urlInput" placeholder="请输入新闻链接（http/https）" />
              <el-button type="primary" @click="detectUrl" :loading="loading" class="ai-detect-view__action">链接检测</el-button>
            </el-tab-pane>
          </el-tabs>

          <DetectionResult v-if="activeTab !== 'url' && displayResult" :result="displayResult" class="ai-detect-view__result" />
          <NewsDetectionResult v-if="activeTab === 'url' && urlResult" :result="urlResult" class="ai-detect-view__result" />
        </section>
      </el-tab-pane>
<!-- 
      <el-tab-pane label="内容风险检测" name="news">
        <section class="ai-detect-view__workspace-panel">
          <NewsDetectView v-if="activeWorkspace === 'news'" embedded />
        </section>
      </el-tab-pane> -->

      <el-tab-pane label="话术分类识别" name="classify">
        <section class="ai-detect-view__workspace-panel">
          <FakeNewsClassifyView v-if="activeWorkspace === 'classify'" embedded />
        </section>
      </el-tab-pane>

      <el-tab-pane label="风险核验" name="fact-check">
        <section class="ai-detect-view__workspace-panel">
          <FactCheckView v-if="activeWorkspace === 'fact-check'" embedded />
        </section>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { detectionApi } from '@/api/detection'
import { ElMessage } from 'element-plus'
import DetectionResult from '@/components/detection/DetectionResult.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import NewsDetectView from '@/views/detection/NewsDetectView.vue'
import FakeNewsClassifyView from '@/views/detection/FakeNewsClassifyView.vue'
import FactCheckView from '@/views/fact-check/FactCheckView.vue'
import type { DetectionDisplayResult } from '@/types/detection'
import { normalizeDetectionResult } from '@/utils/detectionResult'
import NewsDetectionResult from '@/components/detection/NewsDetectionResult.vue'
import type { ConsistencyDisplayResult } from '@/types/newsDetection'
import { normalizeConsistencyDetectionResult } from '@/utils/newsDetectionResult'

const activeWorkspace = ref('multimodal')
const activeTab = ref('text')
const textInput = ref('')
const selectedFile = ref<File | null>(null)
const audioFile = ref<File | null>(null)
const imagePreviewUrl = ref('')
const displayResult = ref<DetectionDisplayResult | null>(null)
const urlInput = ref('')
const urlResult = ref<ConsistencyDisplayResult | null>(null)
const loading = ref(false)

function revokePreviewUrl() {
  if (!imagePreviewUrl.value) return
  URL.revokeObjectURL(imagePreviewUrl.value)
  imagePreviewUrl.value = ''
}

function handleFileSelect(file: File) {
  selectedFile.value = file
  displayResult.value = null
  urlResult.value = null
  revokePreviewUrl()
  imagePreviewUrl.value = URL.createObjectURL(file)
}

function handleAudioSelect(uploadFile: any) {
  if (uploadFile?.raw) {
    audioFile.value = uploadFile.raw as File
    displayResult.value = null
    urlResult.value = null
  }
}

async function detectText() {
  if (!textInput.value.trim()) return ElMessage.warning('请输入聊天记录或可疑文本')
  loading.value = true
  try {
    const rawResult = await detectionApi.detectAIText(textInput.value)
    displayResult.value = normalizeDetectionResult({
      resultKind: 'text',
      rawResult,
      textPreview: textInput.value.trim(),
    })
    urlResult.value = null
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '分析失败')
  } finally { loading.value = false }
}

async function detectImage() {
  if (!selectedFile.value) return
  loading.value = true
  try {
    const rawResult = await detectionApi.detectAIImage(selectedFile.value)
    displayResult.value = normalizeDetectionResult({
      resultKind: 'image',
      rawResult,
      imagePreviewUrl: imagePreviewUrl.value,
    })
    urlResult.value = null
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '分析失败')
  } finally { loading.value = false }
}

async function detectAudio() {
  if (!audioFile.value) return ElMessage.warning('请先选择语音文件')
  loading.value = true
  try {
    const rawResult = await detectionApi.detectAudioRisk(audioFile.value)
    displayResult.value = normalizeDetectionResult({
      resultKind: 'audio',
      rawResult,
      textPreview: rawResult.transcript || '',
    })
    urlResult.value = null
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '语音分析失败')
  } finally { loading.value = false }
}

async function detectUrl() {
  const url = urlInput.value.trim()
  if (!url) return ElMessage.warning('请输入链接')
  loading.value = true
  try {
    const rawResult = await detectionApi.detectByUrl(url)
    urlResult.value = normalizeConsistencyDetectionResult(rawResult)
    displayResult.value = null
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '链接检测失败')
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  revokePreviewUrl()
})
</script>

<style scoped lang="scss">
.ai-detect-view {
  display: grid;
  gap: 18px;
}

.ai-detect-view__hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(78, 183, 255, 0.18);
  border-radius: 26px;
  background:
    radial-gradient(circle at top left, rgba(20, 129, 255, 0.18), transparent 44%),
    linear-gradient(180deg, rgba(9, 31, 58, 0.92), rgba(5, 18, 35, 0.96));
  box-shadow: 0 18px 48px rgba(0, 7, 19, 0.36);
}

.ai-detect-view__eyebrow {
  margin: 0 0 8px;
  color: #55e4ff;
  font-size: 13px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.ai-detect-view__hero h2 {
  margin: 0;
  color: #eef8ff;
  font-size: clamp(28px, 3vw, 38px);
  line-height: 1.14;
}

.ai-detect-view__summary {
  max-width: 68ch;
  margin: 12px 0 0;
  color: rgba(219, 237, 255, 0.82);
  line-height: 1.7;
}

.ai-detect-view__hero-badges {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  justify-content: flex-end;
  gap: 10px;
  max-width: 360px;
}

.ai-detect-view__hero-badges span {
  min-height: 42px;
  padding: 10px 14px;
  border: 1px solid rgba(113, 205, 255, 0.22);
  border-radius: 999px;
  background: rgba(7, 20, 38, 0.56);
  color: #dff6ff;
  font-size: 14px;
  white-space: nowrap;
}

.ai-detect-view__workspace-tabs {
  margin-top: 2px;
}

.ai-detect-view__workspace-panel {
  padding: 22px 24px 26px;
  border: 1px solid rgba(144, 204, 255, 0.14);
  border-radius: 26px;
  background: linear-gradient(180deg, rgba(8, 24, 44, 0.88), rgba(5, 16, 31, 0.96));
  backdrop-filter: blur(16px);
}

.ai-detect-view__panel-header {
  margin-bottom: 16px;
}

.ai-detect-view__panel-header h3 {
  margin: 0;
  color: #eef8ff;
  font-size: 22px;
}

.ai-detect-view__panel-header p {
  margin: 8px 0 0;
  color: rgba(214, 232, 248, 0.78);
  line-height: 1.68;
}

.ai-detect-view__tool-tabs {
  margin-top: 10px;
}

.ai-detect-view__action {
  margin-top: 12px;
}

.ai-detect-view__preview-card {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid rgba(163, 206, 255, 0.16);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(15, 33, 58, 0.68), rgba(8, 16, 30, 0.96));
}

.ai-detect-view__preview-label {
  margin-bottom: 12px;
  color: #c4d3e3;
  font-size: 14px;
}

.ai-detect-view__preview-image {
  display: block;
  width: 100%;
  max-width: 360px;
  border-radius: 16px;
  object-fit: cover;
}

.ai-detect-view__audio-name {
  color: #eef6ff;
  word-break: break-all;
}

.ai-detect-view__result {
  margin-top: 16px;
}

@media (max-width: 1080px) {
  .ai-detect-view__hero {
    grid-template-columns: 1fr;
  }

  .ai-detect-view__hero-badges {
    justify-content: flex-start;
    max-width: none;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .ai-detect-view__hero,
  .ai-detect-view__workspace-panel {
    animation: ai-detect-panel-enter 280ms ease-out;
  }
}

@keyframes ai-detect-panel-enter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
