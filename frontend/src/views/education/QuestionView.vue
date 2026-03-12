<template>
  <div class="question-view page-shell">
    <div class="question-view__intro">
      <h2>反诈实战测试</h2>
      <p>按阶段抽取训练题，结合 DeepSeek 新题与精选题库，持续提升你的识诈、核验与处置能力。</p>
    </div>

    <div class="question-view__toolbar">
      <div class="question-view__toolbar-actions">
        <el-button @click="fetchQuestions(false)" :loading="loading">重抽题目</el-button>
        <el-button class = 'change-button' type="primary" plain @click="fetchQuestions(true)" :loading="refreshing">换一批</el-button>
      </div>
    </div>

    <el-alert
      v-if="questions.length"
      :title="`当前共 ${questions.length} 题，覆盖 ${questionTagsLabel}`"
      type="info"
      :closable="false"
      class="question-view__summary"
    />

    <div v-if="loading && !questions.length" class="question-view__loading">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else-if="!submitted">
      <el-card v-for="(q, qi) in questions" :key="q.question_id" class="question-view__question-card">
        <div class="question-view__question-meta">
          <el-tag size="small" effect="dark">{{ difficultyLabel(q.difficulty) }}</el-tag>
          <el-tag size="small" type="info">{{ q.category }}</el-tag>
          <el-tag size="small" type="success">{{ q.source_type === 'generated' ? 'DeepSeek 新题' : '精选题库' }}</el-tag>
        </div>
        <h4>{{ qi + 1 }}. {{ q.question }}</h4>
        <p class="question-view__question-type">{{ q.fraud_type }}</p>
        <el-radio-group v-model="answers[q.question_id]" class="question-view__options">
          <el-radio v-for="(opt, oi) in q.options" :key="oi" :value="oi">{{ opt }}</el-radio>
        </el-radio-group>
      </el-card>
      <el-button type="primary" @click="submit" :disabled="!allAnswered || submitting" :loading="submitting">提交答案</el-button>
    </div>

    <el-card v-else class="question-view__result-card">
      <template #header>测试结果</template>
      <el-result :icon="result?.passed ? 'success' : 'warning'" :title="`得分: ${result?.correct || 0} / ${result?.total || 0}`">
        <template #sub-title>
          {{ resultSummary }}
        </template>
        <template #extra>
          <el-button type="primary" @click="reset">重新测试</el-button>
          <el-button plain @click="fetchQuestions(true)">生成新题</el-button>
        </template>
      </el-result>

      <el-card v-if="result" class="question-view__diagnosis-card" shadow="never">
        <template #header>学习诊断</template>
        <p class="question-view__diagnosis-summary">{{ result.summary }}</p>
        <div class="question-view__diagnosis-tags">
          <el-tag type="warning">风险画像：{{ riskProfileLabel(result.risk_profile) }}</el-tag>
          <el-tag type="info">推荐阶段：{{ difficultyLabel(result.recommended_stage) }}</el-tag>
        </div>

        <div v-if="result.weaknesses?.length" class="question-view__weakness-list">
          <div v-for="item in result.weaknesses" :key="item.fraud_type" class="question-view__weakness-item">
            <p class="question-view__weakness-title">
              {{ item.fraud_type }}
              <el-tag size="small" type="danger">错 {{ item.wrong_count }}/{{ item.total }}</el-tag>
              <el-tag size="small" effect="plain">正确率 {{ item.accuracy }}%</el-tag>
            </p>
            <p class="question-view__weakness-tip">{{ item.suggestion }}</p>
          </div>
        </div>

        <ul v-if="result.next_actions?.length" class="question-view__next-actions">
          <li v-for="(action, ai) in result.next_actions" :key="ai">{{ action }}</li>
        </ul>

        <div class="question-view__learning-panel">
          <p class="question-view__learning-title">学习目标</p>
          <p class="question-view__learning-objective">{{ result.learning_objective }}</p>

          <div class="question-view__learning-grid">
            <div class="question-view__learning-block">
              <p class="question-view__block-title">知识盲区</p>
              <ul>
                <li v-for="(item, idx) in result.knowledge_gaps" :key="`gap-${idx}`">{{ item }}</li>
              </ul>
            </div>
            <div class="question-view__learning-block">
              <p class="question-view__block-title">微课卡片</p>
              <ul>
                <li v-for="(item, idx) in result.micro_lessons" :key="`lesson-${idx}`">{{ item }}</li>
              </ul>
            </div>
            <div class="question-view__learning-block">
              <p class="question-view__block-title">高频误区</p>
              <ul>
                <li v-for="(item, idx) in result.common_mistakes" :key="`mistake-${idx}`">{{ item }}</li>
              </ul>
            </div>
          </div>

          <p class="question-view__coach-feedback">{{ result.coach_feedback }}</p>
        </div>

        <div v-if="result.recent_trend?.length" class="question-view__trend">
          <p class="question-view__trend-title">近3次训练趋势</p>
          <div class="question-view__trend-list">
            <div v-for="(point, ti) in result.recent_trend" :key="`${point.timestamp}-${ti}`" class="question-view__trend-item">
              <span>{{ formatTrendTime(point.timestamp) }}</span>
              <!-- <strong>{{ point.score }} 分</strong> -->
              <el-tag size="small" :type="point.passed ? 'success' : 'danger'">{{ point.passed ? '通过' : '未通过' }}</el-tag>
            </div>
          </div>
          <p
            v-if="result.trend_delta !== null && result.trend_delta !== undefined"
            :class="['question-view__trend-delta', result.trend_delta >= 0 ? 'is-up' : 'is-down']"
          >
            较上次 {{ result.trend_delta >= 0 ? '提升' : '下降' }} {{ Math.abs(result.trend_delta) }} 分
          </p>
        </div>

      </el-card>

      <div class="question-view__answers">
        <div v-for="(detail, qi) in result?.details || []" :key="detail.question_id" class="question-view__answer-item">
          <div class="question-view__answer-head">
            <p><strong>{{ qi + 1 }}. {{ detail.question }}</strong></p>
            <el-tag size="small" :type="detail.is_correct ? 'success' : 'danger'">
              {{ detail.is_correct ? '回答正确' : '需要复盘' }}
            </el-tag>
          </div>
          <p :class="['question-view__answer-status', detail.is_correct ? 'is-correct' : 'is-wrong']">
            你的答案: {{ resolveOption(detail.options, detail.selected) }}
          </p>
          <p class="question-view__answer-correct">正确答案: {{ resolveOption(detail.options, detail.correct_answer) }}</p>
          <p class="question-view__answer-explanation">{{ detail.explanation }}</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { educationApi, type EducationQuestionItem, type SubmitTestResponse } from '@/api/education'

