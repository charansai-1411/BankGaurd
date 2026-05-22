from typing import Dict, Any

async def call_agent(agent_type: str, query: str, context: str, call_depth: int) -> Dict[str, Any]:
    """
    API compliance agent delegation call. Max depth check = 2.
    Can only delegate downwards (e.g. to Codebase Agent).
    """
    if call_depth >= 2:
        return {
            "status": "error",
            "message": "Max call depth reached. Analysis restricted to current API scope."
        }
        
    return {
        "status": "success",
        "originating_agent": agent_type,
        "query": query,
        "findings": [
            {
                "regulation_clause_ref": "TLS-1.2",
                "finding_text": f"API delegation codebase result for query: {query}",
                "severity": "CRITICAL"
            }
        ]
    }
