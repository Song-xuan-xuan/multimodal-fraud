import api from './index'
import type {
  CrowdBoardProgressResponse,
  EvidenceBoardItem,
  EvidenceBoardListResponse,
  EvidenceBoardStats,
} from '@/types/insight'

interface RawEvidenceItem {
  id: number
  news_id: string
  source: string
  status: 'pending' | 'approved' | 'rejected'
  submitted_at: string
}

interface RawEvidenceListResponse {
  items: RawEvidenceItem[]
  total: number
}

interface NewsMeta {
  title: string
  platform: string
  label: string
  credibility?: {
    verification_progress?: number
  }
}

export interface EvidenceBoardQuery {
  page?: number
  pageSize?: number
  status?: 'pending' | 'approved' | 'rejected'
  keyword?: string
}

export interface CrowdBoardProgressQuery {
  page?: number
  pageSize?: number
  keyword?: string
  minProgress?: number
  maxProgress?: number
}

async function fetchNewsMetaMap(newsIds: string[]): Promise<Map<string, NewsMeta>> {
  const uniqueIds = Array.from(new Set(newsIds.filter(Boolean)))
  const responses = await Promise.allSettled(
    uniqueIds.map((id) => api.get<NewsMeta>(`/news/${encodeURIComponent(id)}`)),
  )

  const metaMap = new Map<string, NewsMeta>()
  responses.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      metaMap.set(uniqueIds[index], result.value.data)
    }
  })

  return metaMap
}

export const evidenceApi = {
  async listBoard(query: EvidenceBoardQuery = {}): Promise<EvidenceBoardListResponse> {
    const page = Math.max(1, query.page || 1)
    const pageSize = Math.max(1, query.pageSize || 10)

    const { data } = await api.get<RawEvidenceListResponse>('/community/evidence/my')
    const rawItems = data.items || []
    const newsMetaMap = await fetchNewsMetaMap(rawItems.map((item) => item.news_id))

    const normalized: EvidenceBoardItem[] = rawItems.map((item) => {
      const meta = newsMetaMap.get(item.news_id)
      return {
        id: item.id,
        news_id: item.news_id,
        title: meta?.title || `新闻 ${item.news_id}`,
        platform: meta?.platform || '-',
        label: meta?.label || '-',
        submitted_at: item.submitted_at,
        status: item.status,
        source: item.source || '',
      }
    })

    const keyword = query.keyword?.trim().toLowerCase() || ''

    const filtered = normalized.filter((item) => {
      if (query.status && item.status !== query.status) return false
      if (!keyword) return true
      return (
        item.title.toLowerCase().includes(keyword)
        || item.news_id.toLowerCase().includes(keyword)
        || item.platform.toLowerCase().includes(keyword)
      )
    })

    const start = (page - 1) * pageSize
    const end = start + pageSize

    return {
      total: filtered.length,
      items: filtered.slice(start, end),
    }
  },

  async getBoardStats(): Promise<EvidenceBoardStats> {
    const { data } = await api.get<RawEvidenceListResponse>('/community/evidence/my')
    const items = data.items || []
    const pending = items.filter((item) => item.status === 'pending').length
    const approved = items.filter((item) => item.status === 'approved').length
    const rejected = items.filter((item) => item.status === 'rejected').length

    return {
      total: items.length,
      pending,
      approved,
      rejected,
    }
  },

  async listVerificationProgress(query: CrowdBoardProgressQuery = {}): Promise<CrowdBoardProgressResponse> {
    const page = Math.max(1, query.page || 1)
    const pageSize = Math.max(1, query.pageSize || 10)
    const minProgress = Math.max(0, Math.min(100, query.minProgress ?? 0))
    const maxProgress = Math.max(0, Math.min(100, query.maxProgress ?? 100))

    const { data } = await api.get('/news/', {
      params: {
        page,
        per_page: pageSize,
        ...(query.keyword?.trim() ? { keyword: query.keyword.trim() } : {}),
      },
    })

    const items = (data.items || [])
      .map((item: any) => ({
        news_id: String(item.news_id || ''),
        title: String(item.title || ''),
        platform: String(item.platform || ''),
        label: String(item.label || ''),
        verification_progress: Number(item.credibility?.verification_progress || 0),
      }))
      .filter((item: any) => item.verification_progress >= minProgress && item.verification_progress <= maxProgress)

    return {
      items,
      total: items.length,
      page,
      page_size: pageSize,
    }
  },
}
