from typing import Dict, Any

async def call_agent(agent_type: str, query: str, context: str, call_depth: int) -> Dict[str, Any]:
    """
    Delegation tool routing tasks between agents. Enforces call_depth limit of 2.
    """
    if call_depth >= 2:
        return {
            "status": "error",
            "message": f"Max call depth reached ({call_depth}). Analysis restricted to current agent scope."
        }
        
    # Stub peer calling dispatch logic
    return {
        "status": "success",
        "originating_agent": agent_type,
        "query": query,
        "findings": [
            {
                "regulation_clause_ref": "4.3",
                "finding_text": f"Mock peer finding for '{query}' at depth {call_depth + 1}",
                "severity": "HIGH"
            }
        ]
    }
