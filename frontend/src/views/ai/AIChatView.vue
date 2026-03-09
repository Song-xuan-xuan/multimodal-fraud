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
            <span>{{ chat.title }}</span>
            <el-button text size="small" @click.stop="deleteChat(chat.id)">移除</el-button>
          </div>
        </div>
      </el-aside>
      <el-main class="ai-chat__main">
        <div class="messages" ref="messagesRef">
          <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <el-empty v-if="!messages.length" description="开始进行反诈咨询吧" />
        </div>
        <div class="ai-chat__composer">
          <el-input v-model="input" placeholder="输入你的问题、聊天片段或可疑情况..." @keyup.enter="send" />
          <el-button type="primary" @click="send" :loading="sending">咨询</el-button>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { chatApi } from '@/api/chat'
import { ElMessage } from 'element-plus'

const chatList = ref<any[]>([])
const currentChatId = ref('')
const messages = ref<any[]>([])
const input = ref('')
const sending = ref(false)
const messagesRef = ref<HTMLElement | null>(null)

onMounted(() => loadChats())

async function loadChats() {
  try {
    const res = await chatApi.list()
    chatList.value = res.items || []
  } catch (e) { console.error(e) }
}

async function createChat() {
  try {
    const chat = await chatApi.create()
    chatList.value.unshift(chat)
    await selectChat(chat.id)
  } catch (e: any) { ElMessage.error('创建咨询失败') }
}

async function selectChat(id: string) {
  currentChatId.value = id
  try {
    const chat = await chatApi.get(id)
    messages.value = chat.messages || []
    await nextTick()
    scrollToBottom()
  } catch (e) { console.error(e) }
}

async function send() {
  if (!input.value.trim() || !currentChatId.value) return
  sending.value = true
  try {
    const res = await chatApi.sendMessage(currentChatId.value, input.value)
    messages.value.push(res.user_message, res.assistant_message)
    input.value = ''
    await nextTick()
    scrollToBottom()
  } catch (e: any) { ElMessage.error('咨询失败') }
  finally { sending.value = false }
}

async function deleteChat(id: string) {
  try {
    await chatApi.delete(id)
    chatList.value = chatList.value.filter(c => c.id !== id)
    if (currentChatId.value === id) { currentChatId.value = ''; messages.value = [] }
  } catch (e) { ElMessage.error('移除失败') }
}

function scrollToBottom() {
  if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
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

.ai-chat__main {
  display: flex;
  flex-direction: column;
  padding: 0;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
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

.message.user .message-content {
  display: inline-block;
  float: right;
  clear: both;
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--tech-color-brand-gradient);
  color: var(--tech-text-inverse);
}

.message.assistant .message-content {
  display: inline-block;
  max-width: 70%;
  padding: 8px 12px;
  border: 1px solid var(--tech-theme-border);
  border-radius: 8px;
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 22%, var(--tech-theme-surface-panel));
  color: var(--tech-theme-text-regular);
}

.messages::after {
  content: '';
  display: table;
  clear: both;
}
</style>


