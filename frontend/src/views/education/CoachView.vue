<template>
  <div class="coach-view page-shell">
    <div class="coach-view__intro">
      <h2>反诈教练</h2>
      <p>围绕你的训练薄弱点，向反诈教练提问并获得可执行学习建议。</p>
    </div>

    <el-card class="coach-view__card">
      <div class="coach-view__form">
        <div class="coach-view__headline">
          <span>输入你的训练困惑，教练会给出分步学习动作。</span>
        </div>

        <div class="coach-view__quick-prompts">
          <el-button
            v-for="(item, idx) in quickPrompts"
            :key="idx"
            text
            class="coach-view__prompt-chip"
            @click="question = item"
          >
            {{ item }}
          </el-button>
        </div>

        <el-input
          v-model="question"
          type="textarea"
          :rows="5"
          resize="none"
          placeholder="例如：我总是被“官方客服+紧急处理”带节奏，如何建立稳定核验习惯？"
        />

        <el-input
          v-model.number="score"
          type="number"
          placeholder="可选：填写最近一次测试分数（0-100）"
          min="0"
          max="100"
        />

        <el-select v-model="wrongTopics" multiple filterable allow-create default-first-option placeholder="可选：输入你的薄弱主题">
          <el-option label="虚假客服退款" value="虚假客服退款" />
          <el-option label="兼职刷单" value="兼职刷单" />
          <el-option label="虚假征信" value="虚假征信" />
          <el-option label="AI 语音冒充" value="AI 语音冒充" />
          <el-option label="投资理财诈骗" value="投资理财诈骗" />
        </el-select>

        <div class="coach-view__action-row">
          <el-button class="change-button" :loading="loading" @click="submit">向教练提问</el-button>
          <el-button text @click="resetForm">清空输入</el-button>
        </div>
      </div>

      <div v-if="result" class="coach-view__result">
        <h3>教练建议</h3>
        <p>{{ result.reply }}</p>
        <ul>
          <li v-for="(action, idx) in result.actions" :key="idx">{{ action }}</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { educationApi, type EducationCoachResponse } from '@/api/education'

const question = ref('')
const score = ref<number | undefined>(undefined)
const wrongTopics = ref<string[]>([])
const loading = ref(false)
const result = ref<EducationCoachResponse | null>(null)
const quickPrompts = [
  '我总在“紧急处理”场景里慌张，怎么训练稳定节奏？',
  '刷单和投资骗局有哪些共性触发词？',
  '如何建立一套简单可执行的核验清单？',
]

async function submit() {
  const prompt = question.value.trim()
  if (!prompt) {
    ElMessage.warning('请输入训练问题')
    return
  }
  loading.value = true
  try {
    result.value = await educationApi.askCoach({
      question: prompt,
      score: typeof score.value === 'number' ? score.value : undefined,
      wrong_topics: wrongTopics.value,
    })
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '教练回复失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  question.value = ''
  score.value = undefined
  wrongTopics.value = []
  result.value = null
}
</script>

<style scoped lang="scss">
.coach-view__intro p {
  margin-top: 12px;
  color: var(--tech-theme-text-secondary);
}

.coach-view__card {
  margin-top: 18px;
  border: 1px solid rgba(0, 224, 255, 0.2);
  background: linear-gradient(180deg, rgba(0, 30, 60, 0.65), rgba(0, 16, 40, 0.6));
}

.coach-view__form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.coach-view__headline {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--tech-theme-text-secondary);
}

.coach-view__quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.coach-view__prompt-chip {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0, 224, 255, 0.28);
  color: #84f8ff;
  background: rgba(0, 176, 255, 0.08);
}

.coach-view__action-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.coach-view__result {
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px dashed rgba(0, 224, 255, 0.3);
  background: rgba(0, 32, 64, 0.45);
}

.coach-view__result p,
.coach-view__result ul {
  color: var(--tech-theme-text-secondary);
}

.coach-view__result ul {
  margin-top: 8px;
  padding-left: 18px;
}

.change-button {
  background: linear-gradient(90deg, #00d8ff, #29b2ff);
  color: #fff;
  border: none;
  box-shadow: 0 0 16px rgba(0, 216, 255, 0.35);
}
</style>
