<template>
  <PageAnchorRail
    :items="anchors"
    :active-target="activeTarget"
    title="详情导航"
    kicker="QUICK LINKS"
    @navigate="emit('navigate', $event)"
  />
</template>

<script setup lang="ts">
import PageAnchorRail from '@/components/page/PageAnchorRail.vue'

interface AnchorItem {
  target: string
  label: string
}

defineProps<{
  anchors: AnchorItem[]
  activeTarget: string
}>()

const emit = defineEmits<{
  (event: 'navigate', target: string): void
}>()
</script>
