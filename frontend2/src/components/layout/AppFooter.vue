<template>
  <footer class="app-footer">
    <div class="app-footer__inner">
      <div class="app-footer__summary">
        <p class="app-footer__eyebrow">FraudShield Archive</p>
        <strong>多模态反诈助手</strong>
        <p>聚合风险识别、案例检索、报告生成与协同治理能力，保持前台入口与后台工作流的一致视觉秩序。</p>
      </div>
      <div class="app-footer__links">
        <RouterLink to="/detection/ai">风险分析</RouterLink>
        <RouterLink to="/detection/news">内容风险检测</RouterLink>
        <RouterLink to="/ai/assistant">反诈助手</RouterLink>
        <RouterLink to="/dashboard">进入后台</RouterLink>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped lang="scss">
.app-footer {
  width: min(1680px, calc(100vw - 24px));
  margin: 0 auto 18px;
  border: 1px solid var(--app-border-default);
  border-radius: 28px;
  background: color-mix(in srgb, var(--app-surface-elevated) 92%, white 8%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.08);
  backdrop-filter: blur(10px);
}

.app-footer__inner {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  padding: 24px 28px;
  color: var(--app-text-secondary);
}

.app-footer__summary {
  display: grid;
  gap: 8px;
  max-width: 56ch;
}

.app-footer__eyebrow {
  margin: 0;
  color: var(--app-text-tertiary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.app-footer__inner strong {
  color: var(--app-text-primary);
}

.app-footer__inner p {
  margin: 0;
  line-height: 1.7;
}

.app-footer__links {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.app-footer__links a {
  color: var(--app-text-secondary);
  text-decoration: none;
  transition:
    color var(--tech-duration-fast) var(--tech-ease-out),
    border-color var(--tech-duration-fast) var(--tech-ease-out),
    background-color var(--tech-duration-fast) var(--tech-ease-out);
  padding: 8px 12px;
  border: 1px solid var(--app-border-default);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-surface-note) 72%, white 28%);
}

.app-footer__links a:hover,
.app-footer__links a:focus-visible {
  color: var(--app-text-primary);
  border-color: var(--app-border-strong);
  background: color-mix(in srgb, var(--app-surface-accent) 18%, white 82%);
  outline: none;
}

@media (max-width: 900px) {
  .app-footer {
    width: calc(100vw - 16px);
    margin-bottom: 12px;
  }

  .app-footer__inner {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
  }
}
</style>
