<template>
  <div>
    <h2>多模态反诈分析</h2>
    <el-tabs v-model="activeTab" style="margin-top: 16px">
      <el-tab-pane label="文本风险分析" name="text">
        <el-input v-model="textInput" type="textarea" :rows="6" placeholder="请输入聊天记录、短信内容或可疑话术..." />
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
    </el-tabs>
    <DetectionResult v-if="displayResult" :result="displayResult" class="ai-detect-view__result" />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { detectionApi } from '@/api/detection'
import { ElMessage } from 'element-plus'
import DetectionResult from '@/components/detection/DetectionResult.vue'
import FileUpload from '@/components/common/FileUpload.vue'
import type { DetectionDisplayResult } from '@/types/detection'
import { normalizeDetectionResult } from '@/utils/detectionResult'

const activeTab = ref('text')
const textInput = ref('')
const selectedFile = ref<File | null>(null)
const audioFile = ref<File | null>(null)
const imagePreviewUrl = ref('')
const displayResult = ref<DetectionDisplayResult | null>(null)
const loading = ref(false)

function revokePreviewUrl() {
  if (!imagePreviewUrl.value) return
  URL.revokeObjectURL(imagePreviewUrl.value)
  imagePreviewUrl.value = ''
}

function handleFileSelect(file: File) {
  selectedFile.value = file
  displayResult.value = null
  revokePreviewUrl()
  imagePreviewUrl.value = URL.createObjectURL(file)
}

function handleAudioSelect(uploadFile: any) {
  if (uploadFile?.raw) {
    audioFile.value = uploadFile.raw as File
    displayResult.value = null
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
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '语音分析失败')
  } finally { loading.value = false }
}

onBeforeUnmount(() => {
  revokePreviewUrl()
})
</script>

<style scoped lang="scss">
.ai-detect-view__tabs {
  margin-top: 16px;
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
</style>
