import { nextTick, onBeforeUnmount, ref, type MaybeRefOrGetter } from 'vue'

export interface AnchorSyncItem {
  target: string
}

export interface AnchorSyncOptions {
  rootMargin?: string
  threshold?: number[]
  topOffset?: number
}

function resolveAnchorTargets(anchors: MaybeRefOrGetter<AnchorSyncItem[]>): AnchorSyncItem[] {
  if (typeof anchors === 'function') {
    return anchors()
  }
  if ('value' in anchors) {
    return anchors.value
  }
  return anchors
}

export function useAnchorSync(
  anchors: MaybeRefOrGetter<AnchorSyncItem[]>,
  options: AnchorSyncOptions = {},
) {
  const activeTarget = ref('')
  let observer: IntersectionObserver | null = null

  function disconnect() {
    observer?.disconnect()
    observer = null
  }

  function getTargets() {
    return resolveAnchorTargets(anchors)
  }

  function setInitialActive() {
    const list = getTargets()
    activeTarget.value = list[0]?.target || ''
  }

  function scrollToTarget(target: string, behavior: ScrollBehavior = 'smooth') {
    const element = document.getElementById(target)
    if (!element) return false

    activeTarget.value = target
    const topOffset = options.topOffset ?? 96
    const nextTop = element.getBoundingClientRect().top + window.scrollY - topOffset
    window.scrollTo({ top: Math.max(nextTop, 0), behavior })
    return true
  }

  function observe() {
    disconnect()
    const list = getTargets()
    if (!list.length) {
      activeTarget.value = ''
      return
    }

    observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0]

        if (visibleEntry?.target?.id) {
          activeTarget.value = visibleEntry.target.id
        }
      },
      {
        root: null,
        rootMargin: options.rootMargin ?? '-24% 0px -58% 0px',
        threshold: options.threshold ?? [0, 0.1, 0.3, 0.6, 1],
      },
    )

    list.forEach((anchor) => {
      const element = document.getElementById(anchor.target)
      if (element) {
        observer?.observe(element)
      }
    })

    if (!activeTarget.value) {
      setInitialActive()
    }
  }

  async function refresh() {
    await nextTick()
    observe()
  }

  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    activeTarget,
    refresh,
    observe,
    disconnect,
    setInitialActive,
    scrollToTarget,
  }
}
