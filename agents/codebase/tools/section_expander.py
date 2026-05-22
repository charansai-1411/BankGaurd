from typing import List, Dict, Any

def expand(chunk_id: str, window: int = 2) -> List[Dict[str, Any]]:
    """
    Fetches adjacent file line ranges or code chunks.
    """
    return [
        {
            "chunk_id": chunk_id,
            "content": "Expanded source code scope...",
            "metadata": {"file_path": "payment_client.py"}
        }
    ]
