<template>
  <div class="ai-chat tech-panel">
    <el-container class="ai-chat__layout">
      <el-aside width="250px" class="ai-chat__sidebar">
        <el-button type="primary" class="ai-chat__create" @click="createChat">新建咨询</el-button>
        <div class="chat-list">
          <div
            v-for="chat in chatList"
            :key="chat.id"
            class="chat-item"
            :class="{ active: currentChatId === chat.id }"
            @click="selectChat(chat.id)"
          >
            <span class="chat-item__title" :title="chat.title">{{ chat.title }}</span>
            <div class="chat-item__actions">
              <el-button text size="small" @click.stop="renameChat(chat)">重命名</el-button>
              <el-button text size="small" @click.stop="deleteChat(chat)">移除</el-button>
            </div>
          </div>
        </div>
      </el-aside>
      <el-main class="ai-chat__main">
        <div class="ai-chat__notice">
          <span class="ai-chat__notice-title">统一反诈助手</span>
          <span class="ai-chat__notice-text">本系统基于大模型技术，结合反诈知识库和历史对话，提供智能化的反诈咨询服务。请勿输入任何敏感个人信息。</span>
        </div>

        <div class="messages tech-scrollbar" ref="messagesRef">
          <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
            <div class="message-row">
              <div v-if="msg.role === 'assistant'" class="message-avatar">
                <img
                  v-if="assistantAvatarAvailable"
                  :src="assistantAvatarSrc"
                  alt="AI 助手头像"
                  class="message-avatar__image"
                  @error="assistantAvatarAvailable = false"
                />
                <span v-else class="message-avatar__fallback">AI</span>
              </div>
              <div class="message-bubble">
                <div
                  v-if="msg.role === 'assistant'"
                  class="message-content message-content--markdown"
                  v-html="renderAssistantMessage(msg.content)"
                />
                <div v-else class="message-content">{{ msg.content }}</div>
              </div>
            </div>
            <div class="message-meta">
              <span>{{ formatMessageTime(msg.created_at) }}</span>
              <span v-if="resolveRetrievalBadge(msg)" class="message-meta__badge">
                {{ resolveRetrievalBadge(msg) }}
              </span>
              <span v-if="msg.role === 'assistant' && msg.sources?.length">{{ msg.sources.length }} 条相关资料</span>
              <span v-else-if="msg.role === 'assistant'">未附带检索资料</span>
            </div>
            <div v-if="msg.role === 'assistant' && msg.sources?.length" class="message-sources">
              <div class="message-sources__header">
                <span class="message-sources__label">相关事件与资料</span>
                <el-button
                  v-if="msg.sources.length > SOURCE_PREVIEW_LIMIT"
                  text
                  size="small"
                  class="message-sources__toggle"
                  @click="toggleSources(msg.id)"
                >
                  {{ isSourcesExpanded(msg.id) ? '收起资料' : `展开全部 ${msg.sources.length} 条` }}
                </el-button>
              </div>
              <RagSourceCard
                v-for="(source, index) in visibleSources(msg)"
                :key="`${msg.id}-${index}`"
                :source="source"
              />
            </div>
          </div>
          <div v-if="sending" class="message assistant message--loading">
            <div class="message-row">
              <div class="message-avatar">
                <img
                  v-if="assistantAvatarAvailable"
                  :src="assistantAvatarSrc"
                  alt="AI 助手头像"
                  class="message-avatar__image"
                  @error="assistantAvatarAvailable = false"
                />
                <span v-else class="message-avatar__fallback">AI</span>
              </div>
              <div class="message-bubble">
                <div class="message-content">
                  <span class="message-loading">
                    <span class="message-loading__dot" />
                    <span class="message-loading__dot" />
                    <span class="message-loading__dot" />
                  </span>
                </div>
              </div>
            </div>
            <div class="message-meta">
              <span>处理中</span>
            </div>
          </div>
          <el-empty v-if="!messages.length" description="开始进行反诈咨询吧" />
        </div>

        <div v-if="lastFailedPrompt" class="ai-chat__retry-banner">
          <div class="ai-chat__retry-copy">
            <span class="ai-chat__retry-title">上一条消息发送失败</span>
            <span class="ai-chat__retry-text">可直接重试，或继续编辑后再次发送。</span>
          </div>
          <el-button class="ai-chat__retry-button" @click="retryLastPrompt">重试上一条</el-button>
        </div>

        <div class="ai-chat__composer">
          <el-input
            v-model="input"
            placeholder="输入你的问题、聊天片段或可疑情况..."
            :disabled="sending"
            @keyup.enter="send"
          />
          <el-button type="primary" @click="send" :loading="sending">咨询</el-button>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { chatApi } from '@/api/chat'
