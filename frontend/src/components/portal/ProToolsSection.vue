<template>
  <section id="pro-tools" class="portal-section" data-reveal>
    <div class="portal-section__heading">
      <p class="portal-section__eyebrow">知真系统 · 专业工具</p>
      <h2>保留旧版工具分区，同时对接当前产品入口</h2>
      <p>工具卡统一支持 hover glow 与清晰 CTA，既延续旧版科技风，也避免跳到已不存在的历史页面。</p>
    </div>

    <div class="tool-grid">
      <article
        v-for="item in items"
        :key="item.title"
        class="tool-card tech-panel"
        data-reveal
        @click="emit('navigate', item.route)"
      >
        <div class="tool-card__icon">{{ item.symbol }}</div>
        <h3>{{ item.title }}</h3>
        <ul>
          <li v-for="feature in item.features" :key="feature">{{ feature }}</li>
        </ul>
        <button class="tool-card__action">{{ item.cta }}</button>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  navigate: [route: string]
}>()

const items = [
  {
    title: '趋势分析',
    symbol: 'T',
    route: '/insight/hotspot',
    cta: '查看热点趋势',
    features: ['热点新闻追踪', '舆情波动观察', '传播路径研判'],
  },
  {
    title: '智能助手',
    symbol: 'A',
    route: '/ai/assistant',
    cta: '唤起智能助手',
    features: ['个性化建议', '新闻摘要整理', '任务协作支持'],
  },
  {
    title: '深度解析',
    symbol: 'D',
    route: '/fact-check',
    cta: '进入事实核查',
    features: ['图文内容核验', '文本证据分析', '链路结果沉淀'],
  },
]
</script>

<style scoped lang="scss">
.portal-section {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.portal-section__heading {
  max-width: 760px;
}

.portal-section__eyebrow {
  margin: 0 0 8px;
  color: rgba(124, 231, 255, 0.84);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 12px;
}

.portal-section__heading h2 {
  margin: 0;
  font-size: clamp(28px, 4vw, 40px);
  color: #f5fbff;
}

.portal-section__heading p:last-child {
  margin: 14px 0 0;
  color: rgba(216, 232, 244, 0.74);
  line-height: 1.75;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.tool-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 280px;
  padding: 24px;
  cursor: pointer;
  background:
    radial-gradient(circle at 15% 15%, rgba(124, 231, 255, 0.12), transparent 26%),
    linear-gradient(180deg, rgba(8, 20, 34, 0.92), rgba(6, 14, 24, 0.96));
  transition: transform var(--tech-duration-base) var(--tech-ease-out), box-shadow var(--tech-duration-base) var(--tech-ease-out), border-color var(--tech-duration-base) var(--tech-ease-out);
}

.tool-card:hover {
  transform: translateY(-6px);
  border-color: rgba(124, 231, 255, 0.26);
  box-shadow: 0 18px 40px rgba(4, 12, 24, 0.44), 0 0 24px rgba(124, 231, 255, 0.12);
}

.tool-card__icon {
  width: 56px;
  height: 56px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(124, 231, 255, 0.32), rgba(93, 139, 255, 0.2));
  color: #f5fbff;
  font-size: 24px;
  font-weight: 700;
}

.tool-card h3 {
  margin: 0;
  font-size: 24px;
  color: #f5fbff;
}

.tool-card ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 18px;
}

.tool-card li {
  color: rgba(216, 232, 244, 0.74);
  line-height: 1.7;
}

.tool-card__action {
  margin-top: auto;
  align-self: flex-start;
  border: none;
  background: transparent;
  color: #7ce7ff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 960px) {
  .tool-grid {
    grid-template-columns: 1fr;
  }
}
</style>
