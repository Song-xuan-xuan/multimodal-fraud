import api from './index'

export interface ProfileData {
  age_group: string | null
  gender: string | null
  occupation: string | null
  region: string | null
  concern_tags: string[]
  guardian_name: string | null
  guardian_relation: string | null
  guardian_email: string | null
  guardian_notify_enabled: boolean | null
}

export interface RecentDetection {
  detection_type: string
  risk_level: string | null
  created_at: string
}

export interface RecentReport {
  report_id: string
  type: string
  description: string
  status: string
  created_at: string
}

export interface RecentEvidence {
  id: number
  news_id: string
  content: string
  status: string
  submitted_at: string
}

export interface RecentChat {
  id: string
  title: string
  message_count: number
  created_at: string
}

export interface BehaviorStats {
  detection_count: number
  fact_check_count: number
  report_count: number
  evidence_count: number
  chat_count: number
  recent_detections: RecentDetection[]
  recent_reports: RecentReport[]
  recent_evidences: RecentEvidence[]
  recent_chats: RecentChat[]
}

export interface RoleDefenseStrategy {
  role_label: string
  risk_summary: string
  high_risk_types: string[]
  defense_tips: string[]
}

export interface UserProfileResponse {
  username: string
  profile: ProfileData
  stats: BehaviorStats
  role_defense: RoleDefenseStrategy
}

export interface ProfileUpdatePayload {
  age_group?: string | null
  gender?: string | null
  occupation?: string | null
  region?: string | null
  concern_tags?: string[]
  guardian_name?: string | null
  guardian_relation?: string | null
  guardian_email?: string | null
  guardian_notify_enabled?: boolean | null
}

export interface SuggestionResponse {
  suggestions: string[]
}

export const profileApi = {
  async getMe() {
    const { data } = await api.get<UserProfileResponse>('/profile/me')
    return data
  },

  async updateMe(payload: ProfileUpdatePayload) {
    const { data } = await api.put<UserProfileResponse>('/profile/me', payload)
    return data
  },

  async getSuggestions() {
    const { data } = await api.get<SuggestionResponse>('/profile/suggestions')
    return data
  },

  async withdrawReport(reportId: string) {
    const { data } = await api.delete(`/report/withdraw/${reportId}`)
    return data as { message: string; report_id: string }
  },
}
