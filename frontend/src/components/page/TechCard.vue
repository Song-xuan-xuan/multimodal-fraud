<template>
  <el-card class="tech-card" shadow="never" :class="{ 'is-hoverable': hoverable }">
    <slot />
  </el-card>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    hoverable?: boolean
  }>(),
  {
    hoverable: true,
  },
)
</script>

<style scoped>
.tech-card {
  border: 1px solid var(--tech-border-color);
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(14, 28, 48, 0.94), rgba(8, 18, 34, 0.96)),
    var(--tech-bg-card);
  box-shadow:
    var(--tech-shadow-sm),
    inset 0 1px 0 rgba(125, 211, 252, 0.04);
  transition:
    transform 0.24s ease,
    box-shadow 0.24s ease,
    border-color 0.24s ease,
    background 0.24s ease;
}

.tech-card.is-hoverable:hover {
  transform: translateY(-2px);
  border-color: var(--tech-border-strong);
  background:
    linear-gradient(180deg, rgba(16, 34, 58, 0.96), rgba(8, 18, 34, 0.98)),
    var(--tech-bg-card);
  box-shadow: var(--tech-shadow-md);
}

.tech-card :deep(.el-card__header) {
  padding: 20px 24px 0;
  border-bottom: none;
}

.tech-card :deep(.el-card__body) {
  padding: 20px 24px 24px;
}
</style>