import type { ChatListItem, ChatMessage } from '@/api/chat'
import RagSourceCard from '@/components/rag/RagSourceCard.vue'
import { renderChatMarkdown } from '@/utils/chatMarkdown'

const chatList = ref<ChatListItem[]>([])
const currentChatId = ref('')
const messages = ref<ChatMessage[]>([])
const input = ref('')
const sending = ref(false)
const messagesRef = ref<HTMLElement | null>(null)
const lastFailedPrompt = ref('')
const expandedSourceMessageIds = ref<number[]>([])
const assistantAvatarSrc = '/images/ai-assistant-avatar.png'
const assistantAvatarAvailable = ref(true)

let listRequestId = 0
let detailRequestId = 0
const SOURCE_PREVIEW_LIMIT = 2

onMounted(() => {
  void loadChats()
})

async function loadChats() {
  const requestId = ++listRequestId
  try {
    const res = await chatApi.list()
    if (requestId !== listRequestId) return

    chatList.value = res.items || []
    if (!currentChatId.value && chatList.value.length) {
      await selectChat(chatList.value[0].id)
    }
  } catch (error) {
    console.error(error)
  }
}

async function createChat() {
  try {
    const chat = await chatApi.create()
    chatList.value.unshift(toChatListItem(chat))
    await selectChat(chat.id)
  } catch (error) {
    console.error(error)
    ElMessage.error('创建咨询失败')
  }
}

async function selectChat(id: string) {
  currentChatId.value = id
  const requestId = ++detailRequestId

  try {
    const chat = await chatApi.get(id)
    if (requestId !== detailRequestId || currentChatId.value !== id) return

    messages.value = chat.messages || []
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error(error)
  }
}

async function send() {
  const content = input.value.trim()
  if (!content) return

  sending.value = true
  try {
    let targetChatId = currentChatId.value
    if (!targetChatId) {
      const chat = await chatApi.create()
      chatList.value.unshift(toChatListItem(chat))
      currentChatId.value = chat.id
      targetChatId = chat.id
    }

    const res = await chatApi.sendMessage(targetChatId, content)
    messages.value.push(res.user_message, res.assistant_message)
    input.value = ''
    lastFailedPrompt.value = ''
    await nextTick()
    scrollToBottom()
    await loadChats()
  } catch (error) {
    console.error(error)
    lastFailedPrompt.value = content
    input.value = content
    ElMessage.error(resolveChatError(error))
  } finally {
    sending.value = false
  }
}

