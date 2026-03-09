import api from './index'

export interface ReportSubmitPayload {
  type: string
  url?: string
  description: string
}

export interface ReportItem {
  report_id: string
  type: string
  url: string
  description: string
  status: string
  created_at: string
}

export interface ReportListParams {
  page?: number
  page_size?: number
  type?: string
  status?: string
  keyword?: string
}

export interface ReportListResponse {
  items: ReportItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const reportApi = {
  async submit(payload: ReportSubmitPayload) {
    const { data } = await api.post('/report/submit', payload)
    return data as { report_id: string; message: string }
  },

  async my(params: ReportListParams = {}) {
    const { data } = await api.get('/report/my', { params })
    return data as ReportListResponse
  },
}
