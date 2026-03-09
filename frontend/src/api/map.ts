import api from './index'

export interface ProvinceMapStat {
  province: string
  total: number
  fake_count: number
  real_count: number
  unknown_count: number
  value: number
}

export interface ChinaMapDataResponse {
  provinces: ProvinceMapStat[]
  total_news: number
  total_fake: number
  updated_at: string
}

export interface ProvinceNewsItem {
  news_id: string
  title: string
  label: string
  platform: string
  publish_time: string
  location: string
}

export interface ProvinceDetailResponse {
  province: string
  stats: ProvinceMapStat
  items: ProvinceNewsItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ProvinceDetailParams {
  page?: number
  page_size?: number
  label?: string
}

export const mapApi = {
  async chinaGeoJson() {
    const { data } = await api.get('/map/china-geojson')
    return data
  },

  async chinaData() {
    const { data } = await api.get<ChinaMapDataResponse>('/map/china-data')
    return data
  },

  async provinceDetail(province: string, params: ProvinceDetailParams = {}) {
    const { data } = await api.get<ProvinceDetailResponse>(`/map/province/${encodeURIComponent(province)}`, { params })
    return data
  },
}
