<template>
  <button type="button" class="rag-source-card" @click="openDetails">
    <div class="rag-source-card__meta">
      <el-tag size="small" effect="plain">{{ detail.type }}</el-tag>
      <el-tag v-if="source.metadata?.fraud_type" size="small" effect="plain" type="danger">
        {{ source.metadata.fraud_type }}
      </el-tag>
      <span class="rag-source-card__score">相关度 {{ (source.score * 100).toFixed(0) }}%</span>
    </div>
    <div class="rag-source-card__title">{{ detail.title }}</div>
    <div class="rag-source-card__text">{{ detail.summary }}</div>
    <div class="rag-source-card__footer">
      <span class="rag-source-card__source">{{ detail.sourceLabel }}</span>
      <span class="rag-source-card__hint">查看详情</span>
    </div>
  </button>

  <el-dialog
    v-model="dialogVisible"
    append-to-body
    align-center
    destroy-on-close
    class="rag-source-dialog"
    modal-class="rag-source-dialog-overlay"
    width="760px"
  >
    <template #header>
      <div class="rag-source-dialog__hero">
        <div class="rag-source-dialog__hero-copy">
          <span class="rag-source-dialog__eyebrow">参考资料</span>
          <h3 class="rag-source-dialog__title">{{ detail.title }}</h3>
          <p class="rag-source-dialog__subtitle">{{ detail.summary }}</p>
        </div>
        <div class="rag-source-dialog__hero-meta">
          <span class="rag-source-dialog__hero-score">相关度 {{ (source.score * 100).toFixed(0) }}%</span>
          <div class="rag-source-dialog__chips">
            <el-tag size="small" effect="plain">{{ detail.type }}</el-tag>
            <el-tag v-if="source.metadata?.fraud_type" size="small" effect="plain" type="danger">
              {{ source.metadata.fraud_type }}
            </el-tag>
            <el-tag v-if="detail.sourceLabel" size="small" effect="plain" type="info">
              {{ detail.sourceLabel }}
            </el-tag>
          </div>
        </div>
      </div>
    </template>

    <div class="rag-source-dialog__body tech-scrollbar">
      <section class="rag-source-dialog__section">
        <span class="rag-source-dialog__label">资料标识</span>
        <div class="rag-source-dialog__value-grid">
          <div class="rag-source-dialog__value-card">
            <span class="rag-source-dialog__value-key">ID</span>
            <span class="rag-source-dialog__value">{{ detail.id }}</span>
          </div>
          <div class="rag-source-dialog__value-card">
            <span class="rag-source-dialog__value-key">类型</span>
            <span class="rag-source-dialog__value">{{ detail.type }}</span>
          </div>
          <div class="rag-source-dialog__value-card">
            <span class="rag-source-dialog__value-key">来源</span>
            <span class="rag-source-dialog__value">{{ detail.sourceLabel }}</span>
          </div>
        </div>
      </section>

      <section class="rag-source-dialog__section">
        <span class="rag-source-dialog__label">摘要</span>
        <div class="rag-source-dialog__summary">
          {{ detail.summary }}
        </div>
      </section>

      <section class="rag-source-dialog__section">
        <span class="rag-source-dialog__label">正文</span>
        <div class="rag-source-dialog__content tech-scrollbar">
          {{ detail.content }}
        </div>
      </section>

      <section class="rag-source-dialog__section">
        <span class="rag-source-dialog__label">来源链接</span>
        <a
          v-if="isSourceLink"
          class="rag-source-dialog__link"
          :href="detail.source"
          target="_blank"
          rel="noreferrer"
        >
          {{ detail.source }}
        </a>
        <div v-else class="rag-source-dialog__source-text">{{ detail.source }}</div>
      </section>
    </div>

    <template #footer>
      <div class="rag-source-dialog__footer">
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button
          v-if="isSourceLink"
          type="primary"
          @click="openSourceLink"
        >
          打开来源
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { RagSource } from '@/types/rag'
import { parseRagSourceDetail } from '@/types/rag'

const props = defineProps<{
  source: RagSource
}>()

