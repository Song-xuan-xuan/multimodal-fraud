import api from './index'
import type { AgentAnalyzeResponse } from '@/types/agent'

export const agentApi = {
  async analyze(payload: { text?: string; image?: File | null; audio?: File | null }) {
    const formData = new FormData()
    if (payload.text?.trim()) formData.append('text', payload.text.trim())
    if (payload.image) formData.append('image', payload.image)
    if (payload.audio) formData.append('audio', payload.audio)

    const { data } = await api.post<AgentAnalyzeResponse>('/agent/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,
    })
    return data
  },
}
