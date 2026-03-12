from pydantic import BaseModel, Field


class EducationStage(BaseModel):
    stage_id: str
    name: str
    description: str


class EducationCase(BaseModel):
    case_id: str
    title: str
    summary: str
    analysis: str
    tips: list[str] = Field(default_factory=list)


class EducationStageDetailResponse(BaseModel):
    stage_id: str
    name: str
    description: str
    cases: list[EducationCase] = Field(default_factory=list)


class EducationQuestion(BaseModel):
    question_id: str
    question: str
    options: list[str] = Field(default_factory=list)
    answer: int = 0
    explanation: str = ""
    category: str = ""
    difficulty: str = "beginner"
    fraud_type: str = ""
    source_type: str = "static"


class EducationQuestionPublic(BaseModel):
    question_id: str
    question: str
    options: list[str] = Field(default_factory=list)
    category: str = ""
    difficulty: str = "beginner"
    fraud_type: str = ""
    source_type: str = "static"


class EducationQuestionsResponse(BaseModel):
    items: list[EducationQuestionPublic] = Field(default_factory=list)
    total: int = 0


class SubmitTestRequest(BaseModel):
    question_ids: list[str] = Field(default_factory=list)
    answers: dict[str, int] = Field(default_factory=dict)


class SubmitTestDetail(BaseModel):
    question_id: str
    question: str
    options: list[str] = Field(default_factory=list)
    selected: int | None = None
    correct_answer: int
    is_correct: bool
    explanation: str = ""
    category: str = ""
    difficulty: str = "beginner"
    fraud_type: str = ""
    source_type: str = "static"


class WeaknessItem(BaseModel):
    fraud_type: str
    wrong_count: int = 0
    total: int = 0
    accuracy: float = 0.0
    suggestion: str = ""


class TrendPoint(BaseModel):
    timestamp: str
    score: float
    passed: bool


class SubmitTestResponse(BaseModel):
    total: int = 0
    correct: int = 0
    score: float = 0.0
    passed: bool = False
    details: list[SubmitTestDetail] = Field(default_factory=list)
    risk_profile: str = "medium"
    weaknesses: list[WeaknessItem] = Field(default_factory=list)
    recommended_stage: str = "beginner"
    next_actions: list[str] = Field(default_factory=list)
    summary: str = ""
    recent_trend: list[TrendPoint] = Field(default_factory=list)
    trend_delta: float | None = None
    learning_objective: str = ""
    knowledge_gaps: list[str] = Field(default_factory=list)
    micro_lessons: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    coach_feedback: str = ""
    next_plan: list[str] = Field(default_factory=list)


class EducationCoachRequest(BaseModel):
    question: str = ""
    stage_id: str | None = None
    score: float | None = None
    wrong_topics: list[str] = Field(default_factory=list)


class EducationCoachResponse(BaseModel):
    reply: str = ""
    actions: list[str] = Field(default_factory=list)
