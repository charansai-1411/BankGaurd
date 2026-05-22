from pydantic import BaseModel, Field
from typing import List, Optional

class DiagnoseRequest(BaseModel):
    agent_type: str = Field(..., description="Target compliance agent (rbi_compliance, api_compliance, codebase)")
    mode: str = Field(..., description="Analysis mode (full_diagnosis, predefined_questions)")

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    agent_type: str
    mode: str
    report_url: Optional[str] = None

class QuestionSchema(BaseModel):
    id: str
    agent_domain: str
    question_text: str
    is_active: bool

class ChatMessage(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response_text: str
    citations: List[str]

class GapFinding(BaseModel):
    regulation_clause_ref: str
    originating_agent: str
    finding_text: str
    severity: str
    evidence_verified: bool
    similarity_score: float
