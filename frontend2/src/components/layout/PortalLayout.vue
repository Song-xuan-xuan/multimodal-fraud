<template>
  <AppLayout :content-class="contentClass" page-class="portal-layout">
    <template #header>
      <PortalHeader />
    </template>

    <section
      :class="['portal-layout__stage', { 'portal-layout__stage--home': isHomeRoute, 'portal-layout__stage--footerless': hideFooter }]"
    >
      <div class="portal-layout__rail" aria-hidden="true">
        <span>情报门户</span>
        <span>证据卷宗</span>
        <span>风险预警</span>
      </div>
      <div :class="['portal-layout__canvas', { 'portal-layout__canvas--home': isHomeRoute, 'portal-layout__canvas--footerless': hideFooter }]">
        <router-view />
      </div>
    </section>

    <template v-if="!hideFooter" #footer>
      <AppFooter />
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { appRouteName } from '@/router'
import AppFooter from './AppFooter.vue'
import AppLayout from './AppLayout.vue'
import PortalHeader from './PortalHeader.vue'

const route = useRoute()
const isHomeRoute = computed(() => route.name === appRouteName.home)
const hideFooter = computed(() => isHomeRoute.value)
const contentClass = computed(() => (isHomeRoute.value ? 'portal-layout__content portal-layout__content--home' : 'portal-layout__content'))
</script>

<style scoped lang="scss">
.portal-layout :deep(.portal-layout__content) {
  min-height: calc(100vh - 72px - 113px);
  width: 100%;
  padding: 0 0 32px;
}

.portal-layout :deep(.portal-layout__content--home) {
  min-height: calc(100vh - 72px);
  padding: 0;
  overflow: hidden;
}

.portal-layout__stage {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 148px) minmax(0, 1fr);
  gap: 24px;
  width: min(1680px, calc(100vw - 48px));
  margin: 0 auto;
  padding-top: 28px;
}

.portal-layout__stage--footerless {
  min-height: calc(100vh - 72px);
}

.portal-layout__rail {
  position: sticky;
  top: 112px;
  display: grid;
  align-content: start;
  gap: 12px;
  min-height: 0;
}

.portal-layout__rail span {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 10px 14px;
  border: 1px solid var(--app-border-default);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface-elevated) 90%, white 10%);
  color: var(--app-text-secondary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.portal-layout__canvas {
  width: min(1480px, 100%);
  margin: 0 auto;
}

.portal-layout__canvas--home {
  width: 100%;
  max-width: none;
  height: calc(100vh - 72px);
  overflow: hidden;
}

.portal-layout__canvas--home :deep(.portal-home) {
  height: 100%;
  overflow: hidden;
}

@media (max-width: 1080px) {
  .portal-layout__stage {
    grid-template-columns: 1fr;
    width: min(100vw - 24px, 1680px);
    gap: 16px;
  }

  .portal-layout__rail {
    position: static;
    grid-auto-flow: column;
    grid-auto-columns: max-content;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .portal-layout__canvas--home {
    height: auto;
    min-height: calc(100vh - 72px);
  }
}
</style>
