<template>
  <div class="ai-assistant-view page-shell">
    <h2>反诈知识助手 (RAG)</h2>
    <el-card class="ai-assistant-view__card">
      <div v-if="ragStatus !== 'ready'" class="rag-status-banner" :class="`rag-status-banner--${ragStatus}`">
        <span class="rag-status-banner__title">{{ statusTitle }}</span>
        <span class="rag-status-banner__text">{{ statusDescription }}</span>
      </div>

      <div class="messages tech-scrollbar">
        <div v-for="(msg, i) in conversation" :key="i" :class="['message', msg.role]">
          <div class="message-content">{{ msg.content }}</div>
          <div v-if="msg.sources?.length" class="sources">
            <strong>参考案例与法规：</strong>
            <RagSourceCard v-for="(s, j) in msg.sources" :key="j" :source="s" />
          </div>
        </div>
        <el-empty v-if="!conversation.length" description="向反诈助手描述你的可疑场景" />
      </div>

      <div class="ai-assistant-view__composer">
        <el-input
          v-model="question"
          :disabled="composerDisabled"
          :placeholder="composerPlaceholder"
          @keyup.enter="ask"
        />
        <el-button type="primary" @click="ask" :loading="loading" :disabled="composerDisabled">提问</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ragApi } from '@/api/rag'
import { ElMessage } from 'element-plus'
import RagSourceCard from '@/components/rag/RagSourceCard.vue'
import type { RagSource } from '@/types/rag'

const question = ref('')
const conversation = ref<Array<{ role: 'user' | 'assistant'; content: string; sources?: RagSource[] }>>([])
const sessionId = ref('')
const loading = ref(false)
const ragStatus = ref<'ready' | 'warming_up' | 'error' | 'not_initialized'>('not_initialized')
let healthTimer: number | null = null

const composerDisabled = computed(() => loading.value || ragStatus.value !== 'ready')
const composerPlaceholder = computed(() => {
  if (ragStatus.value === 'warming_up') return '知识库预热中，请稍候...'
  if (ragStatus.value === 'error') return '知识库加载失败，请检查后端日志'
  if (ragStatus.value === 'not_initialized') return '知识库初始化中，请稍候...'
  return '请输入你的问题、可疑话术或诈骗场景...'
})
const statusTitle = computed(() => {
  switch (ragStatus.value) {
    case 'warming_up':
      return '知识库预热中'
    case 'error':
      return '知识库加载失败'
    case 'not_initialized':
      return '知识库初始化中'
    default:
      return '知识库已就绪'
  }
})
const statusDescription = computed(() => {
  switch (ragStatus.value) {
    case 'warming_up':
      return '后台正在加载反诈索引。首次启动会较慢，完成后即可正常提问。'
    case 'error':
      return 'RAG 当前不可用，请检查后端环境、索引文件和依赖安装情况。'
    case 'not_initialized':
      return '正在等待知识库服务进入可用状态。'
    default:
      return ''
  }
})

async function refreshHealth(showError = false) {
  try {
    const res = await ragApi.health()
    ragStatus.value = res.status
    if (res.ready) {
      ragStatus.value = 'ready'
      stopHealthPolling()
    } else if (ragStatus.value === 'warming_up' || ragStatus.value === 'not_initialized') {
      startHealthPolling()
    }
  } catch (e) {
    ragStatus.value = 'error'
    stopHealthPolling()
    if (showError) ElMessage.error('知识库状态检查失败')
  }
}

function startHealthPolling() {
  if (healthTimer !== null) return
  healthTimer = window.setInterval(() => {
    void refreshHealth()
  }, 5000)
}

function stopHealthPolling() {
  if (healthTimer !== null) {
    window.clearInterval(healthTimer)
    healthTimer = null
  }
}

async function ask() {
  if (!question.value.trim() || composerDisabled.value) return
  const q = question.value
  conversation.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true
  try {
    const res = await ragApi.ask(q, sessionId.value || undefined)
    sessionId.value = res.session_id
    conversation.value.push({ role: 'assistant', content: res.answer, sources: res.sources })
  } catch (e: any) {
    ElMessage.error(ragStatus.value === 'ready' ? '查询失败' : '知识库尚未就绪')
    conversation.value.push({ role: 'assistant', content: '抱歉，查询失败，请重试。' })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void refreshHealth(true)
})

onBeforeUnmount(() => {
  stopHealthPolling()
})
</script>

<style scoped lang="scss">
.ai-assistant-view__card {
  margin-top: 16px;
}

.rag-status-banner {
  display: grid;
  gap: 4px;
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--tech-theme-border);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 18%, transparent);
}

.rag-status-banner--warming_up,
.rag-status-banner--not_initialized {
  border-color: color-mix(in srgb, var(--tech-color-brand-primary) 35%, var(--tech-theme-border));
  background: color-mix(in srgb, var(--tech-color-brand-primary) 10%, var(--tech-theme-surface-panel));
}

.rag-status-banner--error {
  border-color: color-mix(in srgb, #ff6b6b 45%, var(--tech-theme-border));
  background: color-mix(in srgb, #ff6b6b 10%, var(--tech-theme-surface-panel));
}

.rag-status-banner__title {
  color: var(--tech-theme-text-primary);
  font-size: 13px;
  font-weight: 600;
}

.rag-status-banner__text {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
  line-height: 1.6;
}

.messages {
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.message {
  margin-bottom: 12px;
}

.message.user .message-content {
  background: var(--tech-color-brand-gradient);
  color: var(--tech-text-inverse);
  padding: 8px 12px;
  border-radius: 8px;
  display: inline-block;
  float: right;
  clear: both;
}

.message.assistant .message-content {
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 22%, var(--tech-theme-surface-panel));
  color: var(--tech-theme-text-regular);
  border: 1px solid var(--tech-theme-border);
  padding: 8px 12px;
  border-radius: 8px;
  display: inline-block;
  clear: both;
}

.messages::after {
  content: '';
  display: table;
  clear: both;
}

.sources {
  margin-top: 8px;
  font-size: 12px;
  color: var(--tech-theme-text-secondary);
  clear: both;
}

.ai-assistant-view__composer {
  display: flex;
  gap: 8px;
}
</style>
