<template>
  <div class="floating-actions">
    <button
      v-for="item in items"
      :key="item.label"
      type="button"
      class="floating-actions__item tech-surface"
      @click="$emit('navigate', item.path)"
    >
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
  min-width: 138px;
  padding: 12px 14px;
  color: inherit;
  cursor: pointer;
  border: 1px solid color-mix(in srgb, var(--tech-color-primary) 18%, transparent);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 28%, transparent);
  transition:
    transform var(--tech-duration-fast) var(--tech-ease-out),
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    background var(--tech-duration-fast) var(--tech-ease-out);
}

.floating-actions__item:first-child {
  background: color-mix(in srgb, var(--tech-color-primary-soft) 42%, transparent);
  box-shadow: var(--tech-theme-glow-soft);
}

.floating-actions__item:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--tech-color-primary) 28%, transparent);
}

.floating-actions__icon {
  font-size: 18px;
  color: var(--tech-color-primary-strong);
}

.floating-actions__label {
  font-size: 13px;
  color: var(--tech-text-primary);
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
