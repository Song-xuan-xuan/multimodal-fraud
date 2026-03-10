<template>
  <section class="guardian-action-card" :class="`guardian-action-card--${priority}`">
    <div class="guardian-action-card__header">
      <div>
        <h3>监护人联动建议</h3>
        <span>{{ priorityLabel }}</span>
      </div>
      <div class="guardian-action-card__actions">
        <el-button size="small" plain @click="copyNotice">复制通知内容</el-button>
        <el-button size="small" plain @click="copyChecklistSummary">复制处置摘要</el-button>
      </div>
    </div>

    <p class="guardian-action-card__notice">{{ action.notice }}</p>

    <div class="guardian-action-card__meta">
      <div class="guardian-action-card__meta-item">
        <span class="guardian-action-card__label">联动对象</span>
        <strong>{{ action.target_role || '监护人/家属' }}</strong>
      </div>
      <div class="guardian-action-card__meta-item">
        <span class="guardian-action-card__label">下一步</span>
        <strong>{{ action.next_step || '人工复核' }}</strong>
      </div>
    </div>

    <div v-if="action.message_template" class="guardian-action-card__section">
      <span class="guardian-action-card__label">建议通知模板</span>
      <p class="guardian-action-card__message">{{ action.message_template }}</p>
    </div>

    <div v-if="action.checklist.length" class="guardian-action-card__section">
      <span class="guardian-action-card__label">建议处置清单</span>
      <ul>
        <li v-for="item in action.checklist" :key="item">{{ item }}</li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { GuardianActionInfo } from '@/types/agent'

const props = defineProps<{
  action: GuardianActionInfo
}>()

const priority = computed(() => props.action.priority || 'none')
const priorityLabel = computed(() => {
  if (priority.value === 'urgent') return '紧急联动'
  if (priority.value === 'recommended') return '建议联动'
  return '无需联动'
})

async function copyText(value: string, successMessage: string) {
  try {
    await navigator.clipboard.writeText(value)
    ElMessage.success(successMessage)
  } catch {
    ElMessage.error('复制失败，请检查浏览器权限')
  }
}

function copyNotice() {
  void copyText(props.action.notice || '暂无通知内容', '监护人通知内容已复制')
}

function copyChecklistSummary() {
  const summary = props.action.checklist.length
    ? props.action.checklist.map((item, index) => `${index + 1}. ${item}`).join('\n')
    : '暂无处置清单'
  void copyText(summary, '干预摘要已复制')
}
</script>

<style scoped lang="scss">
.guardian-action-card {
  margin-top: 16px;
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(150, 208, 255, 0.14);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 12%, transparent);
}

.guardian-action-card--urgent {
  border-color: rgba(255, 107, 107, 0.28);
  background: linear-gradient(180deg, rgba(94, 16, 24, 0.88), rgba(60, 12, 18, 0.96));
}

.guardian-action-card--recommended {
  border-color: rgba(255, 195, 75, 0.28);
  background: linear-gradient(180deg, rgba(77, 49, 11, 0.88), rgba(54, 34, 8, 0.96));
}

.guardian-action-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.guardian-action-card__header h3 {
  margin: 0;
  font-size: 18px;
}

.guardian-action-card__header span,
.guardian-action-card__label {
  color: var(--tech-theme-text-secondary);
  font-size: 12px;
}

.guardian-action-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.guardian-action-card__notice {
  margin: 12px 0 0;
  color: var(--tech-theme-text-primary);
  line-height: 1.75;
}

.guardian-action-card__meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.guardian-action-card__meta-item {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(150, 208, 255, 0.12);
  background: color-mix(in srgb, var(--tech-theme-surface-accent) 12%, transparent);
}

.guardian-action-card__meta-item strong,
.guardian-action-card__message {
  color: var(--tech-theme-text-primary);
  line-height: 1.75;
}

.guardian-action-card__section {
  margin-top: 14px;
}

.guardian-action-card__section ul {
  margin: 8px 0 0;
  padding-left: 18px;
  color: var(--tech-theme-text-regular);
  line-height: 1.8;
}

@media (max-width: 720px) {
  .guardian-action-card__header {
    flex-direction: column;
  }

  .guardian-action-card__meta {
    grid-template-columns: 1fr;
  }
}
</style>
