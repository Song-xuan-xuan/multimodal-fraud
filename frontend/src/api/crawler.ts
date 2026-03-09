import api from './index'

export interface CrawlerNewsItem {
  title: string
  url: string
  source: string
  summary: string
  publish_time: string
}

export interface CrawlerListResponse {
  news: CrawlerNewsItem[]
  total: number
}

export interface CrawlerSearchResponse {
  news: CrawlerNewsItem[]
  stats: { sources: Record<string, number>; total: number }
}

export const crawlerApi = {
  async getLatest(): Promise<CrawlerListResponse> {
    const { data } = await api.get('/crawler/latest')
    return data
  },

  async search(keyword: string, platform = 'all'): Promise<CrawlerSearchResponse> {
    const { data } = await api.get('/crawler/search', { params: { keyword, platform } })
    return data
  },
}
