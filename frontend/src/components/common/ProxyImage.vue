<template>
  <div class="proxy-image" :style="containerStyle">
    <el-image
      v-if="currentSrc"
      :key="currentSrc"
      class="image"
      :src="currentSrc"
      :fit="fit"
      @error="onError"
    >
      <template #error>
        <div class="fallback">
          <div class="fallback-content">
            <span class="fallback-title">图片加载失败</span>
            <span class="fallback-subtitle">可尝试重新获取代理地址</span>
            <el-button size="small" @click="retry">重试</el-button>
          </div>
        </div>
      </template>
    </el-image>

    <div v-else class="fallback">
      <div class="fallback-content">
        <span class="fallback-title">暂无可用图片</span>
        <span class="fallback-subtitle">当前未提供有效封面</span>
        <el-button size="small" @click="retry">重试</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { mediaApi } from '@/api/media'

const props = withDefaults(
  defineProps<{
    src: string
    width?: string
    height?: string
    fit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
  }>(),
  {
    width: '100%',
    height: '280px',
    fit: 'cover',
  },
)

const candidateIndex = ref(0)

const candidates = computed(() => mediaApi.buildCandidates(props.src))
const currentSrc = computed(() => candidates.value[candidateIndex.value]?.src || '')

const containerStyle = computed(() => ({
  width: props.width,
  height: props.height,
}))

function onError() {
  if (candidateIndex.value < candidates.value.length - 1) {
    candidateIndex.value += 1
  }
}

function retry() {
  candidateIndex.value = 0
}

watch(
  () => props.src,
  () => {
    candidateIndex.value = 0
  },
)
</script>

<style scoped>
.proxy-image {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--tech-border-color);
  border-radius: 24px;
  background:
    radial-gradient(circle at top, rgba(76, 201, 255, 0.1), transparent 42%),
    linear-gradient(180deg, rgba(14, 28, 48, 0.94), rgba(8, 18, 34, 0.96));
  box-shadow: var(--tech-shadow-sm);
}

.proxy-image::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 72px;
  background: linear-gradient(180deg, transparent, rgba(8, 18, 34, 0.28));
  pointer-events: none;
}

.image {
  width: 100%;
  height: 100%;
}

.fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.fallback-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--tech-text-secondary);
  text-align: center;
}

.fallback-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.fallback-subtitle {
  font-size: 13px;
  line-height: 1.5;
}

.fallback :deep(.el-button) {
  border-color: var(--tech-border-strong);
  background: rgba(76, 201, 255, 0.08);
  color: var(--tech-color-primary-strong);
}

.fallback :deep(.el-button:hover) {
  background: rgba(76, 201, 255, 0.14);
}
</style>
