<template>
  <section class="stats-section tech-panel" data-reveal>
    <article
      v-for="item in items"
      :key="item.title"
      class="stats-section__item"
      data-reveal
      data-reveal-origin="bottom"
    >
      <strong>{{ item.value }}</strong>
      <h3>{{ item.title }}</h3>
      <p>{{ item.description }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
const items = [
  {
    value: 'Deep',
    title: '深度学习技术',
    description: '采用深度学习分析链路，对复杂文本与多模态内容进行高精度识别。',
  },
  {
    value: 'Fusion',
    title: '多模态融合',
    description: '整合文本、图像、传播轨迹与用户协同反馈，形成统一判断视图。',
  },
  {
    value: 'Graph',
    title: '知识图谱',
    description: '以实体与关系网络承接旧版知识能力，强化深度解析与检索效率。',
  },
  {
    value: 'RealTime',
    title: '实时分析引擎',
    description: '支持快速响应和持续更新，让门户首页也能呈现稳定的实时感。',
  },
]
</script>

<style scoped lang="scss">
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  overflow: hidden;
  padding: 0;
  background: rgba(124, 231, 255, 0.08);
}

.stats-section__item {
  display: flex;
  min-height: 220px;
  flex-direction: column;
  gap: 12px;
  padding: 28px 24px;
  background: rgba(8, 19, 32, 0.92);
  transition: transform var(--tech-duration-base) var(--tech-ease-out), background var(--tech-duration-base) var(--tech-ease-out);
}

.stats-section__item:hover {
  transform: translateY(-4px);
  background: rgba(12, 26, 40, 0.96);
}

.stats-section__item strong {
  color: #7ce7ff;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.stats-section__item h3 {
  margin: 0;
  color: #f5fbff;
  font-size: 20px;
}

.stats-section__item p {
  margin: 0;
  color: rgba(216, 232, 244, 0.7);
  line-height: 1.72;
}

@media (max-width: 1100px) {
  .stats-section {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .stats-section__item {
    min-height: 180px;
  }
}
</style>
