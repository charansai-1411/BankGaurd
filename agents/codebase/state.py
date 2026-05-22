from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    job_id: str
    agent_domain: str
    mode: str
    call_depth: int
    regulation_chunks: List[Dict[str, Any]]
    current_chunk_index: int
    findings: List[Dict[str, Any]]
    retry_count: int
    session_memory: List[Dict[str, Any]]
    report_url: str
