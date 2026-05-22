from typing import List, Dict, Any

def expand(chunk_id: str, window: int = 2) -> List[Dict[str, Any]]:
    """
    Fetches adjacent specification or regulation chunks.
    """
    return [
        {
            "chunk_id": chunk_id,
            "content": "Expanded OpenAPI segment context...",
            "metadata": {"endpoint_path": "/payments"}
        }
    ]
