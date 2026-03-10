<template>
  <TechCard class="province-panel" v-loading="loading" :hoverable="false">
    <template v-if="province">
      <div class="header-row">
        <div>
          <p class="panel-kicker">PROVINCE DETAIL</p>
          <h3 class="panel-title">{{ province }}传播详情</h3>
        </div>
        <el-select v-model="labelFilter" size="small" style="width: 140px" @change="loadData(1)">
          <el-option label="全部" value="all" />
          <el-option label="仅谣言" value="fake" />
          <el-option label="仅真实" value="real" />
        </el-select>
      </div>

      <el-empty v-if="!detail && !loading" description="暂无地区信息" />

      <template v-else-if="detail">
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">总数</span>
            <strong class="stat-value">{{ detail.stats.total }}</strong>
          </div>
          <div class="stat-card">
            <span class="stat-label">谣言</span>
            <strong class="stat-value">{{ detail.stats.fake_count }}</strong>
          </div>
          <div class="stat-card">
            <span class="stat-label">真实</span>
            <strong class="stat-value">{{ detail.stats.real_count }}</strong>
          </div>
        </div>

        <el-table :data="detail.items || []" size="small" stripe class="detail-table">
          <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
          <el-table-column prop="label" label="标签" width="110" />
          <el-table-column prop="platform" label="平台" width="110" />
        </el-table>

        <el-empty v-if="detail.items.length === 0" description="该省暂无详情新闻" />

        <div class="pager">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="detail.total"
            :current-page="page"
            :page-size="pageSize"
            @current-change="loadData"
          />
        </div>
      </template>
    </template>

    <el-empty v-else description="暂无地区信息" />
  </TechCard>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { mapApi, type ProvinceDetailResponse } from '@/api/map'
import TechCard from '@/components/page/TechCard.vue'

const props = defineProps<{
  province: string
}>()

const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const labelFilter = ref<'all' | 'fake' | 'real'>('all')
const detail = ref<ProvinceDetailResponse | null>(null)

async function loadData(nextPage = page.value) {
  if (!props.province) {
    detail.value = null
    return
  }

  loading.value = true
  page.value = nextPage
  try {
    detail.value = await mapApi.provinceDetail(props.province, {
      page: page.value,
      page_size: pageSize.value,
      ...(labelFilter.value !== 'all' ? { label: labelFilter.value } : {}),
    })
    page.value = detail.value.page
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '省份详情加载失败')
  } finally {
    loading.value = false
  }
}

watch(
  () => props.province,
  () => {
    page.value = 1
    labelFilter.value = 'all'
    void loadData(1)
  },
  { immediate: true },
)
</script>

<style scoped>
.province-panel {
  width: 100%;
}

.header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.panel-kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--el-color-primary);
}

.panel-title {
  margin: 0;
  font-size: 18px;
  line-height: 1.3;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  padding: 14px;
  border-radius: 16px;
  background: rgba(76, 201, 255, 0.06);
  border: 1px solid rgba(76, 201, 255, 0.14);
}

.stat-label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: var(--tech-text-secondary, #a0aec0);
}

.stat-value {
  font-size: 22px;
  line-height: 1;
  color: var(--tech-text-primary, #e2e8f0);
}

.detail-table {
  margin-top: 12px;
}

.detail-table :deep(.el-table__header-wrapper th) {
  background: rgba(76, 201, 255, 0.06) !important;
  color: var(--tech-text-secondary, #a0aec0);
}

.detail-table :deep(.el-table__body-wrapper) {
  background: transparent;
}

.detail-table :deep(.el-table__row) {
  background: rgba(14, 28, 54, 0.6);
  color: var(--tech-text-regular, #ccc);
}

.detail-table :deep(.el-table__row--striped td.el-table__cell) {
  background: rgba(76, 201, 255, 0.04) !important;
}

.detail-table :deep(tr:hover > td.el-table__cell) {
  background: rgba(76, 201, 255, 0.10) !important;
}

.detail-table :deep(.el-table__inner-wrapper::before) {
  background-color: rgba(76, 201, 255, 0.08);
}

.detail-table :deep(td.el-table__cell),
.detail-table :deep(th.el-table__cell) {
  border-bottom-color: rgba(76, 201, 255, 0.08);
}

.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.pager :deep(.el-pagination button),
.pager :deep(.el-pager li) {
  background: rgba(76, 201, 255, 0.04);
  border-color: rgba(76, 201, 255, 0.12);
  color: var(--tech-text-secondary, #a0aec0);
}

.pager :deep(.el-pager li.is-active) {
  background: rgba(76, 201, 255, 0.14);
  border-color: rgba(76, 201, 255, 0.24);
  color: var(--tech-color-primary-strong, #4cc9ff);
}

@media (max-width: 768px) {
  .header-row {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
