<template>
  <el-header class="workbench-header">
    <div class="workbench-header__inner">
      <div class="workbench-header__branding">
        <RouterLink :to="appRoute.dashboard" class="workbench-header__brand">治理后台</RouterLink>
        <div class="workbench-header__meta">
          <p class="workbench-header__eyebrow">{{ currentRouteMeta.pageGroup || '后台' }}</p>
          <strong class="workbench-header__title">{{ currentRouteMeta.pageTitle || '后台' }}</strong>
        </div>
      </div>

      <el-menu mode="horizontal" :default-active="activeMenu" class="workbench-header__menu" @select="handleMenuSelect">
        <el-menu-item :index="backendDirectNav.routeName">{{ backendDirectNav.label }}</el-menu-item>
        <el-sub-menu
          v-for="group in backendNavGroups"
          :key="group.index"
          :index="group.index"
          popper-class="workbench-header__menu-popper"
        >
          <template #title>{{ group.label }}</template>
          <el-menu-item v-for="item in group.items" :key="item.routeName" :index="item.routeName">
            {{ item.label }}
          </el-menu-item>
        </el-sub-menu>
      </el-menu>

      <div class="workbench-header__actions">
        <span class="workbench-header__username">{{ authStore.username }}</span>
        <el-button class="workbench-header__action-button" type="primary" plain @click="router.push(appRoute.home)">返回前台</el-button>
        <el-button class="workbench-header__text-button" text @click="handleLogout">退出</el-button>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { appRoute } from '@/router'
import { useAuthStore } from '@/stores/auth'
import { backendDirectNav, buildBackendNavGroups } from './navigation'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentRouteMeta = computed(() => route.meta as {
  pageGroup?: string
  pageTitle?: string
})

const activeMenu = computed(() => String(route.name || backendDirectNav.routeName))
const backendNavGroups = computed(() => buildBackendNavGroups(authStore.username))

function handleMenuSelect(index: string) {
  void router.push({ name: index })
}

function handleLogout() {
  authStore.logout()
  void router.push(appRoute.login)
}
</script>

<style scoped lang="scss">
.workbench-header {
  position: sticky;
  top: 0;
  z-index: var(--tech-z-sticky);
  height: 72px;
  padding: 0;
  background: linear-gradient(180deg, color-mix(in srgb, var(--tech-color-brand-cyan) 10%, transparent) 0%, var(--tech-theme-surface-glass-strong) 100%);
  border-bottom: 1px solid var(--tech-theme-border);
  box-shadow: var(--tech-shadow-sm);
  backdrop-filter: blur(18px);
}

.workbench-header__inner {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 24px;
  width: min(1680px, calc(100vw - 64px));
  height: 100%;
  margin: 0 auto;
  overflow: hidden;
}

.workbench-header__branding {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.workbench-header__brand {
  color: var(--tech-theme-text-brand);
  font-size: 20px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}

.workbench-header__meta {
  display: grid;
  min-width: 0;
}

.workbench-header__eyebrow {
  margin: 0 0 4px;
  font-size: 12px;
  color: var(--tech-theme-text-tertiary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.workbench-header__title {
  color: var(--tech-theme-text-primary);
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.workbench-header__menu {
  min-width: 0;
  width: 100%;
  overflow: hidden;
  border-bottom: none;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: color-mix(in srgb, var(--tech-color-primary-soft) 82%, transparent);
  --el-menu-item-height: 72px;
  --el-menu-active-color: var(--tech-color-primary-strong);
  --el-menu-text-color: var(--tech-theme-text-secondary);
}

.workbench-header__menu :deep(.el-menu--horizontal) {
  display: flex;
  width: 100%;
  min-width: 0;
  border-bottom: none;
}

.workbench-header__menu :deep(.el-menu-item),
.workbench-header__menu :deep(.el-sub-menu__title) {
  position: relative;
  border-bottom: none;
  color: var(--tech-theme-text-secondary);
  font-weight: 500;
  transition:
    color var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out),
    box-shadow var(--tech-duration-fast) var(--tech-ease-out);
}

.workbench-header__menu :deep(.el-menu-item:hover),
.workbench-header__menu :deep(.el-sub-menu__title:hover),
.workbench-header__menu :deep(.el-menu-item:focus-visible),
.workbench-header__menu :deep(.el-sub-menu__title:focus-visible) {
  color: var(--tech-theme-text-primary);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 82%, transparent);
  box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--tech-color-primary) 28%, transparent);
  outline: none;
}

.workbench-header__menu :deep(.el-menu-item.is-active),
.workbench-header__menu :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: var(--tech-color-primary-strong);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 100%, transparent);
  box-shadow: inset 0 -2px 0 var(--tech-color-primary);
}

.workbench-header__menu :deep(.el-sub-menu__icon-arrow) {
  color: inherit;
}

.workbench-header__actions {
  
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.workbench-header__username {
  padding: 8px 14px;
  border: 1px solid var(--tech-theme-border);
  border-radius: var(--tech-radius-pill);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 40%, transparent);
  color: var(--tech-theme-text-regular);
  white-space: nowrap;
}
.workbench-header__action-button {
  color: rgba(210, 245, 255, 0.88);
  border-color: rgba(210, 245, 255, 0.88);
  background: linear-gradient(135deg, rgba(46, 205, 176, 0.18), rgba(36, 119, 255, 0.16));
  box-shadow: 0 0 0 1px rgba(124, 231, 255, 0.08), 0 0 24px rgba(92, 255, 225, 0.14);
}

:global(.workbench-header__menu-popper) {
  border: 1px solid var(--tech-theme-border-strong);
  border-radius: var(--tech-radius-md);
  background: var(--tech-theme-surface-elevated);
  box-shadow: var(--tech-shadow-lg);
  backdrop-filter: blur(18px);
}

:global(.workbench-header__menu-popper .el-menu) {
  border-right: none;
  background: transparent;
}

:global(.workbench-header__menu-popper .el-menu-item) {
  color: var(--tech-theme-text-secondary);
}

:global(.workbench-header__menu-popper .el-menu-item:hover),
:global(.workbench-header__menu-popper .el-menu-item:focus-visible) {
  color: var(--tech-theme-text-primary);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 88%, transparent);
  outline: none;
}

:global(.workbench-header__menu-popper .el-menu-item.is-active) {
  color: var(--tech-color-primary-strong);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 100%, transparent);
}
@media (max-width: 1520px) {
  .workbench-header {
    height: auto;
  }

  .workbench-header__inner {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px 0;
  }

  .workbench-header__menu {
    order: 3;
  }

  .workbench-header__actions {
    justify-content: flex-end;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .workbench-header__inner {
    width: min(100vw - 24px, 1680px);
  }

  .workbench-header__branding {
    align-items: flex-start;
    flex-direction: column;
  }

  .workbench-header__actions {
    justify-content: flex-start;
  }

  .workbench-header__username {
    display: none;
  }
}

</style>

.workbench-header :deep(.el-button--primary.is-plain),
.workbench-header :deep(.el-button--primary.is-plain span) {
  color: #eef9ff !important;
}

.workbench-header__actions :deep(.el-button--primary.is-plain),
.workbench-header__actions :deep(.el-button--primary.is-plain span) {
  color: #eef9ff !important;
}
