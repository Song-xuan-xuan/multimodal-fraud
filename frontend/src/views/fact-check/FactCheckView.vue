<template>
  <div class="fact-check-view page-shell">
    <h2>诈骗话术与承诺核验</h2>
    <el-form label-position="top" class="fact-check-view__form">
      <el-form-item label="需要核验的话术或承诺">
        <el-input v-model="text" type="textarea" :rows="5" placeholder="输入对方的话术、投资承诺、客服说明或可疑声明..." />
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="useAdvanced">使用深度风险检索</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="check" :loading="loading">开始核验</el-button>
      </el-form-item>
    </el-form>

    <el-card v-if="result" class="fact-check-view__card">
      <template #header>
        <div class="fact-check-view__card-header">
          <span>核验结果</span>
          <el-button type="success" size="small" @click="saveCurrentResult" :loading="saving">保存结果</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="结论">
          <el-tag :type="result.verdict === '可信' ? 'success' : result.verdict === '不可信' ? 'danger' : 'warning'">
            {{ result.verdict }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="置信度">
          <el-progress :percentage="Math.round((result.confidence || 0) * 100)" />
        </el-descriptions-item>
      </el-descriptions>
      <p v-if="result.explanation" class="fact-check-view__explanation">{{ result.explanation }}</p>

      <el-divider>参考依据</el-divider>
      <el-table :data="result.sources || []" size="small">
        <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
        <el-table-column prop="relevance" label="相关度" width="100">
          <template #default="{ row }">{{ Math.round((row.relevance || 0) * 100) }}%</template>
        </el-table-column>
        <el-table-column label="链接" width="100">
          <template #default="{ row }">
            <el-link v-if="row.url" :href="row.url" target="_blank" type="primary">查看</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="fact-check-view__card">
      <template #header>
        <div class="fact-check-view__card-header">
          <span>历史核验记录</span>
          <el-button size="small" @click="loadHistory" :loading="loadingHistory">刷新</el-button>
        </div>
      </template>

      <el-form inline class="fact-check-view__filters">
        <el-form-item label="结论">
          <el-select v-model="historyFilters.verdict" placeholder="全部状态" clearable class="fact-check-view__select fact-check-view__select--verdict" @change="onHistoryFilterChange">
            <el-option label="可信" value="可信" />
            <el-option label="不可信" value="不可信" />
            <el-option label="存疑" value="存疑" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="historyFilters.keyword"
            placeholder="按话术内容搜索"
            clearable
            class="fact-check-view__keyword"
            @keyup.enter="onHistoryFilterChange"
            @clear="onHistoryFilterChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button @click="onHistoryFilterChange">筛选</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="history.items" v-loading="loadingHistory" stripe>
        <el-table-column prop="id" label="记录ID" width="170" />
        <el-table-column prop="query" label="内容" min-width="280" show-overflow-tooltip />
        <el-table-column prop="verdict" label="结论" width="110" />
        <el-table-column prop="confidence" label="置信度" width="100">
          <template #default="{ row }">{{ Math.round((row.confidence || 0) * 100) }}%</template>
        </el-table-column>
        <el-table-column prop="checked_at" label="时间" width="210" />
        <el-table-column label="操作" width="90">
          <template #default="{ row }">
            <el-button text type="danger" @click="deleteHistory(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="fact-check-view__pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="history.total"
          :current-page="history.page"
          :page-size="history.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="onHistoryPageChange"
          @size-change="onHistoryPageSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { factCheckApi, type FactCheckHistoryItem, type FactCheckResult } from '@/api/fact-check'
import { ElMessage, ElMessageBox } from 'element-plus'
import { asPositiveInt, asString, replaceQueryKeepingOthers } from '@/composables/useQueryState'

const route = useRoute()
const router = useRouter()

const text = ref('')
const useAdvanced = ref(false)
const result = ref<FactCheckResult | null>(null)
const loading = ref(false)
const saving = ref(false)
const loadingHistory = ref(false)

const history = reactive<{ items: FactCheckHistoryItem[]; total: number; page: number; pageSize: number }>({
  items: [],
  total: 0,
  page: 1,
  pageSize: 20,
})
const historyFilters = reactive<{ verdict?: string; keyword?: string }>({
  verdict: undefined,
  keyword: undefined,
})
const routeSync = reactive({
  isInternalQueryUpdate: false,
  lastLoadedQueryKey: '',
})

function applyQueryState() {
  historyFilters.verdict = asString(route.query.fc_verdict) ?? asString(route.query.verdict)
  historyFilters.keyword = asString(route.query.fc_keyword) ?? asString(route.query.keyword)
  history.pageSize = asPositiveInt(route.query.fc_page_size ?? route.query.page_size, 20, 1, 200)
  history.page = asPositiveInt(route.query.fc_page ?? route.query.page, 1)
}

function getHistoryQueryKey() {
  return JSON.stringify({
    fc_verdict: historyFilters.verdict || '',
    fc_keyword: historyFilters.keyword?.trim() || '',
    fc_page: history.page,
    fc_page_size: history.pageSize,
  })
}

async function syncQueryState() {
  routeSync.isInternalQueryUpdate = true
  try {
    await replaceQueryKeepingOthers(
      router,
      route.query,
      ['verdict', 'keyword', 'page', 'page_size', 'fc_verdict', 'fc_keyword', 'fc_page', 'fc_page_size'],
      {
        ...(historyFilters.verdict ? { fc_verdict: historyFilters.verdict } : {}),
        ...(historyFilters.keyword?.trim() ? { fc_keyword: historyFilters.keyword.trim() } : {}),
        fc_page: String(history.page),
        fc_page_size: String(history.pageSize),
      },
    )
  } finally {
    routeSync.isInternalQueryUpdate = false
  }
}

async function migrateLegacyQueryIfNeeded() {
  if (
    route.query.verdict === undefined &&
    route.query.keyword === undefined &&
    route.query.page === undefined &&
    route.query.page_size === undefined
  ) {
    return
  }
  await syncQueryState()
}

async function check() {
  if (!text.value.trim()) return ElMessage.warning('请输入内容')
  loading.value = true
  try {
    result.value = await factCheckApi.check(text.value, useAdvanced.value)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '核查失败')
  } finally {
    loading.value = false
  }
}

