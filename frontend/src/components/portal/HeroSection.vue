<template>
  <section class="hero-section" data-reveal data-reveal-origin="scale">
    <img class="hero-section__image" src="/home.png" alt="数字安全盾主视觉" />

    <div class="hero-section__backdrop" aria-hidden="true" />
    <div class="hero-section__vignette" aria-hidden="true" />
    <div class="hero-section__core-glow" aria-hidden="true" />

    <div class="hero-section__actions">
      <el-button type="primary" size="large" @click="emit('primary')">开始风险分析</el-button>
      <el-button size="large" plain @click="emit('secondary')">查看风险看板</el-button>
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
  object-fit: contain;
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
    linear-gradient(90deg, rgba(0, 0, 0, 0.66) 0%, rgba(0, 0, 0, 0.08) 26%, rgba(0, 0, 0, 0.08) 74%, rgba(0, 0, 0, 0.66) 100%),
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

.hero-section__actions {
  position: absolute;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 5;
  display: flex;
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
  .hero-section__actions {
    flex-direction: column;
    width: min(100%, 280px);
    bottom: 20px;
  }

  .hero-section__actions :deep(.el-button) {
    width: 100%;
  }
}
</style>


