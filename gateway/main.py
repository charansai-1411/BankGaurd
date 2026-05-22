import json
import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from gateway.middleware.auth import JWTAuthMiddleware
from gateway.routers import diagnosis, questions, chat
from shared.redis_client import get_redis_connection

app = FastAPI(
    title="BankGuard Gateway",
    description="Secure entry point and route dispatcher for BankGuard services",
    version="2.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Auth Middleware
app.add_middleware(JWTAuthMiddleware)

# Include Routers
app.add_include_router = app.include_router  # standard alias
app.include_router(diagnosis.router, prefix="/jobs", tags=["Diagnosis"])
app.include_router(questions.router, prefix="/questions", tags=["Predefined Questions"])
app.include_router(chat.router, prefix="/chat", tags=["Free Chat"])

@app.get("/diagnose/stream/{job_id}")
async def stream_diagnose_job(job_id: str):
    """
    SSE stream endpoint subscribing to Redis Pub/Sub channel for a given job_id.
    Yields data: {"agent": ..., "tool": ..., "status": ..., "message": ...}
    """
    async def event_generator():
        r = get_redis_connection()
        pubsub = r.pubsub()
        channel = f"job:stream:{job_id}"
        pubsub.subscribe(channel)
        
        # Send initial handshake event
        yield f"data: {json.dumps({'agent': 'system', 'tool': 'stream_connect', 'status': 'connected', 'message': 'SSE stream connected'})}\n\n"
        
        try:
            while True:
                # Synchronous pubsub.get_message check. Use short timeout.
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
                if message:
                    data = message["data"]
                    yield f"data: {data}\n\n"
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print(f"SSE client disconnected for job {job_id}")
            pubsub.unsubscribe(channel)
        except Exception as e:
            print(f"SSE stream error: {e}")
            pubsub.unsubscribe(channel)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "gateway"}
