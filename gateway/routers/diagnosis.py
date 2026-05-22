from fastapi import APIRouter, HTTPException, Depends
from shared.models import DiagnoseRequest, JobStatusResponse
# Stub references to db and redis enqueuers to be filled during logic implementation
# from shared.db import supabase_client
# from shared.redis_client import get_redis_client

router = APIRouter()

@router.post("/diagnose", response_model=JobStatusResponse)
async def create_diagnosis_job(payload: DiagnoseRequest):
    """
    1. Validate permissions
    2. Write PENDING row in Supabase jobs table
    3. Enqueue job on Redis (ARQ worker) with call_depth=0
    4. Return status info with job_id
    """
    # Stub response
    return {
        "job_id": "job_123456789_stub",
        "status": "PENDING",
        "agent_type": payload.agent_type,
        "mode": payload.mode,
        "report_url": None
    }

@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Query Supabase jobs table for the current job status
    """
    # Stub response
    return {
        "job_id": job_id,
        "status": "READY",
        "agent_type": "rbi_compliance",
        "mode": "full_diagnosis",
        "report_url": "https://r2.bankguard.dev/reports/stub_report.pdf"
    }
