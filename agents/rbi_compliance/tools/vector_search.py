from typing import List, Dict, Any

def search(query: str, namespace: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    cosine_sim >= 0.70 search on vectors where is_active=true.
    """
    # Stub implementation to be hooked to Supabase pgvector client
    return [
        {
            "chunk_id": "c_stub_1",
            "content": f"Mock content matching '{query}' in namespace '{namespace}'",
            "similarity": 0.88,
            "metadata": {"chunk_index": 1, "document_id": "doc_stub"}
        }
    ]
