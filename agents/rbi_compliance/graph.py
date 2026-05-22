import json
from langgraph.graph import StateGraph, END
from agents.rbi_compliance.state import AgentState
from shared.db import get_db_client
from shared.gemini_client import get_gemini_model
from agents.shared.tools.vector_search import search
from agents.shared.tools.evidence_validator import validate
from agents.shared.tools.severity_calculator import calculate_severity
from agents.shared.tools.agent_delegator import call_agent
from agents.rbi_compliance.prompts import (
    RELEVANCE_SYSTEM_PROMPT,
    QUERY_GENERATOR_PROMPT,
    QUERY_REPHRASE_PROMPT,
    ANALYSIS_SYSTEM_PROMPT
)

def clean_json_response(text: str) -> str:
    """
    Cleans markdown formatting blocks (e.g. ```json ... ```) from Gemini responses.
    """
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

# Nodes
def initialize_state(state: AgentState):
    """
    Load regulation chunks for this agent domain.
    """
    domain = state.get("agent_domain") or "rbi_compliance"
    
    # Only fetch chunks if they aren't pre-populated (e.g. by tests/delegation)
    chunks = state.get("regulation_chunks")
    if not chunks:
        db = get_db_client()
        namespace = f"{domain}_regulation"
        response = db.table("vector_store").select("id, content, metadata").eq("namespace", namespace).eq("is_active", True).execute()
        chunks = response.data or []
        # Sort by chunk_index in metadata
        chunks.sort(key=lambda x: x.get("metadata", {}).get("chunk_index") or 0)
        
    return {
        "regulation_chunks": chunks,
        "current_chunk_index": 0,
        "findings": [],
        "retry_count": 0,
        "session_memory": []
    }

def relevance_reasoner(state: AgentState):
    """
    Evaluates current regulation chunk to decide: SKIP, INVESTIGATE, or DELEGATE.
    """
    idx = state["current_chunk_index"]
    chunks = state.get("regulation_chunks", [])
    
    if idx >= len(chunks):
        return {"session_memory": [{"decision": "SKIP"}]}
        
    current_chunk = chunks[idx]
    chunk_text = current_chunk["content"]
    
    model = get_gemini_model("gemini-1.5-pro")
    
    try:
        response = model.generate_content(
            f"{RELEVANCE_SYSTEM_PROMPT}\n\nRegulation Chunk Content:\n{chunk_text}"
        )
        cleaned = clean_json_response(response.text)
        result = json.loads(cleaned)
    except Exception as e:
        print(f"Error in relevance_reasoner parsing: {e}")
        # Default fallback to INVESTIGATE
        result = {
            "decision": "INVESTIGATE",
            "reason": "Failed to parse relevance JSON, fallback to standard investigation.",
            "delegation_target": None,
            "delegation_query": None
        }
        
    return {"session_memory": [result]}

def tool_caller(state: AgentState):
    """
    Invokes vector search tool or triggers inter-agent delegation.
    """
    idx = state["current_chunk_index"]
    chunk = state["regulation_chunks"][idx]
    chunk_text = chunk["content"]
    
    # Retrieve the decision from relevance reasoner stored in session_memory
    decision_obj = state["session_memory"][-1]
    decision = decision_obj.get("decision", "INVESTIGATE")
    
    model = get_gemini_model("gemini-1.5-flash")
    
    # 1. Handle Delegation
    if decision == "DELEGATE":
        target = decision_obj.get("delegation_target")
        query = decision_obj.get("delegation_query") or chunk_text
        call_depth = state.get("call_depth", 0)
        
        delegated_findings = call_agent(target, query, chunk_text, call_depth)
        
        # Merge delegated findings into main findings
        current_findings = list(state.get("findings", []))
        current_findings.extend(delegated_findings)
        
        return {"findings": current_findings, "session_memory": state["session_memory"] + [{"status": "delegated"}]}
        
    # 2. Handle Investigation (Vector Search)
    retry = state.get("retry_count", 0)
    
    # Generate search query
    if retry == 0:
        try:
            prompt = QUERY_GENERATOR_PROMPT.format(chunk_text=chunk_text)
            q_res = model.generate_content(prompt)
            query = q_res.text.strip()
        except Exception:
            query = chunk_text[:200]
    else:
        # Rephrase query for retry
        prev_query = state["session_memory"][-2].get("search_query", chunk_text[:200])
        try:
            prompt = QUERY_REPHRASE_PROMPT.format(original_query=prev_query, chunk_text=chunk_text)
            q_res = model.generate_content(prompt)
            query = q_res.text.strip()
        except Exception:
            query = f"{prev_query} compliance"
            
    # Search target bank policies
    target_namespace = f"{state.get('agent_domain')}_bank_doc"
    doc_id = chunk.get("metadata", {}).get("document_id")
    
    search_results = search(query=query, namespace=target_namespace, top_k=3, document_id=doc_id)
    
    # Store search metrics for conditional router
    max_sim = max([r["similarity"] for r in search_results]) if search_results else 0.0
    
    step_memory = {
        "search_query": query,
        "search_results": search_results,
        "max_similarity": max_sim
    }
    
    next_retry = retry
    if max_sim < 0.60:
        next_retry = retry + 1
        
    return {
        "session_memory": state["session_memory"] + [step_memory],
        "retry_count": next_retry
    }

