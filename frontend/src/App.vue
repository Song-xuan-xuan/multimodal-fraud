<template>
  <component :is="layoutComponent" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AuthLayout from '@/components/layout/AuthLayout.vue'
import PortalLayout from '@/components/layout/PortalLayout.vue'
import WorkbenchLayout from '@/components/layout/WorkbenchLayout.vue'

const route = useRoute()

const layoutComponent = computed(() => {
  if (route.meta.layout === 'backend') {
    return WorkbenchLayout
  }

  if (route.meta.layout === 'auth') {
    return AuthLayout
  }

  return PortalLayout
})
</script>
