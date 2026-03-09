<template>
  <!-- <footer class="app-footer">
    <div class="app-footer__inner">
      <div>
        <strong>多模态反诈助手</strong>
        <p>聚合风险识别、案例检索、报告生成与协同治理能力。</p>
      </div>
      <div class="app-footer__links">
        <RouterLink to="/detection/ai">风险分析</RouterLink>
        <RouterLink to="/detection/news">内容风险检测</RouterLink>
        <RouterLink to="/ai/assistant">反诈助手</RouterLink>
        <RouterLink to="/dashboard">进入后台</RouterLink>
      </div>
    </div>
  </footer> -->
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped lang="scss">
.app-footer {
  border-top: 1px solid var(--tech-theme-border);
  background: linear-gradient(180deg, color-mix(in srgb, var(--tech-color-brand-cyan) 8%, transparent) 0%, var(--tech-theme-surface-glass-strong) 100%);
  box-shadow: 0 -8px 24px rgba(1, 8, 20, 0.18);
  backdrop-filter: blur(18px);
}

.app-footer__inner {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px 32px 32px;
  color: var(--tech-theme-text-secondary);
}

.app-footer__inner strong {
  color: var(--tech-theme-text-primary);
}

.app-footer__inner p {
  margin: 8px 0 0;
}

.app-footer__links {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.app-footer__links a {
  color: var(--tech-theme-text-brand);
  text-decoration: none;
  transition:
    color var(--tech-duration-fast) var(--tech-ease-out),
    text-shadow var(--tech-duration-fast) var(--tech-ease-out);
}

.app-footer__links a:hover,
.app-footer__links a:focus-visible {
  color: var(--tech-color-primary-strong);
  text-shadow: 0 0 18px color-mix(in srgb, var(--tech-color-primary) 28%, transparent);
  outline: none;
}
</style>


