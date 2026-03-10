<template>
  <div class="news-list-view" :class="pageMotionClass">
    <!-- <section class="hero-section">
      <div>
        <p class="hero-eyebrow">资讯中心</p>
        <h1 class="hero-title">新闻列表</h1>
        <p class="hero-description">延续旧版筛选、结果浏览与详情跳转路径，提供更清晰的分区与统一状态反馈。</p>
      </div>
    </section> -->

    <NewsFilterPanel
      v-model="draftFilters"
      :options="optionSets"
      :loading="loading"
      @apply="handleApply"
      @reset="handleReset"
    />

    <NewsResultSummary :summary="summary" :filters="appliedFilters" />

    <el-card shadow="never" class="content-card">
      <template #header>
        <NewsListToolbar v-model:mode="viewMode" :loading="loading" @refresh="fetchList" />
      </template>

      <el-alert
        v-if="errorMessage"
        class="content-alert"
        type="error"
        show-icon
        :closable="false"
        :title="errorMessage"
      />

      <el-skeleton v-if="loading" :rows="6" animated class="loading-skeleton" />

      <NewsListEmptyState
        v-else-if="!displayItems.length"
        :type="errorMessage ? 'error' : 'empty'"
        :title="errorMessage ? '加载失败' : '暂无匹配结果'"
        :description="errorMessage || '没有找到符合条件的新闻，请调整筛选条件后重试。'"
        :action-text="errorMessage ? '重新加载' : '重置筛选'"
        @action="errorMessage ? fetchList() : handleReset()"
      />

      <template v-else>
        <NewsCardList :items="displayItems" :mode="viewMode" @select="goToDetail" />
        <NewsListPagination
          :page="queryState.page"
          :per-page="appliedFilters.perPage"
          :total="summary.total"
          @change="handlePageChange"
        />
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { NewsItem } from '@/api/news'
import { newsApi } from '@/api/news'
import { appRoute } from '@/router'
import { useRouteTransition } from '@/composables/useRouteTransition'
import NewsCardList from '@/components/news/list/NewsCardList.vue'
import NewsFilterPanel from '@/components/news/list/NewsFilterPanel.vue'
import NewsListEmptyState from '@/components/news/list/NewsListEmptyState.vue'
import NewsListPagination from '@/components/news/list/NewsListPagination.vue'
import NewsListToolbar from '@/components/news/list/NewsListToolbar.vue'
import NewsResultSummary from '@/components/news/list/NewsResultSummary.vue'
import { useNewsListFilters } from '@/composables/news/useNewsListFilters'
import type { NewsListOptionSets, NewsListSummary } from '@/types/newsList'

const router = useRouter()
const { pageMotionClass } = useRouteTransition()
const { queryState, draftFilters, appliedFilters, apply, reset, goToPage } = useNewsListFilters()

const loading = ref(false)
const errorMessage = ref('')
const viewMode = ref<'card' | 'table'>('card')
const rawItems = ref<NewsItem[]>([])
const total = ref(0)
const totalPages = ref(0)
let listRequestId = 0

const baseLabels = ['投资理财', '刷单返利', '客服退款', '身份冒充', '待研判']
const basePerPageOptions = [10, 20, 50]

const optionSets = computed<NewsListOptionSets>(() => {
  const platforms = new Set<string>()
  const labels = new Set<string>(baseLabels)
  const propagationPlatforms = new Set<string>()

  rawItems.value.forEach((item) => {
    if (item.platform) {
      platforms.add(item.platform)
    }
    if (item.label) {
      labels.add(item.label)
    }

    const timeline = item.propagation_data?.timeline
    if (Array.isArray(timeline)) {
      timeline.forEach((entry: any) => {
        if (entry?.platform) {
          propagationPlatforms.add(String(entry.platform))
        }
      })
    }
  })

  return {
    platforms: Array.from(platforms),
    labels: Array.from(labels),
    propagationPlatforms: Array.from(propagationPlatforms),
    perPageOptions: basePerPageOptions,
  }
})

const displayItems = computed(() => {
  return rawItems.value.filter((item) => {
    const score = Number(item.credibility?.score ?? 0) * 100
    const min = appliedFilters.value.minCredibility ? Number(appliedFilters.value.minCredibility) : undefined
    const max = appliedFilters.value.maxCredibility ? Number(appliedFilters.value.maxCredibility) : undefined

    if (min !== undefined && score < min) return false
    if (max !== undefined && score > max) return false

    if (appliedFilters.value.propagationPlatform) {
      const timeline = item.propagation_data?.timeline
      const matched = Array.isArray(timeline)
        && timeline.some((entry: any) => String(entry?.platform || '') === appliedFilters.value.propagationPlatform)
      if (!matched) return false
    }

    if (appliedFilters.value.startDate && item.publish_time && item.publish_time < appliedFilters.value.startDate) {
      return false
    }
    if (appliedFilters.value.endDate && item.publish_time && item.publish_time > appliedFilters.value.endDate) {
      return false
    }

    return true
  })
})

