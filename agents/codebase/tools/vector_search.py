from typing import List, Dict, Any

def search(query: str, namespace: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search vector database for codebase chunks or regulations. Similarity threshold >= 0.70.
    """
    return [
        {
            "chunk_id": "code_stub_1",
            "content": f"def payment_client():\\n    # Mock function matching '{query}'",
            "similarity": 0.85,
            "metadata": {"file_path": "payment_client.py", "line_range": [30, 60]}
        }
    ]
