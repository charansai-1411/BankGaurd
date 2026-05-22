from typing import List, Dict, Any

def expand(chunk_id: str, window: int = 2) -> List[Dict[str, Any]]:
    """
    Fetches chunks before and after a given chunk by index.
    """
    # Stub database fetch
    return [
        {
            "chunk_id": "c_stub_prev",
            "content": "Previous chunk context...",
            "metadata": {"chunk_index": 0}
        },
        {
            "chunk_id": chunk_id,
            "content": "Core chunk content...",
            "metadata": {"chunk_index": 1}
        },
        {
            "chunk_id": "c_stub_next",
            "content": "Following chunk context...",
            "metadata": {"chunk_index": 2}
        }
    ]
