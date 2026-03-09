import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { asPositiveInt, asString, replaceQueryKeepingOthers } from '@/composables/useQueryState'
import type { NewsListFilters, NewsListQueryState } from '@/types/newsList'

const DEFAULT_PER_PAGE = 20
const QUERY_KEYS = [
  'page',
  'keyword',
  'platform',
  'label',
  'minCredibility',
  'maxCredibility',
  'propagationPlatform',
  'startDate',
  'endDate',
  'perPage',
  'autoApply',
] as const

function createDefaultFilters(): NewsListFilters {
  return {
    keyword: '',
    platform: '',
    label: '',
    minCredibility: '',
    maxCredibility: '',
    propagationPlatform: '',
    startDate: '',
    endDate: '',
    perPage: DEFAULT_PER_PAGE,
    autoApply: false,
  }
}

function normalizeRangeValue(value: string) {
  const trimmed = value.trim()
  if (!trimmed) return ''
  const numeric = Number(trimmed)
  if (!Number.isFinite(numeric)) return ''
  return String(Math.min(Math.max(numeric, 0), 100))
}

function parseQueryState(query: Record<string, unknown>): NewsListQueryState {
  return {
    page: asPositiveInt(query.page, 1),
    keyword: asString(query.keyword),
    platform: asString(query.platform),
    label: asString(query.label),
    minCredibility: asString(query.minCredibility),
    maxCredibility: asString(query.maxCredibility),
    propagationPlatform: asString(query.propagationPlatform),
    startDate: asString(query.startDate),
    endDate: asString(query.endDate),
    perPage: asPositiveInt(query.perPage, DEFAULT_PER_PAGE, 1, 100),
    autoApply: query.autoApply === '1',
  }
}

function toFilters(state: NewsListQueryState): NewsListFilters {
  const defaults = createDefaultFilters()
  return {
    ...defaults,
    keyword: state.keyword || '',
    platform: state.platform || '',
    label: state.label || '',
    minCredibility: state.minCredibility || '',
    maxCredibility: state.maxCredibility || '',
    propagationPlatform: state.propagationPlatform || '',
    startDate: state.startDate || '',
    endDate: state.endDate || '',
    perPage: state.perPage,
    autoApply: Boolean(state.autoApply),
  }
}

function serializeQuery(state: NewsListQueryState): Record<string, string> {
  return {
    page: String(state.page),
    perPage: String(state.perPage),
    ...(state.keyword ? { keyword: state.keyword } : {}),
    ...(state.platform ? { platform: state.platform } : {}),
    ...(state.label ? { label: state.label } : {}),
    ...(state.minCredibility ? { minCredibility: state.minCredibility } : {}),
    ...(state.maxCredibility ? { maxCredibility: state.maxCredibility } : {}),
    ...(state.propagationPlatform ? { propagationPlatform: state.propagationPlatform } : {}),
    ...(state.startDate ? { startDate: state.startDate } : {}),
    ...(state.endDate ? { endDate: state.endDate } : {}),
    ...(state.autoApply ? { autoApply: '1' } : {}),
  }
}

export function useNewsListFilters() {
  const route = useRoute()
  const router = useRouter()

  const queryState = ref<NewsListQueryState>(parseQueryState(route.query))
  const draftFilters = ref<NewsListFilters>(toFilters(queryState.value))

  watch(
    () => route.query,
    (query) => {
      const nextState = parseQueryState(query)
      queryState.value = nextState
      draftFilters.value = toFilters(nextState)
    },
    { immediate: true },
  )

  const appliedFilters = computed<NewsListFilters>(() => toFilters(queryState.value))

  async function updateQuery(nextState: Partial<NewsListQueryState>) {
    const merged: NewsListQueryState = {
      ...queryState.value,
      ...nextState,
    }

    merged.page = asPositiveInt(merged.page, 1)
    merged.perPage = asPositiveInt(merged.perPage, DEFAULT_PER_PAGE, 1, 100)
    merged.minCredibility = normalizeRangeValue(merged.minCredibility || '') || undefined
    merged.maxCredibility = normalizeRangeValue(merged.maxCredibility || '') || undefined

    await replaceQueryKeepingOthers(router, route.query, [...QUERY_KEYS], serializeQuery(merged))
  }

  async function apply(filters = draftFilters.value) {
    await updateQuery({
      page: 1,
      keyword: filters.keyword.trim() || undefined,
      platform: filters.platform || undefined,
      label: filters.label || undefined,
      minCredibility: filters.minCredibility || undefined,
      maxCredibility: filters.maxCredibility || undefined,
      propagationPlatform: filters.propagationPlatform || undefined,
      startDate: filters.startDate || undefined,
      endDate: filters.endDate || undefined,
      perPage: filters.perPage,
      autoApply: filters.autoApply,
    })
  }

  async function reset() {
    const defaults = createDefaultFilters()
    draftFilters.value = defaults
    await updateQuery({
      page: 1,
      keyword: undefined,
      platform: undefined,
      label: undefined,
      minCredibility: undefined,
      maxCredibility: undefined,
      propagationPlatform: undefined,
      startDate: undefined,
      endDate: undefined,
      perPage: defaults.perPage,
      autoApply: false,
    })
  }

  async function goToPage(page: number) {
    await updateQuery({ page })
  }

  async function setPerPage(perPage: number) {
    draftFilters.value.perPage = perPage
    await updateQuery({ page: 1, perPage, autoApply: draftFilters.value.autoApply })
  }

  async function setAutoApply(value: boolean) {
    draftFilters.value.autoApply = value
    await updateQuery({ page: 1, autoApply: value })
  }

  return {
    queryState,
    draftFilters,
    appliedFilters,
    apply,
    reset,
    goToPage,
    setPerPage,
    setAutoApply,
  }
}
