<template>
  <el-card shadow="never" class="summary-card">
    <div class="summary-layout">
      <div>
        <div class="summary-eyebrow">结果概览</div>
        <h2 class="summary-title">
          共找到 {{ summary.total }} 条案例
          <span class="summary-subtitle">当前显示 {{ summary.rangeStart }}-{{ summary.rangeEnd }}</span>
        </h2>
      </div>

      <div class="summary-metrics">
        <div class="metric-item">
          <span class="metric-label">当前页</span>
          <strong>{{ summary.currentPage }}/{{ summary.totalPages || 1 }}</strong>
        </div>
        <div class="metric-item">
          <span class="metric-label">已启用筛选</span>
          <strong>{{ summary.activeFilterCount }}</strong>
        </div>
      </div>
    </div>

    <div v-if="activeTags.length" class="tag-list">
      <el-tag v-for="tag in activeTags" :key="tag" size="small" effect="plain">{{ tag }}</el-tag>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NewsListFilters, NewsListSummary } from '@/types/newsList'

const props = defineProps<{
  summary: NewsListSummary
  filters: NewsListFilters
}>()

const activeTags = computed(() => {
  const tags: string[] = []
  if (props.filters.keyword) tags.push(`关键词：${props.filters.keyword}`)
  if (props.filters.platform) tags.push(`平台：${props.filters.platform}`)
  if (props.filters.label) tags.push(`标签：${props.filters.label}`)
  if (props.filters.minCredibility) tags.push(`风险度 ≥ ${props.filters.minCredibility}`)
  if (props.filters.maxCredibility) tags.push(`风险度 ≤ ${props.filters.maxCredibility}`)
  if (props.filters.propagationPlatform) tags.push(`传播平台：${props.filters.propagationPlatform}`)
  if (props.filters.startDate) tags.push(`开始：${props.filters.startDate}`)
  if (props.filters.endDate) tags.push(`结束：${props.filters.endDate}`)
  return tags
})
</script>

<style scoped>
.summary-card {
  border: 1px solid var(--tech-border-color);
}

.summary-layout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.summary-eyebrow {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.summary-title {
  margin: 6px 0 0;
  font-size: 24px;
  line-height: 1.3;
  color: var(--tech-text-primary);
}

.summary-subtitle {
  margin-left: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--tech-text-secondary);
}

.summary-metrics {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.metric-item {
  min-width: 120px;
  padding: 12px 14px;
  border: 1px solid var(--tech-border-color);
  border-radius: var(--tech-radius-sm);
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
}

.tag-list {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 768px) {
  .summary-layout {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-title {
    font-size: 20px;
  }
}
</style>

