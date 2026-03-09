<template>
  <el-card shadow="never" class="filter-panel">
    <template #header>
      <div class="panel-header">
        <div>
          <h3 class="panel-title">筛选条件</h3>
          <p class="panel-description">按关键词、平台、标签与传播特征快速缩小结果范围。</p>
        </div>
        <div class="panel-actions">
          <el-button @click="$emit('reset')">重置</el-button>
          <el-button type="primary" :loading="loading" @click="$emit('apply')">应用筛选</el-button>
        </div>
      </div>
    </template>

    <div class="filter-grid">
      <div class="field field-keyword">
        <label class="field-label">搜索新闻</label>
        <el-input
          :model-value="modelValue.keyword"
          placeholder="输入标题、摘要或关键词"
          clearable
          @update:model-value="updateField('keyword', $event)"
          @keyup.enter="$emit('apply')"
        />
      </div>

      <div class="field">
        <label class="field-label">平台</label>
        <el-select
          :model-value="modelValue.platform"
          placeholder="所有平台"
          clearable
          @update:model-value="updateField('platform', $event || '')"
        >
          <el-option v-for="platform in options.platforms" :key="platform" :label="platform" :value="platform" />
        </el-select>
      </div>

      <div class="field">
        <label class="field-label">标签</label>
        <el-select
          :model-value="modelValue.label"
          placeholder="所有标签"
          clearable
          @update:model-value="updateField('label', $event || '')"
        >
          <el-option v-for="label in options.labels" :key="label" :label="label" :value="label" />
        </el-select>
      </div>

      <div class="field">
        <label class="field-label">最小风险度</label>
        <el-input
          :model-value="modelValue.minCredibility"
          placeholder="0-100"
          clearable
          @update:model-value="updateField('minCredibility', sanitizeRange($event))"
        />
      </div>

      <div class="field">
        <label class="field-label">最大风险度</label>
        <el-input
          :model-value="modelValue.maxCredibility"
          placeholder="0-100"
          clearable
          @update:model-value="updateField('maxCredibility', sanitizeRange($event))"
        />
      </div>

      <div class="field">
        <label class="field-label">传播平台</label>
        <el-select
          :model-value="modelValue.propagationPlatform"
          placeholder="所有传播平台"
          clearable
          @update:model-value="updateField('propagationPlatform', $event || '')"
        >
          <el-option
            v-for="platform in options.propagationPlatforms"
            :key="platform"
            :label="platform"
            :value="platform"
          />
        </el-select>
      </div>

      <div class="field">
        <label class="field-label">开始日期</label>
        <el-date-picker
          :model-value="toDate(modelValue.startDate)"
          type="date"
          placeholder="开始日期"
          value-format="YYYY-MM-DD"
          @update:model-value="updateField('startDate', $event || '')"
        />
      </div>

      <div class="field">
        <label class="field-label">结束日期</label>
        <el-date-picker
          :model-value="toDate(modelValue.endDate)"
          type="date"
          placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @update:model-value="updateField('endDate', $event || '')"
        />
      </div>

      <div class="field">
        <label class="field-label">每页数量</label>
        <el-select
          :model-value="modelValue.perPage"
          @update:model-value="updateField('perPage', Number($event) || 20)"
        >
          <el-option v-for="value in options.perPageOptions" :key="value" :label="`${value} 条/页`" :value="value" />
        </el-select>
      </div>

      <div class="field field-switch">
        <label class="field-label">自动应用</label>
        <el-switch
          :model-value="modelValue.autoApply"
          inline-prompt
          active-text="开"
          inactive-text="关"
          @update:model-value="handleAutoApplyChange"
        />
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { NewsListFilters, NewsListOptionSets } from '@/types/newsList'

const props = defineProps<{
  modelValue: NewsListFilters
  options: NewsListOptionSets
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: NewsListFilters]
  apply: []
  reset: []
}>()

function updateField<K extends keyof NewsListFilters>(key: K, value: NewsListFilters[K]) {
  const next = {
    ...props.modelValue,
    [key]: value,
  }
  emit('update:modelValue', next)
  if (next.autoApply && key !== 'autoApply') {
    emit('apply')
  }
}

function handleAutoApplyChange(value: string | number | boolean) {
  const enabled = Boolean(value)
  emit('update:modelValue', {
    ...props.modelValue,
    autoApply: enabled,
  })
  if (enabled) {
    emit('apply')
  }
}

function sanitizeRange(value: string | number) {
  const text = String(value || '').replace(/[^\d.]/g, '')
  if (!text) return ''
  const numeric = Number(text)
  if (!Number.isFinite(numeric)) return ''
  return String(Math.min(Math.max(numeric, 0), 100))
}

function toDate(value: string) {
  return value || undefined
}
</script>

<style scoped>
.filter-panel {
  border: 1px solid var(--tech-border-color);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--tech-text-primary);
}

.panel-description {
  margin: 6px 0 0;
  color: var(--tech-text-secondary);
  font-size: 13px;
}

.panel-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}

.field {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-keyword {
  grid-column: span 6;
}

.field-switch {
  justify-content: flex-end;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-secondary);
}

@media (max-width: 1024px) {
  .field,
  .field-keyword {
    grid-column: span 6;
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
  }

  .field,
  .field-keyword {
    grid-column: span 12;
  }
}
</style>

