<template>
  <section id="core-features" class="portal-section" data-reveal>
    <div class="portal-section__heading">
      <p class="portal-section__eyebrow">AuthentiAI · 核心功能</p>
      <h2>面向真实业务链路的检测入口</h2>
      <p>将旧版首页核心功能重构为清晰可达的能力卡，覆盖分类判别、AI 检测、智能问答与一致性分析。</p>
    </div>

    <div class="card-grid card-grid--four">
      <article
        v-for="item in items"
        :key="item.title"
        class="portal-card portal-card--feature tech-panel"
        data-reveal
        data-reveal-origin="bottom"
        @click="emit('navigate', item.route)"
      >
        <div class="portal-card__beam" :style="{ '--beam': item.glow }" />
        <div class="portal-card__visual" :style="{ '--accent': item.glow }">
          <span>{{ item.kicker }}</span>
        </div>
        <div class="portal-card__body">
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
          <div class="portal-card__tags">
            <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
        <button class="portal-card__action">立即进入</button>
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
    title: '新闻虚假判别',
    description: '快速对新闻文本进行真假分类与风险初筛，适合舆情研判前置筛查。',
    kicker: 'Classification',
    route: '/detection/classify',
    glow: 'rgba(124, 231, 255, 0.55)',
    tags: ['新闻判别', '快速筛查', '风险提示'],
  },
  {
    title: 'AI 生成检测',
    description: '识别 AI 生成文本与图像内容，辅助定位可疑生成痕迹。',
    kicker: 'AIGC Detect',
    route: '/detection/ai',
    glow: 'rgba(117, 150, 255, 0.52)',
    tags: ['文本识别', '图片分析', '实时检测'],
  },
  {
    title: '新闻分析助手',
    description: '通过对话方式整理线索、解释判断依据并协助拆解复杂疑点。',
    kicker: 'AI Assistant',
    route: '/ai/chat',
    glow: 'rgba(87, 238, 197, 0.46)',
    tags: ['智能问答', '辅助研判', '即时交互'],
  },
  {
    title: '新闻一致性检测',
    description: '支持多种输入方式对内容一致性与可信度进行综合分析。',
    kicker: 'Consistency',
    route: '/detection/news',
    glow: 'rgba(255, 166, 92, 0.44)',
    tags: ['多源输入', '一致性分析', '深度核验'],
  },
]
</script>

<style scoped lang="scss">
.portal-section {
  display: flex;
  flex-direction: column;
  gap: 56px;
  padding: 48px clamp(24px, 4vw, 40px);
  border-radius: 32px;
  background: linear-gradient(180deg, rgba(248, 251, 255, 0.98), rgba(240, 246, 255, 0.94));
  box-shadow: 0 24px 56px rgba(15, 23, 42, 0.08);
}

.portal-section__heading {
  max-width: 760px;
}

.portal-section__eyebrow {
  margin: 0 0 8px;
  color: #2674b8;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 700;
}

.portal-section__heading h2 {
  margin: 0;
  font-size: clamp(28px, 4vw, 40px);
  color: #10253d;
}

.portal-section__heading p:last-child {
  margin: 14px 0 0;
  color: #5d6b7b;
  line-height: 1.75;
}

.card-grid {
  display: grid;
  gap: 24px;
}

.card-grid--four {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.portal-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 360px;
  padding: 0;
  cursor: pointer;
  transition: transform var(--tech-duration-base) var(--tech-ease-out), box-shadow var(--tech-duration-base) var(--tech-ease-out), border-color var(--tech-duration-base) var(--tech-ease-out);
}

.portal-card:hover {
  transform: translateY(-6px);
  border-color: rgba(124, 231, 255, 0.26);
  box-shadow: 0 18px 40px rgba(4, 12, 24, 0.44), 0 0 24px rgba(124, 231, 255, 0.12);
}

.portal-card__beam {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top left, var(--beam), transparent 36%);
  opacity: 0.9;
  pointer-events: none;
}

.portal-card__visual {
  position: relative;
  min-height: 120px;
  padding: 22px;
  display: flex;
  align-items: flex-start;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.01)),
    linear-gradient(135deg, color-mix(in srgb, var(--accent) 26%, transparent), transparent 62%);
}

.portal-card__visual span {
  display: inline-flex;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(7, 18, 30, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(234, 244, 255, 0.86);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.portal-card__body {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 14px;
  padding: 22px;
}

.portal-card__body h3 {
  margin: 0;
  color: #f5fbff;
  font-size: 22px;
}

.portal-card__body p {
  margin: 0;
  color: rgba(214, 232, 244, 0.72);
  line-height: 1.72;
}

.portal-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.portal-card__tags span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(124, 231, 255, 0.12);
  color: rgba(225, 239, 248, 0.82);
  font-size: 12px;
}

.portal-card__action {
  margin: 0 22px 22px;
  align-self: flex-start;
  border: none;
  background: transparent;
  color: #7ce7ff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 1200px) {
  .portal-section {
    padding: 40px 28px;
  }

  .card-grid--four {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .portal-section {
    padding: 32px 20px;
    gap: 40px;
  }

  .card-grid--four {
    grid-template-columns: 1fr;
  }
}
</style>
