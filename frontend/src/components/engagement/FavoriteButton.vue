<template>
  <el-button
    class="favorite-button"
    :type="favorited ? 'warning' : 'default'"
    :plain="!favorited"
    @click="onToggle"
  >
    {{ favorited ? '已收藏' : '收藏' }}
  </el-button>
</template>

<script setup lang="ts">
const props = defineProps<{
  favorited: boolean
}>()

const emit = defineEmits<{
  (event: 'toggle'): void
}>()

function onToggle() {
  emit('toggle')
}
</script>

<style scoped>
.favorite-button {
  min-width: 92px;
}
</style>
