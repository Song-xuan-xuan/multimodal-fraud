<template>
  <div class="page-shell dashboard-view" :class="pageMotionClass">
    <header class="dashboard-hero tech-panel">
      <div class="dashboard-hero__content">
        <p class="dashboard-hero__eyebrow">信息驾驶舱</p>
        <div class="dashboard-hero__title-row">
          <div>
            <h1>多模态反诈监测总览</h1>
            <p>
              聚合风险事件、案例态势、重点线索与智能助手入口，作为反诈助手的统一监测中心。
            </p>
          </div>
          <div class="dashboard-hero__actions">
            <el-button type="primary" @click="navigate(appRoute.newsList())">进入案例库</el-button>
            <el-button v-if="isAdmin" @click="navigate(appRoute.adminReviewWorkbench)">治理工作台</el-button>
          </div>
        </div>
        <StatsCardGrid :items="statsCards" />
        <el-alert
          v-if="errorMessage"
          class="dashboard-view__alert"
          type="warning"
          show-icon
          :closable="false"
          :title="errorMessage"
        />
      </div>
    </header>

    <DashboardGrid>
      <template #hero>
        <section class="dashboard-command tech-panel">
          <div class="dashboard-command__head">
            <div>
              <p class="dashboard-command__eyebrow">值守摘要</p>
              <h2>当前班次重点</h2>
            </div>
            <el-tag type="info" effect="dark">{{ formattedUpdatedAt }}</el-tag>
          </div>
          <div class="dashboard-command__body">
            <article v-for="item in commandBriefs" :key="item.label" class="dashboard-command__brief tech-surface">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <small>{{ item.tip }}</small>
            </article>
          </div>
        </section>
      </template>

      <template #map>
        <MapInsightCard :metrics="mapMetrics" :provinces="mapProvincePins" @navigate="navigate" />
      </template>

      <template #hotspot>
        <HotspotCard
          :total-news="hotspotSummary.total_news"
          :total-fake="hotspotSummary.total_fake"
          :updated-at="formattedUpdatedAt"
          :provinces="hotspotTopProvinces"
          @navigate="navigate"
        />
      </template>

      <template #rumors>
        <TopRumorsCard :items="topRumors" @navigate="navigate" @open-news="openNewsDetail" />
      </template>

      <template #media>
        <MediaRankingRail :items="mediaRanking" @navigate="navigate" />
      </template>
    </DashboardGrid>

    <AlertBubble :alerts="alerts" @action="onAlertAction" />
    <AIPopupPanel @navigate="navigate" />
    <FloatingQuickActions :items="quickActions" @navigate="navigate" />
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, reactive, ref } from 'vue'
import { useRouter, type RouteLocationRaw } from 'vue-router'
import api from '@/api/index'
import { newsApi, type NewsItem } from '@/api/news'
import { hotspotApi } from '@/api/hotspot'
import { mapApi } from '@/api/map'
import { appRoute, normalizeAppRouteTarget } from '@/router'
import { useRouteTransition } from '@/composables/useRouteTransition'
import type { HotspotSummaryResponse } from '@/types/insight'
import DashboardGrid from '@/components/dashboard/DashboardGrid.vue'
// import AlertBubble from '@/components/dashboard/AlertBubble.vue'
// import AIPopupPanel from '@/components/dashboard/AIPopupPanel.vue'
import FloatingQuickActions from '@/components/dashboard/FloatingQuickActions.vue'
import MediaRankingRail from '@/components/dashboard/MediaRankingRail.vue'
import HotspotCard from '@/components/dashboard/HotspotCard.vue'
import StatsCardGrid from '@/components/dashboard/StatsCardGrid.vue'
import TopRumorsCard from '@/components/dashboard/TopRumorsCard.vue'
import { useAuthStore } from '@/stores/auth'
import { isAdminUsername } from '@/components/layout/navigation'

const MapInsightCard = defineAsyncComponent(() => import('@/components/dashboard/MapInsightCard.vue'))

const router = useRouter()
const authStore = useAuthStore()
const { pageMotionClass } = useRouteTransition()
const isAdmin = computed(() => isAdminUsername(authStore.username))

const recentNews = ref<NewsItem[]>([])
const loading = ref(false)
const errorMessage = ref('')
let summaryRequestId = 0
const stats = reactive({
  total: 0,
  fake: 0,
  verified: 0,
  pending: 0,
})
const hotspotSummary = reactive<HotspotSummaryResponse>({
  provinces: [],
  total_news: 0,
  total_fake: 0,
  updated_at: '',
})

