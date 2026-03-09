<template>
  <section :id="sectionId" class="section-wrapper">
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <div>
            <h3 class="section-title">{{ title }}</h3>
            <p v-if="description" class="section-description">{{ description }}</p>
          </div>
          <slot name="extra" />
        </div>
      </template>

      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <slot v-if="hasData" />
        <slot v-else name="empty">
          <el-empty :description="emptyText" />
        </slot>
      </template>
    </el-card>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  sectionId: string
  title: string
  description?: string
  hasData?: boolean
  loading?: boolean
  emptyText?: string
}>()
</script>

<style scoped>
.section-wrapper {
  scroll-margin-top: 88px;
}

.section-card {
  border-radius: 12px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.section-description {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
