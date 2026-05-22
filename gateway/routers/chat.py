from fastapi import APIRouter, HTTPException
import json
from shared.models import ChatMessage, ChatResponse
from shared.redis_client import get_redis_connection
from shared.gemini_client import get_gemini_model
from agents.shared.tools.vector_search import search

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def session_chat(payload: ChatMessage):
    """
    Handles Mode C synchronous chat:
    1. Reads session history from Upstash Redis using payload.session_id (TTL 30m)
    2. Performs vector search across all namespaces for grounded context
    3. Prompts Gemini with context and history to generate a grounded response
    4. Updates session memory in Redis and returns response to client
    """
    try:
        r = get_redis_connection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")
        
    session_key = f"chat:{payload.session_id}"
    
    # 1. Read history
    try:
        history_str = r.get(session_key)
        history = json.loads(history_str) if history_str else []
    except Exception as e:
        print(f"Error reading chat history from Redis: {e}")
        history = []
        
    # 2. Vector Search for relevant context
    context_chunks = []
    # Search all namespaces that might contain relevant knowledge
    for ns in ["rbi_compliance_regulation", "api_specs", "codebase"]:
        try:
            res = search(payload.message, ns, top_k=2)
            context_chunks.extend(res)
        except Exception as e:
            print(f"Error querying namespace {ns}: {e}")
            
    # Sort candidates by similarity
    context_chunks.sort(key=lambda x: x.get("similarity", 0.0), reverse=True)
    top_context = context_chunks[:4]
    
    # 3. Construct grounding context text
    context_lines = []
    for c in top_context:
        ns = c.get("metadata", {}).get("namespace", "unknown")
        context_lines.append(f"Source ({ns}):\n{c['content']}")
    context_text = "\n\n".join(context_lines)
    
    # Construct history
    # Keep last 6 turns (12 messages)
    history_subset = history[-12:]
    history_text = ""
    for msg in history_subset:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"
        
    # Construct final prompt
    prompt = (
        "You are an expert compliance auditing assistant for BankGuard.\n"
        "Your goal is to answer the user's question, grounded strictly in the provided context and history.\n"
        "If the context does not contain the answer, say that you cannot find the answer in the local compliance documents.\n\n"
        f"Grounded Context:\n{context_text}\n\n"
        f"Conversation History:\n{history_text}"
        f"User: {payload.message}\n"
        "Assistant:"
    )
    
    # Generate content via Gemini
    try:
        model = get_gemini_model("gemini-1.5-pro")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
        
    # 4. Generate citations list
    citations = []
    for c in top_context:
        meta = c.get("metadata", {})
        doc_id = meta.get("document_id", "unknown")
        file_path = meta.get("file_path") or meta.get("file_name") or c.get("id")[:8]
        citations.append(f"{meta.get('namespace', 'unknown')}:{file_path}")
        
    # Deduplicate citations
    citations = list(dict.fromkeys(citations))
    
    # 5. Save updated history to Redis
    try:
        history.append({"role": "user", "content": payload.message})
        history.append({"role": "model", "content": response_text})
        r.setex(session_key, 1800, json.dumps(history)) # TTL 30 minutes
    except Exception as e:
        print(f"Error saving chat history to Redis: {e}")
        
    return {
        "session_id": payload.session_id,
        "response_text": response_text,
        "citations": citations
    }

