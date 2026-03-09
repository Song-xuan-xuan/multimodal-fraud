<template>
  <div class="section-header">
    <div class="section-header__body">
      <p v-if="eyebrow" class="section-header__eyebrow">{{ eyebrow }}</p>
      <div class="section-header__title-row">
        <div>
          <h2 class="section-header__title">{{ title }}</h2>
          <p v-if="description" class="section-header__description">{{ description }}</p>
        </div>
        <slot name="meta" />
      </div>
    </div>
    <div v-if="$slots.actions" class="section-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  eyebrow?: string
}>()
</script>

<style scoped lang="scss">
.section-header {
  --section-accent: rgba(86, 194, 255, 0.12);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.section-header__body {
  flex: 1;
  min-width: min(100%, 320px);
}

.section-header__eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #56c2ff;
}

.section-header__title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.section-header__title {
  margin: 0;
  font-size: clamp(20px, 2.4vw, 28px);
  color: var(--tech-text-primary);
  text-shadow: 0 0 18px rgba(86, 194, 255, 0.08);
}

.section-header__description {
  margin: 8px 0 0;
  max-width: 72ch;
  color: var(--tech-text-secondary);
  line-height: 1.7;
}

.section-header__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
