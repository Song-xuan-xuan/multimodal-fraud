<template>
  <div class="report-view page-shell">
    <div class="report-view__submit-card">
      <el-card class="report-view__card report-view__card--narrow">
        <h2>线索举报</h2>
        <el-form label-position="top">
          <el-form-item label="举报类型">
            <el-select v-model="form.type" placeholder="选择举报类型" class="report-view__full-width">
              <el-option label="风险事件" value="fake_news" />
              <el-option label="不良内容" value="bad_content" />
              <el-option label="平台问题" value="platform_issue" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="相关链接">
            <el-input v-model="form.url" placeholder="可选，填写相关链接" />
          </el-form-item>
          <el-form-item label="详细描述">
            <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请描述举报内容" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submit" :loading="loading">提交举报</el-button>
            <el-button @click="reset">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card v-if="submitted" class="report-view__card report-view__card--narrow">
        <el-result icon="success" title="举报提交成功" sub-title="感谢你的反馈，我们会尽快处理。" />
      </el-card>
    </div>

    <el-card class="report-view__card">
      <div class="report-view__header">
        <h3>我的举报记录</h3>
        <span class="report-view__count">共 {{ reports.total }} 条</span>
      </div>

      <el-form inline class="report-view__filters">
        <el-form-item label="类型">
          <el-select v-model="filters.type" placeholder="全部" clearable class="report-view__select report-view__select--type" @change="onFilterChange">
            <el-option label="风险事件" value="fake_news" />
            <el-option label="不良内容" value="bad_content" />
            <el-option label="平台问题" value="platform_issue" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable class="report-view__select report-view__select--status" @change="onFilterChange">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="done" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="标题/描述关键词" class="report-view__keyword" clearable @keyup.enter="onFilterChange" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onFilterChange">筛选</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="reports.items" v-loading="loadingReports" stripe>
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="url" label="链接" min-width="220" />
        <el-table-column prop="description" label="描述" min-width="260" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column prop="created_at" label="提交时间" width="180" />
      </el-table>

      <div class="report-view__pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="reports.total"
          :current-page="reports.page"
          :page-size="reports.pageSize"
          :page-sizes="[10, 20, 50]"
          @current-change="onPageChange"
          @size-change="onPageSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { reportApi, type ReportItem } from '@/api/report'
import { asPositiveInt, asString, replaceQueryKeepingOthers } from '@/composables/useQueryState'

const route = useRoute()
const router = useRouter()

const form = reactive({ type: '', url: '', description: '' })
const loading = ref(false)
const loadingReports = ref(false)
const submitted = ref(false)
const reports = reactive<{ items: ReportItem[]; total: number; page: number; pageSize: number }>({
  items: [],
  total: 0,
  page: 1,
  pageSize: 20,
})
const filters = reactive<{ type?: string; status?: string; keyword?: string }>({
  type: undefined,
  status: undefined,
  keyword: undefined,
})
const routeSync = reactive({
  isInternalQueryUpdate: false,
  lastLoadedQueryKey: '',
})

function applyQueryState() {
  filters.type = asString(route.query.r_type) ?? asString(route.query.type)
  filters.status = asString(route.query.r_status) ?? asString(route.query.status)
  filters.keyword = asString(route.query.r_keyword) ?? asString(route.query.keyword)
  reports.pageSize = asPositiveInt(route.query.r_page_size ?? route.query.page_size, 20, 1, 200)
  reports.page = asPositiveInt(route.query.r_page ?? route.query.page, 1)
}

function getReportQueryKey() {
  return JSON.stringify({
    r_type: filters.type || '',
    r_status: filters.status || '',
    r_keyword: filters.keyword?.trim() || '',
    r_page: reports.page,
    r_page_size: reports.pageSize,
  })
}

async function syncQueryState() {
  routeSync.isInternalQueryUpdate = true
  try {
    await replaceQueryKeepingOthers(
      router,
      route.query,
      ['type', 'status', 'keyword', 'page', 'page_size', 'r_type', 'r_status', 'r_keyword', 'r_page', 'r_page_size'],
      {
        ...(filters.type ? { r_type: filters.type } : {}),
        ...(filters.status ? { r_status: filters.status } : {}),
        ...(filters.keyword?.trim() ? { r_keyword: filters.keyword.trim() } : {}),
        r_page: String(reports.page),
        r_page_size: String(reports.pageSize),
      },
    )
  } finally {
    routeSync.isInternalQueryUpdate = false
  }
}

