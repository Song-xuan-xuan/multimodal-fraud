import api from './index'

export interface FactCheckSource {
  title: string
  url: string
  snippet: string
  relevance: number
}

export interface FactCheckResult {
  query: string
  verdict: string
  confidence: number
  explanation: string
  sources: FactCheckSource[]
  evidence_unavailable?: boolean
}

export interface FactCheckHistoryItem {
  id: string
  query: string
  verdict: string
  confidence: number
  checked_at: string
}

export interface FactCheckHistoryParams {
  page?: number
  page_size?: number
  verdict?: string
  keyword?: string
}

export interface FactCheckHistoryResponse {
  items: FactCheckHistoryItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const factCheckApi = {
  async check(text: string, useAdvanced = false) {
    const { data } = await api.post('/fact-check/check', { text, use_advanced: useAdvanced })
    return data as FactCheckResult
  },

  async multiSource(text: string, sources: string[] = []) {
    const { data } = await api.post('/fact-check/multi-source', { text, sources })
    return data as FactCheckResult
  },

  async evidenceOnly(text: string) {
    const { data } = await api.post('/fact-check/evidence-only', { text })
    return data as { query: string; evidence: FactCheckSource[]; total_sources: number }
  },

  async save(payload: { query: string; verdict: string; confidence: number; explanation: string; save_type?: string }) {
    const { data } = await api.post('/fact-check/save', payload)
    return data as { id: string; message: string }
  },

  async history(params: FactCheckHistoryParams = {}) {
    const { data } = await api.get('/fact-check/history', { params })
    return data as FactCheckHistoryResponse
  },

  async deleteHistory(recordId: string) {
    const { data } = await api.delete(`/fact-check/history/${recordId}`)
    return data as { message: string }
  },
}
