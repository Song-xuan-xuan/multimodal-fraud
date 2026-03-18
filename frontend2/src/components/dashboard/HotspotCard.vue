<template>
  <section class="hotspot-card">
    <div class="hotspot-card__header">
      <div>
        <p class="hotspot-card__eyebrow">热点追踪</p>
        <h3>省域风险排行</h3>
      </div>
      <el-button text type="primary" @click="$emit('navigate', '/insight/hotspot')">查看趋势</el-button>
    </div>

    <div class="hotspot-card__summary">
      <article class="hotspot-card__summary-item is-primary">
        <span>新闻总量</span>
        <strong>{{ totalNews }}</strong>
      </article>
      <article class="hotspot-card__summary-item is-danger">
        <span>谣言总量</span>
        <strong>{{ totalFake }}</strong>
      </article>
      <article class="hotspot-card__summary-item is-info">
        <span>更新时间</span>
        <strong>{{ updatedAt }}</strong>
      </article>
    </div>

    <div class="hotspot-card__list">
      <article v-for="item in provinces" :key="item.province" class="hotspot-card__item">
        <div>
          <strong>{{ item.province }}</strong>
          <p>谣言 {{ item.fake_count }} / 总量 {{ item.total }}</p>
        </div>
        <el-progress :percentage="item.fake_ratio" :stroke-width="10" color="var(--tech-color-danger)" />
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
defineEmits<{
  navigate: [path: string]
}>()

defineProps<{
  totalNews: number
  totalFake: number
  updatedAt: string
  provinces: Array<{ province: string; total: number; fake_count: number; fake_ratio: number }>
}>()
</script>

<style scoped lang="scss">
.hotspot-card {
  height: 100%;
  padding: 22px;
  border: 1px solid var(--app-border-default);
  border-radius: 28px;
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
}

.hotspot-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.hotspot-card__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.hotspot-card__header h3,
.hotspot-card__item p {
  margin: 0;
}

.hotspot-card__summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.hotspot-card__summary-item,
.hotspot-card__item {
  padding: 14px;
  border-radius: 18px;
  border: 1px solid var(--app-border-default);
  background: color-mix(in srgb, var(--app-surface-card) 92%, white 8%);
}

.hotspot-card__summary-item.is-primary {
  background: color-mix(in srgb, var(--app-accent-primary-soft) 48%, white 52%);
  border-color: color-mix(in srgb, var(--tech-color-primary) 20%, transparent);
}

.hotspot-card__summary-item.is-danger {
  background: color-mix(in srgb, var(--app-status-danger-soft) 58%, white 42%);
  border-color: color-mix(in srgb, var(--tech-color-danger) 24%, transparent);
}

.hotspot-card__summary-item.is-info {
  background: color-mix(in srgb, var(--app-status-info-soft) 48%, white 52%);
  border-color: color-mix(in srgb, var(--tech-color-info) 20%, transparent);
}

.hotspot-card__summary-item span,
.hotspot-card__item p {
  color: var(--app-text-secondary);
  font-size: 12px;
}

.hotspot-card__summary-item strong {
  display: block;
  margin-top: 8px;
  font-size: 20px;
}

.hotspot-card__summary-item.is-primary strong {
  color: var(--tech-color-primary-strong);
}

.hotspot-card__summary-item.is-danger strong {
  color: var(--tech-text-danger);
}

.hotspot-card__summary-item.is-info strong {
  color: var(--tech-color-info);
}

.hotspot-card__list {
  display: grid;
  gap: 12px;
}

.hotspot-card__item {
  display: grid;
  gap: 10px;
  border-color: color-mix(in srgb, var(--tech-color-danger) 18%, transparent);
}

.hotspot-card__item strong {
  color: var(--tech-text-danger);
}

@media (max-width: 900px) {
  .hotspot-card__summary {
    grid-template-columns: 1fr;
  }
}
</style>
