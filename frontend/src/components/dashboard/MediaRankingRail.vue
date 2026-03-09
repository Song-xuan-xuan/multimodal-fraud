<template>
  <section class="media-rail tech-panel">
    <div class="media-rail__header">
      <div>
        <p class="media-rail__eyebrow">媒体分布</p>
        <h3>传播平台排行</h3>
      </div>
      <el-button text type="primary" @click="$emit('navigate', '/news')">查看资讯池</el-button>
    </div>

    <div class="media-rail__list">
      <article v-for="item in items" :key="item.name" class="media-rail__item">
        <div class="media-rail__title">
          <span class="media-rail__rank">{{ item.rank }}</span>
          <div>
            <strong>{{ item.name }}</strong>
            <p>{{ item.description }}</p>
          </div>
        </div>
        <div class="media-rail__metric">
          <strong>{{ item.value }}</strong>
          <span>{{ item.share }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
defineEmits<{
  navigate: [path: string]
}>()

defineProps<{
  items: Array<{ rank: string; name: string; description: string; value: number; share: string }>
}>()
</script>

<style scoped lang="scss">
.media-rail {
  height: 100%;
  padding: 20px;
}

.media-rail__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.media-rail__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.media-rail__header h3 {
  margin: 0;
}

.media-rail__list {
  display: grid;
  gap: 12px;
}

.media-rail__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px;
  border-radius: var(--tech-radius-sm);
  background: color-mix(in srgb, var(--tech-color-primary-soft) 28%, rgba(255, 255, 255, 0.04));
  border: 1px solid color-mix(in srgb, var(--tech-color-primary) 18%, transparent);
}

.media-rail__item:first-child {
  background: color-mix(in srgb, var(--tech-color-primary-soft) 40%, rgba(255, 255, 255, 0.04));
  box-shadow: var(--tech-theme-glow-soft);
}

.media-rail__title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.media-rail__rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--tech-color-primary-soft) 100%, transparent);
  color: var(--tech-color-primary-strong);
  font-size: 12px;
}

.media-rail__title p,
.media-rail__metric span {
  margin: 4px 0 0;
  color: var(--tech-text-secondary);
  font-size: 12px;
}

.media-rail__metric {
  text-align: right;
}

.media-rail__metric strong {
  color: var(--tech-color-primary-strong);
}
</style>
