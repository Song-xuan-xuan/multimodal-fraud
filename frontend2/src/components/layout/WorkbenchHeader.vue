<template>
  <el-header class="workbench-header">
    <div class="workbench-header__frame">
      <div class="workbench-header__inner">
        <div class="workbench-header__branding">
          <RouterLink :to="appRoute.dashboard" class="workbench-header__brand">治理后台</RouterLink>
          <div class="workbench-header__meta">
            <p class="workbench-header__eyebrow">{{ currentRouteMeta.pageGroup || '后台' }}</p>
            <strong class="workbench-header__title">{{ currentRouteMeta.pageTitle || '后台' }}</strong>
            <small class="workbench-header__caption">风险档案馆式工作台，保留既有治理入口与角色能力。</small>
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
          <div class="workbench-header__status-panel">
            <span>当前身份</span>
            <strong>{{ authStore.username }}</strong>
            <small>{{ showAdminWorkbenchButton ? '含审核工作台权限' : '标准治理工作流' }}</small>
          </div>
          <el-button
            v-if="showAdminWorkbenchButton"
            class="workbench-header__review-button"
            type="primary"
            plain
            @click="router.push(appRoute.adminReviewWorkbench)"
          >
            审核工作台
          </el-button>
          <el-button class="workbench-header__action-button" type="primary" plain @click="router.push(appRoute.home)">返回前台</el-button>
          <el-button class="workbench-header__text-button" text @click="handleLogout">退出</el-button>
        </div>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { appRoute } from '@/router'
import { useAuthStore } from '@/stores/auth'
import { backendDirectNav, buildBackendNavGroups, isAdminUsername } from './navigation'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentRouteMeta = computed(() => route.meta as {
  pageGroup?: string
  pageTitle?: string
})

const activeMenu = computed(() => String(route.name || backendDirectNav.routeName))
const backendNavGroups = computed(() => buildBackendNavGroups(authStore.username))
const showAdminWorkbenchButton = computed(() => isAdminUsername(authStore.username))

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
  height: auto;
  padding: 0;
  background: transparent;
}

.workbench-header__frame {
  width: min(1680px, calc(100vw - 24px));
  margin: 12px auto 0;
  padding: 16px 18px;
  border: 1px solid var(--app-border-default);
  border-radius: 28px;
  background: color-mix(in srgb, var(--app-surface-panel) 86%, white 14%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
  backdrop-filter: blur(10px);
}

.workbench-header__inner {
  display: grid;
  grid-template-columns: minmax(240px, auto) minmax(0, 1fr) minmax(280px, auto);
  align-items: center;
  gap: 24px;
  overflow: hidden;
}

.workbench-header__branding {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.workbench-header__brand {
  color: var(--app-text-primary);
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
  color: var(--app-text-tertiary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.workbench-header__title {
  color: var(--app-text-primary);
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.workbench-header__caption {
  color: var(--app-text-tertiary);
  font-size: 13px;
}

.workbench-header__menu {
  min-width: 0;
  width: 100%;
  overflow: hidden;
  border-bottom: none;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: color-mix(in srgb, var(--app-surface-accent) 16%, transparent);
  --el-menu-item-height: 52px;
  --el-menu-active-color: var(--app-accent-primary-strong);
  --el-menu-text-color: var(--app-text-secondary);
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
  color: var(--app-text-secondary);
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
  color: var(--app-text-primary);
  background: color-mix(in srgb, var(--app-surface-accent) 14%, transparent);
  box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--app-accent-primary) 26%, transparent);
  outline: none;
}

.workbench-header__menu :deep(.el-menu-item.is-active),
.workbench-header__menu :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: var(--app-accent-primary-strong);
  background: color-mix(in srgb, var(--app-surface-accent) 20%, transparent);
  box-shadow: inset 0 -2px 0 var(--app-accent-primary);
}

.workbench-header__menu :deep(.el-sub-menu__icon-arrow) {
  color: inherit;
}

.workbench-header__actions {
  display: flex;
  min-width: 280px;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.workbench-header__status-panel {
  display: grid;
  gap: 2px;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid var(--app-border-default);
  border-radius: 18px;
  background: color-mix(in srgb, var(--app-surface-note) 72%, white 28%);
}

.workbench-header__status-panel span,
.workbench-header__status-panel small {
  color: var(--app-text-tertiary);
}

.workbench-header__status-panel span {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.workbench-header__status-panel strong {
  color: var(--app-text-primary);
  font-size: 14px;
}

.workbench-header__review-button {
  color: var(--app-text-primary);
  border-color: color-mix(in srgb, var(--app-status-warning) 28%, transparent);
  background: color-mix(in srgb, var(--app-status-warning-soft) 58%, var(--app-surface-elevated));
  box-shadow: 0 8px 18px rgba(185, 76, 58, 0.08);
}

.workbench-header__review-button:hover,
.workbench-header__review-button:focus-visible {
  border-color: color-mix(in srgb, var(--app-status-warning) 42%, transparent);
  background: color-mix(in srgb, var(--app-status-warning-soft) 72%, white 28%);
  box-shadow: 0 10px 22px rgba(185, 76, 58, 0.12);
}

.workbench-header__action-button {
  color: var(--app-text-primary);
  border-color: color-mix(in srgb, var(--app-accent-primary) 28%, transparent);
  background: color-mix(in srgb, var(--app-surface-accent) 18%, white 82%);
  box-shadow: 0 8px 18px rgba(23, 48, 74, 0.08);
}

.workbench-header__text-button {
  color: var(--app-text-secondary);
}

:global(.workbench-header__menu-popper) {
  border: 1px solid var(--app-border-strong);
  border-radius: var(--tech-radius-md);
  background: var(--app-surface-elevated);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.12);
  backdrop-filter: blur(10px);
}

:global(.workbench-header__menu-popper .el-menu) {
  border-right: none;
  background: transparent;
}

:global(.workbench-header__menu-popper .el-menu-item) {
  color: var(--app-text-secondary);
}

:global(.workbench-header__menu-popper .el-menu-item:hover),
:global(.workbench-header__menu-popper .el-menu-item:focus-visible) {
  color: var(--app-text-primary);
  background: color-mix(in srgb, var(--app-surface-accent) 18%, transparent);
  outline: none;
}

:global(.workbench-header__menu-popper .el-menu-item.is-active) {
  color: var(--app-accent-primary-strong);
  background: color-mix(in srgb, var(--app-surface-accent) 26%, transparent);
}

@media (max-width: 1520px) {
  .workbench-header__inner {
    grid-template-columns: 1fr;
    gap: 12px;
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
  .workbench-header__branding {
    align-items: flex-start;
    flex-direction: column;
  }

  .workbench-header__actions {
    justify-content: flex-start;
    min-width: 0;
  }

  .workbench-header__frame {
    width: calc(100vw - 16px);
    margin-top: 8px;
    padding: 12px;
  }
}

.workbench-header :deep(.el-button--primary.is-plain),
.workbench-header :deep(.el-button--primary.is-plain span) {
  color: var(--app-text-primary) !important;
}

.workbench-header__actions :deep(.workbench-header__review-button.el-button--primary.is-plain),
.workbench-header__actions :deep(.workbench-header__review-button.el-button--primary.is-plain span) {
  color: var(--app-text-primary) !important;
}

.workbench-header__actions :deep(.el-button--primary.is-plain),
.workbench-header__actions :deep(.el-button--primary.is-plain span) {
  color: var(--app-text-primary) !important;
}
</style>
