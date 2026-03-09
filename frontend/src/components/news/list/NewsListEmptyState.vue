<template>
  <el-card shadow="never" class="empty-card">
    <el-result :icon="icon" :title="title" :sub-title="description">
      <template #extra>
        <el-button v-if="actionText" type="primary" @click="$emit('action')">{{ actionText }}</el-button>
      </template>
    </el-result>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  type: 'empty' | 'error'
  title?: string
  description?: string
  actionText?: string
}>()

defineEmits<{
  action: []
}>()

const icon = computed(() => (props.type === 'error' ? 'error' : 'info'))
</script>

<style scoped>
.empty-card {
  border: 1px dashed var(--tech-border-strong);
  background: rgba(7, 17, 31, 0.72);
}
</style>