const questions = ref<EducationQuestionItem[]>([])
const answers = ref<Record<string, number>>({})
const submitted = ref(false)
const loading = ref(false)
const refreshing = ref(false)
const submitting = ref(false)
const result = ref<SubmitTestResponse | null>(null)

const allAnswered = computed(() => questions.value.length > 0 && questions.value.every((question) => Number.isInteger(answers.value[question.question_id]) && answers.value[question.question_id] >= 0))
const questionTagsLabel = computed(() => Array.from(new Set(questions.value.map((question) => question.fraud_type).filter(Boolean))).join(' / ') || '综合诈骗类型')
const resultSummary = computed(() => {
  const score = result.value?.score || 0
  if (score >= 85) return '你的反诈警觉性很高，已经具备较强的风险识别能力。'
  if (score >= 60) return '整体判断不错，但仍建议继续强化高频诈骗场景的拆解能力。'
  return '当前风险识别能力还有明显提升空间，建议优先复盘错题并继续换题训练。'
})

async function fetchQuestions(refresh: boolean) {
  if (refresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }

  try {
    const response = await educationApi.getQuestions({
      count: 5,
      refresh,
    })
    questions.value = response.items
    answers.value = Object.fromEntries(response.items.map((item) => [item.question_id, -1]))
    submitted.value = false
    result.value = null
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '加载训练题失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

async function submit() {
  if (!allAnswered.value) {
    ElMessage.warning('请先完成全部题目')
    return
  }

  submitting.value = true
  try {
    result.value = await educationApi.submitTest({
      question_ids: questions.value.map((question) => question.question_id),
      answers: answers.value,
    })
    submitted.value = true
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '提交测试失败')
  } finally {
    submitting.value = false
  }
}

function reset() {
  answers.value = Object.fromEntries(questions.value.map((item) => [item.question_id, -1]))
  submitted.value = false
  result.value = null
}

function resolveOption(options: string[], index: number | null | undefined) {
  if (typeof index !== 'number' || index < 0 || index >= options.length) {
    return '未作答'
  }
  return options[index]
}

function difficultyLabel(difficulty: string) {
  if (difficulty === 'advanced') return '高级'
  if (difficulty === 'intermediate') return '中级'
  return '基础'
}

function riskProfileLabel(level: string) {
  if (level === 'low') return '低风险'
  if (level === 'high') return '高风险'
  return '中风险'
}

function formatTrendTime(timestamp: string) {
  if (!timestamp) return '--'
  return timestamp.replace('T', ' ').slice(5, 16)
}

onMounted(() => {
  void fetchQuestions(false)
})
</script>

<style scoped lang="scss">
.question-view__intro p {
  margin: 12px 0 0;
  color: var(--tech-theme-text-secondary);
}

.question-view__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 18px 0;
}

