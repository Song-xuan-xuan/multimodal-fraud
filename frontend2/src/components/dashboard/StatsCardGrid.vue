<template>
  <section class="stats-grid">
    <article v-for="item in items" :key="item.label" :class="['stats-grid__item', `is-${item.tone}`]">
      <div class="stats-grid__copy">
        <p>{{ item.label }}</p>
        <strong>{{ item.value }}</strong>
      </div>
      <span :class="['stats-grid__signal', item.tone]">{{ item.tip }}</span>
    </article>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ label: string; value: string | number; tip: string; tone: 'primary' | 'danger' | 'success' | 'warning' }>
}>()
</script>

<style scoped lang="scss">
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stats-grid__item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 18px;
  border: 1px solid var(--app-border-default);
  border-radius: 22px;
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 16px 34px rgba(31, 41, 51, 0.08);
}

.stats-grid__copy {
  min-width: 0;
}

.stats-grid__item.is-primary {
  border-color: color-mix(in srgb, var(--tech-color-primary) 24%, transparent);
}

.stats-grid__item.is-danger {
  border-color: color-mix(in srgb, var(--tech-color-danger) 28%, transparent);
  background: linear-gradient(180deg, color-mix(in srgb, var(--app-status-danger-soft) 56%, white 44%) 0%, var(--app-surface-elevated) 100%);
}

.stats-grid__item.is-success {
  border-color: color-mix(in srgb, var(--tech-color-success) 24%, transparent);
  background: linear-gradient(180deg, color-mix(in srgb, var(--app-status-success-soft) 58%, white 42%) 0%, var(--app-surface-elevated) 100%);
}

.stats-grid__item.is-warning {
  border-color: color-mix(in srgb, var(--tech-color-warning) 26%, transparent);
  background: linear-gradient(180deg, color-mix(in srgb, var(--app-status-warning-soft) 58%, white 42%) 0%, var(--app-surface-elevated) 100%);
}

.stats-grid__item p {
  margin: 0 0 10px;
  color: var(--app-text-secondary);
}

.stats-grid__item strong {
  font-size: clamp(28px, 4vw, 40px);
  color: var(--app-text-primary);
}

.stats-grid__item.is-primary strong {
  color: var(--tech-color-primary-strong);
}

.stats-grid__item.is-danger strong {
  color: var(--tech-text-danger);
}

.stats-grid__item.is-success strong {
  color: var(--tech-text-success);
}

.stats-grid__item.is-warning strong {
  color: var(--tech-text-warning);
}

.stats-grid__signal {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  white-space: nowrap;
  border: 1px solid transparent;
}

.stats-grid__signal.primary {
  background: color-mix(in srgb, var(--tech-color-primary-soft) 100%, white 0%);
  color: var(--tech-color-primary-strong);
}

.stats-grid__signal.danger {
  background: color-mix(in srgb, var(--tech-color-danger-soft) 100%, white 0%);
  color: var(--tech-text-danger);
}

.stats-grid__signal.success {
  background: color-mix(in srgb, var(--tech-color-success-soft) 100%, white 0%);
  color: var(--tech-text-success);
}

.stats-grid__signal.warning {
  background: color-mix(in srgb, var(--tech-color-warning-soft) 100%, white 0%);
  color: var(--tech-text-warning);
}

@media (max-width: 1100px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid__item {
    flex-direction: column;
  }
}
</style>
