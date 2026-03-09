<template>
  <div class="modal-shell">
    <div v-if="$slots.header" class="modal-shell-header">
      <slot name="header" />
    </div>
    <div class="modal-shell-body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="modal-shell-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<style scoped>
.modal-shell {
  padding: 4px;
}

.modal-shell-header {
  margin-bottom: 12px;
}

.modal-shell-body {
  padding: 4px 2px;
}

.modal-shell-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
