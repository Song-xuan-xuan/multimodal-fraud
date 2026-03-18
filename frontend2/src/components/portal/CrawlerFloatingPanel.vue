<template>
  <div class="crawler-panel" :class="{ 'is-collapsed': collapsed }">
    <button v-if="collapsed" class="crawler-panel__tab" @click="collapsed = false">
      <span class="crawler-panel__tab-label">快报</span>
      <span class="crawler-panel__tab-badge" v-if="newsList.length">{{ newsList.length }}</span>
    </button>

    <transition name="panel-slide">
      <div v-if="!collapsed" class="crawler-panel__body">
        <div class="crawler-panel__header">
          <div>
            <p class="crawler-panel__eyebrow">实时快报</p>
            <h3>情报抓取更新</h3>
          </div>
          <div class="crawler-panel__actions">
            <button class="crawler-panel__btn" :disabled="loading" @click="fetchNews" title="刷新">
              <svg :class="{ 'is-spinning': loading }" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6M1 20v-6h6" />
                <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
              </svg>
            </button>
            <button class="crawler-panel__btn" @click="collapsed = true" title="收起">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </div>

        <div v-if="loading && !newsList.length" class="crawler-panel__loading">
          <div class="crawler-panel__spinner" />
          <span>正在同步最新资讯...</span>
        </div>

        <div v-else class="crawler-panel__list">
          <a
            v-for="(item, idx) in newsList"
            :key="idx"
            :href="item.url"
            target="_blank"
            rel="noopener"
            class="crawler-panel__card"
            :style="{ '--idx': idx }"
          >
            <div class="crawler-panel__card-head">
              <span class="crawler-panel__source">{{ item.source }}</span>
              <span class="crawler-panel__link">查看原文</span>
            </div>
            <p class="crawler-panel__card-title">{{ item.title }}</p>
            <span class="crawler-panel__card-time">{{ item.publish_time }}</span>
          </a>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { crawlerApi, type CrawlerNewsItem } from '@/api/crawler'

const CRAWLER_CACHE_KEY = 'portal_crawler_news_cache'

const collapsed = ref(false)
const loading = ref(false)
const newsList = ref<CrawlerNewsItem[]>([])

function readCache() {
  if (typeof window === 'undefined') return

  try {
    const cached = localStorage.getItem(CRAWLER_CACHE_KEY)
    if (!cached) return

    const parsed = JSON.parse(cached) as { news?: CrawlerNewsItem[] }
    if (Array.isArray(parsed.news) && parsed.news.length > 0) {
      newsList.value = parsed.news.slice(0, 8)
    }
  } catch (error) {
    console.warn('读取实时新闻缓存失败', error)
  }
}

function writeCache(items: CrawlerNewsItem[]) {
  if (typeof window === 'undefined') return

  try {
    localStorage.setItem(
      CRAWLER_CACHE_KEY,
      JSON.stringify({
        news: items.slice(0, 8),
      }),
    )
  } catch (error) {
    console.warn('写入实时新闻缓存失败', error)
  }
}

async function fetchNews() {
  loading.value = true
  try {
    const res = await crawlerApi.getLatest()
    newsList.value = res.news.slice(0, 8)
    writeCache(newsList.value)
  } catch (e) {
    console.error('获取实时新闻失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  readCache()
  if (newsList.value.length === 0) {
    void fetchNews()
  }
})
</script>

<style scoped lang="scss">
.crawler-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  pointer-events: auto;
}

.crawler-panel__tab,
.crawler-panel__body,
.crawler-panel__card {
  border: 1px solid var(--app-border-default);
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
}

.crawler-panel__tab {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 14px;
  color: var(--app-text-primary);
  cursor: pointer;
  transition:
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    transform var(--tech-duration-fast) var(--tech-ease-out);
}

.crawler-panel__tab:hover {
  border-color: var(--app-border-strong);
  transform: translateY(-1px);
}

.crawler-panel__tab-label {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.crawler-panel__tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-status-danger) 84%, white 16%);
  color: var(--app-text-inverse);
  font-size: 12px;
  font-weight: 700;
}

.crawler-panel__body {
  width: min(360px, calc(100vw - 40px));
  max-height: calc(100vh - 72px - 56px);
  display: flex;
  flex-direction: column;
  border-radius: 24px;
  overflow: hidden;
}

.crawler-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 18px 14px;
  border-bottom: 1px solid color-mix(in srgb, var(--app-border-default) 78%, transparent);
}

.crawler-panel__eyebrow {
  margin: 0 0 6px;
  color: var(--app-text-secondary);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.crawler-panel__header h3 {
  margin: 0;
  color: var(--app-text-primary);
  font-size: 18px;
}

.crawler-panel__actions {
  display: flex;
  gap: 6px;
}

.crawler-panel__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--app-border-default);
  border-radius: 10px;
  background: var(--app-surface-card);
  color: var(--app-text-secondary);
  cursor: pointer;
  transition:
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out),
    color var(--tech-duration-fast) var(--tech-ease-out);
}

.crawler-panel__btn:hover {
  border-color: var(--app-border-strong);
  background: color-mix(in srgb, var(--app-surface-note) 84%, white 16%);
  color: var(--app-text-primary);
}

.crawler-panel__btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.crawler-panel__btn svg.is-spinning,
.crawler-panel__spinner {
  animation: spin 0.8s linear infinite;
}

.crawler-panel__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 16px;
  color: var(--app-text-secondary);
  font-size: 13px;
}

.crawler-panel__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid color-mix(in srgb, var(--app-border-default) 72%, transparent);
  border-top-color: var(--app-text-danger);
  border-radius: 50%;
}

.crawler-panel__list {
  display: grid;
  gap: 10px;
  padding: 14px;
  overflow-y: auto;
}

.crawler-panel__card {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 18px;
  text-decoration: none;
  animation: card-enter 0.36s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: calc(var(--idx) * 0.04s);
  transition:
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    transform var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out);
}

.crawler-panel__card:hover {
  border-color: var(--app-border-strong);
  background: color-mix(in srgb, var(--app-surface-note) 78%, white 22%);
  transform: translateY(-1px);
}

.crawler-panel__card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.crawler-panel__source,
.crawler-panel__link {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.crawler-panel__source {
  color: var(--app-text-danger);
}

.crawler-panel__link {
  color: var(--app-text-tertiary);
}

.crawler-panel__card-title {
  margin: 0;
  color: var(--app-text-primary);
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.crawler-panel__card-time {
  color: var(--app-text-tertiary);
  font-size: 12px;
}

.panel-slide-enter-active {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.24s ease;
}

.panel-slide-leave-active {
  transition: transform 0.22s ease-in, opacity 0.16s ease;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@keyframes card-enter {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .crawler-panel {
    top: 12px;
    right: 12px;
  }

  .crawler-panel__body {
    width: calc(100vw - 24px);
    max-height: 46vh;
  }
}
</style>
