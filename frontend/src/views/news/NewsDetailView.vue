<template>
  <div class="news-detail-view" v-loading="loading">
    <div class="detail-page-header">
      <el-page-header @back="$router.back()" :content="detail?.baseInfo.title || '新闻详情'" />
      <p v-if="detail?.baseInfo.summary" class="detail-summary">{{ detail.baseInfo.summary }}</p>
    </div>

    <el-alert
      v-if="errorMessage"
      class="error-alert"
      type="error"
      show-icon
      :closable="false"
    >
      <template #title>
        <div class="error-alert__content">
          <span>{{ errorMessage }}</span>
          <el-button text type="primary" @click="fetchDetail">重试</el-button>
        </div>
      </template>
    </el-alert>

    <el-empty v-if="!loading && !detail" description="暂无详情数据" />

    <div v-else-if="detail" class="detail-layout">
      <main class="detail-main">
        <PageSection
          section-id="base-info"
          eyebrow="NEWS DETAIL"
          title="基础信息"
          description="聚合案例标题、来源、时间与主体内容，作为后续风险分析与传播研判的入口。"
        >
          <TechCard>
            <BaseInfoCard :base-info="detail.baseInfo" />
          </TechCard>
        </PageSection>

        <PageSection
          v-if="detail.baseInfo.picUrl"
          section-id="detail-cover"
          eyebrow="VISUAL SNAPSHOT"
          title="相关图片"
          description="保留原始配图入口，提供更强的视觉聚焦与失败回退体验。"
        >
          <ProxyImage :src="detail.baseInfo.picUrl" height="360px" fit="cover" />
        </PageSection>

        <PageSection
          section-id="credibility"
          eyebrow="CREDIBILITY"
          title="风险分析"
          description="从来源、内容、逻辑与传播等维度展示当前案例的风险判定结果。"
        >
          <TechCard>
            <CredibilityDimensionCard :credibility="detail.credibility" />
          </TechCard>
        </PageSection>

        <PageSection
          v-if="moduleVisibility.propagationTrend"
          section-id="propagation-trend"
          eyebrow="PROPAGATION"
          title="传播趋势"
          description="回顾传播热度随时间变化的节奏，帮助识别爆发节点。"
        >
          <TechCard>
            <PropagationTimelineCard :propagation="detail.propagation" />
          </TechCard>
        </PageSection>

        <PageSection
          v-if="moduleVisibility.propagationPlatforms"
          section-id="propagation-platforms"
          eyebrow="PROPAGATION"
          title="平台分布"
          description="查看不同平台承载的传播份额，识别扩散主阵地。"
        >
          <TechCard>
            <PropagationGeoCard :propagation="detail.propagation" mode="platforms" />
          </TechCard>
        </PageSection>

        <PageSection
          v-if="moduleVisibility.propagationRegions"
          section-id="propagation-regions"
          eyebrow="PROPAGATION"
          title="地域分布"
          description="定位地域扩散范围，并联动省份详情展开进一步筛查。"
        >
          <TechCard>
            <PropagationGeoCard :propagation="detail.propagation" mode="regions" />
          </TechCard>
        </PageSection>

        <PageSection
          section-id="audience-profile"
          eyebrow="AUDIENCE"
          title="用户画像"
          description="整理受众画像信息，辅助判断传播对象与内容偏向。"
        >
          <TechCard>
            <AudienceProfileCard :items="audienceProfileItems" :empty-text="detail.propagation.emptyReason" />
          </TechCard>
        </PageSection>

        <PageSection
          v-if="moduleVisibility.relationsRelatedNews"
          section-id="related-news"
          eyebrow="RELATIONS"
          title="相关新闻"
          description="关联历史新闻与近似议题，帮助快速建立上下文。"
        >
          <TechCard>
            <RelatedNewsListCard :items="detail.relations.relatedNews" :empty-text="detail.relations.emptyReason" />
          </TechCard>
        </PageSection>

        <PageSection
          v-if="moduleVisibility.relationsKnowledgeNodes"
          section-id="knowledge-nodes"
          eyebrow="RELATIONS"
          title="知识节点"
          description="抽取核心节点，辅助构建风险链路与实体关系。"
        >
          <TechCard>
            <KnowledgeNodesCard
              :nodes="detail.relations.knowledgeNodes"
              :edges="[]"
              :empty-text="detail.relations.emptyReason"
            />
          </TechCard>
        </PageSection>

        <PageSection
          v-if="moduleVisibility.relationsEdges"
          section-id="relation-edges"
          eyebrow="RELATIONS"
          title="关系连线"
          description="展示知识节点之间的结构连线，方便复核传播关系。"
        >
          <TechCard>
            <KnowledgeNodesCard
              :nodes="detail.relations.knowledgeNodes"
              :edges="detail.relations.edges"
              :empty-text="detail.relations.emptyReason"
            />
          </TechCard>
        </PageSection>
      </main>

      <aside class="detail-side">
        <DetailAnchorNav :anchors="enhancedAnchors" :active-target="activeTarget" @navigate="scrollToSection" />
        <ProvinceDetailPanel :province="currentProvince" />
      </aside>
    </div>

    <FloatingActionRail v-if="detail">
      <NewsActionBar
        ref="actionBarRef"
        :favorited="favorited"
        :stats="feedbackStats"
        :my-vote="myVote"
        :vote-loading="engagementLoading.vote"
        :rebuttal-loading="engagementLoading.rebuttal"
        @toggle-favorite="handleToggleFavorite"
        @vote="handleVote"
        @submit-rebuttal="handleSubmitRebuttal"
      />
    </FloatingActionRail>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import DetailAnchorNav from '@/components/news/detail/DetailAnchorNav.vue'
