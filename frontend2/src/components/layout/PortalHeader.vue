<template>
  <el-header :class="['portal-header', { 'portal-header--home': isHomeRoute }]">
    <div class="portal-header__frame">
      <div class="portal-header__inner">
        <div class="portal-header__brand-block">
          <RouterLink :to="appRoute.home" class="portal-header__brand">FraudShield</RouterLink>
          <div class="portal-header__brand-copy">
            <p>反诈情报门户</p>
            <small>{{ isHomeRoute ? '品牌总览与任务入口' : '分析入口与前台工作流' }}</small>
          </div>
        </div>

        <el-menu mode="horizontal" :default-active="activeMenu" class="portal-header__menu" @select="handleMenuSelect">
          <el-menu-item :index="frontendDirectNav.routeName">{{ frontendDirectNav.label }}</el-menu-item>
          <el-menu-item v-for="item in frontendPrimaryNav" :key="item.routeName" :index="item.routeName">
            {{ item.label }}
          </el-menu-item>
          <el-sub-menu
            v-for="group in frontendNavGroups"
            :key="group.index"
            :index="group.index"
            popper-class="portal-header__menu-popper"
          >
            <template #title>{{ group.label }}</template>
            <el-menu-item v-for="item in group.items" :key="item.routeName" :index="item.routeName">
              {{ item.label }}
            </el-menu-item>
          </el-sub-menu>
        </el-menu>

        <div class="portal-header__actions">
          <div class="portal-header__status-panel">
            <span class="portal-header__status-label">今日状态</span>
            <strong>{{ formattedDate }}</strong>
            <small>{{ authStore.isLoggedIn ? '已登录，可直接进入治理后台' : '未登录，需先验证身份' }}</small>
          </div>
          <template v-if="authStore.isLoggedIn">
            <span class="portal-header__username">{{ authStore.username }}</span>
            <el-button class="portal-header__action-button" type="primary" plain @click="router.push(appRoute.dashboard)">进入后台</el-button>
            <el-button class="portal-header__text-button" text @click="handleLogout">退出</el-button>
          </template>
          <template v-else>
            <el-button class="portal-header__auth-button portal-header__auth-button--primary" type="primary" plain @click="openAuth('login')">登录</el-button>
            <el-button class="portal-header__auth-button portal-header__auth-button--secondary" @click="openAuth('register')">注册</el-button>
          </template>
        </div>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { appRoute, appRouteName } from '@/router'
