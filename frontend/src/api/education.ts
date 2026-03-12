import api from './index'

export interface EducationStage {
  stage_id: string
  name: string
  description: string
}

export interface EducationCase {
  case_id: string
  title: string
  summary: string
  analysis: string
  tips: string[]
}

export interface EducationStageDetail {
  stage_id: string
  name: string
  description: string
  cases: EducationCase[]
}

export interface EducationQuestionItem {
  question_id: string
  question: string
  options: string[]
  category: string
  difficulty: string
  fraud_type: string
  source_type: string
}

export interface EducationQuestionsResponse {
  items: EducationQuestionItem[]
  total: number
}

export interface SubmitTestDetail {
  question_id: string
  question: string
  options: string[]
  selected: number | null
  correct_answer: number
  is_correct: boolean
  explanation: string
  category: string
  difficulty: string
  fraud_type: string
  source_type: string
}

export interface WeaknessItem {
  fraud_type: string
  wrong_count: number
  total: number
  accuracy: number
  suggestion: string
}

export interface TrendPoint {
  timestamp: string
  score: number
  passed: boolean
}

export interface SubmitTestResponse {
  total: number
  correct: number
  score: number
  passed: boolean
  details: SubmitTestDetail[]
  risk_profile: 'low' | 'medium' | 'high' | string
  weaknesses: WeaknessItem[]
  recommended_stage: 'beginner' | 'intermediate' | 'advanced' | string
  next_actions: string[]
  summary: string
  recent_trend: TrendPoint[]
  trend_delta: number | null
  learning_objective: string
  knowledge_gaps: string[]
  micro_lessons: string[]
  common_mistakes: string[]
  coach_feedback: string
  next_plan: string[]
}

export interface EducationCoachResponse {
  reply: string
  actions: string[]
}

export const educationApi = {
  async getStages() {
    const { data } = await api.get('/education/stages')
    return data as EducationStage[]
  },

  async getStage(stageId: string) {
    const { data } = await api.get(`/education/stage/${stageId}`)
    return data as EducationStageDetail
  },

  async getQuestions(params?: { count?: number; stageId?: string; refresh?: boolean }) {
    const { data } = await api.get('/education/questions', {
      params: {
        count: params?.count,
        stage_id: params?.stageId,
        refresh: params?.refresh || undefined,
      },
    })
    return data as EducationQuestionsResponse
  },

  async submitTest(payload: { question_ids: string[]; answers: Record<string, number> }) {
    const { data } = await api.post('/education/submit-test', payload)
    return data as SubmitTestResponse
  },

  async askCoach(payload: { question: string; stage_id?: string; score?: number; wrong_topics?: string[] }) {
    const { data } = await api.post('/education/coach', payload)
    return data as EducationCoachResponse
  },
}
