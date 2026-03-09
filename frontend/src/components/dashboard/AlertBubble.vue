<template>
  <transition name="alert-bubble">
    <div v-if="visible && alerts.length" class="alert-bubble tech-panel">
      <div class="alert-bubble__header">
        <span class="alert-bubble__eyebrow">实时提醒</span>
        <el-button text @click="visible = false">收起</el-button>
      </div>
      <div class="alert-bubble__list tech-scrollbar">
        <article v-for="alert in alerts" :key="alert.title" :class="['alert-bubble__item', `is-${alert.level}`]">
          <div class="alert-bubble__meta">
            <span :class="['alert-bubble__level', `is-${alert.level}`]">{{ alert.levelText }}</span>
            <span>{{ alert.time }}</span>
          </div>
          <h4>{{ alert.title }}</h4>
          <p>{{ alert.description }}</p>
          <el-button v-if="alert.actionLabel" text type="primary" @click="$emit('action', alert.actionPath)">
            {{ alert.actionLabel }}
          </el-button>
        </article>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

export interface DashboardAlertItem {
  title: string
  description: string
  time: string
  level: 'critical' | 'warning' | 'info'
  levelText: string
  actionLabel?: string
  actionPath?: string
}

defineEmits<{
  action: [path?: string]
}>()

defineProps<{
  alerts: DashboardAlertItem[]
}>()

const visible = ref(true)
</script>

<style scoped lang="scss">
.alert-bubble {
  position: fixed;
  top: 92px;
  right: 24px;
  z-index: var(--tech-z-overlay);
  width: min(360px, calc(100vw - 32px));
  padding: 16px;
}

.alert-bubble__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.alert-bubble__eyebrow {
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tech-text-danger);
}

.alert-bubble__list {
  display: grid;
  gap: 10px;
  max-height: 320px;
  overflow: auto;
}

.alert-bubble__item {
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--tech-radius-sm);
  background: rgba(8, 19, 36, 0.76);
}

.alert-bubble__item.is-critical {
  border-color: color-mix(in srgb, var(--tech-color-danger) 26%, transparent);
  background: var(--tech-theme-surface-danger);
  box-shadow: var(--tech-theme-glow-soft);
}

.alert-bubble__item.is-warning {
  border-color: color-mix(in srgb, var(--tech-color-warning) 24%, transparent);
  background: var(--tech-theme-surface-warning);
}

.alert-bubble__item.is-info {
  border-color: color-mix(in srgb, var(--tech-color-info) 24%, transparent);
  background: var(--tech-theme-surface-info);
}

.alert-bubble__item h4 {
  margin: 8px 0 6px;
  font-size: 15px;
  color: var(--tech-text-primary);
}

.alert-bubble__item p {
  margin: 0;
  color: var(--tech-text-secondary);
  line-height: 1.5;
  font-size: 13px;
}

.alert-bubble__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: var(--tech-text-secondary);
}

.alert-bubble__level {
  padding: 2px 8px;
  border-radius: var(--tech-radius-pill);
}

.alert-bubble__level.is-critical {
  color: var(--tech-text-danger);
  background: color-mix(in srgb, var(--tech-color-danger-soft) 100%, transparent);
}

.alert-bubble__level.is-warning {
  color: var(--tech-text-warning);
  background: color-mix(in srgb, var(--tech-color-warning-soft) 100%, transparent);
}

.alert-bubble__level.is-info {
  color: var(--tech-color-info);
  background: color-mix(in srgb, var(--tech-color-info-soft) 100%, transparent);
}

.alert-bubble-enter-active,
.alert-bubble-leave-active {
  transition: all var(--tech-duration-base) var(--tech-ease-out);
}

.alert-bubble-enter-from,
.alert-bubble-leave-to {
  opacity: 0;
  transform: translateY(-12px) scale(0.98);
}

@media (max-width: 900px) {
  .alert-bubble {
    top: auto;
    bottom: 90px;
    right: 16px;
  }
}
</style>
