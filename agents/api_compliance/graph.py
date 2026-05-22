from langgraph.graph import StateGraph, END
from agents.api_compliance.state import AgentState

# Node stubs
def initialize_state(state: AgentState):
    return {"current_chunk_index": 0, "findings": [], "retry_count": 0}

def relevance_reasoner(state: AgentState):
    return state

def tool_caller(state: AgentState):
    return state

def gap_analyzer(state: AgentState):
    return state

def append_finding(state: AgentState):
    return {"current_chunk_index": state["current_chunk_index"] + 1}

def compile_report(state: AgentState):
    return state

# Routing functions
def route_relevance(state: AgentState):
    return "tool_caller"

def route_quality(state: AgentState):
    return "analyzer"

def route_next_chunk(state: AgentState):
    if state["current_chunk_index"] < len(state.get("regulation_chunks", [])):
        return "relevance_reasoner"
    return "compile_report"

workflow = StateGraph(AgentState)

workflow.add_node("initialize", initialize_state)
workflow.add_node("relevance_reasoner", relevance_reasoner)
workflow.add_node("tool_caller", tool_caller)
workflow.add_node("gap_analyzer", gap_analyzer)
workflow.add_node("append_finding", append_finding)
workflow.add_node("compile_report", compile_report)

workflow.set_entry_point("initialize")
workflow.add_edge("initialize", "relevance_reasoner")

workflow.add_conditional_edges(
    "relevance_reasoner",
    route_relevance,
    {
        "skip": "append_finding",
        "tool_caller": "tool_caller",
        "delegate": "append_finding"
    }
)

workflow.add_conditional_edges(
    "tool_caller",
    route_quality,
    {
        "analyzer": "gap_analyzer",
        "retry": "tool_caller",
        "insufficient": "append_finding"
    }
)

workflow.add_edge("gap_analyzer", "append_finding")

workflow.add_conditional_edges(
    "append_finding",
    route_next_chunk,
    {
        "relevance_reasoner": "relevance_reasoner",
        "compile_report": "compile_report"
    }
)

workflow.add_edge("compile_report", END)

app = workflow.compile()
