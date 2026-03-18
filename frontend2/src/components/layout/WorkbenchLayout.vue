<template>
  <AppLayout page-class="workbench-layout" content-class="workbench-layout__content">
    <template #header>
      <WorkbenchHeader />
    </template>

    <section class="workbench-layout__stage">
      <aside class="workbench-layout__rail" aria-label="治理节奏">
        <article>
          <span>01</span>
          <strong>洞察</strong>
        </article>
        <article>
          <span>02</span>
          <strong>研判</strong>
        </article>
        <article>
          <span>03</span>
          <strong>处置</strong>
        </article>
      </aside>

      <div class="workbench-layout__canvas">
        <router-view />
      </div>
    </section>
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
    radial-gradient(circle at top left, color-mix(in srgb, var(--app-accent-primary) 8%, transparent), transparent 34%),
    linear-gradient(180deg, var(--tech-theme-surface-base) 0%, var(--tech-theme-surface-canvas) 100%);
}

.workbench-layout__stage {
  display: grid;
  grid-template-columns: minmax(0, 168px) minmax(0, 1fr);
  gap: 24px;
  width: min(1680px, calc(100vw - 48px));
  margin: 0 auto;
}

.workbench-layout__rail {
  display: grid;
  align-content: start;
  gap: 12px;
}

.workbench-layout__rail article {
  display: grid;
  gap: 6px;
  padding: 16px;
  border: 1px solid var(--app-border-default);
  border-radius: 18px;
  background: var(--app-surface-elevated);
  box-shadow: 0 10px 24px rgba(31, 41, 51, 0.05);
}

.workbench-layout__rail span {
  color: var(--app-text-tertiary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.workbench-layout__rail strong {
  color: var(--app-text-primary);
  font-size: 18px;
}

.workbench-layout__canvas {
  min-width: 0;
}

@media (max-width: 1080px) {
  .workbench-layout__stage {
    grid-template-columns: 1fr;
    width: min(100vw - 24px, 1680px);
  }

  .workbench-layout__rail {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .workbench-layout__rail {
    grid-template-columns: 1fr;
  }
}
</style>
