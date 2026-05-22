# BankGuard — Project Memory and Core Specifications

This document serves as the central reference and source of truth for the **BankGuard** multi-agent compliance platform. It outlines the architecture, data structures, execution loops, tools, and configurations, ensuring deep contextual preservation.

---

## 1. Executive Summary
BankGuard is a LangGraph-powered multi-agent compliance platform designed to audit bank documents, API specs, and source code against regulatory frameworks (e.g., RBI Guidelines). 

Instead of traditional RAG (Retrieval-Augmented Generation) which performs a simple query-lookup, BankGuard implements a **ReAct loop** using LangGraph's explicit StateGraph execution. The agents reason section-by-section, calling specialized tools to fetch evidence, scraping live regulations, checking compliance severity deterministically, and delegating to peer agents when cross-domain expertise is required.

---

## 2. Core Architectural Principles
1. **Reason Before Acting**: Every regulation section is analyzed before tools are triggered. Non-actionable or irrelevant sections are skipped to conserve tokens and prevent noise.
2. **Tools Over Prompts**: Complex tasks (e.g., vector search, AST parsing, scoring, code analysis) are executed by typed, deterministic python tools, not left to LLM generation.
3. **Delegate, Don't Duplicate**: Domain-specific queries are delegated to specialized agents (Compliance $\rightarrow$ API $\rightarrow$ Codebase) using an explicit peer-to-peer call mechanism.
4. **Explicit State Graph**: Every state change, transition, and loop is defined in a LangGraph `StateGraph` in Python, providing predictability, checkpointing, and easy auditing.
5. **Evidence Is Mandatory**: All gap findings must include verified citations pointing to active database chunks. Fallbacks (e.g., "I don't know") trigger when matching similarity falls below 0.70.

---

## 3. System Architecture & Component Mapping

```
                                   +-------------------+
                                   |    Client Layer   |
                                   | (React / Swagger) |
                                   +---------+---------+
                                             | HTTPS / Supabase JWT
                                             v
                                   +---------+---------+
                                   |  FastAPI Gateway  |
                                   +---------+---------+
                                             | Enqueues ARQ job
                                             v
                                   +---------+---------+
                                   |    ARQ Queue      |
                                   +----+----+----+----+
                                        |    |    |
                   +--------------------+    |    +--------------------+
                   |                         |                         |
                   v                         v                         v
        +----------+----------+   +----------+----------+   +----------+----------+
        |    RBI Compliance   |   |    API Compliance   |   |   Codebase Agent    |
        |    Agent Service    |   |    Agent Service    |   |    Agent Service    |
        +----------+----------+   +----------+----------+   +----------+----------+
                   |                         |                         |
                   +-------------------------+-------------------------+
                                             |
                                             v
                                  +----------+----------+
                                  |    Shared Layer     |
                                  | (R2, Redis, Gemini) |
                                  +---------------------+
```

### Services Overview
1. **API Gateway (`gateway/`)**: Single point of entry. Validates Supabase JWT, parses requests, writes jobs to Supabase, enqueues worker tasks with `call_depth=0`.
2. **Ingestion Service (`ingestion/`)**: Document parsing (PDFs, OpenAPI JSON/YAML, Code ZIPs), tree-sitter AST function chunking, Gemini text-embedding-004 vector generation, version updating.
3. **RBI Compliance Agent (`agents/rbi_compliance/`)**: Conducts audits of general policy documents against RBI circulars. Delegates API tasks to API Agent and codebase validation tasks to Codebase Agent.
4. **API Compliance Agent (`agents/api_compliance/`)**: Conducts audits on OpenAPI specs. Can delegate codebase validations to Codebase Agent.
5. **Codebase Agent (`agents/codebase/`)**: Inspects source code repos for regulatory gaps. Acts as a terminal agent (never delegates further, max call depth 2).
6. **Async Job Worker (`worker/`)**: Runs the long-running analysis workflows. Uses Jinja2 and WeasyPrint to compile audit reports to PDFs and uploads them to Cloudflare R2.

---

## 4. LangGraph ReAct Loop State & Transitions

The agent executes a state machine with the following nodes and logic:

### The State Schema
```python
class AgentState(TypedDict):
    job_id: str
    agent_domain: str
    mode: str
    call_depth: int
    regulation_chunks: List[Dict]
    current_chunk_index: int
    findings: List[Dict]
    retry_count: int
    session_memory: List[Dict]
    report_url: str
```

