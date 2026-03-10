<template>
  <el-result
    v-if="appError"
    icon="error"
    class="app-error-state"
    title="页面加载失败"
    :sub-title="appError"
  >
    <template #extra>
      <el-button type="primary" @click="retryRender">重试当前页面</el-button>
      <el-button @click="reloadPage">刷新页面</el-button>
    </template>
  </el-result>
  <component :is="layoutComponent" v-else :key="layoutRenderKey" />
</template>

<script setup lang="ts">
import { computed, onErrorCaptured, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AuthLayout from '@/components/layout/AuthLayout.vue'
import PortalLayout from '@/components/layout/PortalLayout.vue'
import WorkbenchLayout from '@/components/layout/WorkbenchLayout.vue'

const route = useRoute()
const appError = ref('')
const layoutRenderKey = ref(0)

const layoutComponent = computed(() => {
  if (route.meta.layout === 'backend') {
    return WorkbenchLayout
  }

  if (route.meta.layout === 'auth') {
    return AuthLayout
  }

  return PortalLayout
})

function normalizeErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message || '页面出现异常，请稍后重试。'
  }
  if (typeof error === 'string' && error.trim()) {
    return error
  }
  return '页面出现异常，请稍后重试。'
}

function retryRender() {
  appError.value = ''
  layoutRenderKey.value += 1
}

function reloadPage() {
  if (typeof window !== 'undefined') {
    window.location.reload()
  }
}

watch(
  () => route.fullPath,
  () => {
    appError.value = ''
  },
)

onErrorCaptured((error) => {
  appError.value = normalizeErrorMessage(error)
  return false
})
</script>

<style scoped lang="scss">
.app-error-state {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--tech-color-brand-cyan) 6%, transparent) 0%, transparent 18%),
    linear-gradient(180deg, var(--tech-theme-surface-base) 0%, var(--tech-theme-surface-canvas) 100%);
}
</style>