.question-view__toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.question-view__summary {
  margin-bottom: 18px;
}

.question-view__loading {
  margin-top: 18px;
}

.question-view__question-card {
  margin-bottom: 16px;
}

.question-view__question-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.question-view__question-type {
  margin: 8px 0 0;
  color: var(--tech-theme-text-secondary);
}

.question-view__options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.question-view__result-card {
  margin-top: 16px;
}

.question-view__answers {
  margin-top: 16px;
}

.question-view__diagnosis-card {
  margin-top: 16px;
}

.question-view__diagnosis-summary {
  margin-bottom: 10px;
  color: var(--tech-theme-text-secondary);
}

.question-view__diagnosis-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.question-view__weakness-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.question-view__weakness-item {
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.question-view__weakness-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.question-view__weakness-tip {
  color: var(--tech-theme-text-secondary);
}

.question-view__next-actions {
  margin: 8px 0 0;
  padding-left: 18px;
  color: var(--tech-theme-text-secondary);
}

.question-view__trend {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed rgba(255, 255, 255, 0.14);
}

.question-view__trend-title {
  margin-bottom: 8px;
  font-weight: 600;
}

.question-view__trend-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.question-view__trend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--tech-theme-text-secondary);
}

.question-view__trend-item strong {
  color: var(--tech-theme-text-primary);
}

.question-view__trend-delta {
  margin-top: 10px;
  font-weight: 600;
}

.question-view__trend-delta.is-up {
  color: var(--tech-text-success);
}

.question-view__trend-delta.is-down {
  color: var(--tech-text-warning);
}

.question-view__learning-panel {
  margin-top: 12px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
}

.question-view__learning-title {
  margin-bottom: 8px;
  font-weight: 600;
}

.question-view__learning-objective,
.question-view__coach-feedback {
  color: var(--tech-theme-text-secondary);
  line-height: 1.72;
}

.question-view__learning-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.question-view__learning-block {
  padding: 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.question-view__block-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.question-view__learning-block ul {
  padding-left: 16px;
  margin: 0;
  color: var(--tech-theme-text-secondary);
}

.question-view__answer-item {
  margin-bottom: 12px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.question-view__answer-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.question-view__answer-status.is-correct {
  color: var(--tech-text-success);
}

.question-view__answer-status.is-wrong,
.question-view__answer-correct {
  color: var(--tech-text-warning);
}

.question-view__answer-explanation {
  margin-top: 8px;
  color: var(--tech-theme-text-secondary);
  line-height: 1.72;
}
.change-button {
  background-color: var(--tech-color-primary);
  color: #fff;
  border: none;
}

@media (max-width: 960px) {
  .question-view__learning-grid {
    grid-template-columns: 1fr;
  }
}
</style>
