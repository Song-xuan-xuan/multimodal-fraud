import { computed, nextTick, onBeforeUnmount, onMounted, ref, toValue, watch, type MaybeRefOrGetter } from 'vue'

export type MotionPreset = 'fade' | 'slide-up' | 'slide-left'
export type RevealOrigin = 'bottom' | 'left' | 'right' | 'scale'

export interface PageRevealOptions {
  selector?: string
  threshold?: number
  rootMargin?: string
  stagger?: number
  origin?: RevealOrigin
  disabled?: MaybeRefOrGetter<boolean>
}

function resolveOrigin(origin: RevealOrigin): string {
  if (origin === 'bottom') return 'bottom'
  return origin
}

export function usePageMotion(preset: MaybeRefOrGetter<MotionPreset> = 'fade', options: PageRevealOptions = {}) {
  const isReady = ref(false)
  const observer = ref<IntersectionObserver | null>(null)

  const pageMotionClass = computed(() => {
    const current = toValue(preset)
    if (current === 'slide-left') return 'motion-slide-in-right'
    if (current === 'slide-up') return 'motion-fade-in-up'
    return 'motion-fade-in-up'
  })

  function disconnect() {
    observer.value?.disconnect()
    observer.value = null
  }

  function revealTargets() {
    if (typeof window === 'undefined') return

    disconnect()
    const selector = options.selector ?? '[data-reveal]'
    const targets = Array.from(document.querySelectorAll<HTMLElement>(selector))
    if (!targets.length) return

    const disabled = Boolean(toValue(options.disabled)) || window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const stagger = options.stagger ?? 60
    const origin = resolveOrigin(options.origin ?? 'bottom')

    targets.forEach((element, index) => {
      element.classList.add('motion-reveal')
      element.dataset.revealOrigin = element.dataset.revealOrigin || origin
      element.style.setProperty('--reveal-delay', `${index * stagger}ms`)
      if (disabled) {
        element.classList.add('is-visible')
      } else {
        element.classList.remove('is-visible')
      }
    })

    if (disabled) return

    observer.value = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return
          entry.target.classList.add('is-visible')
          observer.value?.unobserve(entry.target)
        })
      },
      {
        threshold: options.threshold ?? 0.16,
        rootMargin: options.rootMargin ?? '0px 0px -12% 0px',
      },
    )

    targets.forEach((element) => observer.value?.observe(element))
  }

  async function setupReveal() {
    await nextTick()
    revealTargets()
    isReady.value = true
  }

  onMounted(() => {
    void setupReveal()
  })

  onBeforeUnmount(() => {
    disconnect()
  })

  watch(
    () => [toValue(preset), toValue(options.disabled)],
    () => {
      void setupReveal()
    },
  )

  return {
    isReady,
    pageMotionClass,
    setupReveal,
    disconnectReveal: disconnect,
  }
}
