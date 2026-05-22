from fastapi import APIRouter, Depends, HTTPException
from typing import List
from shared.models import QuestionSchema

router = APIRouter()

@router.get("/", response_model=List[QuestionSchema])
async def get_predefined_questions(agent_domain: str):
    """
    Fetches active predefined questions for the given domain from Supabase.
    """
    # Stub response
    return [
        {
            "id": "q1",
            "agent_domain": agent_domain,
            "question_text": "Does the payment infrastructure enforce TLS 1.2+ for client communication?",
            "is_active": True
        },
        {
            "id": "q2",
            "agent_domain": agent_domain,
            "question_text": "Is access control configured using role-based policies (RBAC)?",
            "is_active": True
        }
    ]

@router.post("/run")
async def run_predefined_questions(agent_domain: str):
    """
    Triggers Mode B audit: fetches active questions and enqueues a batch diagnosis job.
    """
    return {
        "status": "enqueued",
        "job_id": "job_predefined_stub",
        "questions_count": 2
    }
