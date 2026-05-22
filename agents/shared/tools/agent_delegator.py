import os

def call_agent(agent_type: str, query: str, context: str, call_depth: int) -> list[dict]:
    """
    Triggers peer-to-peer delegation to another compliance agent.
    Enforces a strict recursion depth ceiling (call_depth < 2).
    Imports graphs dynamically to prevent circular dependencies.
    """
    print(f"[Delegator] Delegating query to '{agent_type}' at call depth: {call_depth}")
    
    if call_depth >= 2:
        print("[Delegator] Max delegation depth reached. Blocking call.")
        return [{
            "status": "error",
            "message": f"Delegation to '{agent_type}' blocked: maximum depth limit of 2 exceeded.",
            "severity": "HIGH",
            "gap_description": f"Auditor attempted to delegate cross-domain query '{query}' but delegation ceiling was hit."
        }]
        
    # Prepare initial state for the sub-agent
    delegated_state = {
        "job_id": f"delegated_{agent_type}_{os.urandom(4).hex()}",
        "agent_domain": agent_type,
        "mode": "full_diagnosis",
        "call_depth": call_depth + 1,
        # Create a virtual regulation chunk containing the delegation query
        "regulation_chunks": [{
            "id": f"delegated_chunk_{os.urandom(4).hex()}",
            "content": f"Audit query: {query}. Context: {context}",
            "metadata": {"is_mandatory": True, "document_id": "delegated_ref"}
        }],
        "current_chunk_index": 0,
        "findings": [],
        "retry_count": 0,
        "session_memory": [],
        "report_url": ""
    }
    
    try:
        if agent_type == "rbi_compliance":
            from agents.rbi_compliance.graph import app as rbi_app
            sub_graph = rbi_app
        elif agent_type == "api_compliance":
            from agents.api_compliance.graph import app as api_app
            sub_graph = api_app
        elif agent_type == "codebase":
            from agents.codebase.graph import app as codebase_app
            sub_graph = codebase_app
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        # Run sub-agent graph execution
        result_state = sub_graph.invoke(delegated_state)
        return result_state.get("findings", [])
        
    except Exception as e:
        print(f"[Delegator] Error executing delegated graph for '{agent_type}': {e}")
        return [{
            "status": "error",
            "message": f"Failed to execute delegation to {agent_type}: {str(e)}",
            "severity": "HIGH",
            "gap_description": f"Delegation error occurred: {str(e)}"
        }]