async function saveCurrentResult() {
  if (!result.value) return
  saving.value = true
  try {
    await factCheckApi.save({
      query: result.value.query || text.value,
      verdict: result.value.verdict,
      confidence: result.value.confidence,
      explanation: result.value.explanation,
      save_type: 'all',
    })
    ElMessage.success('已保存到历史核验记录')
    history.page = 1
    await loadHistory()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function loadHistory(syncQuery = true) {
  loadingHistory.value = true
  try {
    if (syncQuery) await syncQueryState()
    const data = await factCheckApi.history({
      page: history.page,
      page_size: history.pageSize,
      verdict: historyFilters.verdict,
      keyword: historyFilters.keyword,
    })
    history.items = data.items
    history.total = data.total
    history.page = data.page
    history.pageSize = data.page_size

    const normalizedKey = getHistoryQueryKey()
    routeSync.lastLoadedQueryKey = normalizedKey
    if (syncQuery) {
      await syncQueryState()
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '历史核验记录加载失败')
  } finally {
    loadingHistory.value = false
  }
}

function onHistoryFilterChange() {
  history.page = 1
  void loadHistory()
}

function onHistoryPageChange(page: number) {
  history.page = page
  void loadHistory()
}

function onHistoryPageSizeChange(size: number) {
  history.pageSize = size
  history.page = 1
  void loadHistory()
}

async function deleteHistory(id: string) {
  try {
    await ElMessageBox.confirm('确定删除这条历史核验记录吗？', '提示', { type: 'warning' })
    await factCheckApi.deleteHistory(id)
    ElMessage.success('删除成功')
    if (history.items.length === 1 && history.page > 1) {
      history.page -= 1
    }
    await loadHistory()
  } catch {
    // user cancelled or request failed (already messaged by interceptor/catch)
  }
}

watch(
  () => [route.query.fc_verdict, route.query.fc_keyword, route.query.fc_page, route.query.fc_page_size],
  async () => {
    if (routeSync.isInternalQueryUpdate) return
    applyQueryState()
    const nextKey = getHistoryQueryKey()
    if (nextKey === routeSync.lastLoadedQueryKey) return
    await loadHistory(false)
  },
)

onMounted(async () => {
  applyQueryState()
  await migrateLegacyQueryIfNeeded()
  await loadHistory(false)
})
</script>

<style scoped lang="scss">
.fact-check-view__form {
  margin-top: 16px;
  max-width: 760px;
}

.fact-check-view__card {
  margin-top: 16px;
}

.fact-check-view__card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fact-check-view__explanation {
  margin-top: 12px;
  color: var(--tech-theme-text-regular);
}

.fact-check-view__filters {
  margin-bottom: 12px;
}

.fact-check-view__select--verdict {
  width: 140px;
}

.fact-check-view__keyword {
  width: 220px;
}

.fact-check-view__pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>


