# Codebase Agent — Context & Specifications

This agent performs semantic code audits, matching bank source repositories against RBI IT security, cryptography, encryption, and coding regulation frameworks.

---

## 1. Goal
To audit source code repositories directly, checking details like hardcoded keys, encryption protocols, TLS versions, database connection parameters, and error sanitation procedures.

---

## 2. Operations
* **Primary Source Ingest**: Software development compliance rules, cryptographic standards, logging and exception handling regulations.
* **Vector Search Target**: Ingested codebase segments parsed at AST function/class levels using tree-sitter (namespace: `codebase_bank_doc`).
* **Codebase Specific Tools**:
  * **Tree-Sitter Chunker Tool**: AST-aware chunking function mapping codes into structural tokens rather than arbitrary offsets.

---

## 3. Important to Remember
> [!IMPORTANT]
> - **Terminal Agent**: The Codebase Agent is a terminal agent. It does not delegate further. It must not register or execute the `inter_agent_call` delegation tool.
> - **Fuzzy Evidence Citations**: Cited findings must output exact file paths and line ranges (e.g., `payment_client.py:L45-L60`) inside the metadata to enable developers to verify and patch code directly.
