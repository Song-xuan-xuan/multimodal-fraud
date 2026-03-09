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


class EducationQuestionPublic(BaseModel):
    question_id: str
    question: str
    options: list[str] = Field(default_factory=list)


class EducationQuestionsResponse(BaseModel):
    items: list[EducationQuestionPublic] = Field(default_factory=list)


class SubmitTestRequest(BaseModel):
    answers: dict[str, int] = Field(default_factory=dict)


class SubmitTestResponse(BaseModel):
    total: int = 0
    correct: int = 0
    score: float = 0.0
    passed: bool = False
    details: list[dict] = Field(default_factory=list)
