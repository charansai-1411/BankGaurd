from typing import Dict, Any

async def call_agent(agent_type: str, query: str, context: str, call_depth: int) -> Dict[str, Any]:
    """
    Codebase agent is terminal and cannot delegate further.
    """
    return {
        "status": "error",
        "message": "Codebase Agent is a terminal node and cannot delegate further."
    }
