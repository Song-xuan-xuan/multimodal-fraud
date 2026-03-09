<template>
  <div class="content-wrap" v-loading="loading">
    <el-table v-if="mode === 'table'" :data="items" stripe class="news-table" @row-click="handleSelect">
      <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="table-title-cell">
            <strong>{{ row.title || '无标题' }}</strong>
            <span class="table-summary">{{ row.summary || '暂无摘要' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="标签" width="110">
        <template #default="{ row }">
          <el-tag class="news-tag" :class="resolveTagClass(row)" effect="plain">{{ row.label || '未分类' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="platform" label="平台" width="120" />
      <el-table-column label="风险度" width="120">
        <template #default="{ row }">
          <span class="credibility-text" :class="resolveCredibilityClass(row.credibility?.score)">{{ formatPercent(row.credibility?.score) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="publish_time" label="发布时间" width="180" />
      <el-table-column label="操作" width="110" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click.stop="handleSelect(row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div v-else class="card-grid">
      <article v-for="item in items" :key="item.news_id" class="news-card" @click="handleSelect(item)">
        <div class="card-top">
          <el-tag class="news-tag" :class="resolveTagClass(item)" effect="plain">{{ item.label || '未分类' }}</el-tag>
          <span class="card-platform">{{ item.platform || '未知平台' }}</span>
        </div>

        <h3 class="card-title">{{ item.title || '无标题' }}</h3>
        <p class="card-summary">{{ item.summary || '暂无摘要' }}</p>

        <div class="card-meta">
          <span>发布时间：{{ item.publish_time || '-' }}</span>
          <span class="credibility-text" :class="resolveCredibilityClass(item.credibility?.score)">风险度：{{ formatPercent(item.credibility?.score) }}</span>
          <span>地区：{{ item.location || '-' }}</span>
        </div>

        <div class="card-footer">
          <span class="card-link">进入详情</span>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NewsItem } from '@/api/news'

const props = defineProps<{
  items: NewsItem[]
  mode: 'card' | 'table'
  loading?: boolean
}>()

const emit = defineEmits<{
  select: [item: NewsItem]
}>()

function formatPercent(value?: number) {
  return `${Math.round((value || 0) * 100)}%`
}

function resolveTagClass(item: NewsItem) {
  return item.iscredit ? 'tag-credit' : 'tag-risk'
}

function resolveCredibilityClass(score?: number) {
  const normalized = Number(score || 0)
  if (normalized >= 0.75) return 'credibility-high'
  if (normalized >= 0.45) return 'credibility-mid'
  return 'credibility-low'
}

function handleSelect(item: NewsItem) {
  emit('select', item)
}
</script>

<style scoped>
.content-wrap {
  min-height: 220px;
}

.news-table {
  width: 100%;
}

.news-table :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-border-color: var(--tech-divider-color);
  --el-table-header-bg-color: rgba(76, 201, 255, 0.06);
  --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.08);
  --el-table-text-color: var(--tech-text-regular);
  --el-table-header-text-color: var(--tech-text-secondary);
}

.news-table :deep(.el-table th.el-table__cell) {
  background: rgba(76, 201, 255, 0.06);
}

.table-title-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.table-title-cell strong {
  color: var(--tech-text-primary);
}

.table-summary {
  color: var(--tech-text-secondary);
  font-size: 12px;
  line-height: 1.5;
}

.news-tag {
  border-color: transparent;
  font-weight: 600;
}

.news-tag.tag-credit {
  background: rgba(34, 197, 94, 0.14);
  color: var(--tech-color-success-text);
}

.news-tag.tag-risk {
  background: rgba(248, 113, 113, 0.14);
  color: var(--tech-color-danger-text);
}

.credibility-text {
  font-weight: 600;
}

.credibility-text.credibility-high {
  color: var(--tech-color-success-text);
}

.credibility-text.credibility-mid {
  color: var(--tech-color-warning-text);
}

.credibility-text.credibility-low {
  color: var(--tech-color-danger-text);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.news-card {
  padding: 20px;
  border: 1px solid var(--tech-border-color);
  border-radius: var(--tech-radius-md);
  background: linear-gradient(180deg, rgba(14, 28, 48, 0.92) 0%, rgba(8, 18, 34, 0.96) 100%);
  box-shadow: var(--tech-shadow-sm);
  cursor: pointer;
  transition:
    transform var(--tech-duration-fast) var(--tech-ease-out),
    box-shadow var(--tech-duration-fast) var(--tech-ease-out),
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    background var(--tech-duration-fast) var(--tech-ease-out);
}

.news-card:hover {
  transform: translateY(-4px);
  border-color: var(--tech-border-strong);
  background: linear-gradient(180deg, rgba(16, 34, 58, 0.96) 0%, rgba(8, 18, 34, 0.98) 100%);
  box-shadow: var(--tech-shadow-md);
}

.card-top,
.card-meta,
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-platform,
.card-meta {
  color: var(--tech-text-secondary);
  font-size: 12px;
}

.card-title {
  margin: 16px 0 10px;
  color: var(--tech-text-primary);
  font-size: 18px;
  line-height: 1.5;
}

.card-summary {
  min-height: 66px;
  margin: 0;
  color: var(--tech-text-regular);
  line-height: 1.7;
}

.card-meta {
  margin-top: 18px;
  flex-wrap: wrap;
}

.card-link {
  margin-top: 16px;
  color: var(--tech-color-primary-strong);
  font-weight: 600;
}
</style>

