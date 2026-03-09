<template>
  <div class="crawler-panel" :class="{ 'is-collapsed': collapsed }">
    <!-- 折叠时的小标签 -->
    <button v-if="collapsed" class="crawler-panel__tab" @click="collapsed = false">
      <span class="crawler-panel__tab-icon">&#x1F4F0;</span>
      <span class="crawler-panel__tab-badge" v-if="newsList.length">{{ newsList.length }}</span>
    </button>

    <!-- 展开的面板 -->
    <transition name="panel-slide">
      <div v-if="!collapsed" class="crawler-panel__body">
        <!-- 面板头部 -->
        <div class="crawler-panel__header">
          <div class="crawler-panel__title-row">
            <span class="crawler-panel__dot" />
            <h3>实时新闻</h3>
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

        <!-- 加载中 -->
        <div v-if="loading && !newsList.length" class="crawler-panel__loading">
          <div class="crawler-panel__spinner" />
          <span>抓取中...</span>
        </div>

        <!-- 新闻列表 -->
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
            <!-- 悬停扫光 -->
            <span class="crawler-panel__card-shine" aria-hidden="true" />
            <!-- 左侧高亮条 -->
            <span class="crawler-panel__card-accent" aria-hidden="true" />

            <div class="crawler-panel__card-head">
              <span class="crawler-panel__source">{{ item.source }}</span>
              <svg class="crawler-panel__arrow" viewBox="0 0 20 20" width="14" height="14">
                <path d="M5 10h8m0 0l-3-3m3 3l-3 3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
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

const collapsed = ref(false)
const loading = ref(false)
const newsList = ref<CrawlerNewsItem[]>([])

async function fetchNews() {
  loading.value = true
  try {
    const res = await crawlerApi.getLatest()
    newsList.value = res.news.slice(0, 8)
  } catch (e) {
    console.error('获取实时新闻失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchNews()
})
</script>

<style scoped lang="scss">
/* ---- 容器定位 ---- */
.crawler-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  pointer-events: auto;
}

/* ---- 折叠标签 ---- */
.crawler-panel__tab {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: 1px solid rgba(124, 231, 255, 0.2);
  border-radius: 12px;
  background: rgba(6, 16, 30, 0.82);
  backdrop-filter: blur(16px);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
  animation: tab-breathe 2.4s ease-in-out infinite;
}

.crawler-panel__tab:hover {
  border-color: rgba(124, 231, 255, 0.5);
  box-shadow: 0 0 24px rgba(124, 231, 255, 0.18);
  transform: scale(1.08);
  animation: none;
}

@keyframes tab-breathe {
  0%, 100% { box-shadow: 0 0 12px rgba(124, 231, 255, 0.08); }
  50% { box-shadow: 0 0 20px rgba(124, 231, 255, 0.22); }
}

.crawler-panel__tab-icon {
  font-size: 20px;
}

.crawler-panel__tab-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: linear-gradient(135deg, #28c8b4, #328cff);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
}

/* ---- 展开面板 ---- */
.crawler-panel__body {
  width: 320px;
  max-height: calc(100vh - 72px - 48px);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(124, 231, 255, 0.14);
  border-radius: 16px;
  background: rgba(6, 16, 30, 0.88);
  backdrop-filter: blur(24px);
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 40px rgba(124, 231, 255, 0.06);
  overflow: hidden;
}

/* ---- 头部 ---- */
.crawler-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.crawler-panel__title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.crawler-panel__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #28c8b4;
  box-shadow: 0 0 8px rgba(40, 200, 180, 0.6);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.crawler-panel__header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(234, 244, 255, 0.92);
  letter-spacing: 0.03em;
}

.crawler-panel__actions {
  display: flex;
  gap: 4px;
}

.crawler-panel__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(200, 220, 240, 0.7);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.crawler-panel__btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #7ce7ff;
}

.crawler-panel__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.crawler-panel__btn svg.is-spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ---- 加载中 ---- */
.crawler-panel__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 16px;
  color: rgba(200, 220, 240, 0.5);
  font-size: 13px;
}

