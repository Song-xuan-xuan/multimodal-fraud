<template>
  <div class="workbench-page crowd-board-view">
    <PageHero
      tone="workbench"
      eyebrow="运营工作台"
      title="众筹看板"
      description="统一呈现众包提交、审核状态与核验进度，作为运营视角下的工作台页面。"
    >
      <article class="hero-metric tech-panel">
        <span>提交总数</span>
        <strong>{{ stats.total }}</strong>
        <small>累计线索</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>待审核</span>
        <strong>{{ stats.pending }}</strong>
        <small>需要人工处理</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>已通过</span>
        <strong>{{ stats.approved }}</strong>
        <small>已纳入证据池</small>
      </article>
      <article class="hero-metric tech-panel">
        <span>已驳回</span>
        <strong>{{ stats.rejected }}</strong>
        <small>已完成筛除</small>
      </article>
      <template #actions>
        <el-button @click="refreshAll" :loading="loadingBoard || loadingProgress">刷新</el-button>
      </template>
    </PageHero>

    <section class="content-section tech-panel">
      <SectionHeader eyebrow="筛选条件" title="看板筛选" description="统一工作台的工具区视觉，聚合状态、关键词与进度筛选操作。" />
      <el-form inline class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部状态" class="filter-select" @change="loadBoard(1)">
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="filters.keyword"
            clearable
            placeholder="按新闻标题/ID/平台"
            class="filter-keyword"
            @keyup.enter="loadBoard(1)"
            @clear="loadBoard(1)"
          />
        </el-form-item>
        <el-form-item label="进度区间">
          <el-slider
            v-model="progressRange"
            range
            :min="0"
            :max="100"
            :step="5"
            class="filter-slider"
            @change="loadProgress"
          />
        </el-form-item>
      </el-form>
    </section>

    <section class="content-section tech-panel">
      <SectionHeader eyebrow="提交列表" title="我的证据提交" description="统一表格容器边界与分页区节奏，聚焦当前用户提交记录。" />
      <div class="table-shell" v-loading="loadingBoard">
        <el-table v-if="board.items.length" :data="board.items" stripe class="data-table">
          <el-table-column prop="id" label="提交ID" width="96" />
          <el-table-column prop="news_id" label="新闻ID" width="180" />
          <el-table-column prop="title" label="新闻标题" min-width="260" show-overflow-tooltip />
          <el-table-column prop="platform" label="平台" width="110" />
          <el-table-column prop="label" label="新闻标签" width="100" />
          <el-table-column prop="submitted_at" label="提交时间" width="180" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else-if="!loadingBoard" description="暂无证据提交记录" class="panel-empty" />
      </div>
      <div class="table-pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="board.total"
          :current-page="boardPage"
          :page-size="boardPageSize"
          :page-sizes="[10, 20, 50]"
          @current-change="loadBoard"
          @size-change="onBoardPageSizeChange"
        />
      </div>
    </section>

    <section class="content-section tech-panel">
      <SectionHeader eyebrow="核验进度" title="新闻核验进度" description="用统一图表/表格容器展示众包核验流程，避免页面像临时业务拼接。" />
      <div class="table-shell" v-loading="loadingProgress">
        <el-table v-if="progress.items.length" :data="progress.items" stripe class="data-table">
          <el-table-column prop="news_id" label="新闻ID" width="180" />
          <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
          <el-table-column prop="platform" label="平台" width="100" />
          <el-table-column prop="label" label="标签" width="100" />
          <el-table-column label="核验进度" min-width="240">
            <template #default="{ row }">
              <el-progress :percentage="row.verification_progress" :stroke-width="14" />
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else-if="!loadingProgress" description="暂无核验进度数据" class="panel-empty" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { evidenceApi } from '@/api/evidence'
import type { CrowdBoardProgressResponse, EvidenceBoardListResponse, EvidenceBoardStats } from '@/types/insight'
import SectionHeader from '@/components/dashboard/SectionHeader.vue'
import PageHero from '@/components/page/PageHero.vue'

const loadingBoard = ref(false)
const loadingProgress = ref(false)

const boardPage = ref(1)
const boardPageSize = ref(10)
const progressRange = ref<[number, number]>([0, 100])

const filters = reactive<{ status?: 'pending' | 'approved' | 'rejected'; keyword?: string }>({
  status: undefined,
  keyword: '',
})

const stats = reactive<EvidenceBoardStats>({ total: 0, pending: 0, approved: 0, rejected: 0 })

const board = reactive<EvidenceBoardListResponse>({
  items: [],
  total: 0,
})

const progress = reactive<CrowdBoardProgressResponse>({
  items: [],
  total: 0,
  page: 1,
  page_size: 20,
})

function statusLabel(status: string) {
  if (status === 'pending') return '待审核'
  if (status === 'approved') return '已通过'
  if (status === 'rejected') return '已驳回'
  return status
}

function statusTagType(status: string): 'warning' | 'success' | 'danger' | 'info' {
  if (status === 'pending') return 'warning'
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'danger'
  return 'info'
}

async function loadStats() {
  try {
    const data = await evidenceApi.getBoardStats()
    stats.total = data.total
    stats.pending = data.pending
    stats.approved = data.approved
    stats.rejected = data.rejected
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '统计数据加载失败')
  }
}

async function loadBoard(page = boardPage.value) {
  boardPage.value = page
  loadingBoard.value = true
  try {
    const data = await evidenceApi.listBoard({
      page: boardPage.value,
      pageSize: boardPageSize.value,
      status: filters.status,
      keyword: filters.keyword,
    })
    board.items = data.items
    board.total = data.total
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '看板数据加载失败')
  } finally {
    loadingBoard.value = false
  }
}

function onBoardPageSizeChange(size: number) {
  boardPageSize.value = size
  boardPage.value = 1
  void loadBoard(1)
}

async function loadProgress() {
  loadingProgress.value = true
  try {
    const data = await evidenceApi.listVerificationProgress({
      page: 1,
      pageSize: 20,
      keyword: filters.keyword,
      minProgress: progressRange.value[0],
      maxProgress: progressRange.value[1],
    })
    progress.items = data.items
    progress.total = data.total
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '进度数据加载失败')
  } finally {
    loadingProgress.value = false
  }
}

async function refreshAll() {
  await Promise.all([loadStats(), loadBoard(boardPage.value), loadProgress()])
}

onMounted(async () => {
  await refreshAll()
})
</script>

<style scoped lang="scss">
.workbench-page {
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

.content-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.filter-select {
  width: 140px;
}

.filter-keyword {
  width: 260px;
}

.filter-slider {
  width: 240px;
}

.table-shell {
  min-height: 180px;
}

.table-pagination {
  display: flex;
  justify-content: flex-end;
}

.panel-empty {
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.data-table {
  --el-table-border-color: rgba(131, 168, 201, 0.18);
  --el-table-header-bg-color: rgba(76, 201, 255, 0.08);
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

  .filter-keyword,
  .filter-slider {
    width: 100%;
  }
}
</style>
