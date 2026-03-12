<template>
  <div class="fake-news-classify-view">
    <h2 v-if="!embedded">诈骗话术分类识别</h2>
    <el-form label-position="top" class="fake-news-classify-view__form">
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="输入标题" />
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" :rows="8" placeholder="输入正文内容" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="detect" :loading="loading">开始分类检测</el-button>
      </el-form-item>
    </el-form>
    <el-card v-if="result" class="fake-news-classify-view__card">
      <template #header>分类结果</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="分类标签">
          <el-tag :type="result.label === '可信' ? 'success' : result.label === '虚假' ? 'danger' : 'warning'">
            {{ result.label }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险评分">
          <el-progress :percentage="Math.round((result.credibility_score || 0) * 10)" />
        </el-descriptions-item>
      </el-descriptions>
      <div v-if="result.dimensions" class="fake-news-classify-view__dimensions">
        <h4>多维度分析</h4>
        <el-descriptions :column="2" border class="fake-news-classify-view__descriptions">
          <el-descriptions-item v-for="(val, key) in (result.dimensions as Record<string, number>)" :key="key" :label="dimensionLabel(String(key))">
            <el-progress :percentage="Math.round(val * 100)" :stroke-width="12" />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <el-alert v-if="result.conclusion" :title="result.conclusion" type="info" show-icon class="fake-news-classify-view__alert" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { detectionApi } from '@/api/detection'
import { ElMessage } from 'element-plus'

withDefaults(defineProps<{ embedded?: boolean }>(), {
  embedded: false,
})

const form = reactive({ title: '', content: '' })
const result = ref<any>(null)
const loading = ref(false)

const dimensionLabels: Record<string, string> = {
  title_exaggeration: '诱导性标题程度',
  content_credibility: '内容风险度',
  title_content_overlap: '话术一致性',
  sentiment_volatility: '情绪操控强度',
}

function dimensionLabel(key: string) {
  return dimensionLabels[key] || key
}

async function detect() {
  if (!form.content.trim()) return ElMessage.warning('请输入待识别的话术内容')
  loading.value = true
  try {
    result.value = await detectionApi.detectNews(form.title, form.content)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '识别失败')
  } finally { loading.value = false }
}
</script>

<style scoped lang="scss">
.fake-news-classify-view__form {
  margin-top: 16px;
  max-width: 600px;
}

.fake-news-classify-view__card {
  margin-top: 16px;
}

.fake-news-classify-view__dimensions {
  margin-top: 16px;
}

.fake-news-classify-view__descriptions {
  margin-top: 8px;
}

.fake-news-classify-view__alert {
  margin-top: 16px;
}
</style>
