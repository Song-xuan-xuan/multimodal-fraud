<template>
  <SectionStateWrapper
    section-id="audience-profile"
    title="受众画像"
    :has-data="items.length > 0"
    :empty-text="emptyText || '暂无受众画像数据'"
  >
    <el-descriptions :column="2" border>
      <el-descriptions-item v-for="item in items" :key="item.label" :label="item.label">
        {{ item.value }}
      </el-descriptions-item>
    </el-descriptions>
  </SectionStateWrapper>
</template>

<script setup lang="ts">
interface AudienceItem {
  label: string
  value: string
}

defineProps<{
  items: AudienceItem[]
  emptyText?: string
}>()
</script>
