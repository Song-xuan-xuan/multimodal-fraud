<template>
  <SectionStateWrapper
    section-id="propagation-trend"
    title="传播趋势"
    :has-data="trendData.length > 0"
    :empty-text="propagation?.emptyReason || '暂无传播趋势数据'"
  >
    <template #extra>
      <el-tag type="info">提及总量 {{ propagation?.totalMentions || 0 }}</el-tag>
    </template>

    <el-alert
      v-if="propagation?.peakTimestamp"
      type="success"
      :closable="false"
      :title="`峰值时间：${propagation.peakTimestamp}`"
      show-icon
    />

    <el-timeline class="timeline">
      <el-timeline-item
        v-for="item in trendData"
        :key="`${item.timestamp}-${item.value}`"
        :timestamp="item.timestamp"
        placement="top"
      >
        <span class="timeline-value">传播量：{{ item.value }}</span>
      </el-timeline-item>
    </el-timeline>
  </SectionStateWrapper>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { NewsDetailPropagationVM } from '@/types/newsDetail'
import SectionStateWrapper from './SectionStateWrapper.vue'

const props = defineProps<{
  propagation: NewsDetailPropagationVM | null
}>()

const trendData = computed(() => props.propagation?.trend ?? [])
</script>

<style scoped>
.timeline {
  margin-top: 14px;
}

.timeline-value {
  color: var(--el-text-color-regular);
}
</style>
