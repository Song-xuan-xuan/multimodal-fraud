import api from './index'
import type { HotspotSummaryResponse, HotspotTrendPoint, HotspotTrendResponse } from '@/types/insight'

interface NewsListItem {
  news_id: string
  publish_time: string
  location: string
  label: string
}

interface NewsListResult {
  items: NewsListItem[]
  total_pages: number
}

function normalizeProvince(location: string): string {
  if (!location) return '未知'
  return location
    .trim()
    .replace('壮族自治区', '')
    .replace('维吾尔自治区', '')
    .replace('回族自治区', '')
    .replace('自治区', '')
    .replace('特别行政区', '')
    .replace('省', '')
    .replace('市', '')
}

function isFakeLabel(label: string): boolean {
  const normalized = (label || '').toLowerCase()
  return ['fake', '谣', '假'].some((token) => normalized.includes(token))
}

function isRealLabel(label: string): boolean {
  const normalized = (label || '').toLowerCase()
  return ['real', '真', '可信'].some((token) => normalized.includes(token))
}

function normalizeDate(input: string): string {
  if (!input) return ''
  const byT = input.split('T')[0]
  if (byT) return byT
  return input.slice(0, 10)
}

export const hotspotApi = {
  async getSummary(): Promise<HotspotSummaryResponse> {
    const { data } = await api.get('/map/china-data')
    const provinces = (data.provinces || []).map((item: any) => {
      const total = Number(item.total || 0)
      const fakeCount = Number(item.fake_count || 0)
      return {
        province: String(item.province || ''),
        total,
        fake_count: fakeCount,
        real_count: Number(item.real_count || 0),
        unknown_count: Number(item.unknown_count || 0),
        fake_ratio: total > 0 ? Number(((fakeCount / total) * 100).toFixed(2)) : 0,
      }
    })

    return {
      provinces,
      total_news: Number(data.total_news || 0),
      total_fake: Number(data.total_fake || 0),
      updated_at: String(data.updated_at || ''),
    }
  },

  async getTrend(params: { province?: string; pageLimit?: number; pageSize?: number } = {}): Promise<HotspotTrendResponse> {
    const province = params.province || ''
    const pageLimit = params.pageLimit ?? 6
    const pageSize = params.pageSize ?? 50

    const allItems: NewsListItem[] = []
    let page = 1
    let totalPages = 1

    while (page <= totalPages && page <= pageLimit) {
      const { data } = await api.get<NewsListResult>('/news/', {
        params: { page, per_page: pageSize },
      })

      const pageItems = data.items || []
      allItems.push(...pageItems)
      totalPages = Math.max(1, Number(data.total_pages || 1))
      page += 1
    }

    const dateMap = new Map<string, { fake: number; real: number; total: number }>()

    allItems.forEach((item) => {
      if (province) {
        const normalized = normalizeProvince(item.location || '')
        if (normalized !== province) return
      }

      const date = normalizeDate(item.publish_time || '')
      if (!date) return

      const current = dateMap.get(date) || { fake: 0, real: 0, total: 0 }
      current.total += 1
      if (isFakeLabel(item.label || '')) {
        current.fake += 1
      } else if (isRealLabel(item.label || '')) {
        current.real += 1
      }
      dateMap.set(date, current)
    })

    const points: HotspotTrendPoint[] = Array.from(dateMap.entries())
      .map(([date, value]) => ({ date, ...value }))
      .sort((a, b) => a.date.localeCompare(b.date))

    return { points }
  },
}
