<template>
  <div class="floating-actions">
    <button v-for="item in items" :key="item.label" type="button" class="floating-actions__item" @click="$emit('navigate', item.path)">
      <span class="floating-actions__icon">{{ item.icon }}</span>
      <span class="floating-actions__label">{{ item.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  navigate: [path: string]
}>()

defineProps<{
  items: Array<{ label: string; path: string; icon: string }>
}>()
</script>

<style scoped lang="scss">
.floating-actions {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: var(--tech-z-sticky);
  display: grid;
  gap: 10px;
}

.floating-actions__item {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-width: 142px;
  padding: 12px 14px;
  color: inherit;
  cursor: pointer;
  border: 1px solid var(--app-border-default);
  border-radius: 16px;
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 16px 30px rgba(31, 41, 51, 0.08);
  transition:
    transform var(--tech-duration-fast) var(--tech-ease-out),
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    background var(--tech-duration-fast) var(--tech-ease-out);
}

.floating-actions__item:first-child {
  background: color-mix(in srgb, var(--app-status-danger-soft) 42%, white 58%);
}

.floating-actions__item:hover {
  transform: translateY(-1px);
  border-color: var(--app-border-strong);
}

.floating-actions__icon {
  font-size: 18px;
  color: var(--tech-color-primary-strong);
}

.floating-actions__label {
  font-size: 13px;
  color: var(--app-text-primary);
}

@media (max-width: 900px) {
  .floating-actions {
    right: 16px;
    bottom: 16px;
  }

  .floating-actions__item {
    min-width: 112px;
  }
}
</style>
