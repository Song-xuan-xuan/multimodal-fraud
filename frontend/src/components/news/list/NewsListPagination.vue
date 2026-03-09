<template>
  <div class="pagination-wrap">
    <div class="pagination-meta">每页 {{ perPage }} 条，共 {{ total }} 条</div>
    <el-pagination
      :current-page="page"
      :page-size="perPage"
      :total="total"
      layout="prev, pager, next"
      :pager-count="7"
      background
      @current-change="$emit('change', $event)"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  page: number
  perPage: number
  total: number
}>()

defineEmits<{
  change: [page: number]
}>()
</script>

<style scoped>
.pagination-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 4px 0;
}

.pagination-meta {
  font-size: 13px;
  color: var(--tech-text-secondary);
}

@media (max-width: 768px) {
  .pagination-wrap {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
