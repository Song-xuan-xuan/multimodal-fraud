<template>
  <div :class="['news-detect-view', { 'page-shell': !embedded, 'news-detect-view--embedded': embedded }]">
    <h2 v-if="!embedded">内容风险检测</h2>

    <el-form label-position="top" class="news-detect-view__form">
      <el-form-item label="标题（可选）">
        <el-input v-model="form.title" placeholder="输入新闻标题" />
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" :rows="8" placeholder="输入新闻正文内容" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="detectNews">内容检测</el-button>
      </el-form-item>
    </el-form>

    <DetectionResult v-if="displayResult" :result="displayResult" class="news-detect-view__result" />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { detectionApi } from '@/api/detection'
import DetectionResult from '@/components/detection/DetectionResult.vue'
import type { DetectionDisplayResult } from '@/types/detection'
import { normalizeDetectionResult } from '@/utils/detectionResult'

withDefaults(defineProps<{ embedded?: boolean }>(), {
  embedded: false,
})

const loading = ref(false)
const displayResult = ref<DetectionDisplayResult | null>(null)
const form = reactive({
  title: '',
  content: '',
})

function resolveErrorMessage(error: any) {
  return error?.response?.data?.detail || '分析失败'
}

async function detectNews() {
  if (!form.content.trim()) {
    return ElMessage.warning('请输入内容')
  }
  loading.value = true
  try {
    const result = await detectionApi.detectNews(form.title, form.content)
    const probability = Math.max(0, Math.min(1, Number(result.confidence ?? 0)))
    displayResult.value = normalizeDetectionResult({
      resultKind: 'text',
      rawResult: {
        label: result.label || '未知',
        probability,
        confidence: probability,
        summary: result.summary || '',
        conclusion: result.conclusion || '',
      },
      textPreview: form.content.trim(),
    })
  } catch (error: any) {
    ElMessage.error(resolveErrorMessage(error))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.news-detect-view__tabs {
  margin-top: 16px;
}

.news-detect-view__form {
  max-width: 720px;
}

.news-detect-view__selected-file {
  color: #606266;
  font-size: 14px;
}

.news-detect-view__result {
  margin-top: 16px;
}

.news-detect-view--embedded {
  padding: 0;
}
</style>
