<template>
  <div class="forum-view page-shell">
    <h2>讨论论坛</h2>
    <el-card class="forum-view__card">
      <div class="forum-view__toolbar">
        <el-input v-model="newTitle" placeholder="标题" class="forum-view__title-input" />
        <el-input v-model="newContent" placeholder="发表你的看法..." @keyup.enter="sendPost" />
        <el-button type="primary" @click="sendPost" :loading="posting">发送</el-button>
      </div>
      <div class="message-list" v-loading="loading">
        <div v-for="post in posts" :key="post.id" class="forum-message">
          <strong>{{ post.author }}</strong>
          <el-tag size="small" class="forum-view__tag">{{ post.title }}</el-tag>
          <span class="forum-view__time">{{ formatTime(post.created_at) }}</span>
          <p>{{ post.content }}</p>
        </div>
        <el-empty v-if="!loading && !posts.length" description="暂无帖子，来发表第一条吧" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/index'
import { ElMessage } from 'element-plus'

interface Post { id: number; title: string; content: string; author: string; created_at: string }

const posts = ref<Post[]>([])
const newTitle = ref('')
const newContent = ref('')
const loading = ref(false)
const posting = ref(false)

function formatTime(iso: string) {
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

async function loadPosts() {
  loading.value = true
  try {
    const { data } = await api.get('/community/forum/posts')
    posts.value = data.items
  } catch { ElMessage.error('加载帖子失败') }
  finally { loading.value = false }
}

async function sendPost() {
  if (!newContent.value.trim()) return ElMessage.warning('请输入内容')
  posting.value = true
  try {
    const { data } = await api.post('/community/forum/posts', {
      title: newTitle.value || '讨论',
      content: newContent.value,
    })
    posts.value.unshift(data)
    newTitle.value = ''
    newContent.value = ''
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '发送失败')
  } finally { posting.value = false }
}

onMounted(loadPosts)
</script>

<style scoped lang="scss">
.forum-view__card {
  margin-top: 16px;
}

.forum-view__toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.forum-view__title-input {
  width: 200px;
}

.forum-view__tag {
  margin-left: 8px;
}

.forum-view__time {
  margin-left: 8px;
  font-size: 12px;
  color: var(--tech-theme-text-tertiary);
}

.forum-message {
  padding: 12px 0;
  border-bottom: 1px solid var(--tech-theme-border);
}

.forum-message p {
  margin-top: 6px;
  color: var(--tech-theme-text-regular);
}
</style>