const provincePinLayout = [
  { left: '18%', top: '22%' },
  { left: '54%', top: '18%' },
  { left: '66%', top: '46%' },
  { left: '30%', top: '58%' },
]

const quickActions = computed(() => [
  { label: '风险分析', path: '/detection/ai', icon: 'AI' },
  { label: '风险核验', path: '/fact-check', icon: 'FC' },
  { label: '线索上报', path: '/report', icon: 'RP' },
  ...(isAdmin.value ? [{ label: '治理工作台', path: '/admin/review-workbench', icon: 'GW' }] : []),
])

const statsCards = computed(() => [
  { label: '事件总数', value: stats.total, tip: '全量风险样本', tone: 'primary' as const },
  { label: '高风险事件', value: stats.fake, tip: '优先处置', tone: 'danger' as const },
  { label: '已研判', value: stats.verified, tip: '报告已生成', tone: 'success' as const },
  { label: '待复核', value: stats.pending, tip: '需进一步复核', tone: 'warning' as const },
])

const topRumors = computed(() => {
  return recentNews.value
    .slice()
    .sort((a, b) => Number(a.iscredit) - Number(b.iscredit))
    .slice(0, 4)
    .map((item) => ({
      news_id: item.news_id,
      title: item.title,
      summary: item.summary || item.content?.slice(0, 70) || '暂无摘要',
      label: item.label,
      platform: item.platform,
      publish_time: formatDate(item.publish_time),
      location: item.location,
      iscredit: item.iscredit,
    }))
})

const hotspotTopProvinces = computed(() => {
  return hotspotSummary.provinces
    .slice()
    .sort((a, b) => b.fake_ratio - a.fake_ratio)
    .slice(0, 4)
})

const mapProvincePins = computed(() => {
  return hotspotTopProvinces.value.map((item, index) => ({
    province: item.province,
    fake_count: item.fake_count,
    style: provincePinLayout[index] || provincePinLayout[provincePinLayout.length - 1],
  }))
})

const mapMetrics = computed(() => [
  {
    label: '高风险区域',
    value: hotspotTopProvinces.value[0]?.province || '-',
    tip: '高风险占比最高地区',
  },
  {
    label: '风险峰值',
    value: hotspotTopProvinces.value[0] ? `${hotspotTopProvinces.value[0].fake_ratio}%` : '-',
    tip: '用于优先派单',
  },
  {
    label: '覆盖省份',
    value: hotspotSummary.provinces.length,
    tip: '地图数据同步完成',
  },
])

const mediaRanking = computed(() => {
  const buckets = new Map<string, number>()
  recentNews.value.forEach((item) => {
    const key = item.platform || '未知来源'
    buckets.set(key, (buckets.get(key) || 0) + 1)
  })

  const total = recentNews.value.length || 1
  return Array.from(buckets.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, value], index) => ({
      rank: `0${index + 1}`,
      name,
      description: index === 0 ? '主要传播来源' : '高频出现来源',
      value,
      share: `${Math.round((value / total) * 100)}% 样本占比`,
    }))
})

