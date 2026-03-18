<template>
  <transition name="ai-popup">
    <div v-if="visible" class="ai-popup">
      <div class="ai-popup__header">
        <div>
          <p class="ai-popup__eyebrow">AI 协同助理</p>
          <h3>一键进入智能研判</h3>
        </div>
        <el-button text @click="visible = false">关闭</el-button>
      </div>

      <p class="ai-popup__desc">根据当前看板态势，快速切换到 AI 检测、问答助理或 Agent 流程。</p>

      <div class="ai-popup__actions">
        <el-button type="primary" @click="$emit('navigate', '/ai/assistant')">知识问答</el-button>
        <el-button @click="$emit('navigate', '/detection/ai')">AI 检测</el-button>
        <el-button @click="$emit('navigate', '/ai/agent')">多 Agent 协作</el-button>
      </div>

      <div class="ai-popup__prompts">
        <button v-for="prompt in prompts" :key="prompt.label" type="button" class="ai-popup__prompt" @click="$emit('navigate', prompt.path)">
          <span>{{ prompt.label }}</span>
          <small>{{ prompt.tip }}</small>
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineEmits<{
  navigate: [path: string]
}>()

const visible = ref(true)

const prompts = [
  { label: '追踪热点脉冲', tip: '查看洞察趋势', path: '/insight/hotspot' },
  { label: '发起事实核查', tip: '进入核查工作台', path: '/fact-check' },
  { label: '整理举报线索', tip: '直达举报面板', path: '/report' },
]
</script>

<style scoped lang="scss">
.ai-popup {
  position: fixed;
  left: 24px;
  bottom: 24px;
  z-index: var(--tech-z-overlay);
  width: min(380px, calc(100vw - 32px));
  padding: 18px;
  border: 1px solid var(--app-border-default);
  border-radius: 24px;
  background: color-mix(in srgb, var(--app-surface-elevated) 94%, white 6%);
  box-shadow: 0 18px 40px rgba(31, 41, 51, 0.12);
}

.ai-popup__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.ai-popup__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--tech-color-primary-strong);
}

.ai-popup__header h3 {
  margin: 0;
  font-size: 20px;
}

.ai-popup__desc {
  margin: 12px 0 16px;
  color: var(--app-text-secondary);
  line-height: 1.6;
}

.ai-popup__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.ai-popup__prompts {
  display: grid;
  gap: 10px;
}

.ai-popup__prompt {
  border: 1px solid var(--app-border-default);
  border-radius: 14px;
  background: color-mix(in srgb, var(--app-surface-note) 76%, white 24%);
  color: inherit;
  text-align: left;
  padding: 12px 14px;
  cursor: pointer;
}

.ai-popup__prompt span,
.ai-popup__prompt small {
  display: block;
}

.ai-popup__prompt small {
  margin-top: 4px;
  color: var(--app-text-secondary);
}

.ai-popup-enter-active,
.ai-popup-leave-active {
  transition: all var(--tech-duration-base) var(--tech-ease-out);
}

.ai-popup-enter-from,
.ai-popup-leave-to {
  opacity: 0;
  transform: translateY(16px);
}

@media (max-width: 900px) {
  .ai-popup {
    left: 16px;
    bottom: 16px;
  }
}
</style>
