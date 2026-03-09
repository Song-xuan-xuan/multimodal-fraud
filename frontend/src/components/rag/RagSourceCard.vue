<template>
  <el-popover
    placement="top-start"
    trigger="click"
    :width="420"
    popper-class="rag-source-card-popover"
    :teleported="false"
  >
    <template #reference>
      <button type="button" class="rag-source-card">
        <div class="rag-source-card__meta">
          <el-tag size="small" effect="plain">{{ detail.type }}</el-tag>
          <el-tag v-if="source.metadata?.fraud_type" size="small" effect="plain" type="danger">
            {{ source.metadata.fraud_type }}
          </el-tag>
          <span class="rag-source-card__score">相关度 {{ (source.score * 100).toFixed(0) }}%</span>
        </div>
        <div class="rag-source-card__title">{{ detail.title }}</div>
        <div class="rag-source-card__text">{{ previewText }}</div>
        <span class="rag-source-card__hint">点击查看详情</span>
      </button>
    </template>

    <div class="rag-source-detail-card">
      <div class="rag-source-detail-card__header">
        <span class="rag-source-detail-card__eyebrow">参考案例</span>
        <span class="rag-source-detail-card__score">相关度 {{ (source.score * 100).toFixed(0) }}%</span>
      </div>

      <div class="rag-source-detail-card__field">
        <span class="rag-source-detail-card__label">ID</span>
        <span class="rag-source-detail-card__value">{{ detail.id }}</span>
      </div>

      <div class="rag-source-detail-card__field">
        <span class="rag-source-detail-card__label">类型</span>
        <span class="rag-source-detail-card__value">{{ detail.type }}</span>
      </div>

      <div class="rag-source-detail-card__field">
        <span class="rag-source-detail-card__label">标题</span>
        <span class="rag-source-detail-card__value">{{ detail.title }}</span>
      </div>

      <div class="rag-source-detail-card__field rag-source-detail-card__field--content">
        <span class="rag-source-detail-card__label">内容</span>
        <div class="rag-source-detail-card__content tech-scrollbar">{{ detail.content }}</div>
      </div>

      <div class="rag-source-detail-card__field">
        <span class="rag-source-detail-card__label">来源</span>
        <span class="rag-source-detail-card__value rag-source-detail-card__value--source">{{ detail.source }}</span>
      </div>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RagSource } from '@/types/rag'
import { parseRagSourceDetail } from '@/types/rag'

const props = defineProps<{
  source: RagSource
}>()

const detail = computed(() => parseRagSourceDetail(props.source))
const previewText = computed(() => {
  const content = detail.value.content || props.source.text || ''
  if (content.length <= 120) return content
  return `${content.slice(0, 120)}...`
})
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

.rag-source-card__hint {
  display: inline-flex;
  margin-top: 8px;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--tech-color-brand-primary);
}

.rag-source-detail-card {
  display: grid;
  gap: 12px;
}

.rag-source-detail-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid color-mix(in srgb, var(--tech-theme-border) 80%, transparent);
}

.rag-source-detail-card__eyebrow {
  color: var(--tech-color-brand-primary);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.rag-source-detail-card__score {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.rag-source-detail-card__field {
  display: grid;
  gap: 6px;
}

.rag-source-detail-card__label {
  color: var(--tech-theme-text-secondary);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.rag-source-detail-card__value {
  color: var(--tech-theme-text-primary);
  line-height: 1.6;
  word-break: break-word;
}

.rag-source-detail-card__field--content {
  min-height: 0;
}

.rag-source-detail-card__content {
  max-height: 240px;
  overflow-y: auto;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--tech-theme-border) 75%, transparent);
  background: color-mix(in srgb, var(--tech-theme-surface-panel) 72%, black 28%);
  color: var(--tech-theme-text-regular);
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
}

.rag-source-detail-card__value--source {
  font-size: 12px;
  color: var(--tech-theme-text-regular);
}
</style>

<style lang="scss">
.rag-source-card-popover.el-popper {
  border: 1px solid color-mix(in srgb, var(--tech-color-brand-primary) 35%, var(--tech-theme-border));
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(7, 28, 61, 0.98), rgba(3, 18, 42, 0.98)),
    radial-gradient(circle at top right, rgba(0, 213, 255, 0.16), transparent 42%);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.36);
}

.rag-source-card-popover.el-popper .el-popper__arrow::before {
  background: rgba(6, 26, 57, 0.98);
  border: 1px solid color-mix(in srgb, var(--tech-color-brand-primary) 35%, var(--tech-theme-border));
}
</style>
