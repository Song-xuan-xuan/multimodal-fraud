import type { NewsItem } from '@/api/news'

export interface NewsListFilters {
  keyword: string
  platform: string
  label: string
  minCredibility: string
  maxCredibility: string
  propagationPlatform: string
  startDate: string
  endDate: string
  perPage: number
  autoApply: boolean
}

export interface NewsListQueryState {
  page: number
  keyword?: string
  platform?: string
  label?: string
  minCredibility?: string
  maxCredibility?: string
  propagationPlatform?: string
  startDate?: string
  endDate?: string
  perPage: number
  autoApply?: boolean
}

export interface NewsListState extends NewsListQueryState {
  items: NewsItem[]
  total: number
  totalPages: number
}

export interface NewsListOptionSets {
  platforms: string[]
  labels: string[]
  propagationPlatforms: string[]
  perPageOptions: number[]
}

export interface NewsListSummary {
  total: number
  currentPage: number
  totalPages: number
  rangeStart: number
  rangeEnd: number
  activeFilterCount: number
}

export interface NewsListFetchParams {
  page?: number
  perPage?: number
  keyword?: string
  platform?: string
  label?: string
  minCredibility?: string
  maxCredibility?: string
  startDate?: string
  endDate?: string
  propagationPlatform?: string
}

export interface NewsListApiResult {
  items: NewsItem[]
  total: number
  page: number
  perPage: number
  totalPages: number
}