.crawler-panel__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(124, 231, 255, 0.18);
  border-top-color: rgba(124, 231, 255, 0.7);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ---- 列表滚动区 ---- */
.crawler-panel__list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 10px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(124, 231, 255, 0.15);
    border-radius: 4px;
  }
}

/* ---- 单条新闻卡片 ---- */
.crawler-panel__card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px 10px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: rgba(255, 255, 255, 0.03);
  text-decoration: none;
  cursor: pointer;
  overflow: hidden;

  /* 交错入场动画 */
  animation: card-enter 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: calc(var(--idx) * 0.06s);

  transition:
    background 0.24s ease,
    border-color 0.24s ease,
    transform 0.24s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.24s ease;
}

@keyframes card-enter {
  from {
    opacity: 0;
    transform: translateX(16px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.crawler-panel__card:hover {
  background: rgba(124, 231, 255, 0.07);
  border-color: rgba(124, 231, 255, 0.22);
  transform: translateX(-3px) scale(1.01);
  box-shadow: 0 4px 20px rgba(124, 231, 255, 0.08);
}

.crawler-panel__card:active {
  transform: translateX(-1px) scale(0.985);
  transition-duration: 0.08s;
}

/* 左侧高亮条 */
.crawler-panel__card-accent {
  position: absolute;
  left: 0;
  top: 20%;
  width: 2.5px;
  height: 60%;
  border-radius: 0 2px 2px 0;
  background: linear-gradient(180deg, #28c8b4, #328cff);
  opacity: 0;
  transform: scaleY(0.4);
  transition: opacity 0.28s ease, transform 0.28s cubic-bezier(0.22, 1, 0.36, 1);
}

.crawler-panel__card:hover .crawler-panel__card-accent {
  opacity: 1;
  transform: scaleY(1);
}

/* 扫光效果 */
.crawler-panel__card-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    105deg,
    transparent 40%,
    rgba(124, 231, 255, 0.06) 45%,
    rgba(124, 231, 255, 0.1) 50%,
    rgba(124, 231, 255, 0.06) 55%,
    transparent 60%
  );
  transform: translateX(-100%);
  pointer-events: none;
  transition: none;
}

.crawler-panel__card:hover .crawler-panel__card-shine {
  transform: translateX(100%);
  transition: transform 0.6s ease;
}

/* 头部 */
.crawler-panel__card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.crawler-panel__source {
  position: relative;
  font-size: 11px;
  color: rgba(124, 231, 255, 0.7);
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* 箭头指示 */
.crawler-panel__arrow {
  color: rgba(124, 231, 255, 0.2);
  flex-shrink: 0;
  transition: color 0.22s, transform 0.22s cubic-bezier(0.22, 1, 0.36, 1);
}

.crawler-panel__card:hover .crawler-panel__arrow {
  color: rgba(124, 231, 255, 0.8);
  transform: translateX(3px);
}

/* 标题 */
.crawler-panel__card-title {
  position: relative;
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: rgba(234, 244, 255, 0.88);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.22s;
}

.crawler-panel__card:hover .crawler-panel__card-title {
  color: rgba(248, 253, 255, 1);
}

/* 时间 */
.crawler-panel__card-time {
  position: relative;
  font-size: 11px;
  color: rgba(200, 220, 240, 0.36);
  transition: color 0.22s;
}

.crawler-panel__card:hover .crawler-panel__card-time {
  color: rgba(200, 220, 240, 0.55);
}

/* ---- 面板滑入动画 ---- */
.panel-slide-enter-active {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.24s ease;
}
.panel-slide-leave-active {
  transition: transform 0.22s ease-in, opacity 0.16s ease;
}
.panel-slide-enter-from {
  transform: translateX(24px) scale(0.96);
  opacity: 0;
}
.panel-slide-leave-to {
  transform: translateX(24px) scale(0.96);
  opacity: 0;
}

/* ---- 响应式 ---- */
@media (max-width: 768px) {
  .crawler-panel__body {
    width: 280px;
  }
}

@media (max-width: 480px) {
  .crawler-panel {
    top: 10px;
    right: 10px;
  }

  .crawler-panel__body {
    width: calc(100vw - 20px);
    max-height: 50vh;
  }
}
</style>
