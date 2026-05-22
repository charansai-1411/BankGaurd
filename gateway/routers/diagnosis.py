from fastapi import APIRouter, HTTPException, Depends
from shared.models import DiagnoseRequest, JobStatusResponse
from shared.db import get_db_client
from shared.redis_client import get_arq_redis_settings
from arq import create_pool

router = APIRouter()

@router.post("/diagnose", response_model=JobStatusResponse)
async def create_diagnosis_job(payload: DiagnoseRequest):
    """
    1. Write PENDING row in Supabase jobs table
    2. Enqueue job on Redis (ARQ worker)
    3. Return status info with job_id
    """
    db = get_db_client()
    
    # 1. Create a PENDING job record in Supabase
    try:
        res = db.table("jobs").insert({
            "status": "PENDING",
            "agent_type": payload.agent_type,
            "mode": payload.mode
        }).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create job in database")
            
        job_data = res.data[0]
        job_id = job_data["id"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    # 2. Enqueue the task with ARQ
    try:
        settings = get_arq_redis_settings()
        pool = await create_pool(settings)
        await pool.enqueue_job("run_compliance_diagnosis", job_id=str(job_id), agent_type=payload.agent_type, mode=payload.mode)
    except Exception as e:
        # If enqueuing fails, transition the job to FAILED in the DB
        try:
            db.table("jobs").update({"status": "FAILED"}).eq("id", job_id).execute()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to enqueue background task: {str(e)}")
        
    return {
        "job_id": str(job_id),
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
    db = get_db_client()
    try:
        res = db.table("jobs").select("*").eq("id", job_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Job not found")
        job = res.data[0]
        return {
            "job_id": str(job["id"]),
            "status": job["status"],
            "agent_type": job["agent_type"],
            "mode": job["mode"],
            "report_url": job.get("report_url")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