import AudienceProfileCard from '@/components/news/detail/AudienceProfileCard.vue'
import BaseInfoCard from '@/components/news/detail/BaseInfoCard.vue'
import CredibilityDimensionCard from '@/components/news/detail/CredibilityDimensionCard.vue'
import KnowledgeNodesCard from '@/components/news/detail/KnowledgeNodesCard.vue'
import PropagationGeoCard from '@/components/news/detail/PropagationGeoCard.vue'
import PropagationTimelineCard from '@/components/news/detail/PropagationTimelineCard.vue'
import RelatedNewsListCard from '@/components/news/detail/RelatedNewsListCard.vue'
import NewsActionBar from '@/components/engagement/NewsActionBar.vue'
import ProxyImage from '@/components/common/ProxyImage.vue'
import ProvinceDetailPanel from '@/components/map/ProvinceDetailPanel.vue'
import FloatingActionRail from '@/components/page/FloatingActionRail.vue'
import PageSection from '@/components/page/PageSection.vue'
import TechCard from '@/components/page/TechCard.vue'
import { useNewsDetailPage } from '@/composables/news/useNewsDetailPage'
import { useEngagementStore } from '@/stores/engagement'
import type { VoteOption } from '@/types/engagement'

const route = useRoute()
const { loading, errorMessage, detail, raw, moduleVisibility, anchors, load, reset } = useNewsDetailPage()
const engagementStore = useEngagementStore()

const actionBarRef = ref<{ closeDialog: () => void } | null>(null)
const activeTarget = ref('')
const currentProvince = ref('')
let observer: IntersectionObserver | null = null
let detailRequestId = 0

const currentNewsId = computed(() => {
  if (detail.value?.baseInfo.newsId) {
    return detail.value.baseInfo.newsId
  }
  return String(route.params.id || '')
})

const feedbackStats = computed(() => engagementStore.getStats(currentNewsId.value))
const myVote = computed(() => engagementStore.getMyVote(currentNewsId.value))
const engagementLoading = computed(() => engagementStore.getLoading(currentNewsId.value))
const favorited = computed(() => engagementStore.isFavorited(currentNewsId.value))

const enhancedAnchors = computed(() => {
  const items: Array<{ target: string; label: string }> = anchors.value.map((anchor) => ({
    target: anchor.target,
    label: anchor.label,
  }))
  const audienceIndex = items.findIndex((item) => item.target === 'related-news')
  if (!items.some((item) => item.target === 'audience-profile')) {
    if (audienceIndex === -1) {
      items.push({ target: 'audience-profile', label: '用户画像' })
    } else {
      items.splice(audienceIndex, 0, { target: 'audience-profile', label: '用户画像' })
    }
  }
  if (detail.value?.baseInfo.picUrl && !items.some((item) => item.target === 'detail-cover')) {
    items.splice(1, 0, { target: 'detail-cover', label: '相关图片' })
  }
  return items
})

const provinceCandidates = computed(() => {
  const set = new Set<string>()
  const location = detail.value?.baseInfo.location?.trim() || ''
  if (location && location !== '-') {
    set.add(location)
  }

  const regions = detail.value?.propagation.regionDistribution || []
  regions.forEach((item) => {
    const name = item.region?.trim()
    if (name) {
      set.add(name)
    }
  })

  return Array.from(set)
})

