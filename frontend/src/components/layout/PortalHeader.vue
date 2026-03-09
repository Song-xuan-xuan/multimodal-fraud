<template>
  <el-header :class="['portal-header', { 'portal-header--home': isHomeRoute }]">
    <div class="portal-header__inner">
      <RouterLink :to="appRoute.home" class="portal-header__brand">AuthentiAI</RouterLink>

      <el-menu mode="horizontal" :default-active="activeMenu" class="portal-header__menu" @select="handleMenuSelect">
        <el-menu-item :index="frontendDirectNav.routeName">{{ frontendDirectNav.label }}</el-menu-item>
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
        <span class="portal-header__date">{{ formattedDate }}</span>
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
  </el-header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { appRoute, appRouteName } from '@/router'
import { useAuthStore } from '@/stores/auth'
import { frontendDirectNav, frontendNavGroups } from './navigation'

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
    const target = frontendNavGroups.flatMap((group) => group.items).find((item) => item.routeName === index)?.route ?? frontendDirectNav.route
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
  height: 72px;
  padding: 0;
  border-bottom: 1px solid var(--tech-theme-border);
  background: linear-gradient(180deg, color-mix(in srgb, var(--tech-color-brand-cyan) 10%, transparent) 0%, var(--tech-theme-surface-glass-strong) 100%);
  box-shadow: var(--tech-shadow-sm);
  backdrop-filter: blur(18px);
}

.portal-header--home {
  background: linear-gradient(180deg, rgba(2, 9, 18, 0.9) 0%, rgba(4, 14, 26, 0.76) 55%, rgba(6, 18, 31, 0.44) 100%);
  border-bottom-color: rgba(124, 231, 255, 0.14);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.28);
}

.portal-header__inner {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 24px;
  width: min(1680px, calc(100vw - 64px));
  height: 100%;
  margin: 0 auto;
  overflow: hidden;
}

.portal-header__brand {
  position: relative;
  color: var(--tech-theme-text-brand);
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.03em;
  text-decoration: none;
  white-space: nowrap;
  transition: color var(--tech-duration-fast) var(--tech-ease-out), text-shadow var(--tech-duration-fast) var(--tech-ease-out);
}

.portal-header--home .portal-header__brand {
  text-shadow: 0 0 18px rgba(92, 255, 225, 0.24);
}

.portal-header__brand:hover,
.portal-header__brand:focus-visible {
  color: var(--tech-color-primary-strong);
  outline: none;
}

.portal-header__menu {
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

.portal-header--home .portal-header__menu {
  --el-menu-hover-bg-color: rgba(92, 255, 225, 0.08);
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
  color: var(--tech-theme-text-secondary);
  font-weight: 500;
  transition:
    color var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out),
    box-shadow var(--tech-duration-fast) var(--tech-ease-out),
    transform var(--tech-duration-fast) var(--tech-ease-out);
}

.portal-header__menu :deep(.el-menu-item:hover),
.portal-header__menu :deep(.el-sub-menu__title:hover),
.portal-header__menu :deep(.el-menu-item:focus-visible),
.portal-header__menu :deep(.el-sub-menu__title:focus-visible) {
  color: var(--tech-theme-text-primary);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 82%, transparent);
  box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--tech-color-primary) 28%, transparent);
  transform: translateY(-1px);
  outline: none;
}

.portal-header__menu :deep(.el-menu-item.is-active),
.portal-header__menu :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: var(--tech-color-primary-strong);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 100%, transparent);
  box-shadow: inset 0 -2px 0 var(--tech-color-primary);
}

.portal-header__menu :deep(.el-sub-menu__icon-arrow) {
  color: inherit;
}

.portal-header__actions {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

.portal-header__date,
.portal-header__username {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 8px 14px;
  border-radius: var(--tech-radius-pill);
  white-space: nowrap;
}

.portal-header__date {
  border: 1px solid rgba(124, 231, 255, 0.18);
  background: rgba(6, 14, 26, 0.46);
  color: #eef9ff;
  font-size: 14px;
  letter-spacing: 0.08em;
}

.portal-header__username {
  border: 1px solid var(--tech-theme-border);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 40%, transparent);
  color: var(--tech-theme-text-regular);
}

.portal-header__auth-button,
.portal-header__action-button {
  color: #eef9ff;
  min-height: 40px;
  padding-inline: 18px;
  border-radius: 999px;
}

.portal-header__auth-button--primary,
.portal-header__action-button {
  border-color: rgba(210, 245, 255, 0.88);
  background: linear-gradient(135deg, rgba(210, 245, 255, 0.88), rgba(210, 245, 255, 0.88));
  box-shadow: 0 0 0 1px rgba(210, 245, 255, 0.88), 0 0 24px rgba(210, 245, 255, 0.88);;
}

.portal-header__auth-button--secondary {
  border-color: rgba(210, 245, 255, 0.88);
  background: rgba(210, 245, 255, 0.88);
  color: rgba(229, 245, 255, 0.92);
}

.portal-header__text-button {
  color: rgba(224, 241, 255, 0.82);
}

:global(.portal-header__menu-popper) {
  border: 1px solid var(--tech-theme-border-strong);
  border-radius: var(--tech-radius-md);
  background: var(--tech-theme-surface-elevated);
  box-shadow: var(--tech-shadow-lg);
  backdrop-filter: blur(18px);
}

:global(.portal-header__menu-popper .el-menu) {
  border-right: none;
  background: transparent;
}

:global(.portal-header__menu-popper .el-menu-item) {
  color: var(--tech-theme-text-secondary);
  transition:
    color var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out);
}

:global(.portal-header__menu-popper .el-menu-item:hover),
:global(.portal-header__menu-popper .el-menu-item:focus-visible) {
  color: var(--tech-theme-text-primary);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 88%, transparent);
  outline: none;
}

:global(.portal-header__menu-popper .el-menu-item.is-active) {
  color: var(--tech-color-primary-strong);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 100%, transparent);
}

@media (max-width: 1520px) {
  .portal-header {
    height: auto;
  }

  .portal-header__inner {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px 0;
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
  .portal-header__inner {
    width: min(100vw - 24px, 1680px);
  }

  .portal-header__actions {
    justify-content: flex-start;
    gap: 10px;
  }

  .portal-header__username {
    display: none;
  }

  .portal-header__date {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style>

.portal-header__action-button,
.portal-header__action-button :deep(span),
.portal-header__auth-button,
.portal-header__auth-button :deep(span) {
  color: #eef9ff !important;
}

