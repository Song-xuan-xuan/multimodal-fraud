export type AdminReviewStatus = 'pending' | 'approved' | 'rejected'
export type AdminReviewActionStatus = Exclude<AdminReviewStatus, 'pending'>

export interface AdminReviewItem {
  id: number
  report_id: string
  type: string
  url: string
  description: string
  reported_by: string
  status: AdminReviewStatus
  review_reason: string
  reviewed_by: string
  reviewed_at: string
  created_at: string
}

export interface AdminReviewQueueResponse {
  items: AdminReviewItem[]
  total: number
}

export interface AdminReviewRequest {
  status: AdminReviewActionStatus
  reason?: string
}

export interface AdminReviewResponse {
  message: string
  item: AdminReviewItem
}

export interface AdminBatchReviewResult {
  succeeded: AdminReviewItem[]
  failed: Array<{
    id: number
    message: string
  }>
}
