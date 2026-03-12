<template>
  <div class="insight-page map-view" :class="pageMotionClass">
    <PageHero
      eyebrow="专题洞察"
      title="风险地图"
      description="以统一专题页壳体呈现全国风险分布、更新时间与区域下钻，增强地图分析页面的边界感。"
    >
      <article class="hero-metric tech-panel danger">
        <span>高风险区域</span>
        <strong>{{ topProvince?.province || '-' }}</strong>
        <small>当前高风险事件最多省份</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>风险峰值</span>
        <strong>{{ topProvince?.fake_count ?? 0 }}</strong>
        <small>按省统计</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>覆盖省份</span>
        <strong>{{ mapData.length }}</strong>
        <small>地图数据维度</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>最近更新</span>
        <strong>{{ formattedUpdatedAt }}</strong>
        <small>同步时间</small>
      </article>
      <template #actions>
        <el-button @click="refreshMapData" :loading="loading">刷新数据</el-button>
      </template>
    </PageHero>

    <section class="content-section tech-panel map-panel">
      <SectionHeader eyebrow="空间分布" title="中国地图分布" description="统一地图、图表与空态容器视觉，支持指标切换与省份下钻。">
        <template #actions>
          <el-radio-group v-model="metric" size="small">
            <el-radio-button label="fake">按高风险数量</el-radio-button>
            <el-radio-button label="total">按新闻总量</el-radio-button>
          </el-radio-group>
        </template>
      </SectionHeader>

      <div class="map-canvas-shell" v-loading="loading">
        <div ref="mapContainerRef" class="map-canvas" />
        <el-empty v-if="!loading && !mapData.length" description="暂无地图数据" class="panel-empty" />
      </div>

      <el-alert
        v-if="errorMsg"
        :title="errorMsg"
        type="error"
        show-icon
        :closable="false"
        class="panel-alert"
      />
    </section>

    <el-drawer v-model="provinceDrawerVisible" :title="provinceDetail?.province ? `${provinceDetail.province} 详情` : '省份详情'" size="48%">
      <div class="drawer-shell">
        <el-skeleton v-if="loadingProvinceDetail" :rows="6" animated />

        <template v-else>
          <el-descriptions v-if="provinceDetail" :column="2" border>
            <el-descriptions-item label="总数">{{ provinceDetail.stats.total }}</el-descriptions-item>
            <el-descriptions-item label="高风险数">{{ provinceDetail.stats.fake_count }}</el-descriptions-item>
            <el-descriptions-item label="低风险数">{{ provinceDetail.stats.real_count }}</el-descriptions-item>
            <el-descriptions-item label="未知标签">{{ provinceDetail.stats.unknown_count }}</el-descriptions-item>
          </el-descriptions>

          <section class="drawer-section tech-panel">
            <SectionHeader eyebrow="明细列表" title="案例列表" description="按标签筛选省份下钻数据，保持与专题页表格容器一致。">
              <template #actions>
                <el-select v-model="provinceLabelFilter" size="small" class="drawer-filter" @change="onProvinceLabelFilterChange">
                  <el-option label="全部标签" value="all" />
                  <el-option label="仅高风险" value="fake" />
                  <el-option label="仅低风险" value="real" />
                </el-select>
              </template>
            </SectionHeader>

            <el-table :data="provinceDetail?.items || []" stripe class="data-table">
              <el-table-column prop="news_id" label="ID" width="160" />
              <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
              <el-table-column prop="label" label="标签" width="120" />
              <el-table-column prop="platform" label="平台" width="120" />
              <el-table-column prop="publish_time" label="发布时间" width="180" />
              <el-table-column label="操作" width="90">
                <template #default="{ row }">
                  <el-button text type="primary" @click="openNewsDetail(row.news_id)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-empty v-if="!provinceDetail?.items?.length" description="该地区暂无明细数据" class="panel-empty panel-empty--compact" />

            <div class="drawer-pagination">
              <el-pagination
                background
                layout="total, sizes, prev, pager, next"
                :total="provinceDetail?.total || 0"
                :current-page="provincePage"
                :page-size="provincePageSize"
                :page-sizes="[10, 20, 50]"
                @current-change="onProvincePageChange"
                @size-change="onProvincePageSizeChange"
              />
            </div>
          </section>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts/core'
import { MapChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'
import { TooltipComponent, VisualMapComponent } from 'echarts/components'
import type { ECharts } from 'echarts/core'
import { appRoute } from '@/router'
import { useRouteTransition } from '@/composables/useRouteTransition'
import { mapApi, type ChinaMapDataResponse, type ProvinceDetailResponse, type ProvinceMapStat } from '@/api/map'
import SectionHeader from '@/components/dashboard/SectionHeader.vue'
import PageHero from '@/components/page/PageHero.vue'
import { chartColors } from '@/utils/chartColors'

echarts.use([MapChart, TooltipComponent, VisualMapComponent, CanvasRenderer])

const router = useRouter()
const { pageMotionClass } = useRouteTransition()

const CHINA_PROVINCES = [
  '北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏',
  '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
  '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '内蒙古', '广西', '西藏',
  '宁夏', '新疆', '香港', '澳门',
]

const mapContainerRef = ref<HTMLDivElement | null>(null)
const chartInstance = ref<ECharts | null>(null)

const metric = ref<'fake' | 'total'>('fake')
const loading = ref(false)
const errorMsg = ref('')
const mapData = ref<ProvinceMapStat[]>([])
const updatedAt = ref('')

const provinceDrawerVisible = ref(false)
const loadingProvinceDetail = ref(false)
const provinceDetail = ref<ProvinceDetailResponse | null>(null)
const provincePage = ref(1)
const provincePageSize = ref(20)
const selectedProvince = ref('')
const provinceLabelFilter = ref<'all' | 'fake' | 'real'>('all')

let cachedGeoJson: any | null = null
let cachedMapData: ProvinceMapStat[] | null = null

const mapColors = chartColors.map
const heroDangerColor = chartColors.semantic.danger

const mapMax = computed(() => {
  if (!mapData.value.length) return 1
  const values = mapData.value.map((item) => (metric.value === 'fake' ? item.fake_count : item.total))
  return Math.max(...values, 1)
})

const formattedUpdatedAt = computed(() => {
  if (!updatedAt.value) return '-'
  const dt = new Date(updatedAt.value)
  if (Number.isNaN(dt.getTime())) return updatedAt.value
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const d = String(dt.getDate()).padStart(2, '0')
  const hh = String(dt.getHours()).padStart(2, '0')
  const mm = String(dt.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${hh}:${mm}`
})

const topProvince = computed(() => {
  return mapData.value.slice().sort((a, b) => b.fake_count - a.fake_count)[0]
})

function getProvinceRiskColor(item?: ProvinceMapStat) {
  if (!item || item.fake_count <= 0) return mapColors.riskLow
  const ratio = item.total ? item.fake_count / item.total : 0
  if (item.fake_count >= Math.max(10, Math.round(mapMax.value * 0.55)) || ratio >= 0.45) return mapColors.riskHigh
  if (item.fake_count >= Math.max(3, Math.round(mapMax.value * 0.22)) || ratio >= 0.2) return mapColors.riskMedium
  return mapColors.riskLow
}

function withAllProvinces(raw: ProvinceMapStat[]) {
  const index = new Map(raw.map((item) => [item.province, item]))
  return CHINA_PROVINCES.map((province) => {
    const hit = index.get(province)
    if (hit) return hit
    return {
      province,
      total: 0,
      fake_count: 0,
      real_count: 0,
      unknown_count: 0,
      value: 0,
    } as ProvinceMapStat
  })
}

async function ensureMapRegistered() {
  try {
    if (!cachedGeoJson) {
      cachedGeoJson = await mapApi.chinaGeoJson()
    }
    echarts.registerMap('china', cachedGeoJson as any)
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '中国地图数据加载失败'
    throw e
  }
}

async function loadChinaData(forceRefresh = false) {
  if (cachedMapData && !forceRefresh) {
    mapData.value = cachedMapData
    return
  }

  const data: ChinaMapDataResponse = await mapApi.chinaData()
  updatedAt.value = data.updated_at || ''
  mapData.value = withAllProvinces(data.provinces || [])
  cachedMapData = mapData.value
}

function renderMap() {
  if (!mapContainerRef.value || !mapData.value.length) return

  if (!chartInstance.value) {
    chartInstance.value = echarts.init(mapContainerRef.value, undefined, {
      renderer: 'canvas',
      useDirtyRect: true,
    })
    chartInstance.value.on('click', (params: any) => {
      const provinceName = String(params?.name || '').trim()
      if (!provinceName) return
      void openProvinceDetail(provinceName)
    })
  }

  const seriesData = mapData.value.map((item) => ({
    name: item.province,
    value: metric.value === 'fake' ? item.fake_count : item.total,
    itemStyle: {
      areaColor: getProvinceRiskColor(item),
    },
  }))

  chartInstance.value.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: chartColors.tooltip.backgroundColor,
      borderColor: mapColors.tooltipBorder,
      textStyle: chartColors.tooltip.textStyle,
      extraCssText: 'box-shadow: 0 14px 32px rgba(0, 0, 0, 0.34); border-radius: 12px;',
      formatter: (params: any) => {
        const name = String(params?.name || '-')
        const hit = mapData.value.find((x) => x.province === name)
        if (!hit) return `${name}<br/>暂无数据`
        const ratio = hit.total ? Math.round((hit.fake_count / hit.total) * 100) : 0
        const riskText = hit.fake_count <= 0 ? '低' : ratio >= 45 || hit.fake_count >= Math.max(10, Math.round(mapMax.value * 0.55)) ? '高' : ratio >= 20 || hit.fake_count >= Math.max(3, Math.round(mapMax.value * 0.22)) ? '中' : '低'
        return `${name}<br/>风险等级：${riskText}<br/>新闻总数：${hit.total}<br/>高风险数：${hit.fake_count}<br/>低风险数：${hit.real_count}<br/>谣言占比：${ratio}%`
      },
    },
    visualMap: {
      min: 0,
      max: mapMax.value,
      left: 'left',
      bottom: 24,
      text: ['高风险', '低风险'],
      calculable: true,
      textStyle: chartColors.legend.textStyle,
      itemWidth: 14,
      itemHeight: 112,
      inRange: {
        color: mapColors.visualRange,
      },
      seriesIndex: 0,
    },
    series: [
      {
        name: metric.value === 'fake' ? '高风险数量' : '新闻总量',
        type: 'map',
        map: 'china',
        roam: true,
        selectedMode: 'single',
        label: { show: false },
        itemStyle: {
          borderColor: mapColors.areaBorder,
          borderWidth: 1,
          areaColor: mapColors.areaBase,
          shadowColor: mapColors.areaShadow,
          shadowBlur: 4,
        },
        emphasis: {
          label: { show: true, color: chartColors.status.label },
          itemStyle: {
            areaColor: mapColors.areaHover,
            borderColor: mapColors.areaSelected,
            borderWidth: 1.2,
            shadowColor: mapColors.areaShadow,
            shadowBlur: 14,
          },
        },
        select: {
          label: { color: chartColors.status.label },
          itemStyle: {
            areaColor: mapColors.areaSelected,
            borderColor: chartColors.status.label,
            borderWidth: 1.4,
            shadowColor: mapColors.areaShadow,
            shadowBlur: 20,
          },
        },
        data: seriesData,
        progressive: 100,
        progressiveThreshold: 500,
      },
    ],
  })
}

async function refreshMapData() {
  loading.value = true
  errorMsg.value = ''
  try {
    cachedMapData = null
    await loadChinaData(true)
    await nextTick()
    renderMap()
    ElMessage.success('地图数据已刷新')
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '地图数据刷新失败'
    ElMessage.error(errorMsg.value)
  } finally {
    loading.value = false
  }
}

async function openProvinceDetail(province: string, page = 1) {
  loadingProvinceDetail.value = true
  provinceDrawerVisible.value = true
  if (selectedProvince.value !== province) {
    provinceLabelFilter.value = 'all'
  }
  selectedProvince.value = province
  provincePage.value = page

  try {
    provinceDetail.value = await mapApi.provinceDetail(province, {
      page: provincePage.value,
      page_size: provincePageSize.value,
      ...(provinceLabelFilter.value !== 'all' ? { label: provinceLabelFilter.value } : {}),
    })
    provincePage.value = provinceDetail.value.page
  } catch (e: any) {
    provinceDrawerVisible.value = false
    ElMessage.error(e?.response?.data?.detail || '省份详情加载失败')
  } finally {
    loadingProvinceDetail.value = false
  }
}

function onProvincePageChange(page: number) {
  if (!selectedProvince.value) return
  void openProvinceDetail(selectedProvince.value, page)
}

function onProvincePageSizeChange(size: number) {
  provincePageSize.value = size
  if (!selectedProvince.value) return
  void openProvinceDetail(selectedProvince.value, 1)
}

function onProvinceLabelFilterChange() {
  if (!selectedProvince.value) return
  void openProvinceDetail(selectedProvince.value, 1)
}

function openNewsDetail(newsId: string) {
  if (!newsId) return
  void router.push(appRoute.newsDetail(newsId))
}

function resizeMap() {
  chartInstance.value?.resize()
}

onMounted(async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    await ensureMapRegistered()
    await loadChinaData()
    await nextTick()
    renderMap()
  } catch {
  } finally {
    loading.value = false
  }

  window.addEventListener('resize', resizeMap)
})

watch(metric, () => {
  renderMap()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeMap)
  chartInstance.value?.dispose()
  chartInstance.value = null
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
  font-size: clamp(22px, 3vw, 32px);
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

.map-panel {
  min-height: 720px;
}

.map-canvas-shell {
  position: relative;
  min-height: 560px;
  border: 1px solid rgba(148, 184, 219, 0.18);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(14, 28, 44, 0.8), rgba(7, 15, 28, 0.98));
  box-shadow: inset 0 1px 0 rgba(86, 194, 255, 0.05);
}

.map-canvas {
  width: 100%;
  height: 560px;
}

.panel-empty {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-empty--compact {
  min-height: 160px;
}

.panel-alert {
  margin-top: 4px;
}

.drawer-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.drawer-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  margin-top: 16px;
}

.drawer-filter {
  width: 160px;
}

.drawer-pagination {
  display: flex;
  justify-content: flex-end;
}

.data-table {
  --el-table-border-color: rgba(131, 168, 201, 0.18);
  --el-table-header-bg-color: rgba(86, 194, 255, 0.08);
  --el-table-tr-bg-color: transparent;
  --el-table-bg-color: transparent;
  --el-table-text-color: var(--tech-text-primary);
}

.data-table :deep(.el-table__header-wrapper th.el-table__cell) {
  background: rgba(86, 194, 255, 0.08) !important;
  color: var(--tech-text-secondary);
  border-bottom: 1px solid rgba(131, 168, 201, 0.2);
}

.data-table :deep(.el-table__row td.el-table__cell) {
  background: rgba(8, 26, 48, 0.52) !important;
  color: var(--tech-text-primary);
  border-bottom: 1px solid rgba(131, 168, 201, 0.14);
}

.data-table :deep(.el-table__row--striped td.el-table__cell) {
  background: rgba(76, 201, 255, 0.06) !important;
}

.data-table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background: rgba(76, 201, 255, 0.14) !important;
}

.data-table :deep(.el-table__inner-wrapper::before) {
  background-color: rgba(131, 168, 201, 0.18);
}

@media (max-width: 640px) {
  .content-section,
  .drawer-section {
    padding: 20px;
  }

  .map-canvas-shell,
  .map-canvas {
    min-height: 420px;
    height: 420px;
  }
}
</style>