const summary = computed<NewsListSummary>(() => {
  const effectiveTotal = errorMessage.value ? 0 : total.value
  const currentCount = displayItems.value.length
  const rangeStart = effectiveTotal === 0 || currentCount === 0 ? 0 : (queryState.value.page - 1) * appliedFilters.value.perPage + 1
  const rangeEnd = rangeStart === 0 ? 0 : rangeStart + currentCount - 1

  let activeFilterCount = 0
  if (appliedFilters.value.keyword) activeFilterCount += 1
  if (appliedFilters.value.platform) activeFilterCount += 1
  if (appliedFilters.value.label) activeFilterCount += 1
  if (appliedFilters.value.minCredibility) activeFilterCount += 1
  if (appliedFilters.value.maxCredibility) activeFilterCount += 1
  if (appliedFilters.value.propagationPlatform) activeFilterCount += 1
  if (appliedFilters.value.startDate) activeFilterCount += 1
  if (appliedFilters.value.endDate) activeFilterCount += 1

  return {
    total: effectiveTotal,
    currentPage: queryState.value.page,
    totalPages: totalPages.value,
    rangeStart,
    rangeEnd,
    activeFilterCount,
  }
})

async function fetchList() {
  const requestId = ++listRequestId
  loading.value = true
  errorMessage.value = ''

  try {
    const result = await newsApi.list({
      page: queryState.value.page,
      perPage: appliedFilters.value.perPage,
      keyword: appliedFilters.value.keyword || undefined,
      label: appliedFilters.value.label || undefined,
      platform: appliedFilters.value.platform || undefined,
    })

    if (requestId !== listRequestId) {
      return
    }

    rawItems.value = result.items
    total.value = result.total
    totalPages.value = result.total_pages
  } catch (error: any) {
    if (requestId !== listRequestId) {
      return
    }
    errorMessage.value = error?.response?.data?.detail || error?.message || '加载新闻列表失败'
    if (!rawItems.value.length) {
      total.value = 0
      totalPages.value = 0
    }
  } finally {
    if (requestId === listRequestId) {
      loading.value = false
    }
  }
}

async function handleApply() {
  await apply()
}

async function handleReset() {
  await reset()
}

async function handlePageChange(page: number) {
  await goToPage(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToDetail(item: NewsItem) {
  void router.push(appRoute.newsDetail(item.news_id))
}

watch(
  () => ({ ...queryState.value }),
  async () => {
    await fetchList()
  },
  { deep: true },
)

onMounted(async () => {
  await fetchList()
})
</script>

<style scoped>
.news-list-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero-section,
.content-card {
  border: 1px solid var(--tech-border-color);
}

.hero-section {
  padding: 28px;
  border-radius: var(--tech-radius-lg);
  background:
    linear-gradient(135deg, rgba(76, 201, 255, 0.12) 0%, rgba(9, 18, 34, 0.18) 42%, rgba(7, 17, 31, 0.96) 100%),
    var(--tech-bg-panel);
  box-shadow: var(--tech-shadow-sm);
}

.hero-eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.hero-title {
  margin: 10px 0 8px;
  font-size: 32px;
  color: var(--tech-text-primary);
}

.hero-description {
  margin: 0;
  max-width: 720px;
  line-height: 1.7;
  color: var(--tech-text-secondary);
}

.content-card {
  background: linear-gradient(180deg, rgba(10, 21, 39, 0.96), rgba(8, 18, 34, 0.98));
  box-shadow: var(--tech-shadow-sm);
}

.content-card :deep(.el-card__header) {
  border-bottom-color: var(--tech-divider-color);
  background: rgba(76, 201, 255, 0.03);
}

.content-card :deep(.el-card__body) {
  color: var(--tech-text-regular);
}

.content-card :deep(.el-pagination button),
.content-card :deep(.el-pagination .el-pager li) {
  border-color: var(--tech-border-color);
  background: rgba(125, 211, 252, 0.04);
  color: var(--tech-text-secondary);
}

.content-card :deep(.el-pagination .el-pager li.is-active) {
  border-color: rgba(76, 201, 255, 0.24);
  background: rgba(76, 201, 255, 0.14);
  color: var(--tech-color-primary-strong);
}

.content-card :deep(.el-empty__description p) {
  color: var(--tech-text-secondary);
}

.content-alert,
.loading-skeleton {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .hero-section {
    padding: 22px;
  }

  .hero-title {
    font-size: 26px;
  }
}
</style>