const formattedUpdatedAt = computed(() => {
  const raw = hotspotSummary.updated_at
  if (!raw) return '刚刚同步'
  const dt = new Date(raw)
  if (Number.isNaN(dt.getTime())) return raw
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`
})

const alerts = computed(() => {
  const topProvince = hotspotTopProvinces.value[0]
  const pendingRumor = topRumors.value[0]
  return [
    {
      title: topProvince ? `${topProvince.province} 风险抬升` : '区域监测已上线',
      description: topProvince
        ? `当前高风险占比 ${topProvince.fake_ratio}%，建议进入热点页查看趋势。`
        : '地图与热点模块已同步，可进入区域洞察页深挖。',
      time: formattedUpdatedAt.value,
      level: 'critical' as const,
      levelText: '高优先级',
      actionLabel: '查看热点',
      actionPath: '/insight/hotspot',
    },
    {
      title: pendingRumor ? '发现待复核内容' : '重点线索池待更新',
      description: pendingRumor
        ? `《${pendingRumor.title.slice(0, 18)}${pendingRumor.title.length > 18 ? '…' : ''}》进入优先复核列表。`
        : '数据为空时将自动回退为总览态提示。',
      time: formattedUpdatedAt.value,
      level: 'warning' as const,
      levelText: '待处理',
      actionLabel: '打开案例库',
      actionPath: '/news',
    },
    {
      title: '反诈助手入口可用',
      description: '可直接跳转到知识问答、风险分析或 Agent 流程。',
      time: formattedUpdatedAt.value,
      level: 'info' as const,
      levelText: '快捷入口',
      actionLabel: '进入助手',
      actionPath: '/ai/assistant',
    },
  ]
})

const commandBriefs = computed(() => [
  {
    label: '重点地区',
    value: hotspotTopProvinces.value[0]?.province || '-',
    tip: '建议优先复核该地区传播链',
  },
  {
    label: '待复核线索',
    value: topRumors.value.length,
    tip: '优先处理首页已聚合条目',
  },
  {
    label: '智能入口',
    value: quickActions.value.length,
    tip: '可快速进入分析、问答与上报流程',
  },
])

function formatDate(value: string) {
  if (!value) return '-'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return value
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

function navigate(target: RouteLocationRaw) {
  void router.push(normalizeAppRouteTarget(target))
}

function openNewsDetail(newsId: string) {
  void router.push(appRoute.newsDetail(newsId))
}

function onAlertAction(path?: string) {
  if (!path) return
  navigate(path)
}

async function loadSummary() {
  const requestId = ++summaryRequestId
  loading.value = true
  errorMessage.value = ''
  try {
    const [newsListResult, hotspotResult] = await Promise.allSettled([
      newsApi.list({ page: 1, perPage: 20 }),
      hotspotApi.getSummary(),
    ])

    if (requestId !== summaryRequestId) {
      return
    }

    const failures: string[] = []

    if (newsListResult.status === 'fulfilled') {
      const newsList = newsListResult.value
      recentNews.value = newsList.items || []
      stats.verified = recentNews.value.filter((item) => item.credibility?.verified).length
    } else {
      failures.push('案例数据')
    }

    if (hotspotResult.status === 'fulfilled') {
      const hotspotSummaryResponse = hotspotResult.value
      hotspotSummary.provinces = hotspotSummaryResponse.provinces || []
      hotspotSummary.total_news = hotspotSummaryResponse.total_news || 0
      hotspotSummary.total_fake = hotspotSummaryResponse.total_fake || 0
      hotspotSummary.updated_at = hotspotSummaryResponse.updated_at || ''
      stats.total = hotspotSummary.total_news
      stats.fake = hotspotSummary.total_fake
    } else {
      failures.push('热点数据')
    }

    stats.pending = Math.max(stats.total - stats.verified, 0)
    if (failures.length) {
      errorMessage.value = `部分数据加载失败：${failures.join('、')}。已显示最近一次可用内容。`
    }
  } catch (error) {
    if (requestId !== summaryRequestId) {
      return
    }
    console.error(error)
    errorMessage.value = '看板数据加载失败，已保留当前页面内容。'
  } finally {
    if (requestId === summaryRequestId) {
      loading.value = false
    }
  }
}

onMounted(() => {
  void loadSummary()
})
</script>

<style scoped lang="scss">
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-view__alert {
  margin-top: 4px;
}

.dashboard-hero,
.dashboard-command {
  padding: 24px;
}

.dashboard-hero__content,
.dashboard-command__body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.dashboard-hero__eyebrow,
.dashboard-command__eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.dashboard-hero__title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.dashboard-hero__title-row h1,
.dashboard-command__head h2 {
  margin: 6px 0 0;
  color: var(--tech-text-primary);
}

.dashboard-hero__title-row p {
  margin: 10px 0 0;
  max-width: 720px;
  color: var(--tech-text-secondary);
  line-height: 1.7;
}

.dashboard-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.dashboard-command__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.dashboard-command__body {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.dashboard-command__brief {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
  border: 1px solid color-mix(in srgb, var(--tech-color-primary) 16%, transparent);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 24%, rgba(255, 255, 255, 0.02));
}

.dashboard-command__brief span,
.dashboard-command__brief small {
  color: var(--tech-text-secondary);
}

.dashboard-command__brief strong {
  color: var(--tech-text-primary);
  font-size: 24px;
}

@media (max-width: 900px) {
  .dashboard-hero__title-row,
  .dashboard-command__head {
    flex-direction: column;
  }

  .dashboard-command__body {
    grid-template-columns: 1fr;
  }
}
</style>
