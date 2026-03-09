<template>
  <div class="toolbar">
    <div class="toolbar-info">
      <h3 class="toolbar-title">结果内容</h3>
      <p class="toolbar-description">可在卡片视图与表格视图之间切换，保持浏览与跳转心智一致。</p>
    </div>

    <div class="toolbar-actions">
      <el-radio-group :model-value="mode" size="small" @update:model-value="$emit('update:mode', $event)">
        <el-radio-button label="card">卡片</el-radio-button>
        <el-radio-button label="table">表格</el-radio-button>
      </el-radio-group>
      <el-button :loading="loading" @click="$emit('refresh')">刷新</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  mode: 'card' | 'table'
  loading?: boolean
}>()

defineEmits<{
  'update:mode': [value: 'card' | 'table']
  refresh: []
}>()
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.toolbar-title {
  margin: 0;
  font-size: 18px;
  color: var(--tech-text-primary);
}

.toolbar-description {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--tech-text-secondary);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