async function migrateLegacyQueryIfNeeded() {
  if (
    route.query.type === undefined &&
    route.query.status === undefined &&
    route.query.keyword === undefined &&
    route.query.page === undefined &&
    route.query.page_size === undefined
  ) {
    return
  }
  await syncQueryState()
}

async function loadMyReports(syncQuery = true) {
  loadingReports.value = true
  try {
    if (syncQuery) await syncQueryState()
    const data = await reportApi.my({
      page: reports.page,
      page_size: reports.pageSize,
      type: filters.type,
      status: filters.status,
      keyword: filters.keyword,
    })
    reports.items = data.items
    reports.total = data.total
    reports.page = data.page
    reports.pageSize = data.page_size

    const normalizedKey = getReportQueryKey()
    routeSync.lastLoadedQueryKey = normalizedKey
    if (syncQuery) {
      await syncQueryState()
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '加载举报记录失败')
  } finally {
    loadingReports.value = false
  }
}

function onFilterChange() {
  reports.page = 1
  void loadMyReports()
}

function onPageChange(page: number) {
  reports.page = page
  void loadMyReports()
}

function onPageSizeChange(size: number) {
  reports.pageSize = size
  reports.page = 1
  void loadMyReports()
}

async function submit() {
  if (!form.type || !form.description.trim()) return ElMessage.warning('请填写举报类型和描述')
  loading.value = true
  try {
    await reportApi.submit(form)
    submitted.value = true
    ElMessage.success('举报提交成功')
    reports.page = 1
    await loadMyReports()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    loading.value = false
  }
}

function reset() {
  form.type = ''
  form.url = ''
  form.description = ''
  submitted.value = false
}

watch(
  () => [route.query.r_type, route.query.r_status, route.query.r_keyword, route.query.r_page, route.query.r_page_size],
  async () => {
    if (routeSync.isInternalQueryUpdate) return
    applyQueryState()
    const nextKey = getReportQueryKey()
    if (nextKey === routeSync.lastLoadedQueryKey) return
    await loadMyReports(false)
  },
)

onMounted(async () => {
  applyQueryState()
  await migrateLegacyQueryIfNeeded()
  await loadMyReports(false)
})
</script>

<style scoped lang="scss">
.report-view__submit-card {
  display: grid;
  gap: 16px;
}

.report-view__card {
  margin-top: 16px;
}

.report-view__card--narrow {
  max-width: 700px;
}

.report-view__full-width {
  width: 100%;
}

.report-view__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-view__count {
  font-size: 12px;
  color: var(--tech-theme-text-tertiary);
}

.report-view__filters {
  margin-bottom: 12px;
}

.report-view__select--type {
  width: 160px;
}

.report-view__select--status {
  width: 140px;
}

.report-view__keyword {
  width: 220px;
}

.report-view__pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

/* Dark theme table overrides */
.report-view :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: rgba(14, 28, 54, 0.6);
  --el-table-header-bg-color: rgba(76, 201, 255, 0.06);
  --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.10);
  --el-table-border-color: rgba(76, 201, 255, 0.08);
  --el-table-header-text-color: var(--tech-text-secondary, #a0aec0);
  --el-table-text-color: var(--tech-text-regular, #ccc);
  color: var(--tech-text-regular, #ccc);
}

.report-view :deep(.el-table__row--striped td.el-table__cell) {
  background: rgba(76, 201, 255, 0.04) !important;
}

.report-view :deep(.el-table__inner-wrapper::before) {
  background-color: rgba(76, 201, 255, 0.08);
}

/* Dark theme card overrides */
.report-view :deep(.el-card) {
  --el-card-bg-color: rgba(10, 21, 39, 0.96);
  border-color: rgba(76, 201, 255, 0.10);
  color: var(--tech-text-regular, #ccc);
}
</style>


