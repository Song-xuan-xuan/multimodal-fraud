<template>
  <SectionStateWrapper section-id="credibility" title="可信度分析" :has-data="Boolean(credibility)">
    <template v-if="credibility">
      <div class="score-layout">
        <div class="score-main">
          <el-progress type="circle" :percentage="scorePercent" :stroke-width="10" :width="120">
            <template #default>
              <span class="score-text">{{ credibility.scorePercentText }}</span>
            </template>
          </el-progress>
          <div>
            <p class="info-line">核验进度：{{ credibility.verificationProgress }}%</p>
            <p class="info-line">核验状态：{{ credibility.verified ? '已核验' : '待核验' }}</p>
          </div>
        </div>
      </div>

      <el-table :data="dimensionRows" size="small" style="width: 100%; margin-top: 16px">
        <el-table-column prop="name" label="维度" width="120" />
        <el-table-column label="分值">
          <template #default="{ row }">
            <el-progress :percentage="row.percent" :stroke-width="12" :show-text="false" />
          </template>
        </el-table-column>
        <el-table-column prop="percentText" label="占比" width="90" />
      </el-table>

      <el-alert
        v-if="credibility.dimensions.content1 || credibility.dimensions.content2"
        class="note"
        type="info"
        :closable="false"
        :description="[credibility.dimensions.content1, credibility.dimensions.content2].filter(Boolean).join('；')"
      />
    </template>
  </SectionStateWrapper>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NewsDetailCredibilityVM } from '@/types/newsDetail'
import SectionStateWrapper from './SectionStateWrapper.vue'

const props = defineProps<{
  credibility: NewsDetailCredibilityVM | null
}>()

const scorePercent = computed(() => {
  if (!props.credibility) return 0
  const normalized = Math.min(1, Math.max(0, props.credibility.score))
  return Math.round(normalized * 1000) / 10
})

const dimensionRows = computed(() => {
  if (!props.credibility) return []
  const dimensionMap = [
    { name: '信源', value: props.credibility.dimensions.source },
    { name: '内容', value: props.credibility.dimensions.content },
    { name: '逻辑', value: props.credibility.dimensions.logic },
    { name: '传播', value: props.credibility.dimensions.propagation },
    { name: '模型', value: props.credibility.dimensions.AI },
  ]

  return dimensionMap.map((item) => {
    const percent = Math.round(Math.min(1, Math.max(0, item.value)) * 1000) / 10
    return {
      ...item,
      percent,
      percentText: `${percent.toFixed(1)}%`,
    }
  })
})
</script>

<style scoped>
.score-layout {
  display: flex;
  justify-content: space-between;
}

.score-main {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-main :deep(.el-progress-circle__track) {
  stroke: rgba(148, 163, 184, 0.18);
}

.score-main :deep(.el-progress-circle__path) {
  stroke: var(--tech-color-primary-strong);
}

.score-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.info-line {
  margin: 0;
  line-height: 1.8;
  color: var(--tech-text-secondary);
}

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

:deep(.el-progress-bar__outer) {
  background: rgba(148, 163, 184, 0.16);
}

:deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, rgba(76, 201, 255, 0.78), rgba(56, 189, 248, 0.96));
}

.note {
  margin-top: 14px;
}
</style>
