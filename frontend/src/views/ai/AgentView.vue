<template>
  <div class="agent-view page-shell">
    <div class="agent-view__intro">
      <h2>AI Agent</h2>
      <p>智能代理可以自动执行多步骤的新闻验证任务</p>
    </div>

    <el-card class="agent-view__card">
      <el-form label-position="top" class="agent-view__form">
        <el-form-item label="任务描述">
          <el-input v-model="task" type="textarea" :rows="4" placeholder="描述你需要 Agent 执行的任务，例如：帮我验证这条新闻的真实性..." />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="execute" :loading="loading">执行任务</el-button>
        </el-form-item>
      </el-form>

      <div v-if="steps.length" class="agent-view__steps">
        <h4>执行步骤</h4>
        <el-timeline>
          <el-timeline-item v-for="(step, i) in steps" :key="i" :type="step.status === 'done' ? 'success' : 'primary'">
            <p><strong>{{ step.name }}</strong></p>
            <p class="agent-view__step-detail">{{ step.detail }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>

      <el-card v-if="result" class="agent-view__result">
        <template #header>执行结果</template>
        <p>{{ result }}</p>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const task = ref('')
const loading = ref(false)
const steps = ref<{ name: string; detail: string; status: string }[]>([])
const result = ref('')

async function execute() {
  if (!task.value.trim()) return ElMessage.warning('请描述任务')
  loading.value = true
  steps.value = []
  result.value = ''

  const agentSteps = [
    { name: '解析任务', detail: '分析用户需求，确定执行计划' },
    { name: '信息检索', detail: '搜索相关新闻和事实来源' },
    { name: '内容分析', detail: '使用AI模型分析文本和图片内容' },
    { name: '交叉验证', detail: '比对多个来源的信息一致性' },
    { name: '生成报告', detail: '汇总分析结果，形成验证报告' },
  ]

  for (const step of agentSteps) {
    steps.value.push({ ...step, status: 'running' })
    await new Promise(resolve => setTimeout(resolve, 800))
    steps.value[steps.value.length - 1].status = 'done'
  }

  result.value = `Agent 已完成对"${task.value.substring(0, 50)}"的分析。基于多源交叉验证，该内容的可信度评估为中等。建议进一步查阅权威来源确认。`
  loading.value = false
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

.agent-view__form {
  max-width: 600px;
}

.agent-view__steps {
  margin-top: 20px;
}

.agent-view__step-detail {
  color: var(--tech-theme-text-secondary);
}

.agent-view__result {
  margin-top: 16px;
}
</style>
