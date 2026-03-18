import api from './index'
import type {
  KnowledgeItemCreatePayload,
  KnowledgeItemListResponse,
  KnowledgeItemResponse,
  KnowledgeItemReviewPayload,
  KnowledgeRebuildResponse,
  KnowledgeIndexStatus,
} from '@/types/knowledge'

export const knowledgeApi = {
  async list(status?: string) {
    const { data } = await api.get('/knowledge/items', { params: status ? { status } : undefined })
    return data as KnowledgeItemListResponse
  },

  async create(payload: KnowledgeItemCreatePayload) {
    const { data } = await api.post('/knowledge/items', payload)
    return data as KnowledgeItemResponse
  },

  async review(itemId: number, payload: KnowledgeItemReviewPayload) {
    const { data } = await api.post(`/knowledge/items/${itemId}/review`, payload)
    return data as KnowledgeItemResponse
  },

  async delete(itemId: number) {
    const { data } = await api.delete(`/knowledge/items/${itemId}`)
    return data as { message: string; id: number }
  },

  async rebuildIndex() {
    const { data } = await api.post('/knowledge/rebuild-index')
    return data as KnowledgeRebuildResponse
  },

  async getIndexStatus() {
    const { data } = await api.get('/knowledge/index-status')
    return data as KnowledgeIndexStatus
  },
}
