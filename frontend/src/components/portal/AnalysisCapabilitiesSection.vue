<template>
  <section id="analysis-capabilities" class="portal-section" data-reveal>
    <div class="portal-section__heading">
      <p class="portal-section__eyebrow">知真系统 · 深度分析能力</p>
      <h2>将旧版深度分析板块映射到现有工作流</h2>
      <p>保留聚合分析、聚合搜索、多智搜证与层级洞察的分区表达，并把跳转统一接入现有 Vue 路由。</p>
    </div>

    <div class="analysis-grid">
      <article
        v-for="item in items"
        :key="item.title"
        class="analysis-card tech-panel"
        data-reveal
        data-reveal-origin="scale"
        @click="emit('navigate', item.route)"
      >
        <div class="analysis-card__header">
          <span>{{ item.serial }}</span>
          <strong>{{ item.kicker }}</strong>
        </div>
        <h3>{{ item.title }}</h3>
        <p>{{ item.description }}</p>
        <ul>
          <li v-for="feature in item.features" :key="feature">{{ feature }}</li>
        </ul>
        <button class="analysis-card__action">立即体验</button>
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
    serial: '01',
    kicker: 'Aggregation',
    title: '聚合分析',
    description: '对应旧版新闻聚合分析入口，聚焦多源线索整合、分析报告与可视化输出。',
    route: '/insight/hotspot',
    features: ['多源数据整合', '热点趋势分析', '可视化研判'],
  },
  {
    serial: '02',
    kicker: 'Search Fusion',
    title: '聚合搜索',
    description: '通过知识网络与热点追踪路径重组旧版一站式搜索体验。',
    route: '/insight/knowledge-graph',
    features: ['多平台线索汇聚', '关联节点检索', '高价值信息排序'],
  },
  {
    serial: '03',
    kicker: 'Multi-Agent',
    title: '多智搜证',
    description: '映射至 Agent 工作流，面向复杂事件的多智能体协同搜证。',
    route: '/ai/agent',
    features: ['多智能体协作', '线索编排', '证据链补全'],
  },
  {
    serial: '04',
    kicker: 'Hierarchy',
    title: '层级分析',
    description: '结合众包看板与事实核查链路，承接旧版层级分析的深挖能力。',
    route: '/evidence/crowd-board',
    features: ['层级拆解', '关联传播节点', '多人协同验证'],
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

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.analysis-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 308px;
  padding: 24px;
  cursor: pointer;
  background:
    radial-gradient(circle at top right, rgba(76, 201, 255, 0.12), transparent 28%),
    linear-gradient(180deg, rgba(9, 21, 35, 0.92), rgba(6, 14, 25, 0.96));
  transition: transform var(--tech-duration-base) var(--tech-ease-out), box-shadow var(--tech-duration-base) var(--tech-ease-out), border-color var(--tech-duration-base) var(--tech-ease-out);
}

.analysis-card:hover {
  transform: translateY(-6px);
  border-color: rgba(124, 231, 255, 0.26);
  box-shadow: 0 18px 40px rgba(4, 12, 24, 0.44), 0 0 24px rgba(124, 231, 255, 0.12);
}

.analysis-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.analysis-card__header span {
  display: inline-flex;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(124, 231, 255, 0.3), rgba(93, 139, 255, 0.18));
  color: #f5fbff;
  font-weight: 700;
}

.analysis-card__header strong {
  color: rgba(124, 231, 255, 0.86);
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.analysis-card h3 {
  margin: 0;
  font-size: 28px;
  color: #f5fbff;
}

.analysis-card p,
.analysis-card li {
  color: rgba(216, 232, 244, 0.74);
  line-height: 1.7;
}

.analysis-card ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 18px;
}

.analysis-card__action {
  margin-top: auto;
  align-self: flex-start;
  border: none;
  background: transparent;
  color: #7ce7ff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 860px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}
</style>
