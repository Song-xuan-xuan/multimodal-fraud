<template>
  <section :id="sectionId" class="page-section" :class="[`align-${align}`]">
    <div v-if="eyebrow || title || description || $slots.headerExtra" class="section-header">
      <div class="section-heading">
        <span v-if="eyebrow" class="section-eyebrow">{{ eyebrow }}</span>
        <h2 v-if="title" class="section-title">{{ title }}</h2>
        <p v-if="description" class="section-description">{{ description }}</p>
      </div>
      <div v-if="$slots.headerExtra" class="section-extra">
        <slot name="headerExtra" />
      </div>
    </div>
    <div class="section-body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    sectionId?: string
    eyebrow?: string
    title?: string
    description?: string
    align?: 'start' | 'center'
  }>(),
  {
    sectionId: undefined,
    eyebrow: '',
    title: '',
    description: '',
    align: 'start',
  },
)
</script>

<style scoped>
.page-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  scroll-margin-top: 108px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.section-heading {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.section-eyebrow {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  padding: 6px 12px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--el-color-primary) 10%, white);
  color: var(--el-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.section-title {
  margin: 0;
  font-size: clamp(20px, 2.2vw, 28px);
  line-height: 1.2;
  color: var(--el-text-color-primary);
}

.section-description {
  margin: 0;
  max-width: 760px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--el-text-color-secondary);
}

.section-extra {
  flex-shrink: 0;
}

.align-center .section-header,
.align-center .section-heading {
  align-items: center;
  text-align: center;
}

.align-center .section-header {
  flex-direction: column;
}

.section-body {
  min-width: 0;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
  }
}
</style>
