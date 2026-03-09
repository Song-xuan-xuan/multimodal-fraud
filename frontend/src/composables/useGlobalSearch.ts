import { computed, ref, toValue, type MaybeRefOrGetter } from 'vue'
import type { LocationQueryRaw, RouteLocationRaw, Router } from 'vue-router'
import { appRoute, normalizeAppRouteTarget } from '@/router'

export interface GlobalSearchOptions {
  route?: MaybeRefOrGetter<RouteLocationRaw>
  queryKey?: string
  trim?: boolean
  keepEmpty?: boolean
}

function normalizeKeyword(value: string, trim = true) {
  return trim ? value.trim() : value
}

function resolveRouteInput(route: RouteLocationRaw): Exclude<RouteLocationRaw, string> {
  const normalized = normalizeAppRouteTarget(route)
  if (typeof normalized === 'string') {
    return { path: normalized }
  }
  return normalized
}

export function useGlobalSearch(initialKeyword = '', options: GlobalSearchOptions) {
  const keyword = ref(initialKeyword)
  const searching = ref(false)

  const normalizedKeyword = computed(() => normalizeKeyword(keyword.value, options.trim !== false))
  const canSearch = computed(() => options.keepEmpty || normalizedKeyword.value.length > 0)

  async function submit(router: Router, overrides?: Partial<GlobalSearchOptions>) {
    const queryKey = overrides?.queryKey ?? options.queryKey ?? 'keyword'
    const keepEmpty = overrides?.keepEmpty ?? options.keepEmpty ?? false
    const route = resolveRouteInput(toValue(overrides?.route ?? options.route ?? appRoute.newsList()))
    const nextKeyword = normalizeKeyword(keyword.value, overrides?.trim ?? options.trim !== false)

    const nextQuery: LocationQueryRaw = {
      ...(route.query ?? {}),
      [queryKey]: keepEmpty || nextKeyword ? nextKeyword : undefined,
    }

    searching.value = true
    try {
      await router.push({
        ...route,
        query: nextQuery,
      })
    } finally {
      searching.value = false
    }
  }

  function fill(value: string) {
    keyword.value = value
  }

  function reset() {
    keyword.value = ''
  }

  return {
    keyword,
    searching,
    normalizedKeyword,
    canSearch,
    fill,
    reset,
    submit,
  }
}
