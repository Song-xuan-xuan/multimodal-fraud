from typing import Any

from pydantic import BaseModel, Field

from app.schemas.profile import ProfileData
from app.schemas.rag import SourceNode


class ModalitySignal(BaseModel):
    modality: str = ""
    signal: str = ""
    score: float = 0.0


class AgentIntentInfo(BaseModel):
    code: str = "general_consultation"
    label: str = "一般咨询"
    confidence: float = 0.0
    reason: str = ""


class FraudTypeInfo(BaseModel):
    code: str = "suspicious_script"
    label: str = "可疑诈骗话术"
    confidence: float = 0.0
    rationale: str = ""


class EvidenceItem(BaseModel):
    title: str = ""
    source: str = ""
    snippet: str = ""
    score: float = 0.0
    modality: str = ""
    kind: str = ""


class InterventionAction(BaseModel):
    label: str = ""
    description: str = ""
    priority: str = "medium"


class InterventionPlanInfo(BaseModel):
    level: str = "low"
    headline: str = ""
    summary: str = ""
    recommended_channel: str = ""
    actions: list[InterventionAction] = Field(default_factory=list)


class GuardianActionInfo(BaseModel):
    priority: str = "none"
    notice: str = ""
    triggered: bool = False
    target_role: str = ""
    message_template: str = ""
    next_step: str = ""
    checklist: list[str] = Field(default_factory=list)


class AgentReportInfo(BaseModel):
    title: str = "安全监测报告"
    executive_summary: str = ""
    findings: list[str] = Field(default_factory=list)
    disposition: str = ""
    recommended_actions: list[str] = Field(default_factory=list)


class AgentAnalyzeResponse(BaseModel):
    risk_level: str = "low"
    risk_score: float = 0.0
    intent: AgentIntentInfo = Field(default_factory=AgentIntentInfo)
    fraud_type: FraudTypeInfo = Field(default_factory=FraudTypeInfo)
    fraud_types: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    intervention_plan: InterventionPlanInfo = Field(default_factory=InterventionPlanInfo)
    modalities_received: list[str] = Field(default_factory=list)
    signals: list[ModalitySignal] = Field(default_factory=list)
    text_result: dict[str, Any] = Field(default_factory=dict)
    image_result: dict[str, Any] = Field(default_factory=dict)
    audio_result: dict[str, Any] = Field(default_factory=dict)
    rag_sources: list[SourceNode] = Field(default_factory=list)
    profile_summary: ProfileData = Field(default_factory=ProfileData)
    recommendations: list[str] = Field(default_factory=list)
    guardian_action_needed: bool = False
    guardian_action: GuardianActionInfo = Field(default_factory=GuardianActionInfo)
    report: AgentReportInfo = Field(default_factory=AgentReportInfo)
    summary: str = ""
