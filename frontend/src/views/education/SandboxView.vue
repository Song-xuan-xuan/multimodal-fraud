<template>
  <div class="sandbox-view page-shell">
    <div class="sandbox-view__intro">
      <h2>沙盒实验</h2>
      <p>在安全环境中体验反诈风险检测。输入任意聊天片段或可疑话术，查看系统的综合分析结果。</p>
    </div>

    <el-form label-position="top" class="sandbox-view__form">
      <el-form-item label="新闻文本">
        <el-input v-model="text" type="textarea" :rows="6" placeholder="请输入新闻正文..." />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="analyze" :loading="loading">开始分析</el-button>
      </el-form-item>
    </el-form>

    <DetectionResult v-if="result" :result="result" class="sandbox-view__result" />
    <el-card v-if="result?.ai_text_detection" class="sandbox-view__meta-card">
      <h4>附加说明</h4>
      <p>系统会结合风险话术特征、表达模式与上下文给出综合判断。</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/index'
import DetectionResult from '@/components/detection/DetectionResult.vue'

const text = ref('')
const loading = ref(false)
const result = ref<any | null>(null)

async function analyze() {
  if (!text.value.trim()) return ElMessage.warning('请输入待分析文本')
  loading.value = true
  try {
    const { data } = await api.post('/detection/news', { text: text.value })
    result.value = data
  } catch {
    ElMessage.error('分析失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.sandbox-view__intro p {
  margin: 12px 0 0;
  color: var(--tech-theme-text-secondary);
}

.sandbox-view__form {
  max-width: 700px;
}

.sandbox-view__result {
  margin-top: 16px;
}

.sandbox-view__meta-card {
  margin-top: 12px;
}

.sandbox-view__meta-card p {
  margin-top: 8px;
  color: var(--tech-theme-text-secondary);
}
</style>