const dialogVisible = ref(false)
const detail = computed(() => parseRagSourceDetail(props.source))
const isSourceLink = computed(() => /^https?:\/\//i.test(detail.value.source))

function openDetails() {
  dialogVisible.value = true
}

function openSourceLink() {
  if (!isSourceLink.value) return
  window.open(detail.value.source, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped lang="scss">
.rag-source-card {
  width: 100%;
  margin-top: 6px;
  padding: 10px 12px;
  border: 1px solid var(--tech-theme-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 18%, transparent);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.rag-source-card:hover {
  border-color: color-mix(in srgb, var(--tech-color-brand-primary) 60%, var(--tech-theme-border));
  box-shadow: 0 12px 24px rgba(0, 173, 255, 0.12);
  transform: translateY(-1px);
}

.rag-source-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.rag-source-card__score {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.rag-source-card__title {
  color: var(--tech-theme-text-primary);
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}

.rag-source-card__text {
  color: var(--tech-theme-text-regular);
  line-height: 1.65;
  font-size: 12px;
}

.rag-source-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 10px;
}

.rag-source-card__source {
  min-width: 0;
  color: var(--tech-theme-text-secondary);
  font-size: 11px;
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rag-source-card__hint {
  display: inline-flex;
  flex-shrink: 0;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--tech-color-brand-primary);
}
</style>

<style lang="scss">
.rag-source-dialog-overlay.el-overlay {
  background:
    radial-gradient(circle at top, rgba(0, 213, 255, 0.14), transparent 30%),
    rgba(2, 8, 20, 0.74);
  backdrop-filter: blur(12px);
  animation: rag-overlay-in 0.28s ease-out;
}

.rag-source-dialog {
  max-width: min(760px, calc(100vw - 32px));
  margin: 0 auto;
}

.rag-source-dialog .el-dialog {
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--tech-color-brand-primary) 34%, var(--tech-theme-border));
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(6, 28, 62, 0.98), rgba(3, 18, 42, 0.98)),
    radial-gradient(circle at top right, rgba(0, 213, 255, 0.16), transparent 42%);
  box-shadow:
    0 32px 80px rgba(0, 0, 0, 0.38),
    0 0 0 1px rgba(85, 223, 255, 0.08);
  animation: rag-dialog-in 0.34s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.rag-source-dialog .el-dialog__header {
  margin-right: 0;
  padding: 0;
}

.rag-source-dialog .el-dialog__headerbtn {
  top: 18px;
  right: 18px;
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.rag-source-dialog .el-dialog__headerbtn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(90deg);
}

.rag-source-dialog .el-dialog__body {
  padding: 0;
}

.rag-source-dialog .el-dialog__footer {
  padding: 0;
}

.rag-source-dialog__hero {
  display: grid;
  gap: 18px;
  padding: 28px 28px 20px;
  border-bottom: 1px solid color-mix(in srgb, var(--tech-theme-border) 80%, transparent);
  background:
    linear-gradient(135deg, rgba(0, 184, 255, 0.12), transparent 46%),
    radial-gradient(circle at top right, rgba(0, 213, 255, 0.2), transparent 38%);
}

.rag-source-dialog__hero-copy {
  display: grid;
  gap: 8px;
}

.rag-source-dialog__eyebrow {
  color: var(--tech-color-brand-primary);
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.rag-source-dialog__title {
  margin: 0;
  color: var(--tech-theme-text-primary);
  font-size: 24px;
  line-height: 1.3;
}

.rag-source-dialog__subtitle {
  margin: 0;
  color: var(--tech-theme-text-secondary);
  line-height: 1.75;
}

.rag-source-dialog__hero-meta {
  display: grid;
  gap: 12px;
}

.rag-source-dialog__hero-score {
  color: var(--tech-theme-text-primary);
  font-size: 14px;
  font-weight: 600;
}

.rag-source-dialog__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.rag-source-dialog__body {
  display: grid;
  gap: 18px;
  max-height: min(64vh, 720px);
  padding: 24px 28px;
  overflow-y: auto;
}

.rag-source-dialog__section {
  display: grid;
  gap: 10px;
}

.rag-source-dialog__label {
  color: var(--tech-theme-text-secondary);
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.rag-source-dialog__value-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.rag-source-dialog__value-card,
.rag-source-dialog__summary,
.rag-source-dialog__content,
.rag-source-dialog__source-text,
.rag-source-dialog__link {
  border: 1px solid color-mix(in srgb, var(--tech-theme-border) 75%, transparent);
  border-radius: 14px;
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 16%, transparent);
}

.rag-source-dialog__value-card {
  display: grid;
  gap: 6px;
  padding: 14px 16px;
}

.rag-source-dialog__value-key {
  color: var(--tech-theme-text-secondary);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.rag-source-dialog__value {
  color: var(--tech-theme-text-primary);
  line-height: 1.6;
  word-break: break-word;
}

.rag-source-dialog__summary {
  padding: 14px 16px;
  color: var(--tech-theme-text-regular);
  line-height: 1.8;
}

.rag-source-dialog__content {
  max-height: 240px;
  overflow-y: auto;
  padding: 16px;
  color: var(--tech-theme-text-regular);
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.rag-source-dialog__link,
.rag-source-dialog__source-text {
  display: block;
  padding: 14px 16px;
  color: var(--tech-theme-text-regular);
  line-height: 1.7;
  word-break: break-all;
}

.rag-source-dialog__link {
  color: var(--tech-color-brand-primary);
  text-decoration: none;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.rag-source-dialog__link:hover {
  border-color: color-mix(in srgb, var(--tech-color-brand-primary) 58%, var(--tech-theme-border));
  box-shadow: 0 14px 32px rgba(0, 173, 255, 0.12);
  transform: translateY(-1px);
}

.rag-source-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 18px 28px 26px;
  border-top: 1px solid color-mix(in srgb, var(--tech-theme-border) 80%, transparent);
  background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.14));
}

@media (max-width: 768px) {
  .rag-source-dialog {
    max-width: calc(100vw - 20px);
  }

  .rag-source-dialog__hero,
  .rag-source-dialog__body,
  .rag-source-dialog__footer {
    padding-left: 18px;
    padding-right: 18px;
  }

  .rag-source-dialog__title {
    font-size: 20px;
  }

  .rag-source-dialog__value-grid {
    grid-template-columns: 1fr;
  }

  .rag-source-dialog__body {
    max-height: 68vh;
  }
}

@keyframes rag-dialog-in {
  0% {
    opacity: 0;
    transform: translateY(24px) scale(0.94);
  }

  60% {
    opacity: 1;
    transform: translateY(-4px) scale(1.01);
  }

  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes rag-overlay-in {
  0% {
    opacity: 0;
  }

  100% {
    opacity: 1;
  }
}
</style>
