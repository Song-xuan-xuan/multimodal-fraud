import api from './index'
import type {
  AdminBatchReviewResult,
  AdminReviewActionStatus,
  AdminReviewItem,
  AdminReviewQueueResponse,
  AdminReviewRequest,
  AdminReviewResponse,
} from '@/types/admin'
import type { KnowledgeItemResponse } from '@/types/knowledge'

export const adminReviewApi = {
  async listSubmissions() {
    const { data } = await api.get('/admin/submissions')
    return data as AdminReviewQueueResponse
  },

  async reviewSubmission(submissionId: number, payload: AdminReviewRequest) {
    const { data } = await api.post(`/admin/submissions/${submissionId}/review`, payload)
    return data as AdminReviewResponse
  },

  async promoteToKnowledge(submissionId: number) {
    const { data } = await api.post(`/admin/submissions/${submissionId}/promote-to-knowledge`)
    return data as { message: string; item: KnowledgeItemResponse }
  },

  async batchReview(ids: number[], status: AdminReviewActionStatus, reason?: string) {
    const jobs = ids.map(async (id) => {
      try {
        const result = await this.reviewSubmission(id, { status, reason })
        return { ok: true as const, id, item: result.item }
      } catch (error: any) {
        return {
          ok: false as const,
          id,
          message: error?.response?.data?.detail || error?.message || '审核失败',
        }
      }
    })

    const settled = await Promise.all(jobs)
    const succeeded: AdminReviewItem[] = []
    const failed: AdminBatchReviewResult['failed'] = []

    settled.forEach((result) => {
      if (result.ok) {
        succeeded.push(result.item)
      } else {
        failed.push({ id: result.id, message: result.message })
      }
    })

    return { succeeded, failed } as AdminBatchReviewResult
  },
}
