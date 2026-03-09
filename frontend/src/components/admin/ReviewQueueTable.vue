<template>
  <div class="review-queue-table tech-panel">
    <el-empty v-if="!loading && !items.length" description="暂无审核数据" class="review-queue-table__empty" />
    <el-table
      v-else
      :data="items"
      :row-key="(row: AdminReviewItem) => row.id"
      stripe
      border
      v-loading="loading"
      class="review-queue-table__table"
      @selection-change="onSelectionChange"
    >
      <el-table-column v-if="selectable" type="selection" width="48" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="report_id" label="举报ID" width="150" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column prop="description" label="描述" min-width="280" show-overflow-tooltip />
      <el-table-column prop="url" label="链接" width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.url || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="reported_by" label="提交人" width="120" />
      <el-table-column prop="created_at" label="提交时间" width="180" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="review_reason" label="审核说明" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.review_reason || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="reviewed_by" label="审核人" width="120">
        <template #default="{ row }">
          {{ row.reviewed_by || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="reviewed_at" label="审核时间" width="180">
        <template #default="{ row }">
          {{ row.reviewed_at || '-' }}
        </template>
      </el-table-column>
      <el-table-column v-if="showActions" label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-space>
            <el-button size="small" type="success" @click="emitReview(row, 'approved')">通过</el-button>
            <el-button size="small" type="danger" @click="emitReview(row, 'rejected')">驳回</el-button>
            <el-button v-if="row.status === 'approved'" size="small" type="primary" plain @click="emitPromote(row)">加入知识库</el-button>
          </el-space>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import type { AdminReviewActionStatus, AdminReviewItem, AdminReviewStatus } from '@/types/admin'

withDefaults(
  defineProps<{
    items: AdminReviewItem[]
    loading?: boolean
    selectable?: boolean
    showActions?: boolean
  }>(),
  {
    loading: false,
    selectable: false,
    showActions: false,
  },
)

const emit = defineEmits<{
  (e: 'selection-change', rows: AdminReviewItem[]): void
  (e: 'review', row: AdminReviewItem, status: AdminReviewActionStatus): void
  (e: 'promote', row: AdminReviewItem): void
}>()

function onSelectionChange(rows: AdminReviewItem[]) {
  emit('selection-change', rows)
}

function emitReview(row: AdminReviewItem, status: AdminReviewActionStatus) {
  emit('review', row, status)
}

function emitPromote(row: AdminReviewItem) {
  emit('promote', row)
}

function statusTagType(status: AdminReviewStatus) {
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'danger'
  return 'warning'
}

function statusLabel(status: AdminReviewStatus) {
  if (status === 'approved') return '已通过'
  if (status === 'rejected') return '已驳回'
  return '待审核'
}
</script>

<style scoped lang="scss">
.review-queue-table {
  padding: 16px;
  border-radius: 20px;
  overflow: hidden;
}

.review-queue-table__empty {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.review-queue-table__table {
  --el-table-border-color: rgba(131, 168, 201, 0.18);
  --el-table-header-bg-color: rgba(8, 28, 52, 0.96);
  --el-table-tr-bg-color: rgba(5, 22, 43, 0.96);
  --el-table-bg-color: rgba(5, 22, 43, 0.96);
  --el-table-text-color: rgba(230, 241, 255, 0.94);
  --el-table-header-text-color: rgba(236, 246, 255, 0.96);
  --el-table-row-hover-bg-color: rgba(10, 36, 66, 0.98);
  --el-fill-color-lighter: rgba(8, 28, 52, 0.98);
  --el-fill-color-light: rgba(10, 36, 66, 0.98);
}

.review-queue-table__table :deep(.el-table),
.review-queue-table__table :deep(.el-table__inner-wrapper),
.review-queue-table__table :deep(.el-table__body-wrapper),
.review-queue-table__table :deep(.el-table__header-wrapper) {
  background: rgba(5, 22, 43, 0.96);
}

.review-queue-table__table :deep(th.el-table__cell) {
  background: rgba(8, 28, 52, 0.98);
  color: rgba(236, 246, 255, 0.96);
}

.review-queue-table__table :deep(td.el-table__cell) {
  background: rgba(5, 22, 43, 0.96);
  color: rgba(230, 241, 255, 0.94);
}

.review-queue-table__table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background: rgba(10, 36, 66, 0.98) !important;
}

.review-queue-table__table :deep(.el-table__body tr.el-table__row--striped > td.el-table__cell) {
  background: rgba(7, 26, 48, 0.98);
}

.review-queue-table__table :deep(.el-table__fixed-right),
.review-queue-table__table :deep(.el-table__fixed-right::before),
.review-queue-table__table :deep(.el-table-fixed-column--right),
.review-queue-table__table :deep(.el-table__fixed),
.review-queue-table__table :deep(.el-table__fixed-header-wrapper),
.review-queue-table__table :deep(.el-table__fixed-body-wrapper) {
  background: rgba(4, 20, 38, 1) !important;
}

.review-queue-table__table :deep(.el-table__fixed-right-patch) {
  background: rgba(8, 28, 52, 0.98) !important;
  border-bottom-color: rgba(131, 168, 201, 0.18);
}

.review-queue-table__table :deep(.el-table__fixed-right td.el-table__cell),
.review-queue-table__table :deep(.el-table__fixed-right th.el-table__cell),
.review-queue-table__table :deep(.el-table__fixed td.el-table__cell),
.review-queue-table__table :deep(.el-table__fixed th.el-table__cell) {
  background: rgba(4, 20, 38, 1) !important;
}

.review-queue-table__table :deep(.el-table__fixed-right .cell),
.review-queue-table__table :deep(.el-table__fixed .cell) {
  color: rgba(236, 246, 255, 0.96);
}

.review-queue-table__table :deep(.el-table__fixed-right) {
  box-shadow: -12px 0 22px rgba(1, 8, 18, 0.58);
}
</style>

.review-queue-table__table :deep(.el-button--primary.is-plain) {
  color: #eef9ff;
  border-color: rgba(92, 200, 255, 0.32);
  background: rgba(8, 52, 88, 0.92);
}

.review-queue-table__table :deep(.el-button--primary.is-plain:hover),
.review-queue-table__table :deep(.el-button--primary.is-plain:focus-visible) {
  color: #ffffff;
  border-color: rgba(124, 231, 255, 0.4);
  background: rgba(10, 68, 112, 0.98);
}
