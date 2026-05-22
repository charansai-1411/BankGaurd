import asyncio
import os
from arq import cron

from shared.db import get_db_client
from shared.r2_client import upload_file_to_r2
from shared.redis_client import get_arq_redis_settings
from worker.report_generator import generate_pdf_report

async def run_compliance_diagnosis(ctx, job_id: str, agent_type: str, mode: str):
    """
    Background compliance audit job:
    1. Update job status to RUNNING in Supabase.
    2. Load predefined questions if mode is 'predefined_questions'.
    3. Import the correct Agent Graph.
    4. Run agent graph invocation in a separate thread.
    5. Map findings to HTML template requirements.
    6. Generate report PDF/HTML.
    7. Upload the compiled report to Cloudflare R2 bucket.
    8. Update job status to READY and save pre-signed R2 URL.
    9. Clean up local temp files.
    """
    print(f"Starting async audit job: {job_id} for agent: {agent_type} (mode: {mode})")
    db = get_db_client()
    
    # 1. Update job status to RUNNING
    db.table("jobs").update({"status": "RUNNING"}).eq("id", job_id).execute()
    
    local_report_path = ""
    try:
        # 2. Dynamic graph import
        if agent_type == "rbi_compliance":
            from agents.rbi_compliance.graph import app as graph_app
        elif agent_type == "api_compliance":
            from agents.api_compliance.graph import app as graph_app
        elif agent_type == "codebase":
            from agents.codebase.graph import app as graph_app
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        # 3. Prepare initial state
        initial_state = {
            "job_id": job_id,
            "agent_domain": agent_type,
            "mode": mode,
            "findings": [],
            "retry_count": 0,
            "session_memory": [],
            "report_url": ""
        }
        
        # Load predefined questions for predefined questions mode
        if mode == "predefined_questions":
            questions_res = db.table("predefined_questions").select("*").eq("agent_domain", agent_type).eq("is_active", True).execute()
            chunks = []
            for q in (questions_res.data or []):
                chunks.append({
                    "id": str(q["id"]),
                    "content": q["question_text"],
                    "metadata": {
                        "is_mandatory": True,
                        "document_id": "predefined_question"
                    }
                })
            initial_state["regulation_chunks"] = chunks
            
        # 4. Run LangGraph reasoner loop in thread to prevent blocking the event loop
        result_state = await asyncio.to_thread(graph_app.invoke, initial_state)
        findings = result_state.get("findings", [])
        
        # 5. Map findings to PDF template expected keys
        mapped_findings = []
        for f in findings:
            # Check if this finding represents a compliance gap
            is_gap = f.get("has_gap", True)
            if isinstance(is_gap, str):
                is_gap = is_gap.lower() in ("true", "1", "yes")
                
            # Keep errors and explicit gaps
            if not is_gap and f.get("status") != "error":
                continue
                
            ref = f.get("regulation_clause_ref") or f.get("chunk_id") or "N/A"
            if ref.startswith("delegated_chunk_") or ref.startswith("predefined_question_"):
                ref = "Delegated Ref"
                
            finding_text = f.get("finding_text") or f.get("gap_description") or f.get("message") or "Compliance gap identified."
            severity = f.get("severity") or "MEDIUM"
            origin = f.get("originating_agent") or agent_type
            
            mapped_findings.append({
                "regulation_clause_ref": ref,
                "originating_agent": origin,
                "finding_text": finding_text,
                "severity": severity
            })
            
        # 6. Generate report PDF/HTML
        os.makedirs("scratch", exist_ok=True)
        report_filename = f"compliance_report_{job_id}.pdf"
        local_report_path = os.path.join("scratch", report_filename)
        
        await asyncio.to_thread(generate_pdf_report, mapped_findings, local_report_path)
        
        # 7. Upload report to Cloudflare R2
        r2_url = await asyncio.to_thread(upload_file_to_r2, local_report_path, report_filename)
        print(f"Uploaded report to R2. URL: {r2_url}")
        
        # 8. Mark job READY in Supabase and save URL
        db.table("jobs").update({
            "status": "READY",
            "report_url": r2_url
        }).eq("id", job_id).execute()
        
        print(f"Finished audit job: {job_id} successfully.")
        return r2_url
        
    except Exception as e:
        print(f"Error executing compliance diagnosis job {job_id}: {e}")
        try:
            db.table("jobs").update({"status": "FAILED"}).eq("id", job_id).execute()
        except Exception as db_err:
            print(f"Failed to set job status to FAILED in database: {db_err}")
        raise e
        
    finally:
        # 9. Clean up temporary files
        try:
            if local_report_path:
                if os.path.exists(local_report_path):
                    os.remove(local_report_path)
                html_path = local_report_path + ".html"
                if os.path.exists(html_path):
                    os.remove(html_path)
        except Exception as cleanup_err:
            print(f"Cleanup warning: {cleanup_err}")

class WorkerSettings:
    functions = [run_compliance_diagnosis]
    redis_settings = get_arq_redis_settings()

