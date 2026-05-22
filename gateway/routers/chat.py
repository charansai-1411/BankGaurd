from fastapi import APIRouter, HTTPException
from shared.models import ChatMessage, ChatResponse

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def session_chat(payload: ChatMessage):
    """
    Handles Mode C synchronous chat:
    1. Reads session history from Upstash Redis using payload.session_id (TTL 30m)
    2. Forwards query + history to agent-specific synchronous endpoint
    3. Receives strict grounded response
    4. Updates session memory in Redis and returns response to client
    """
    # Stub response
    return {
        "session_id": payload.session_id,
        "response_text": "This is a mock chat response grounded in the retrieved compliance documents.",
        "citations": ["rbi_regulation:chunk_42", "bank_doc:chunk_107"]
    }
