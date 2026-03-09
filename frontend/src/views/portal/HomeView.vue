<template>
  <div class="portal-home page-shell" :class="pageMotionClass">
    <HeroSection @primary="handleProtectedRoute('/detection/ai')" @secondary="handleProtectedRoute('/dashboard')" />
    <CrawlerFloatingPanel />
    <AuthDialog v-model="authDialogVisible" :initial-tab="authTab" @success="handleAuthSuccess" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HeroSection from '@/components/portal/HeroSection.vue'
import CrawlerFloatingPanel from '@/components/portal/CrawlerFloatingPanel.vue'
import AuthDialog from '@/components/auth/AuthDialog.vue'
import { usePageMotion } from '@/composables/usePageMotion'
import { useAuthStore } from '@/stores/auth'
import { appRouteName } from '@/router'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { pageMotionClass } = usePageMotion('fade', {
  selector: '[data-reveal]',
  stagger: 80,
  threshold: 0.14,
})

const authDialogVisible = ref(false)
const authTab = ref<'login' | 'register'>('login')
const pendingRoute = ref<string>('')

watch(
  () => route.query,
  (query) => {
    const auth = query.auth
    if (auth === 'login' || auth === 'register') {
      authTab.value = auth
      authDialogVisible.value = true
      pendingRoute.value = typeof query.redirect === 'string' ? query.redirect : ''
    }
  },
  { immediate: true },
)

function handleProtectedRoute(target: string) {
  if (authStore.isLoggedIn) {
    void router.push(target)
    return
  }

  authTab.value = 'login'
  authDialogVisible.value = true
  pendingRoute.value = target
  void router.replace({ name: appRouteName.home, query: { auth: 'login', redirect: target } })
}

function handleAuthSuccess() {
  const next = pendingRoute.value || '/'
  pendingRoute.value = ''
  void router.replace(next)
}
</script>

<style scoped lang="scss">
.portal-home {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  max-width: none;
  margin: 0 auto;
  gap: 0;
  padding: 0;
  overflow: hidden;
}

.portal-home > :deep(.hero-section) {
  width: 100%;
  height: 100%;
  max-width: none;
  margin-left: 0;
}
</style>
