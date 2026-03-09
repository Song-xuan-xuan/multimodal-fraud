export type VoteOption = 'agree' | 'disagree'

export interface FeedbackItem {
  id: number
  news_id: string
  type: 'vote' | 'feedback'
  content: string
  submitted_by: string
  submitted_at: string
  updated_at: string
  status: 'pending' | 'approved' | 'rejected'
  reason: string
  reviewed_by: string
  reviewed_at: string
}

export interface FeedbackSubmitResponse {
  message: string
  item: FeedbackItem
  idempotent: boolean
}

export interface FeedbackListResponse {
  items: FeedbackItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface NewsFeedbackStats {
  news_id: string
  total: number
  vote_total: number
  vote_agree: number
  vote_disagree: number
  feedback_total: number
  pending: number
  approved: number
  rejected: number
}

export interface EngagementLoadingState {
  stats: boolean
  vote: boolean
  rebuttal: boolean
}

export interface EngagementPerNewsState {
  stats: NewsFeedbackStats | null
  myVote: VoteOption | null
  loading: EngagementLoadingState
}
