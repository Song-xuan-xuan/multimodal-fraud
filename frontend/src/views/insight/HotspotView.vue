<template>
  <div class="insight-page hotspot-view">
    <PageHero
      eyebrow="专题洞察"
      title="热点洞察"
      description="统一呈现区域风险总量、类型趋势与省份分布，作为专题分析页的标准入口。"
    >
      <article class="hero-metric tech-panel">
        <span>新闻总量</span>
        <strong>{{ summary.total_news }}</strong>
        <small>全量热点样本</small>
      </article>
      <article class="hero-metric tech-panel danger">
        <span>高风险总量</span>
        <strong>{{ summary.total_fake }}</strong>
        <small>重点核查对象</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>覆盖省份</span>
        <strong>{{ summary.provinces.length }}</strong>
        <small>区域监测范围</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>最近更新</span>
        <strong>{{ updatedAtText }}</strong>
        <small>最新同步时间</small>
      </article>
    </PageHero>

    <section class="content-section tech-panel">
      <SectionHeader eyebrow="趋势监测" title="热点趋势" description="按省份筛选每日风险事件与低风险事件数量变化，统一专题页图表容器表现。">
        <template #actions>
          <el-select v-model="selectedProvince" clearable placeholder="按省份筛选" class="toolbar-select" @change="loadTrend">
            <el-option v-for="item in summary.provinces" :key="item.province" :label="item.province" :value="item.province" />
          </el-select>
          <el-button @click="refresh" :loading="loadingSummary || loadingTrend">刷新</el-button>
        </template>
      </SectionHeader>
      <HotspotTrendChart :points="trend.points" :loading="loadingTrend" />
    </section>

    <section class="content-section tech-panel">
      <SectionHeader eyebrow="区域排行" title="各省热点排行" description="按省份汇总事件量、高风险量与占比，延续洞察页统一表格容器风格。" />
      <el-skeleton v-if="loadingSummary" :rows="6" animated class="panel-skeleton" />
      <el-empty v-else-if="!summary.provinces.length" description="暂无省份排行数据" class="panel-empty" />
      <el-table v-else :data="summary.provinces" stripe class="data-table">
        <el-table-column prop="province" label="省份" width="120" />
        <el-table-column prop="total" label="事件总数" width="110" />
        <el-table-column prop="fake_count" label="高风险数" width="100" />
        <el-table-column prop="real_count" label="真实数" width="100" />
        <el-table-column label="高风险占比" min-width="220">
          <template #default="{ row }">
            <el-progress :percentage="row.fake_ratio" :stroke-width="14" :color="progressColor" />
          </template>
        </el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { hotspotApi } from '@/api/hotspot'
import type { HotspotSummaryResponse, HotspotTrendResponse } from '@/types/insight'
import HotspotTrendChart from '@/components/insight/HotspotTrendChart.vue'
import SectionHeader from '@/components/dashboard/SectionHeader.vue'
import PageHero from '@/components/page/PageHero.vue'
import { chartColors } from '@/utils/chartColors'

const heroDangerColor = chartColors.semantic.danger
const progressColor = chartColors.semantic.fake

const loadingSummary = ref(false)
const loadingTrend = ref(false)
const selectedProvince = ref<string>('')

const summary = reactive<HotspotSummaryResponse>({
  provinces: [],
  total_news: 0,
  total_fake: 0,
  updated_at: '',
})

const trend = reactive<HotspotTrendResponse>({ points: [] })

const updatedAtText = computed(() => {
  if (!summary.updated_at) return '-'
  const dt = new Date(summary.updated_at)
  if (Number.isNaN(dt.getTime())) return summary.updated_at
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const d = String(dt.getDate()).padStart(2, '0')
  const hh = String(dt.getHours()).padStart(2, '0')
  const mm = String(dt.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${hh}:${mm}`
})

async function loadSummary() {
  loadingSummary.value = true
  try {
    const data = await hotspotApi.getSummary()
    summary.provinces = data.provinces
    summary.total_news = data.total_news
    summary.total_fake = data.total_fake
    summary.updated_at = data.updated_at
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '热点统计加载失败')
  } finally {
    loadingSummary.value = false
  }
}

async function loadTrend() {
  loadingTrend.value = true
  try {
    const data = await hotspotApi.getTrend({ province: selectedProvince.value || undefined })
    trend.points = data.points
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '热点趋势加载失败')
  } finally {
    loadingTrend.value = false
  }
}

async function refresh() {
  await Promise.all([loadSummary(), loadTrend()])
}

onMounted(async () => {
  await refresh()
})
</script>

<style scoped lang="scss">
.insight-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-metric {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px;
}

.hero-metric span,
.hero-metric small {
  color: var(--tech-text-secondary);
}

.hero-metric strong {
  font-size: clamp(24px, 3vw, 34px);
  color: var(--tech-text-primary);
}

.hero-metric.danger strong {
  color: v-bind(heroDangerColor);
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
}

.toolbar-select {
  width: 180px;
}

.panel-skeleton,
.panel-empty {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.data-table {
  --el-table-border-color: rgba(131, 168, 201, 0.18);
  --el-table-header-bg-color: rgba(86, 194, 255, 0.08);
  --el-table-tr-bg-color: rgba(14, 28, 54, 0.6);
  --el-table-bg-color: transparent;
  --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.10);
  --el-table-text-color: var(--tech-text-primary);
  --el-table-header-text-color: var(--tech-text-secondary, #a0aec0);
}

.data-table :deep(.el-table__row--striped td.el-table__cell) {
  background: rgba(76, 201, 255, 0.04) !important;
}

:deep(.el-progress-bar__outer) {
  background: rgba(255, 255, 255, 0.06);
}

@media (max-width: 640px) {
  .content-section {
    padding: 20px;
  }
}
</style>

