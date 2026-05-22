# API Gateway Service — Context & Specifications

This component acts as the secure entry point for all client requests. It handles authorization, rate limiting, and route dispatching.

---

## 1. Goal
The primary objective of the Gateway is to authenticate and serialize requests. It acts as an orchestrator for async job initiation and direct synchronous chat streaming, maintaining the security boundary of the platform.

---

## 2. Operations & Routes

* **`POST /jobs/diagnose`**  
  * **Goal**: Initiates a Full Diagnosis (Mode A) or Predefined Questions (Mode B) run.
  * **Behavior**:
    1. Creates a new database row in Supabase `jobs` table with status `PENDING`.
    2. Enqueues a background ARQ job with `job_id`, `agent_type`, `mode`, and injects `call_depth=0` into the initial state.
    3. Returns `job_id` to client immediately.
* **`GET /jobs/{job_id}/status`**  
  * **Goal**: Provides the job's current status for frontend polling.
  * **Behavior**: Reads the `jobs` table in Supabase and returns the current state (`PENDING`, `RUNNING`, `READY`, `FAILED`) and report URL if complete.
* **`POST /jobs/chat`**  
  * **Goal**: Free Chat (Mode C).
  * **Behavior**: Bypasses ARQ workers and forwards query synchronously to the respective Agent's chat handler, supporting real-time streaming with Redis-cached session history.

---

## 3. Middleware & Security
* **Supabase JWT Middleware**: Intercepts headers, verifies client credentials against the Supabase project configuration, and decodes user context. Blocks request if validation fails.
* **Rate Limiting**: Restricts abuse on heavy endpoints (particularly vector generation and LLM calls).

---

## 4. Important to Remember
> [!WARNING]
> - **No Compliance Logic**: The Gateway must remain lightweight. Never run any vector search, LangGraph loops, or Gemini calls inside this service.
> - **Call Depth Boundary**: Always inject `call_depth=0` on new async jobs. Peer delegation calls are handled strictly internally by the agents; the Gateway should not handle recursion depth checks.
> - **Audit Trail Initiation**: Every job submission must write the initial audit event containing client IP, requesting user UID, and timestamp.