const audienceProfileItems = computed(() => {
  const source = raw.value?.propagation_data?.audience_profile
  if (!source || typeof source !== 'object' || Array.isArray(source)) {
    return []
  }
  return Object.entries(source)
    .map(([label, value]) => ({
      label,
      value: typeof value === 'string' ? value : String(value ?? '-'),
    }))
    .filter((item) => item.label.trim())
})

async function fetchDetail() {
  const id = route.params.id as string
  if (!id) return
  const requestId = ++detailRequestId
  await load(id)
  if (requestId !== detailRequestId) {
    return
  }
  if (detail.value?.baseInfo.newsId) {
    try {
      await engagementStore.fetchStats(detail.value.baseInfo.newsId)
    } catch {
      ElMessage.warning('互动数据加载失败，详情主体内容已正常显示')
    }
  }
  if (requestId !== detailRequestId || !detail.value) {
    return
  }
  await nextTick()
  initObserver()
  if (enhancedAnchors.value.length) {
    activeTarget.value = enhancedAnchors.value[0].target
  }
}

function scrollToSection(target: string) {
  const element = document.getElementById(target)
  if (!element) return
  activeTarget.value = target
  element.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function initObserver() {
  observer?.disconnect()
  if (!enhancedAnchors.value.length) return

  observer = new IntersectionObserver(
    (entries) => {
      const visibleEntry = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0]

      if (visibleEntry?.target?.id) {
        activeTarget.value = visibleEntry.target.id
      }
    },
    {
      root: null,
      rootMargin: '-22% 0px -58% 0px',
      threshold: [0, 0.1, 0.3, 0.6, 1],
    },
  )

  enhancedAnchors.value.forEach((anchor) => {
    const element = document.getElementById(anchor.target)
    if (element) {
      observer?.observe(element)
    }
  })
}

function handleToggleFavorite() {
  if (!currentNewsId.value) return
  const next = engagementStore.toggleFavorite(currentNewsId.value)
  ElMessage.success(next ? '已加入收藏' : '已取消收藏')
}

async function handleVote(vote: VoteOption) {
  if (!currentNewsId.value) return
  try {
    await engagementStore.submitVote(currentNewsId.value, vote)
    ElMessage.success('投票提交成功')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '投票失败')
  }
}

async function handleSubmitRebuttal(content: string) {
  if (!currentNewsId.value) return
  try {
    await engagementStore.submitRebuttal(currentNewsId.value, content)
    ElMessage.success('驳斥已提交，等待审核')
    actionBarRef.value?.closeDialog()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '驳斥提交失败')
  }
}

watch(
  () => route.params.id,
  async () => {
    await fetchDetail()
  },
)

watch(
  () => enhancedAnchors.value.map((item) => item.target).join('|'),
  async () => {
    await nextTick()
    initObserver()
  },
)

watch(
  provinceCandidates,
  (list) => {
    if (!list.length) {
      currentProvince.value = ''
      return
    }
    if (!list.includes(currentProvince.value)) {
      currentProvince.value = list[0]
    }
  },
  { immediate: true },
)

onMounted(async () => {
  engagementStore.ensureHydrated()
  await fetchDetail()
})

onBeforeUnmount(() => {
  observer?.disconnect()
  reset()
})
</script>

<style scoped>
.news-detail-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 120px;
}

.detail-page-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px 24px;
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(76, 201, 255, 0.12), transparent 32%),
    linear-gradient(135deg, rgba(14, 28, 48, 0.94), rgba(8, 18, 34, 0.98));
  border: 1px solid var(--tech-border-color);
  box-shadow: var(--tech-shadow-sm);
}

.detail-page-header :deep(.el-page-header__title),
.detail-page-header :deep(.el-page-header__content) {
  color: var(--tech-text-primary);
}

.detail-page-header :deep(.el-page-header__icon) {
  color: var(--tech-color-primary-strong);
}

.detail-summary {
  margin: 0;
  max-width: 860px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--tech-text-secondary);
}

.error-alert {
  margin-top: -8px;
}

.error-alert__content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  align-items: start;
}

.detail-main {
  display: flex;
  flex-direction: column;
  gap: 32px;
  min-width: 0;
}

.detail-side {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 1200px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .detail-side {
    order: -1;
  }
}

@media (max-width: 768px) {
  .news-detail-view {
    gap: 20px;
    padding-bottom: 140px;
  }

  .detail-page-header {
    padding: 18px;
    border-radius: 22px;
  }

  .detail-main {
    gap: 24px;
  }
}
</style>

