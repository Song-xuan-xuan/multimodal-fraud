import api from './index'
import type { RagSource } from '@/types/rag'

export interface RagHealthResponse {
  status: 'ready' | 'warming_up' | 'error' | 'not_initialized'
  ready: boolean
}

export const ragApi = {
  async ask(question: string, sessionId?: string) {
    const { data } = await api.post(
      '/rag/ask',
      { question, session_id: sessionId },
      { timeout: 120000 },
    )
    return data as { answer: string; sources: RagSource[]; session_id: string }
  },
  async health() {
    const { data } = await api.get('/rag/health')
    return data as RagHealthResponse
  },
}