import { useAuthStore } from '@/stores/auth'
import { frontendDirectNav, frontendNavGroups, frontendPrimaryNav } from './navigation'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => String(route.name || frontendDirectNav.routeName))
const isHomeRoute = computed(() => route.name === appRouteName.home)
const formattedDate = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}年${m}月${d}日`
})

function openAuth(mode: 'login' | 'register') {
  void router.push({ name: appRouteName.home, query: { auth: mode } })
}

function handleMenuSelect(index: string) {
  if (!authStore.isLoggedIn && index !== appRouteName.home) {
    const target =
      frontendPrimaryNav.find((item) => item.routeName === index)?.route ??
      frontendNavGroups.flatMap((group) => group.items).find((item) => item.routeName === index)?.route ??
      frontendDirectNav.route
    const redirect = router.resolve(target).fullPath
    void router.push({ name: appRouteName.home, query: { auth: 'login', ...(redirect ? { redirect } : {}) } })
    return
  }
  void router.push({ name: index })
}

function handleLogout() {
  authStore.logout()
  void router.push(appRoute.home)
}
</script>

<style scoped lang="scss">
.portal-header {
  position: sticky;
  top: 0;
  z-index: var(--tech-z-sticky);
  height: auto;
  padding: 0;
  border-bottom: 1px solid transparent;
  background: transparent;
  box-shadow: none;
}

.portal-header__frame {
  width: min(1680px, calc(100vw - 24px));
  margin: 12px auto 0;
  padding: 14px 18px;
  border: 1px solid var(--app-border-default);
  border-radius: 28px;
  background: color-mix(in srgb, var(--app-surface-elevated) 92%, white 8%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
  backdrop-filter: blur(10px);
}

.portal-header__inner {
  display: grid;
  grid-template-columns: minmax(220px, auto) minmax(0, 1fr) minmax(280px, auto);
  align-items: center;
  gap: 24px;
  overflow: hidden;
}

.portal-header__brand-block {
  display: flex;
  align-items: center;
  gap: 16px;
}

.portal-header__brand {
  color: var(--app-text-primary);
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.03em;
  text-decoration: none;
  white-space: nowrap;
}

.portal-header__brand-copy {
  display: grid;
  gap: 2px;
}

.portal-header__brand-copy p,
.portal-header__brand-copy small {
  margin: 0;
}

.portal-header__brand-copy p {
  color: var(--app-text-secondary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.portal-header__brand-copy small {
  color: var(--app-text-tertiary);
  font-size: 13px;
}

.portal-header__brand:hover,
.portal-header__brand:focus-visible {
  color: var(--app-accent-primary-strong);
  outline: none;
}

.portal-header__menu {
  min-width: 0;
  width: 100%;
  overflow: hidden;
  border-bottom: none;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: color-mix(in srgb, var(--app-surface-accent) 18%, transparent);
  --el-menu-item-height: 52px;
  --el-menu-active-color: var(--app-accent-primary-strong);
  --el-menu-text-color: var(--app-text-secondary);
}

.portal-header__menu :deep(.el-menu--horizontal) {
  display: flex;
  width: 100%;
  min-width: 0;
  border-bottom: none;
}

.portal-header__menu :deep(.el-menu-item),
.portal-header__menu :deep(.el-sub-menu__title) {
  position: relative;
  border-bottom: none;
  color: var(--app-text-secondary);
  font-weight: 500;
  transition:
    color var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out),
    box-shadow var(--tech-duration-fast) var(--tech-ease-out);
}

.portal-header__menu :deep(.el-menu-item:hover),
.portal-header__menu :deep(.el-sub-menu__title:hover),
.portal-header__menu :deep(.el-menu-item:focus-visible),
.portal-header__menu :deep(.el-sub-menu__title:focus-visible) {
  color: var(--app-text-primary);
  background: color-mix(in srgb, var(--app-surface-accent) 14%, transparent);
  box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--app-accent-primary) 22%, transparent);
  outline: none;
}

.portal-header__menu :deep(.el-menu-item.is-active),
.portal-header__menu :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: var(--app-accent-primary-strong);
  background: color-mix(in srgb, var(--app-surface-accent) 18%, transparent);
  box-shadow: inset 0 -2px 0 var(--app-accent-primary);
}

.portal-header__menu :deep(.el-sub-menu__icon-arrow) {
  color: inherit;
}

.portal-header__actions {
  display: flex;
  min-width: 280px;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.portal-header__status-panel {
  display: grid;
  gap: 2px;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid var(--app-border-default);
  border-radius: 18px;
  background: color-mix(in srgb, var(--app-surface-accent) 12%, var(--app-surface-elevated));
}

.portal-header__status-label,
.portal-header__status-panel small {
  color: var(--app-text-tertiary);
}

.portal-header__status-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.portal-header__status-panel strong {
  color: var(--app-text-primary);
  font-size: 14px;
}

.portal-header__username {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 8px 14px;
  border: 1px solid var(--app-border-default);
  border-radius: var(--tech-radius-pill);
  background: color-mix(in srgb, var(--app-surface-note) 72%, white 28%);
  color: var(--app-text-regular);
  white-space: nowrap;
}

.portal-header__auth-button,
.portal-header__action-button {
  color: var(--app-text-primary);
  min-height: 40px;
  padding-inline: 18px;
  border-radius: 999px;
}

.portal-header__auth-button--primary,
.portal-header__action-button {
  border-color: color-mix(in srgb, var(--app-accent-primary) 30%, transparent);
  background: color-mix(in srgb, var(--app-surface-accent) 18%, white 82%);
  box-shadow: 0 8px 18px rgba(23, 48, 74, 0.08);
}

.portal-header__auth-button--secondary {
  border-color: var(--app-border-default);
  background: var(--app-surface-elevated);
  color: var(--app-text-regular);
}

.portal-header__text-button {
  color: var(--app-text-secondary);
}

:global(.portal-header__menu-popper) {
  border: 1px solid var(--app-border-strong);
  border-radius: var(--tech-radius-md);
  background: var(--app-surface-elevated);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.12);
  backdrop-filter: blur(10px);
}

:global(.portal-header__menu-popper .el-menu) {
  border-right: none;
  background: transparent;
}

:global(.portal-header__menu-popper .el-menu-item) {
  color: var(--app-text-secondary);
  transition:
    color var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out);
}

:global(.portal-header__menu-popper .el-menu-item:hover),
:global(.portal-header__menu-popper .el-menu-item:focus-visible) {
  color: var(--app-text-primary);
  background: color-mix(in srgb, var(--app-surface-accent) 18%, transparent);
  outline: none;
}

:global(.portal-header__menu-popper .el-menu-item.is-active) {
  color: var(--app-accent-primary-strong);
  background: color-mix(in srgb, var(--app-surface-accent) 26%, transparent);
}

@media (max-width: 1520px) {
  .portal-header__inner {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .portal-header__menu {
    order: 3;
  }

  .portal-header__actions {
    justify-content: flex-end;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .portal-header__actions {
    justify-content: flex-start;
    gap: 10px;
    min-width: 0;
  }

  .portal-header__username {
    display: none;
  }

  .portal-header__frame {
    width: calc(100vw - 16px);
    margin-top: 8px;
    padding: 12px;
  }
}

.portal-header__action-button,
.portal-header__action-button :deep(span),
.portal-header__auth-button,
.portal-header__auth-button :deep(span) {
  color: var(--app-text-primary) !important;
}
</style>
