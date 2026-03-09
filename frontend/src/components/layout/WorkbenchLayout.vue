<template>
  <AppLayout page-class="workbench-layout" content-class="workbench-layout__content">
    <template #header>
      <WorkbenchHeader />
    </template>

    <div class="workbench-layout__canvas">
      <router-view />
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from './AppLayout.vue'
import WorkbenchHeader from './WorkbenchHeader.vue'
</script>

<style scoped lang="scss">
.workbench-layout :deep(.workbench-layout__content) {
  min-height: calc(100vh - 72px);
  padding: 24px 0 32px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--tech-color-brand-cyan) 6%, transparent) 0%, transparent 18%),
    linear-gradient(180deg, var(--tech-theme-surface-base) 0%, var(--tech-theme-surface-canvas) 100%);
}

.workbench-layout__canvas {
  width: min(1680px, calc(100vw - 64px));
  margin: 0 auto;
}
</style>
