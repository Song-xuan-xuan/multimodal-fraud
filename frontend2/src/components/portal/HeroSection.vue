<template>
  <section class="hero-section" data-reveal data-reveal-origin="scale">
    <img class="hero-section__image" src="/home.png" alt="反诈情报主视觉" />
    <div class="hero-section__wash" aria-hidden="true" />
    <div class="hero-section__grid" aria-hidden="true" />

    <div class="hero-section__shell">
      <div class="hero-section__brief">
        <p class="hero-section__eyebrow">FraudShield Dossier / Anti-Fraud Intelligence Portal</p>
        <div class="hero-section__heading">
          <span class="hero-section__kicker">证据卷宗 + 风险警戒</span>
          <h1>多模态反诈情报中枢</h1>
          <p>
            用统一入口承接风险识别、案例检索、协同研判与治理流转，让首页首先像可审阅的反诈档案馆，而不是悬浮科技广告板。
          </p>
        </div>

        <div class="hero-section__actions">
          <el-button type="primary" size="large" @click="emit('primary')">进入专项分析</el-button>
          <el-button size="large" plain @click="emit('secondary')">查看风险看板</el-button>
        </div>

        <div class="hero-section__capsules" aria-label="核心能力标签">
          <span>文本 / 语音 / 图像统一研判</span>
          <span>案例回溯与证据固化</span>
          <span>治理流转与风险复核</span>
        </div>
      </div>

      <div class="hero-section__board">
        <article class="hero-section__board-card hero-section__board-card--alert">
          <div class="hero-section__card-head">
            <span>今日提醒</span>
            <strong>高优先级</strong>
          </div>
          <p>重点查看热点省域、待复核线索与专项分析入口，确保前台情报与后台治理在同一条卷宗链路内协作。</p>
        </article>

        <div class="hero-section__stages" aria-label="情报工作流">
          <article>
            <strong>01 收集</strong>
            <span>接入文本、截图、语音与外部线索。</span>
          </article>
          <article>
            <strong>02 研判</strong>
            <span>结合模型检测与案例检索给出风险结论。</span>
          </article>
          <article>
            <strong>03 处置</strong>
            <span>沉淀预警、上报、复核与工作台任务。</span>
          </article>
          <article>
            <strong>04 归档</strong>
            <span>把新样本纳入知识库与治理闭环。</span>
          </article>
        </div>

        <article class="hero-section__board-card hero-section__board-card--timeline">
          <div class="hero-section__card-head">
            <span>入口分层</span>
            <strong>门户 / 工具 / 后台</strong>
          </div>
          <ul>
            <li>
              <span>门户</span>
              <small>品牌可信度、入口说明与实时快报</small>
            </li>
            <li>
              <span>专项分析</span>
              <small>文本、图像、语音与事实核验工具流</small>
            </li>
            <li>
              <span>治理后台</span>
              <small>风险看板、案例库与审核工作台</small>
            </li>
          </ul>
        </article>
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
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--app-surface-page) 94%, white 6%) 0%, var(--app-surface-canvas) 100%),
    var(--app-surface-page);
}

.hero-section__image,
.hero-section__wash,
.hero-section__grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-section__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  opacity: 0.2;
  filter: saturate(0.65) sepia(0.12);
}

.hero-section__wash {
  background:
    linear-gradient(90deg, rgba(243, 239, 231, 0.98) 0%, rgba(243, 239, 231, 0.82) 42%, rgba(243, 239, 231, 0.5) 100%),
    radial-gradient(circle at top right, color-mix(in srgb, var(--app-status-danger) 10%, transparent), transparent 34%),
    radial-gradient(circle at bottom left, color-mix(in srgb, var(--app-accent-primary) 10%, transparent), transparent 28%);
}

.hero-section__grid {
  background:
    linear-gradient(90deg, transparent 0 11.8%, rgba(31, 41, 51, 0.045) 11.8% 12%, transparent 12% 24%),
    linear-gradient(180deg, transparent 0 11.8%, rgba(31, 41, 51, 0.035) 11.8% 12%, transparent 12% 24%);
  background-size: 220px 220px;
  opacity: 0.18;
}

.hero-section__shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 28px;
  align-items: stretch;
  width: min(1480px, calc(100vw - 48px));
  min-height: 100%;
  margin: 0 auto;
  padding: 56px 0 36px;
}

