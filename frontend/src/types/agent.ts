import type { ProfileData } from '@/api/profile'
import type { RagSource } from '@/types/rag'

export interface AgentSignal {
  modality: string
  signal: string
  score: number
}

export interface GuardianActionInfo {
  priority: string
  notice: string
  triggered: boolean
  target_role: string
  message_template: string
  next_step: string
  checklist: string[]
}

export interface GuardianNotificationInfo {
  attempted: boolean
  sent: boolean
  status: string
  message: string
  recipient_masked: string
}

export interface AgentIntentInfo {
  code: string
  label: string
  confidence: number
  reason: string
}

export interface AgentFraudTypeInfo {
  code: string
  label: string
  confidence: number
  rationale: string
}

export interface AgentEvidenceItem {
  title: string
  source: string
  snippet: string
  score: number
  modality: string
  kind: string
}

export interface AgentInterventionAction {
  label: string
  description: string
  priority: string
}

export interface AgentInterventionPlan {
  level: string
  headline: string
  summary: string
  recommended_channel: string
  actions: AgentInterventionAction[]
}

export interface AgentReportInfo {
  title: string
  executive_summary: string
  findings: string[]
  disposition: string
  recommended_actions: string[]
}

export interface AgentAnalyzeResponse {
  risk_level: string
  risk_score: number
  intent: AgentIntentInfo
  fraud_type: AgentFraudTypeInfo
  fraud_types: string[]
  evidence: AgentEvidenceItem[]
  intervention_plan: AgentInterventionPlan
  modalities_received: string[]
  signals: AgentSignal[]
  text_result: Record<string, any>
  image_result: Record<string, any>
  audio_result: Record<string, any>
  rag_sources: RagSource[]
  profile_summary: ProfileData
  recommendations: string[]
  guardian_action_needed: boolean
  guardian_action: GuardianActionInfo
  guardian_notification: GuardianNotificationInfo
  user_ack_required: boolean
  report: AgentReportInfo
  summary: string
}
