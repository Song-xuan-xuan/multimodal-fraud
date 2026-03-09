<template>
  <el-container direction="vertical" :class="['app-layout', pageClass]">
    <slot name="header" />
    <el-container>
      <slot name="sidebar" />
      <el-main :class="['app-main', contentClass]">
        <slot />
      </el-main>
    </el-container>
    <slot name="footer" />
  </el-container>
</template>

<script setup lang="ts">
defineProps<{
  pageClass?: string
  contentClass?: string
}>()
</script>

<style scoped lang="scss">
.app-layout {
  min-height: 100vh;
  background: transparent;
}

.app-main {
  min-width: 0;
  padding: 0;
}
</style>
