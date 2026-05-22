import math
import json
from shared.db import get_db_client
from shared.gemini_client import get_embedding, get_gemini_model

def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

def magnitude(v):
    return math.sqrt(sum(x * x for x in v))

def cosine_similarity(v1, v2):
    mag1 = magnitude(v1)
    mag2 = magnitude(v2)
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product(v1, v2) / (mag1 * mag2)

def check_semantic_relevance(query: str, chunk_content: str) -> bool:
    """
    Uses Gemini to semantically check if a chunk is relevant to the query.
    Used as a fallback filter when the cosine similarity score is borderline (0.60 to 0.70).
    """
    try:
        # Use gemini-1.5-pro or fallback model
        model = get_gemini_model("gemini-1.5-pro")
        prompt = (
            f"You are a compliance audit agent. Determine if the document chunk below is "
            f"semantically relevant and helpful for verifying the following query.\n\n"
            f"Query: {query}\n\n"
            f"Document Chunk: {chunk_content}\n\n"
            f"Respond with ONLY 'YES' if it is relevant and can be used to audit/verify the query, "
            f"or 'NO' if it is irrelevant. Do not output anything else."
        )
        response = model.generate_content(prompt)
        decision = response.text.strip().upper()
        return "YES" in decision
    except Exception as e:
        print(f"Error in check_semantic_relevance: {e}")
        return False

def search(query: str, namespace: str, top_k: int = 5, document_id: str = None) -> list[dict]:
    """
    Vector similarity search against the vector_store table.
    Filters by namespace and optionally document_id.
    Computes cosine similarity in Python and applies dynamic 0.70 threshold (with 0.60-0.70 LLM fallback).
    """
    db = get_db_client()
    query_emb = get_embedding(query)
    
    # 1. Fetch candidates from database
    builder = db.table("vector_store").select("id, namespace, content, embedding, metadata").eq("namespace", namespace).eq("is_active", True)
    
    if document_id:
        # Filter by document_id stored inside jsonb metadata column
        builder = builder.filter("metadata->>document_id", "eq", document_id)
        
    response = builder.execute()
    records = response.data
    
    # 2. Compute similarities
    scored_records = []
    for r in records:
        emb_data = r["embedding"]
        if isinstance(emb_data, str):
            emb_data = json.loads(emb_data)
            
        sim = cosine_similarity(query_emb, emb_data)
        
        # Dynamic threshold verification
        is_relevant = False
        if sim >= 0.70:
            is_relevant = True
        elif sim >= 0.60:
            # Borderline score, run Gemini semantic filter fallback
            is_relevant = check_semantic_relevance(query, r["content"])
            
        if is_relevant:
            scored_records.append({
                "id": r["id"],
                "content": r["content"],
                "metadata": r["metadata"],
                "similarity": sim
            })
            
    # Sort and return top_k
    scored_records.sort(key=lambda x: x["similarity"], reverse=True)
    return scored_records[:top_k]

def expand(chunk_id: str, window: int = 2) -> list[dict]:
    """
    Retrieves the context surrounding a target chunk inside the same namespace and document.
    """
    db = get_db_client()
    
    # Fetch target chunk metadata to know the document_id and chunk_index (if present)
    target_res = db.table("vector_store").select("namespace, metadata").eq("id", chunk_id).execute()
    if not target_res.data:
        return []
        
    target = target_res.data[0]
    namespace = target["namespace"]
    metadata = target["metadata"]
    document_id = metadata.get("document_id")
    
    # If the chunks don't have explicit line/index numbers, we fetch all for this document
    builder = db.table("vector_store").select("id, content, metadata").eq("namespace", namespace).eq("is_active", True)
    if document_id:
        builder = builder.filter("metadata->>document_id", "eq", document_id)
        
    response = builder.execute()
    records = response.data
    
    # We can try to sort them.
    # Check if there is chunk_index or start_line in metadata to sort
    def get_sort_key(record):
        meta = record["metadata"]
        return meta.get("chunk_index") or meta.get("start_line") or 0
        
    records.sort(key=get_sort_key)
    
    # Find position of target chunk_id
    target_idx = -1
    for idx, r in enumerate(records):
        if r["id"] == chunk_id:
            target_idx = idx
            break
            
    if target_idx == -1:
        return []
        
    # Get window slice
    start = max(0, target_idx - window)
    end = min(len(records), target_idx + window + 1)
    
    return records[start:end]
