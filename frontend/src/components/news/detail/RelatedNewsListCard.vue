<template>
  <SectionStateWrapper
    section-id="related-news"
    title="相关新闻"
    :has-data="items.length > 0"
    :empty-text="emptyText || '暂无相关新闻'"
  >
    <el-table :data="items" stripe>
      <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
      <el-table-column prop="platform" label="平台" width="120" />
      <el-table-column prop="publish_time" label="发布时间" width="180" />
      <el-table-column label="相似度" width="100">
        <template #default="{ row }">{{ `${(row.similarity * 100).toFixed(1)}%` }}</template>
      </el-table-column>
      <el-table-column label="来源" width="90">
        <template #default="{ row }">
          <a :href="row.url" target="_blank" rel="noopener noreferrer">查看</a>
        </template>
      </el-table-column>
    </el-table>
  </SectionStateWrapper>
</template>

<script setup lang="ts">
import type { RelatedNewsItem } from '@/api/news'
import SectionStateWrapper from './SectionStateWrapper.vue'

defineProps<{
  items: RelatedNewsItem[]
  emptyText?: string
}>()
</script>

<style scoped>
:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: rgba(14, 28, 54, 0.6);
  --el-table-border-color: rgba(76, 201, 255, 0.08);
  --el-table-header-bg-color: rgba(76, 201, 255, 0.06);
  --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.10);
  --el-table-text-color: var(--tech-text-regular, #ccc);
  --el-table-header-text-color: var(--tech-text-secondary, #a0aec0);
}

:deep(.el-table__row--striped td.el-table__cell) {
  background: rgba(76, 201, 255, 0.04) !important;
}
</style>
