"""Profile schemas for user profile and behavior stats."""
from typing import Optional

from pydantic import BaseModel, Field


class UserProfileUpdate(BaseModel):
    age_group: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    region: Optional[str] = None
    concern_tags: Optional[list[str]] = None
    guardian_name: Optional[str] = None
    guardian_relation: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_notify_enabled: Optional[bool] = None


class RecentDetection(BaseModel):
    detection_type: str = ""
    risk_level: Optional[str] = None
    created_at: str = ""


class RecentReport(BaseModel):
    report_id: str = ""
    type: str = ""
    description: str = ""
    status: str = ""
    created_at: str = ""


class RecentEvidence(BaseModel):
    id: int = 0
    news_id: str = ""
    content: str = ""
    status: str = ""
    submitted_at: str = ""


class RecentChat(BaseModel):
    id: str = ""
    title: str = ""
    message_count: int = 0
    created_at: str = ""


class BehaviorStats(BaseModel):
    detection_count: int = 0
    fact_check_count: int = 0
    report_count: int = 0
    evidence_count: int = 0
    chat_count: int = 0
    recent_detections: list[RecentDetection] = Field(default_factory=list)
    recent_reports: list[RecentReport] = Field(default_factory=list)
    recent_evidences: list[RecentEvidence] = Field(default_factory=list)
    recent_chats: list[RecentChat] = Field(default_factory=list)


class ProfileData(BaseModel):
    age_group: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    region: Optional[str] = None
    concern_tags: list[str] = Field(default_factory=list)
    guardian_name: Optional[str] = None
    guardian_relation: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_notify_enabled: Optional[bool] = None


class RoleDefenseStrategy(BaseModel):
    role_label: str = ""
    risk_summary: str = ""
    high_risk_types: list[str] = Field(default_factory=list)
    defense_tips: list[str] = Field(default_factory=list)


class UserProfileResponse(BaseModel):
    username: str = ""
    profile: ProfileData = Field(default_factory=ProfileData)
    stats: BehaviorStats = Field(default_factory=BehaviorStats)
    role_defense: RoleDefenseStrategy = Field(default_factory=RoleDefenseStrategy)


class SuggestionResponse(BaseModel):
    suggestions: list[str] = Field(default_factory=list)
