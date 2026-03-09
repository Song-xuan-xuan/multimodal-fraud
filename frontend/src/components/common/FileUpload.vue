<template>
  <el-upload
    :auto-upload="false"
    :on-change="handleChange"
    :limit="1"
    accept="image/*"
    drag
  >
    <el-icon style="font-size: 48px; color: #c0c4cc"><i class="el-icon-upload" /></el-icon>
    <div>拖拽文件到此处，或 <em>点击上传</em></div>
  </el-upload>
</template>

<script setup lang="ts">
const emit = defineEmits<{ (e: 'select', file: File): void }>()

function handleChange(uploadFile: any) {
  if (uploadFile.raw) emit('select', uploadFile.raw)
}
</script>
