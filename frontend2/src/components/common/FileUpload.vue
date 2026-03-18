<template>
  <el-upload :auto-upload="false" :on-change="handleChange" :limit="1" accept="image/*" drag class="file-upload">
    <div class="file-upload__icon-wrap">
      <el-icon class="file-upload__icon"><i class="el-icon-upload" /></el-icon>
    </div>
    <div class="file-upload__title">拖拽文件到此处，或 <em>点击上传</em></div>
    <p class="file-upload__hint">支持常见截图格式，用于风险图片检测。</p>
  </el-upload>
</template>

<script setup lang="ts">
const emit = defineEmits<{ (e: 'select', file: File): void }>()

function handleChange(uploadFile: any) {
  if (uploadFile.raw) emit('select', uploadFile.raw)
}
</script>

<style scoped lang="scss">
.file-upload {
  --upload-shell-bg: color-mix(in srgb, var(--app-surface-note) 78%, white 22%);
}

.file-upload :deep(.el-upload-dragger) {
  border: 1px dashed var(--app-border-strong);
  border-radius: 22px;
  background: var(--upload-shell-bg);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.file-upload__icon-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin-bottom: 8px;
  border-radius: 20px;
  background: color-mix(in srgb, var(--app-surface-elevated) 88%, white 12%);
}

.file-upload__icon {
  font-size: 36px;
  color: var(--tech-color-primary-strong);
}

.file-upload__title {
  color: var(--app-text-primary);
  font-size: 15px;
}

.file-upload__title em {
  color: var(--tech-color-primary-strong);
  font-style: normal;
}

.file-upload__hint {
  margin: 8px 0 0;
  color: var(--app-text-secondary);
  font-size: 13px;
}
</style>
