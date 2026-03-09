<template>
  <section class="dashboard-grid">
    <div class="dashboard-grid__hero">
      <slot name="hero" />
    </div>
    <div class="dashboard-grid__map">
      <slot name="map" />
    </div>
    <div class="dashboard-grid__hotspot">
      <slot name="hotspot" />
    </div>
    <div class="dashboard-grid__rumors">
      <slot name="rumors" />
    </div>
    <div class="dashboard-grid__media">
      <slot name="media" />
    </div>
  </section>
</template>

<style scoped lang="scss">
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.9fr);
  grid-template-areas:
    'hero hero'
    'map hotspot'
    'rumors media';
  gap: var(--tech-space-6);
}

.dashboard-grid__hero {
  grid-area: hero;
}

.dashboard-grid__map {
  grid-area: map;
  min-width: 0;
}

.dashboard-grid__hotspot {
  grid-area: hotspot;
  min-width: 0;
}

.dashboard-grid__rumors {
  grid-area: rumors;
  min-width: 0;
}

.dashboard-grid__media {
  grid-area: media;
  min-width: 0;
}

@media (max-width: 1100px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      'hero'
      'map'
      'hotspot'
      'rumors'
      'media';
  }
}
</style>
