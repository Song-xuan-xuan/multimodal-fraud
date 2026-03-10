<template>
  <div :class="['news-detect-view', { 'page-shell': !embedded, 'news-detect-view--embedded': embedded }]">
    <h2 v-if="!embedded">内容风险检测</h2>

    <el-tabs v-model="activeMode" class="news-detect-view__tabs">
      <el-tab-pane label="综合检测" name="aggregate">
        <el-form label-position="top" class="news-detect-view__form">
          <el-form-item label="标题">
            <el-input v-model="aggregateForm.title" placeholder="输入新闻标题" />
          </el-form-item>
          <el-form-item label="内容">
            <el-input
              v-model="aggregateForm.content"
              type="textarea"
              :rows="8"
              placeholder="输入新闻内容"
            />
          </el-form-item>
          <el-form-item label="来源链接（可选）">
            <el-input v-model="aggregateForm.url" placeholder="输入新闻来源链接" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="detectAggregate">综合检测</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="链接检测" name="url">
        <el-form label-position="top" class="news-detect-view__form">
          <el-form-item label="新闻链接">
            <el-input v-model="urlForm.url" placeholder="输入待检测链接" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="detectUrl">链接检测</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="文件检测" name="file">
        <el-form label-position="top" class="news-detect-view__form">
          <el-form-item label="上传文件">
            <FileUpload @select="handleFileSelect" />
          </el-form-item>
          <el-form-item v-if="selectedFile" label="已选文件">
            <div class="news-detect-view__selected-file">{{ selectedFile.name }}</div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="detectFile">文件检测</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="分段检测" name="segments">
        <el-form label-position="top" class="news-detect-view__form">
          <el-form-item label="标题">
            <el-input v-model="segmentForm.title" placeholder="输入新闻标题" />
          </el-form-item>
          <el-form-item label="内容">
            <el-input
              v-model="segmentForm.content"
              type="textarea"
              :rows="8"
              placeholder="输入待分段检测内容"
            />
          </el-form-item>
          <el-form-item label="分段长度">
            <el-input-number v-model="segmentForm.segmentSize" :min="100" :step="100" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="detectSegments">分段检测</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <NewsDetectionResult
      v-if="displayResult"
      :result="displayResult"
      class="news-detect-view__result"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { detectionApi } from '@/api/detection'
import FileUpload from '@/components/common/FileUpload.vue'
import NewsDetectionResult from '@/components/detection/NewsDetectionResult.vue'
import {
  normalizeAggregateNewsDetectionResult,
  normalizeConsistencyDetectionResult,
  normalizeSegmentDetectionResult,
} from '@/utils/newsDetectionResult'
import type {
  AggregateDisplayResult,
  ConsistencyDisplayResult,
  SegmentsDisplayResult,
} from '@/types/newsDetection'

withDefaults(defineProps<{ embedded?: boolean }>(), {
  embedded: false,
})

const activeMode = ref('aggregate')
const loading = ref(false)
const selectedFile = ref<File | null>(null)
const displayResult = ref<AggregateDisplayResult | ConsistencyDisplayResult | SegmentsDisplayResult | null>(null)

const aggregateForm = reactive({
  title: '',
  content: '',
  url: '',
})

const urlForm = reactive({
  url: '',
})

const segmentForm = reactive({
  title: '',
  content: '',
  segmentSize: 500,
})

function handleFileSelect(file: File) {
  selectedFile.value = file
}

function resolveErrorMessage(error: any) {
  return error?.response?.data?.detail || '分析失败'
}

async function detectAggregate() {
  if (!aggregateForm.content.trim()) {
    return ElMessage.warning('请输入内容')
  }

  loading.value = true
  try {
    const result = await detectionApi.detectAggregate(
      aggregateForm.title,
      aggregateForm.content,
      aggregateForm.url.trim() || undefined,
    )
    displayResult.value = normalizeAggregateNewsDetectionResult(result)
  } catch (error: any) {
    ElMessage.error(resolveErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function detectUrl() {
  const url = urlForm.url.trim()
  if (!url) {
    return ElMessage.warning('请输入链接')
  }

  loading.value = true
  try {
    const result = await detectionApi.detectByUrl(url)
    displayResult.value = normalizeConsistencyDetectionResult(result)
  } catch (error: any) {
    ElMessage.error(resolveErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function detectFile() {
  if (!selectedFile.value) {
    return ElMessage.warning('请先选择文件')
  }

  loading.value = true
  try {
    const result = await detectionApi.detectByFile(selectedFile.value)
    displayResult.value = normalizeConsistencyDetectionResult(result)
  } catch (error: any) {
    ElMessage.error(resolveErrorMessage(error))
  } finally {
    loading.value = false
  }
}

async function detectSegments() {
  if (!segmentForm.content.trim()) {
    return ElMessage.warning('请输入内容')
  }

  loading.value = true
  try {
    const result = await detectionApi.detectSegments(
      segmentForm.title,
      segmentForm.content,
      segmentForm.segmentSize,
    )
    displayResult.value = normalizeSegmentDetectionResult(result)
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
