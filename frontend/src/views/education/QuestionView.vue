<template>
  <div class="question-view page-shell">
    <div class="question-view__intro">
      <h2>知识测试</h2>
      <p>测试你的反诈识别与应对能力</p>
    </div>

    <div v-if="!submitted">
      <el-card v-for="(q, qi) in questions" :key="qi" class="question-view__question-card">
        <h4>{{ qi + 1 }}. {{ q.question }}</h4>
        <el-radio-group v-model="answers[qi]" class="question-view__options">
          <el-radio v-for="(opt, oi) in q.options" :key="oi" :value="oi">{{ opt }}</el-radio>
        </el-radio-group>
      </el-card>
      <el-button type="primary" @click="submit" :disabled="answers.some(a => a === -1)">提交答案</el-button>
    </div>

    <el-card v-else class="question-view__result-card">
      <template #header>测试结果</template>
      <el-result :icon="score >= 3 ? 'success' : 'warning'" :title="`得分: ${score} / ${questions.length}`">
        <template #sub-title>
          {{ score >= 4 ? '你的反诈警觉性很高！' : score >= 2 ? '还需要继续学习常见诈骗识别技巧。' : '建议深入学习常见诈骗套路与应对方法。' }}
        </template>
        <template #extra>
          <el-button type="primary" @click="reset">重新测试</el-button>
        </template>
      </el-result>
      <div class="question-view__answers">
        <div v-for="(q, qi) in questions" :key="qi" class="question-view__answer-item">
          <p><strong>{{ qi + 1 }}. {{ q.question }}</strong></p>
          <p :class="['question-view__answer-status', answers[qi] === q.correct ? 'is-correct' : 'is-wrong']">
            你的答案: {{ q.options[answers[qi]] }} {{ answers[qi] === q.correct ? '✓' : '✗' }}
          </p>
          <p v-if="answers[qi] !== q.correct" class="question-view__answer-correct">正确答案: {{ q.options[q.correct] }}</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const questions = [
  { question: '以下哪种说法最可能带有诈骗诱导性？', options: ['引用官方数据', '使用"震惊""不转不是中国人"等词汇', '标明信息来源', '使用客观中性的语言'], correct: 1 },
  { question: '判断新闻真伪最可靠的方法是什么？', options: ['看转发量', '查看多个权威来源是否报道', '看评论区反应', '看标题是否吸引人'], correct: 1 },
  { question: '以下哪个是AI生成文本的常见特征？', options: ['包含错别字', '内容过于流畅完美，缺少个人风格', '使用了网络用语', '引用了真实数据'], correct: 1 },
  { question: '面对一条可疑新闻，你应该首先做什么？', options: ['立即转发提醒他人', '在评论区发表看法', '查找原始信息来源并交叉验证', '忽略不理'], correct: 2 },
  { question: '以下哪种情况不是诈骗套路的典型特征？', options: ['消息来源不明', '细节描述与已知事实矛盾', '引用了政府公开发布的数据', '配图与文字内容不符'], correct: 2 },
]

const answers = ref<number[]>(questions.map(() => -1))
const submitted = ref(false)
const score = computed(() => questions.filter((q, i) => answers.value[i] === q.correct).length)

function submit() { submitted.value = true }
function reset() { answers.value = questions.map(() => -1); submitted.value = false }
</script>

<style scoped lang="scss">
.question-view__intro p {
  margin: 12px 0 0;
  color: var(--tech-theme-text-secondary);
}

.question-view__question-card {
  margin-bottom: 16px;
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

.question-view__answer-item {
  margin-bottom: 12px;
}

.question-view__answer-status.is-correct {
  color: var(--tech-text-success);
}

.question-view__answer-status.is-wrong,
.question-view__answer-correct {
  color: var(--tech-text-warning);
}
</style>


