from typing import List, Dict, Any

def search(query: str, namespace: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search vector database for API schemas or regulations. Similarity threshold >= 0.70.
    """
    return [
        {
            "chunk_id": "api_stub_1",
            "content": f"Mock API endpoint specification matching '{query}' in namespace '{namespace}'",
            "similarity": 0.82,
            "metadata": {"endpoint_path": "/payments", "method": "POST"}
        }
    ]
