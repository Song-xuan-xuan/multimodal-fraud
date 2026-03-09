import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePageMotion, type MotionPreset } from '@/composables/usePageMotion'

const transitionNameMap: Record<MotionPreset, string> = {
  fade: 'route-fade',
  'slide-up': 'route-slide-up',
  'slide-left': 'route-slide-left',
}

export function useRouteTransition() {
  const route = useRoute()
  const motionPreset = computed<MotionPreset>(() => {
    const preset = route.meta.motionPreset
    return preset === 'slide-left' || preset === 'slide-up' ? preset : 'fade'
  })
  const transitionName = computed(() => transitionNameMap[motionPreset.value])
  const { pageMotionClass } = usePageMotion(motionPreset, {
    selector: '[data-reveal]',
    stagger: 70,
    threshold: 0.12,
  })

  return {
    motionPreset,
    transitionName,
    pageMotionClass,
  }
}
