<template>
  <section class="hero-section" data-reveal data-reveal-origin="scale">
    <img class="hero-section__image" src="/home.png" alt="数字安全盾主视觉" />

    <div class="hero-section__backdrop" aria-hidden="true" />
    <div class="hero-section__vignette" aria-hidden="true" />
    <div class="hero-section__core-glow" aria-hidden="true" />

    <div class="hero-section__brand">
      <p class="hero-section__eyebrow">FraudShield / Anti-Fraud Intelligence Console</p>
      <h1 class="hero-section__title">
        多模态反诈
        <span>智能体中枢</span>
      </h1>
      <p class="hero-section__tagline">感知 · 决策 · 干预 · 进化</p>
      <p class="hero-section__description">
        面向文本、语音、图像与知识检索场景的统一反诈中枢，聚焦高风险诈骗话术识别、实时预警联动与智能决策辅助。
      </p>
      <div class="hero-section__stages" aria-label="智能体闭环能力">
        <article>
          <strong>01 感知</strong>
          <span>统一接入文本、语音、图像与截图</span>
        </article>
        <article>
          <strong>02 决策</strong>
          <span>结合 RAG 检索与诈骗剧本识别输出风险结论</span>
        </article>
        <article>
          <strong>03 干预</strong>
          <span>联动预警提示、监护人通知与处置建议</span>
        </article>
        <article>
          <strong>04 进化</strong>
          <span>新案例审核入库，持续扩充反诈知识图谱</span>
        </article>
      </div>
      <div class="hero-section__chips" aria-label="核心能力标签">
        <span>文本 / 语音 / 视觉</span>
        <span>RAG 反诈知识助手</span>
        <span>实时预警联动</span>
      </div>
      <div class="hero-section__actions">
        <el-button type="primary" size="large" @click="emit('primary')">进入专项分析</el-button>
        <el-button size="large" plain @click="emit('secondary')">查看风险看板</el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  primary: []
  secondary: []
}>()
</script>

<style scoped lang="scss">
.hero-section {
  position: relative;
  overflow: hidden;
  height: 100%;
  min-height: calc(100vh - 72px);
  background: linear-gradient(180deg, rgba(3, 8, 16, 0.98), rgba(1, 4, 10, 1));
}

.hero-section__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
  pointer-events: none;
}

.hero-section__backdrop,
.hero-section__vignette,
.hero-section__core-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-section__backdrop {
  background:
    linear-gradient(90deg, rgba(0, 0, 0, 0.72) 0%, rgba(2, 9, 18, 0.42) 22%, rgba(0, 0, 0, 0.12) 48%, rgba(0, 0, 0, 0.2) 74%, rgba(0, 0, 0, 0.66) 100%),
    linear-gradient(180deg, rgba(0, 0, 0, 0.08) 0%, rgba(0, 0, 0, 0.28) 100%);
  z-index: 2;
}

.hero-section__vignette {
  background: radial-gradient(circle at center, rgba(0, 0, 0, 0) 38%, rgba(0, 0, 0, 0.56) 100%);
  z-index: 3;
}

.hero-section__core-glow {
  inset: 8% 18%;
  background: radial-gradient(circle at center, rgba(92, 255, 225, 0.12) 0%, rgba(36, 170, 255, 0.08) 22%, rgba(0, 0, 0, 0) 60%);
  filter: blur(24px);
  z-index: 2;
}

.hero-section__brand {
  position: absolute;
  top: 50%;
  left: clamp(28px, 6vw, 92px);
  z-index: 5;
  width: min(620px, calc(100vw - 120px));
  transform: translateY(-54%);
  display: grid;
  gap: 16px;
  padding: 0;
}

.hero-section__eyebrow {
  margin: 0;
  color: rgba(125, 238, 255, 0.88);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.hero-section__title {
  margin: 0;
  color: #f3fbff;
  font-size: clamp(38px, 5.4vw, 68px);
  line-height: 0.98;
  letter-spacing: 0.02em;
  text-shadow: 0 10px 34px rgba(3, 12, 28, 0.46);
  display: grid;
  gap: 6px;
}

.hero-section__title span {
  color: rgba(131, 241, 255, 0.98);
}

.hero-section__tagline {
  margin: 0;
  color: rgba(148, 235, 255, 0.92);
  font-size: clamp(16px, 2vw, 22px);
  font-weight: 600;
  letter-spacing: 0.12em;
}

.hero-section__description {
  margin: 0;
  color: rgba(218, 240, 255, 0.9);
  font-size: clamp(14px, 1.4vw, 17px);
  line-height: 1.72;
  max-width: 52ch;
  text-shadow: 0 8px 28px rgba(2, 10, 22, 0.32);
}

.hero-section__stages {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.hero-section__stages article {
  display: grid;
  gap: 6px;
  padding: 14px 16px;
  border: 1px solid rgba(124, 231, 255, 0.12);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(5, 18, 36, 0.4), rgba(4, 14, 28, 0.18));
  box-shadow: inset 0 1px 0 rgba(224, 247, 255, 0.04);
  backdrop-filter: blur(10px);
}

.hero-section__stages strong {
  color: #f4fbff;
  font-size: 14px;
  letter-spacing: 0.04em;
}

.hero-section__stages span {
  color: rgba(206, 231, 247, 0.82);
  font-size: 13px;
  line-height: 1.55;
}

.hero-section__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-section__chips span {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 8px 14px;
  border: 1px solid rgba(124, 231, 255, 0.16);
  border-radius: 999px;
  background: rgba(6, 20, 40, 0.22);
  color: rgba(231, 247, 255, 0.92);
  font-size: 13px;
  letter-spacing: 0.04em;
  box-shadow: 0 10px 24px rgba(1, 8, 18, 0.16);
}

.hero-section__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.hero-section__actions :deep(.el-button) {
  min-width: 160px;
  min-height: 46px;
  border-radius: 999px;
  box-shadow: 0 12px 36px rgba(3, 10, 25, 0.4);
}

.hero-section__actions :deep(.el-button--primary) {
  background: linear-gradient(135deg, rgba(40, 200, 180, 0.85), rgba(50, 140, 255, 0.85));
  border-color: rgba(100, 255, 220, 0.3);
}

.hero-section__actions :deep(.el-button.is-plain) {
  border-color: rgba(124, 231, 255, 0.24);
  background: rgba(11, 28, 46, 0.52);
  color: rgba(200, 240, 255, 0.9);
}

@media (max-width: 640px) {
  .hero-section__brand {
    top: 88px;
    left: 20px;
    width: min(100vw - 40px, 620px);
    transform: none;
    gap: 12px;
  }

  .hero-section__description {
    max-width: none;
  }

  .hero-section__stages {
    grid-template-columns: 1fr;
  }

  .hero-section__chips span {
    min-height: 32px;
    padding: 6px 12px;
    font-size: 12px;
  }

  .hero-section__actions {
    flex-direction: column;
    width: min(100%, 280px);
  }

  .hero-section__actions :deep(.el-button) {
    width: 100%;
  }
}
</style>
