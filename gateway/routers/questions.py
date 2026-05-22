from fastapi import APIRouter, Depends, HTTPException
from typing import List
from shared.models import QuestionSchema
from shared.db import get_db_client
from shared.redis_client import get_arq_redis_settings
from arq import create_pool

router = APIRouter()

@router.get("/", response_model=List[QuestionSchema])
async def get_predefined_questions(agent_domain: str):
    """
    Fetches active predefined questions for the given domain from Supabase.
    """
    db = get_db_client()
    try:
        res = db.table("predefined_questions").select("*").eq("agent_domain", agent_domain).eq("is_active", True).execute()
        questions = []
        for q in res.data:
            questions.append({
                "id": str(q["id"]),
                "agent_domain": q["agent_domain"],
                "question_text": q["question_text"],
                "is_active": q["is_active"]
            })
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/run")
async def run_predefined_questions(agent_domain: str):
    """
    Triggers Mode B audit: fetches active questions and enqueues a batch diagnosis job.
    """
    db = get_db_client()
    try:
        # Get count of active predefined questions first
        questions_res = db.table("predefined_questions").select("id").eq("agent_domain", agent_domain).eq("is_active", True).execute()
        q_count = len(questions_res.data) if questions_res.data else 0
        
        # 1. Create jobs row
        job_res = db.table("jobs").insert({
            "status": "PENDING",
            "agent_type": agent_domain,
            "mode": "predefined_questions"
        }).execute()
        
        if not job_res.data:
            raise HTTPException(status_code=500, detail="Failed to create job in database")
            
        job_id = job_res.data[0]["id"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    # 2. Enqueue background task
    try:
        settings = get_arq_redis_settings()
        pool = await create_pool(settings)
        await pool.enqueue_job("run_compliance_diagnosis", job_id=str(job_id), agent_type=agent_domain, mode="predefined_questions")
    except Exception as e:
        try:
            db.table("jobs").update({"status": "FAILED"}).eq("id", job_id).execute()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to enqueue background task: {str(e)}")
        
    return {
        "status": "enqueued",
        "job_id": str(job_id),
        "questions_count": q_count
    }