### Node Transitions
1. **Initialize State**: Fetches all active regulation chunks (`is_active=true`, ordered by `chunk_index`). Sets `current_chunk_index=0`.
2. **Relevance Reasoner (Decision)**: Inspects the current regulation chunk. Decides if it requires action:
   - **SKIP**: Non-actionable definition or preamble. Advance `chunk_index`.
   - **INVESTIGATE**: Contains a mandate needing audit against bank docs. Route to **Tool Caller**.
   - **DELEGATE**: API or Code specific. Route to **Inter-Agent Call**.
3. **Tool Caller**: Invokes the registered tools (Vector Search, Section Expander, RBI Scraper) and updates state with observations.
4. **Evidence Quality Check (Decision)**:
   - If similarity $\ge 0.70$, route to **Gap Analyzer**.
   - If similarity $< 0.70$, rephrase query using Gemini, increment `retry_count`, and loop back to **Tool Caller** (max 3 retries).
   - If retries exhausted, log as "unable to verify" and advance index.
5. **Gap Analyzer + Evidence Validator**: Generates gap report text. Fuzzy-matches cited text with vector DB contents using **Evidence Validator Tool** (threshold 0.85). Computes severity using **Severity Calculator Tool**.
6. **Append Finding**: Writes `GapFinding` to `findings`. Increments `current_chunk_index`. Returns to **Relevance Reasoner** if chunks remain.
7. **Compile & Generate Report**: Deduplicates findings, runs Jinja2 + WeasyPrint HTML $\rightarrow$ PDF conversion, saves to Cloudflare R2, writes audit logs, marks job `READY`.

---

## 5. Agent Tools & Interface Specifications

All agents are equipped with the following python-decorated tools:

| Tool Name | Python Signature | Purpose & Behavior |
| :--- | :--- | :--- |
| **Vector Search** | `search(query: str, namespace: str, top_k: int = 5)` | Cosine similarity search against `{domain}_regulation` or `{domain}_bank_doc` namespace. Filter `is_active=true`. Similarity cutoff $\ge 0.70$. |
| **Section Expander** | `expand(chunk_id: str, window: int = 2)` | Fetches context chunks preceding/following a target `chunk_index` to handle split clauses. |
| **RBI Scraper** | `scrape_rbi(query: str, circular_type: str)` | Live scrapers querying `rbi.org.in` for matching amendments or newer guidelines when local database is outdated. |
| **Evidence Validator** | `validate(chunk_id: str, cited_text: str)` | Strict fuzzy match (threshold 0.85) verifying LLM citations match DB chunk content. |
| **Severity Calculator** | `calculate_severity(...)` | Deterministic severity assignment: `CRITICAL` (mandatory, zero coverage), `HIGH` (mandatory, weak coverage), `MEDIUM` (advisory, zero coverage), `LOW` (advisory, weak coverage). |
| **Inter-Agent Call** | `call_agent(agent_type: str, query: str, context: str, call_depth: int)` | Serializes P2P delegation. Blocks if `call_depth >= 2`. Converts broad queries to full pipeline jobs and narrow queries to fast-retrieval Q&A. |

---

## 6. Execution Modes (Mutually Exclusive Per Run)

* **Mode A: Full Diagnosis**: Standard section-by-section LangGraph execution. Fully async, run on ARQ.
* **Mode B: Predefined Questions**: Admin-defined lists stored in Supabase table `predefined_questions`. Evaluates questions in a simplified loop without section iteration. Async, run on ARQ.
* **Mode C: Free Chat**: Synchronous endpoint for interactive discussion. Fetches relevant chunks, injects Upstash Redis session history (last 6 turns, TTL 30m), streams grounded response using Gemini.

---

## 7. Storage and DB Schema Definitions
- **Supabase pgvector**:
  - Table: `vector_store` with columns: `id`, `namespace` (`rbi_regulation`, `api_specs_bank_doc`, etc.), `embedding` (vector size 768), `content`, `metadata` (JSON with chunk_index, document_id, version, endpoint_path, line_range), `is_active`, `created_at`.
  - Table: `predefined_questions` with columns: `id`, `agent_domain`, `question_text`, `is_active`.
  - Table: `jobs` with columns: `id`, `status` (`PENDING`, `RUNNING`, `READY`, `FAILED`), `agent_type`, `mode`, `report_url`, `created_at`.
  - Table: `audit_logs` with columns: `id`, `job_id`, `node_name`, `input`, `output`, `created_at`. Append-only RLS policy.
- **Cloudflare R2**: Original uploaded files, ZIP packages, and generated PDFs stored under `r2://bankguard/{agent_domain}/{doc_type}/{version}/`.
- **Upstash Redis**:
  - LangGraph checkpointing database for resuming interrupted workers.
  - Chat session cache with key template `chat:{session_id}` storing conversation history.
