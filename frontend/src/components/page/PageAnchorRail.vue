<template>
  <aside v-if="items.length" class="anchor-rail">
    <button class="anchor-toggle" type="button" @click="expanded = !expanded">
      <span>{{ title }}</span>
      <span class="anchor-toggle-icon" :class="{ 'is-expanded': expanded }">⌃</span>
    </button>

    <el-collapse-transition>
      <div v-show="expanded" class="anchor-panel">
        <div class="anchor-panel-head">
          <span class="anchor-kicker">{{ kicker }}</span>
          <span class="anchor-progress">{{ activeIndexLabel }}</span>
        </div>
        <nav class="anchor-list" aria-label="页面分区导航">
          <button
            v-for="item in normalizedItems"
            :key="item.target"
            class="anchor-item"
            :class="{ 'is-active': activeTarget === item.target }"
            type="button"
            @click="emit('navigate', item.target)"
          >
            <span class="anchor-item-index">{{ item.indexLabel }}</span>
            <span class="anchor-item-label">{{ item.label }}</span>
          </button>
        </nav>
      </div>
    </el-collapse-transition>
  </aside>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

interface AnchorRailItem {
  target: string
  label: string
  indexLabel?: string
}

const props = withDefaults(
  defineProps<{
    items: AnchorRailItem[]
    activeTarget: string
    title?: string
    kicker?: string
    mobileCollapsed?: boolean
  }>(),
  {
    title: '快捷导航',
    kicker: 'PAGE INDEX',
    mobileCollapsed: true,
  },
)

const emit = defineEmits<{
  (event: 'navigate', target: string): void
}>()

const expanded = ref(true)

const normalizedItems = computed(() =>
  props.items.map((item, index) => ({
    ...item,
    indexLabel: item.indexLabel || String(index + 1).padStart(2, '0'),
  })),
)

const activeIndexLabel = computed(() => {
  const activeIndex = normalizedItems.value.findIndex((item) => item.target === props.activeTarget)
  if (activeIndex === -1) {
    return `00 / ${String(normalizedItems.value.length).padStart(2, '0')}`
  }
  return `${String(activeIndex + 1).padStart(2, '0')} / ${String(normalizedItems.value.length).padStart(2, '0')}`
})

function syncExpandedWithViewport() {
  if (typeof window === 'undefined') {
    expanded.value = true
    return
  }
  expanded.value = window.innerWidth > 992 ? true : !props.mobileCollapsed
}

watch(
  () => props.items.length,
  () => {
    if (!props.items.length) {
      expanded.value = false
      return
    }
    syncExpandedWithViewport()
  },
  { immediate: true },
)

onMounted(() => {
  syncExpandedWithViewport()
  window.addEventListener('resize', syncExpandedWithViewport)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncExpandedWithViewport)
})
</script>

<style scoped>
.anchor-rail {
  position: sticky;
  top: 92px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.anchor-toggle {
  display: none;
}

.anchor-panel {
  padding: 18px;
  border: 1px solid var(--tech-border-color);
  border-radius: 22px;
  background:
    radial-gradient(circle at top, rgba(76, 201, 255, 0.08), transparent 42%),
    linear-gradient(180deg, rgba(14, 28, 48, 0.94), rgba(8, 18, 34, 0.96));
  box-shadow: var(--tech-shadow-sm);
}

.anchor-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.anchor-kicker,
.anchor-progress {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--tech-text-secondary);
}

.anchor-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.anchor-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border: 1px solid transparent;
  border-radius: 16px;
  background: rgba(125, 211, 252, 0.04);
  color: var(--tech-text-secondary);
  text-align: left;
  cursor: pointer;
  transition: all 0.22s ease;
}

.anchor-item:hover {
  transform: translateX(2px);
  border-color: var(--tech-border-strong);
  background: rgba(76, 201, 255, 0.08);
  color: var(--tech-color-primary-strong);
}

.anchor-item.is-active {
  border-color: rgba(76, 201, 255, 0.26);
  background: linear-gradient(135deg, rgba(76, 201, 255, 0.14), rgba(125, 211, 252, 0.06));
  color: var(--tech-text-primary);
  box-shadow: inset 0 0 0 1px rgba(76, 201, 255, 0.08);
}

.anchor-item-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 34px;
  height: 34px;
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.14);
  color: var(--tech-text-secondary);
  font-size: 12px;
  font-weight: 700;
}

.anchor-item.is-active .anchor-item-index {
  background: rgba(76, 201, 255, 0.18);
  color: var(--tech-color-primary-strong);
}

.anchor-item-label {
  font-size: 14px;
  line-height: 1.5;
}

@media (max-width: 992px) {
  .anchor-rail {
    position: static;
  }

  .anchor-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 12px 16px;
    border: 1px solid var(--tech-border-color);
    border-radius: 16px;
    background: rgba(10, 21, 39, 0.94);
    color: var(--tech-text-primary);
    font-weight: 600;
  }

  .anchor-toggle-icon {
    transition: transform 0.2s ease;
  }

  .anchor-toggle-icon.is-expanded {
    transform: rotate(180deg);
  }
}
</style>