.hero-section__brief,
.hero-section__board-card,
.hero-section__stages article {
  border: 1px solid var(--app-border-default);
  background: color-mix(in srgb, var(--app-surface-elevated) 92%, white 8%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
}

.hero-section__brief {
  display: grid;
  align-content: center;
  gap: 22px;
  padding: clamp(28px, 5vw, 52px);
  border-radius: 34px;
}

.hero-section__eyebrow,
.hero-section__kicker,
.hero-section__card-head span,
.hero-section__stages strong,
.hero-section__timeline li span {
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero-section__eyebrow {
  margin: 0;
  color: var(--app-text-secondary);
  font-size: 12px;
  font-weight: 700;
}

.hero-section__heading {
  display: grid;
  gap: 14px;
}

.hero-section__kicker {
  color: var(--app-text-danger);
  font-size: 12px;
  font-weight: 700;
}

.hero-section__heading h1 {
  margin: 0;
  color: var(--app-text-primary);
  font-size: clamp(42px, 6vw, 72px);
  line-height: 0.94;
}

.hero-section__heading p {
  max-width: 56ch;
  margin: 0;
  color: var(--app-text-secondary);
  font-size: clamp(15px, 1.4vw, 18px);
  line-height: 1.7;
}

.hero-section__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.hero-section__actions :deep(.el-button) {
  min-width: 168px;
  min-height: 46px;
  border-radius: 999px;
}

.hero-section__actions :deep(.el-button--primary) {
  border-color: color-mix(in srgb, var(--app-status-danger) 26%, transparent);
  background: linear-gradient(135deg, color-mix(in srgb, var(--app-status-danger) 92%, white 8%), color-mix(in srgb, var(--app-accent-primary) 76%, white 24%));
  box-shadow: 0 14px 30px rgba(185, 76, 58, 0.16);
}

.hero-section__actions :deep(.el-button.is-plain) {
  border-color: var(--app-border-strong);
  background: var(--app-surface-card);
  color: var(--app-text-primary);
}

.hero-section__capsules {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-section__capsules span {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 8px 14px;
  border: 1px solid var(--app-border-default);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface-note) 76%, white 24%);
  color: var(--app-text-regular);
  font-size: 13px;
}

.hero-section__board {
  display: grid;
  gap: 16px;
  align-content: center;
}

.hero-section__board-card,
.hero-section__stages article {
  border-radius: 28px;
}

.hero-section__board-card {
  display: grid;
  gap: 12px;
  padding: 22px;
}

.hero-section__board-card--alert {
  background: linear-gradient(180deg, color-mix(in srgb, var(--app-status-danger-soft) 58%, white 42%) 0%, var(--app-surface-elevated) 100%);
}

.hero-section__board-card--timeline {
  background: linear-gradient(180deg, color-mix(in srgb, var(--app-surface-note) 82%, white 18%) 0%, var(--app-surface-elevated) 100%);
}

.hero-section__card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.hero-section__card-head span {
  color: var(--app-text-secondary);
  font-size: 11px;
  font-weight: 700;
}

.hero-section__card-head strong {
  color: var(--app-text-danger);
  font-size: 14px;
}

.hero-section__board-card p,
.hero-section__timeline small {
  margin: 0;
  color: var(--app-text-secondary);
  line-height: 1.65;
}

.hero-section__stages {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.hero-section__stages article {
  display: grid;
  gap: 8px;
  padding: 18px;
}

.hero-section__stages strong {
  color: var(--app-text-primary);
  font-size: 12px;
  font-weight: 700;
}

.hero-section__stages span {
  color: var(--app-text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.hero-section__board-card ul {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.hero-section__board-card li {
  display: grid;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px dashed color-mix(in srgb, var(--app-border-default) 80%, transparent);
}

.hero-section__board-card li:first-child {
  padding-top: 0;
  border-top: none;
}

.hero-section__board-card li span {
  color: var(--app-text-primary);
  font-size: 12px;
  font-weight: 700;
}

@media (max-width: 1180px) {
  .hero-section__shell {
    grid-template-columns: 1fr;
    padding: 28px 0 24px;
  }

  .hero-section__board {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-content: stretch;
  }

  .hero-section__board-card--alert,
  .hero-section__board-card--timeline {
    min-height: 100%;
  }

  .hero-section__stages {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .hero-section__shell {
    width: calc(100vw - 16px);
    gap: 14px;
    padding-bottom: 18px;
  }

  .hero-section__brief,
  .hero-section__board-card,
  .hero-section__stages article {
    border-radius: 24px;
  }

  .hero-section__board,
  .hero-section__stages {
    grid-template-columns: 1fr;
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
