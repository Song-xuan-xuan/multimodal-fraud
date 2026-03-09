import api from './index'
import type {
  FeedbackListResponse,
  FeedbackSubmitResponse,
  NewsFeedbackStats,
  VoteOption,
} from '@/types/engagement'

export const engagementApi = {
  async getStats(newsId: string) {
    const { data } = await api.get<NewsFeedbackStats>(`/feedback/stats/${encodeURIComponent(newsId)}`)
    return data
  },

  async submitVote(newsId: string, vote: VoteOption) {
    const { data } = await api.post<FeedbackSubmitResponse>('/feedback/submit-vote', {
      news_id: newsId,
      vote,
    })
    return data
  },

  async submitRebuttal(newsId: string, feedback: string) {
    const { data } = await api.post<FeedbackSubmitResponse>('/feedback/submit-feedback', {
      news_id: newsId,
      feedback,
    })
    return data
  },

  async getMyFeedback(newsId: string) {
    const { data } = await api.get<FeedbackListResponse>('/feedback/my', {
      params: {
        page: 1,
        page_size: 50,
        news_id: newsId,
        type: 'vote',
      },
    })
    return data
  },
}
