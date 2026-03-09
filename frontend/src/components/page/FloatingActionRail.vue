<template>
  <div class="floating-action-rail">
    <div class="floating-shell">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.floating-action-rail {
  position: sticky;
  bottom: 24px;
  z-index: 20;
  display: flex;
  justify-content: flex-end;
  pointer-events: none;
}

.floating-shell {
  width: min(100%, 420px);
  pointer-events: auto;
}

@media (max-width: 1200px) {
  .floating-action-rail {
    position: fixed;
    right: 20px;
    bottom: 20px;
    left: auto;
  }

  .floating-shell {
    width: min(calc(100vw - 32px), 360px);
  }
}

@media (max-width: 768px) {
  .floating-action-rail {
    right: 12px;
    left: 12px;
    justify-content: center;
  }

  .floating-shell {
    width: 100%;
  }
}
</style>
