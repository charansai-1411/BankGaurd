# Agents Layer — Orchestration & LangGraph ReAct Loops

This directory houses the intelligent core of BankGuard. Each agent is deployed as a standalone service running a LangGraph-defined state machine.

---

## 1. Goal
To analyze regulatory sections systematically, determine applicability, extract evidence from bank documentation/codebase, compute compliance gaps, and generate structured gap findings.

---

## 2. Shared Execution Graph (ReAct Loop)

Every agent implements a StateGraph with the following standard nodes:

```
                  +--------------------------------+
                  |           Initialize           |
                  +---------------+----------------+
                                  |
                                  v
+----------+      +---------------+----------------+
|   Skip   |<-----+       Relevance Reasoner       |
+----+-----+      +-------+----------------+-------+
     |                    |                |
     |                    v                v
     |             +------+-----+   +------+------+
     |             | Tool Caller|   |  Delegate   |
     |             +------+-----+   +------+------+
     |                    |                |
     v                    v                v
+----+--------------------+----------------+-------+
|                 State Update Node                |
+-------------------------+------------------------+
                          |
                          v
                  +-------+--------+
                  | Compile Report |
                  +----------------+
```

### Transition Conditions
* **Relevance Reasoner**: Decides if a regulation chunk is relevant.
  * *Preamble/Glossary* $\rightarrow$ **Skip**.
  * *Policy-Related Requirement* $\rightarrow$ **Investigate** (routes to Tool Caller).
  * *Cross-Domain Requirement* (e.g., General Compliance regulations mentioning API specifications) $\rightarrow$ **Delegate** (routes to Inter-Agent tool).

* **Evidence Quality Check**:
  * If vector search returns similarity $\ge 0.70$ $\rightarrow$ **Compliant / Gap Found**.
  * If similarity $< 0.70$ $\rightarrow$ **Retry** with query rephrasing (up to 3 times) $\rightarrow$ **Insufficient Evidence**.

---

## 3. Inter-Agent Communication Protocol
* **Peer-to-Peer**: No master orchestrator is used. The Compliance Agent calls the API Agent as a tool. The API Agent calls the Codebase Agent as a tool.
* **Call Depth Limit**: To prevent infinite execution loops (e.g., Agent A calling Agent B which calls Agent A), a strict call depth guard is enforced:
  * Maximum call depth = **2**.
  * Initial task starts with `call_depth=0`.
  * If `call_depth >= 2`, delegation tools will reject execution and return an out-of-scope stub.

---

## 4. Important to Remember
> [!IMPORTANT]
> - **State Checkpoint Persistence**: Agent state checkpoints are written to Upstash Redis at the end of every node execution. If a node fails, the ARQ worker resumes from the exact checkpoint.
> - **Strict Grounding**: The LLM must not make up policy names or clauses. If the similarity score is low, it must report a gap or inability to verify.
