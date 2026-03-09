<template>
  <section :class="['page-hero', `page-hero--${tone}`]">
    <div class="page-hero__glow" />
    <div class="page-hero__content">
      <SectionHeader :eyebrow="eyebrow" :title="title" :description="description">
        <template #meta>
          <slot name="meta" />
        </template>
        <template #actions>
          <slot name="actions" />
        </template>
      </SectionHeader>
      <div v-if="$slots.default" class="page-hero__metrics">
        <slot />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import SectionHeader from '@/components/dashboard/SectionHeader.vue'

withDefaults(
  defineProps<{
    title: string
    description?: string
    eyebrow?: string
    tone?: 'insight' | 'workbench'
  }>(),
  {
    tone: 'insight',
  },
)
</script>

<style scoped lang="scss">
.page-hero {
  --page-hero-accent: rgba(86, 194, 255, 0.18);
  --page-hero-line: rgba(86, 194, 255, 0.1);
  position: relative;
  overflow: hidden;
  border-radius: var(--tech-radius-xl, 24px);
  border: 1px solid var(--tech-border-color);
  background: var(--tech-bg-panel);
  box-shadow: var(--tech-shadow-sm);
}

.page-hero--insight {
  --page-hero-accent: rgba(86, 194, 255, 0.18);
  --page-hero-line: rgba(86, 194, 255, 0.1);
  background:
    radial-gradient(circle at top right, var(--page-hero-accent), transparent 36%),
    linear-gradient(135deg, rgba(86, 194, 255, 0.1), rgba(8, 17, 31, 0.95) 58%),
    var(--tech-bg-panel);
}

.page-hero--workbench {
  --page-hero-accent: rgba(120, 227, 189, 0.14);
  --page-hero-line: rgba(120, 227, 189, 0.08);
  background:
    radial-gradient(circle at top right, var(--page-hero-accent), transparent 38%),
    linear-gradient(135deg, rgba(86, 194, 255, 0.06), rgba(8, 17, 31, 0.95) 54%),
    var(--tech-bg-panel);
}

.page-hero__glow {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, var(--page-hero-line), transparent 24%, transparent 76%, var(--page-hero-line)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 34%);
  pointer-events: none;
}

.page-hero__content {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 28px;
}

.page-hero__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

@media (max-width: 1100px) {
  .page-hero__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .page-hero__content {
    padding: 22px;
  }

  .page-hero__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
