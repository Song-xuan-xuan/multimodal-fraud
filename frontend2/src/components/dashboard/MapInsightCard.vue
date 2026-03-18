<template>
  <section class="map-card">
    <div class="map-card__header">
      <div>
        <p class="map-card__eyebrow">态势地图</p>
        <h3>区域传播洞察</h3>
      </div>
      <el-button type="primary" plain @click="$emit('navigate', '/map')">进入全景地图</el-button>
    </div>

    <div class="map-card__body">
      <div class="map-card__canvas">
        <div class="map-card__province" v-for="item in provinces" :key="item.province" :style="item.style">
          <span>{{ item.province }}</span>
          <strong>{{ item.fake_count }}</strong>
        </div>
        <div class="map-card__legend">
          <span>高风险省份分布</span>
          <small>点击进入地图查看明细</small>
        </div>
      </div>
      <div class="map-card__side">
        <article class="map-card__metric" v-for="metric in metrics" :key="metric.label">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <small>{{ metric.tip }}</small>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineEmits<{
  navigate: [path: string]
}>()

defineProps<{
  metrics: Array<{ label: string; value: string | number; tip: string }>
  provinces: Array<{ province: string; fake_count: number; style: Record<string, string> }>
}>()
</script>

<style scoped lang="scss">
.map-card {
  height: 100%;
  padding: 22px;
  border: 1px solid var(--app-border-default);
  border-radius: 28px;
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
}

.map-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.map-card__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.map-card__header h3 {
  margin: 0;
  color: var(--app-text-primary);
}

.map-card__body {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(220px, 0.8fr);
  gap: 16px;
}

.map-card__canvas,
.map-card__metric {
  border: 1px solid var(--app-border-default);
  border-radius: 22px;
  background: color-mix(in srgb, var(--app-surface-card) 92%, white 8%);
}

.map-card__canvas {
  position: relative;
  min-height: 340px;
  overflow: hidden;
  padding: 18px;
  background:
    radial-gradient(circle at 38% 34%, color-mix(in srgb, var(--app-accent-primary) 14%, transparent), transparent 28%),
    radial-gradient(circle at 64% 64%, color-mix(in srgb, var(--app-status-danger) 12%, transparent), transparent 22%),
    linear-gradient(180deg, color-mix(in srgb, var(--app-surface-note) 74%, white 26%) 0%, var(--app-surface-card) 100%);
}

.map-card__province {
  position: absolute;
  display: grid;
  gap: 4px;
  min-width: 92px;
  padding: 10px 12px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--app-status-danger-soft) 58%, white 42%);
  border: 1px solid color-mix(in srgb, var(--app-status-danger) 24%, transparent);
}

.map-card__province span,
.map-card__metric span,
.map-card__metric small,
.map-card__legend small {
  color: var(--app-text-secondary);
}

.map-card__province strong,
.map-card__metric strong {
  font-size: 22px;
  color: var(--app-text-primary);
}

.map-card__province strong {
  color: var(--app-text-danger);
}

.map-card__legend {
  position: absolute;
  left: 18px;
  bottom: 18px;
  display: grid;
  gap: 4px;
  color: var(--tech-color-primary-strong);
}

.map-card__side {
  display: grid;
  gap: 12px;
}

.map-card__metric {
  display: grid;
  gap: 6px;
  padding: 16px;
}

@media (max-width: 900px) {
  .map-card__body {
    grid-template-columns: 1fr;
  }

  .map-card__canvas {
    min-height: 300px;
  }
}
</style>
