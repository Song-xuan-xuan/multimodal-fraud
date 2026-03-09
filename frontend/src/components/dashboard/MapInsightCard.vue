<template>
  <section class="map-card tech-panel">
    <div class="map-card__header">
      <div>
        <p class="map-card__eyebrow">态势地图</p>
        <h3>区域传播洞察</h3>
      </div>
      <el-button type="primary" plain @click="$emit('navigate', '/map')">进入全景地图</el-button>
    </div>

    <div class="map-card__body">
      <div class="map-card__canvas tech-surface">
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
  padding: 20px;
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
}

.map-card__body {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(220px, 0.8fr);
  gap: 16px;
}

.map-card__canvas {
  position: relative;
  min-height: 340px;
  overflow: hidden;
  padding: 18px;
  background:
    radial-gradient(circle at 40% 35%, color-mix(in srgb, var(--tech-color-primary) 18%, transparent), transparent 28%),
    radial-gradient(circle at 60% 60%, color-mix(in srgb, var(--tech-color-danger) 12%, transparent), transparent 24%),
    rgba(4, 12, 23, 0.72);
}

.map-card__province {
  position: absolute;
  display: grid;
  gap: 4px;
  min-width: 92px;
  padding: 10px 12px;
  border-radius: var(--tech-radius-sm);
  background: color-mix(in srgb, var(--tech-color-danger-soft) 52%, rgba(8, 19, 36, 0.92));
  border: 1px solid color-mix(in srgb, var(--tech-color-danger) 28%, transparent);
  box-shadow: var(--tech-theme-glow-soft);
}

.map-card__province span,
.map-card__metric span,
.map-card__metric small,
.map-card__legend small {
  color: var(--tech-text-secondary);
}

.map-card__province strong,
.map-card__metric strong {
  font-size: 22px;
  color: var(--tech-text-primary);
}

.map-card__province strong {
  color: var(--tech-text-danger);
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
  border-radius: var(--tech-radius-sm);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 36%, rgba(255, 255, 255, 0.04));
  border: 1px solid color-mix(in srgb, var(--tech-color-primary) 18%, transparent);
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