async function deleteChat(chat: ChatListItem) {
  try {
    await ElMessageBox.confirm(
      `删除后将无法恢复${chat?.title ? `：“${chat.title}”` : '该对话'}，是否继续？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    await chatApi.delete(chat.id)
    const nextChats = chatList.value.filter((item) => item.id !== chat.id)
    chatList.value = nextChats
    if (currentChatId.value === chat.id) {
      currentChatId.value = ''
      messages.value = []
      if (nextChats.length) {
        await selectChat(nextChats[0].id)
      }
    }
    ElMessage.success('对话已删除')
  } catch (error) {
    if (String((error as any)?.message || '').toLowerCase() === 'cancel') {
      return
    }
    console.error(error)
    ElMessage.error('移除失败')
  }
}

async function renameChat(chat: ChatListItem) {
  try {
    const { value } = await ElMessageBox.prompt('输入新的会话名称', '重命名对话', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: chat.title,
      inputPlaceholder: '请输入对话名称',
      inputValidator: (value) => {
        if (!value || !value.trim()) {
          return '对话名称不能为空'
        }
        if (value.trim().length > 512) {
          return '对话名称不能超过 512 个字符'
        }
        return true
      },
    })

    const normalizedTitle = value.trim()
    if (normalizedTitle === chat.title) {
      return
    }

    const updatedChat = await chatApi.rename(chat.id, normalizedTitle)
    updateChatListItem(updatedChat)
    ElMessage.success('重命名成功')
  } catch (error) {
    if (String((error as any)?.message || '').toLowerCase() === 'cancel') {
      return
    }
    console.error(error)
    ElMessage.error(resolveRenameError(error))
  }
}

function resolveChatError(error: any) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  return '咨询失败，请稍后重试。'
}

function resolveRenameError(error: any) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  return '重命名失败，请稍后重试。'
}

function formatMessageTime(value: string) {
  if (!value) return '刚刚'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '刚刚'
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function resolveRetrievalBadge(message: ChatMessage) {
  if (message.role !== 'assistant') return ''
  if (message.retrieval_mode === 'knowledge_enhanced') return '知识增强回答'
  if (message.retrieval_mode === 'retrieval_empty') return '未命中资料'
  return ''
}

function renderAssistantMessage(content: string) {
  return renderChatMarkdown(content)
}

function visibleSources(message: ChatMessage) {
  if (isSourcesExpanded(message.id)) {
    return message.sources
  }
  return message.sources.slice(0, SOURCE_PREVIEW_LIMIT)
}

function isSourcesExpanded(messageId: number) {
  return expandedSourceMessageIds.value.includes(messageId)
}

function toggleSources(messageId: number) {
  if (isSourcesExpanded(messageId)) {
    expandedSourceMessageIds.value = expandedSourceMessageIds.value.filter((id) => id !== messageId)
    return
  }
  expandedSourceMessageIds.value = [...expandedSourceMessageIds.value, messageId]
}

async function retryLastPrompt() {
  if (!lastFailedPrompt.value || sending.value) return
  input.value = lastFailedPrompt.value
  await send()
}

function toChatListItem(chat: { id: string; title: string; created_at: string; updated_at: string }) {
  return {
    id: chat.id,
    title: chat.title,
    created_at: chat.created_at,
    updated_at: chat.updated_at,
    message_count: 0,
  }
}

function updateChatListItem(chat: { id: string; title: string; created_at: string; updated_at: string }) {
  const updatedItem = toChatListItem(chat)
  chatList.value = chatList.value.map((item) => item.id === chat.id ? {
    ...item,
    ...updatedItem,
    message_count: item.message_count,
  } : item)
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}
</script>

<style scoped lang="scss">
.ai-chat {
  overflow: hidden;
}

.ai-chat__layout {
  height: calc(100vh - 160px);
}

.ai-chat__sidebar {
  padding: 12px;
  border-right: 1px solid var(--tech-theme-border);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 18%, transparent);
}

.ai-chat__create {
  width: 100%;
}

.ai-chat__sidebar-hint {
  margin: 12px 0 0;
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
  line-height: 1.7;
}

.chat-list {
  margin-top: 12px;
}

.chat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-radius: var(--tech-radius-sm);
  color: var(--tech-theme-text-regular);
  cursor: pointer;
  transition:
    background-color var(--tech-duration-fast) var(--tech-ease-out),
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    color var(--tech-duration-fast) var(--tech-ease-out);

  &:hover {
    background: color-mix(in srgb, var(--tech-color-primary-soft) 66%, transparent);
    border-color: color-mix(in srgb, var(--tech-color-primary) 20%, transparent);
  }

  &.active {
    background: color-mix(in srgb, var(--tech-color-primary-soft) 100%, transparent);
    border-color: var(--tech-theme-border-strong);
    color: var(--tech-theme-text-primary);
  }
}

.chat-item__title {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-item__actions {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.ai-chat__main {
  display: flex;
  flex-direction: column;
  padding: 0;
}

.ai-chat__notice {
  display: grid;
  gap: 4px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--tech-theme-border);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--tech-color-primary-soft) 70%, transparent), transparent),
    color-mix(in srgb, var(--tech-theme-surface-accent) 18%, transparent);
}

.ai-chat__notice-title {
  color: var(--tech-theme-text-primary);
  font-size: 13px;
  font-weight: 600;
}

.ai-chat__notice-text {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
  line-height: 1.7;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.ai-chat__retry-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  border-top: 1px solid var(--tech-theme-border);
  background: color-mix(in srgb, #ffb84d 10%, var(--tech-theme-surface-panel));
}

.ai-chat__retry-copy {
  display: grid;
  gap: 2px;
}

.ai-chat__retry-title {
  color: var(--tech-theme-text-primary);
  font-size: 13px;
  font-weight: 600;
}

.ai-chat__retry-text {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.ai-chat__retry-button {
  flex-shrink: 0;
}

.ai-chat__composer {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--tech-theme-border);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 14%, transparent);
}

.message {
  margin-bottom: 12px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.message.user .message-row {
  justify-content: flex-end;
}

.message-bubble {
  max-width: min(72%, 880px);
}

.message-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  margin-top: 2px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--tech-color-brand-primary) 30%, var(--tech-theme-border));
  background:
    radial-gradient(circle at top, rgba(0, 213, 255, 0.24), transparent 58%),
    linear-gradient(135deg, rgba(8, 37, 74, 0.96), rgba(4, 20, 46, 0.98));
  box-shadow: 0 10px 24px rgba(0, 140, 255, 0.12);
  overflow: hidden;
  flex-shrink: 0;
}

.message-avatar__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-avatar__fallback {
  color: var(--tech-color-brand-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.message.user .message-content {
  display: inline-block;
  width: 100%;
  padding: 8px 12px;
  border-radius: 14px;
  background: var(--tech-color-brand-gradient);
  color: var(--tech-text-inverse);
}

.message-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 6px;
  color: var(--tech-theme-text-secondary);
  font-size: 11px;
  clear: both;
}

.message.user .message-meta {
  justify-content: flex-end;
}

.message-meta__badge {
  display: inline-flex;
  align-items: center;
  min-height: 20px;
  padding: 0 8px;
  border: 1px solid color-mix(in srgb, var(--tech-color-brand-primary) 24%, var(--tech-theme-border));
  border-radius: 999px;
  background: color-mix(in srgb, var(--tech-color-brand-primary) 10%, transparent);
  color: var(--tech-theme-text-primary);
  font-size: 11px;
  line-height: 1;
}

.message.assistant .message-content {
  display: inline-block;
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--tech-theme-border);
  border-radius: 16px;
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 22%, var(--tech-theme-surface-panel));
  color: var(--tech-theme-text-regular);
}

.message-content--markdown {
  line-height: 1.78;
}

.message-content--markdown :deep(p) {
  margin: 0 0 12px;
}

.message-content--markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content--markdown :deep(h1),
.message-content--markdown :deep(h2),
.message-content--markdown :deep(h3) {
  margin: 0 0 10px;
  color: var(--tech-theme-text-primary);
  line-height: 1.4;
}

.message-content--markdown :deep(h1) {
  font-size: 20px;
}

.message-content--markdown :deep(h2) {
  font-size: 18px;
}

.message-content--markdown :deep(h3) {
  font-size: 16px;
}

.message-content--markdown :deep(ul),
.message-content--markdown :deep(ol) {
  margin: 0 0 12px;
  padding-left: 20px;
}

.message-content--markdown :deep(li) {
  margin-bottom: 6px;
}

.message-content--markdown :deep(strong) {
  color: var(--tech-theme-text-primary);
}

.message-content--markdown :deep(code) {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  font-family: Consolas, 'Courier New', monospace;
  font-size: 12px;
}

.message-content--markdown :deep(pre) {
  margin: 0 0 12px;
  padding: 12px 14px;
  overflow-x: auto;
  border-radius: 12px;
  background: rgba(2, 10, 22, 0.72);
  border: 1px solid color-mix(in srgb, var(--tech-theme-border) 70%, transparent);
}

.message-content--markdown :deep(pre code) {
  padding: 0;
  background: transparent;
}

.message-content--markdown :deep(blockquote) {
  margin: 0 0 12px;
  padding: 10px 14px;
  border-left: 3px solid var(--tech-color-brand-primary);
  background: rgba(0, 213, 255, 0.08);
  border-radius: 0 12px 12px 0;
}

.message-content--markdown :deep(a) {
  color: var(--tech-color-brand-primary);
  text-decoration: underline;
}

.message--loading .message-content {
  border-style: dashed;
}

.message-loading {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.message-loading__dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--tech-color-brand-primary);
  animation: ai-chat-pulse 1.2s ease-in-out infinite;
}

.message-loading__dot:nth-child(2) {
  animation-delay: 0.15s;
}

.message-loading__dot:nth-child(3) {
  animation-delay: 0.3s;
}

.message-sources {
  clear: both;
  max-width: min(560px, 100%);
  margin-top: 8px;
}

.message-sources__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.message-sources__label {
  display: inline-flex;
  margin-bottom: 4px;
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.message-sources__toggle {
  padding: 0;
}

.messages::after {
  content: '';
  display: table;
  clear: both;
}

@keyframes ai-chat-pulse {
  0%,
  80%,
  100% {
    opacity: 0.25;
    transform: translateY(0);
  }

  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
}
</style>