def gap_analyzer(state: AgentState):
    """
    Compares mandate text against retrieved policies evidence to identify compliance gaps.
    """
    idx = state["current_chunk_index"]
    chunk = state["regulation_chunks"][idx]
    chunk_text = chunk["content"]
    
    step_memory = state["session_memory"][-1]
    search_results = step_memory.get("search_results", [])
    max_sim = step_memory.get("max_similarity", 0.0)
    
    # If the retry loop is exhausted and evidence is insufficient, record finding immediately without calling LLM
    if max_sim < 0.60:
        finding = {
            "chunk_id": chunk["id"],
            "regulation_text": chunk_text,
            "has_gap": True,
            "coverage_level": "none",
            "gap_description": "No compliance evidence could be retrieved after query-rephrase retry cycles.",
            "cited_text": "",
            "validation_status": "insufficient_evidence"
        }
        severity = calculate_severity(chunk.get("metadata", {}).get("is_mandatory", True), "none")
        finding["severity"] = severity
        
        current_findings = list(state.get("findings", []))
        current_findings.append(finding)
        return {"findings": current_findings}
        
    evidence_text = "\n\n".join([
        f"Result {i+1} (Doc: {r['metadata'].get('file_name', 'unknown')}, Sim: {r['similarity']:.2f}):\n{r['content']}"
        for i, r in enumerate(search_results)
    ]) if search_results else "No matching evidence found in bank policies."
    
    model = get_gemini_model("gemini-1.5-pro")
    
    try:
        prompt = ANALYSIS_SYSTEM_PROMPT.format(mandate=chunk_text, evidence=evidence_text)
        res = model.generate_content(prompt)
        cleaned = clean_json_response(res.text)
        analysis = json.loads(cleaned)
    except Exception as e:
        print(f"Error in gap_analyzer parsing: {e}")
        analysis = {
            "has_gap": True,
            "coverage_level": "none",
            "is_mandatory": True,
            "gap_description": "Failed to analyze compliance gap via model. Defaulting to gap status.",
            "cited_text": ""
        }
        
    has_gap = analysis.get("has_gap", False)
    coverage = analysis.get("coverage_level", "none")
    is_mandatory = analysis.get("is_mandatory", True)
    gap_desc = analysis.get("gap_description", "")
    cited_text = analysis.get("cited_text", "")
    
    finding = {
        "chunk_id": chunk["id"],
        "regulation_text": chunk_text,
        "has_gap": has_gap,
        "coverage_level": coverage,
        "gap_description": gap_desc,
        "cited_text": cited_text,
        "validation_status": "unverified"
    }
    
    # Verify citation citation matches source chunk
    if cited_text and search_results:
        # Find best matching search result
        best_match = search_results[0]
        val_res = validate(best_match["id"], cited_text)
        finding["validation_status"] = val_res["status"]
        
    severity = calculate_severity(is_mandatory, coverage)
    finding["severity"] = severity
    
    current_findings = list(state.get("findings", []))
    current_findings.append(finding)
    
    return {"findings": current_findings}

def append_finding(state: AgentState):
    """
    Saves current pointer progress.
    """
    return {
        "current_chunk_index": state["current_chunk_index"] + 1,
        "retry_count": 0
    }

def compile_report(state: AgentState):
    """
    Concludes the graph execution, deduplicates findings, and prepares final state metadata.
    """
    findings = state.get("findings", [])
    unique_findings = []
    seen = set()
    for f in findings:
        key = (f.get("chunk_id"), f.get("regulation_text"), f.get("gap_description"))
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)
            
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "NONE": 4}
    try:
        unique_findings.sort(key=lambda x: severity_order.get(x.get("severity", "NONE"), 4))
    except Exception as e:
        print(f"Error sorting findings: {e}")
        
    return {"findings": unique_findings}

# Routing logic
def route_relevance(state: AgentState):
    decision_obj = state["session_memory"][-1]
    decision = decision_obj.get("decision", "SKIP").lower()
    if decision == "skip":
        return "skip"
    elif decision == "delegate":
        return "delegate"
    else:
        return "tool_caller"

def route_quality(state: AgentState):
    # If the step was delegation, skip validation and proceed directly
    last_step = state["session_memory"][-1]
    if last_step.get("status") == "delegated":
        return "insufficient" # Triggers direct progression to next chunk
        
    max_sim = last_step.get("max_similarity", 0.0)
    retry = state.get("retry_count", 0)
    
    if max_sim >= 0.60:
        return "analyzer"
    elif retry < 3:
        return "retry"
    else:
        return "analyzer"

def route_next_chunk(state: AgentState):
    if state["current_chunk_index"] < len(state.get("regulation_chunks", [])):
        return "relevance_reasoner"
    return "compile_report"

# Build Graph
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
        "delegate": "tool_caller"
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
