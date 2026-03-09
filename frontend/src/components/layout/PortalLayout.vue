<template>
  <AppLayout :content-class="contentClass" page-class="portal-layout">
    <template #header>
      <PortalHeader />
    </template>

    <div :class="['portal-layout__canvas', { 'portal-layout__canvas--home': isHomeRoute, 'portal-layout__canvas--footerless': hideFooter }]">
      <router-view />
    </div>

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

.portal-layout__canvas {
  width: min(1440px, calc(100vw - 64px));
  margin: 0 auto;
  padding-top: 32px;
}

.portal-layout__canvas--footerless {
  min-height: calc(100vh - 72px);
}

.portal-layout__canvas--home {
  width: 100%;
  max-width: none;
  height: calc(100vh - 72px);
  padding-top: 0;
  overflow: hidden;
}

.portal-layout__canvas--home :deep(.portal-home) {
  height: 100%;
  overflow: hidden;
}
</style>
