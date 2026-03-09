import api from './index'

export interface ProfileData {
  age_group: string | null
  gender: string | null
  occupation: string | null
  region: string | null
  concern_tags: string[]
}

export interface RecentDetection {
  detection_type: string
  risk_level: string | null
  created_at: string
}

export interface BehaviorStats {
  detection_count: number
  fact_check_count: number
  report_count: number
  evidence_count: number
  chat_count: number
  recent_detections: RecentDetection[]
}

export interface UserProfileResponse {
  username: string
  profile: ProfileData
  stats: BehaviorStats
}

export interface ProfileUpdatePayload {
  age_group?: string | null
  gender?: string | null
  occupation?: string | null
  region?: string | null
  concern_tags?: string[]
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
}
