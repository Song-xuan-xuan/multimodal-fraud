<template>
  <SectionStateWrapper :section-id="sectionId" :title="title" :has-data="rows.length > 0" :empty-text="emptyText">
    <el-table :data="rows" size="small" stripe class="geo-table">
      <el-table-column :prop="nameKey" :label="nameLabel" min-width="140" />
      <el-table-column prop="count" label="数量" width="100" />
      <el-table-column v-if="mode === 'platforms'" label="占比" width="120">
        <template #default="{ row }">
          <span class="ratio-text">{{ typeof row.ratio === 'number' ? `${(row.ratio * 100).toFixed(1)}%` : '-' }}</span>
        </template>
      </el-table-column>
    </el-table>
  </SectionStateWrapper>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NewsDetailPropagationVM } from '@/types/newsDetail'
import SectionStateWrapper from './SectionStateWrapper.vue'

const props = defineProps<{
  propagation: NewsDetailPropagationVM | null
  mode: 'platforms' | 'regions'
}>()

const sectionId = computed(() => (props.mode === 'platforms' ? 'propagation-platforms' : 'propagation-regions'))
const title = computed(() => (props.mode === 'platforms' ? '传播平台分布' : '传播地域分布'))
const nameKey = computed(() => (props.mode === 'platforms' ? 'platform' : 'region'))
const nameLabel = computed(() => (props.mode === 'platforms' ? '平台' : '地区'))

const rows = computed(() => {
  if (!props.propagation) return []
  return props.mode === 'platforms' ? props.propagation.platformDistribution : props.propagation.regionDistribution
})

const emptyText = computed(() => props.propagation?.emptyReason || '暂无传播分布数据')
</script>

<style scoped>
.geo-table :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-border-color: var(--tech-divider-color);
  --el-table-header-bg-color: rgba(76, 201, 255, 0.06);
  --el-table-row-hover-bg-color: rgba(76, 201, 255, 0.08);
  --el-table-text-color: var(--tech-text-regular);
  --el-table-header-text-color: var(--tech-text-secondary);
}

.ratio-text {
  color: var(--tech-color-primary-strong);
  font-weight: 600;
}
</style>
