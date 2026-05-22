# Supabase Migration Layer — Context & Specifications

This component contains database migration scripts, configuring PostgreSQL structures, vector extensions, and Row-Level Security policies.

---

## 1. Goal
To instantiate database schemas supporting pgvector searches, configure admin-editable audit query stores, and lock down audit trails with append-only access controls.

---

## 2. Migration Schema Scripts
* **`001_create_vectors.sql`**: Enables pgvector extension, creates the primary `vector_store` table, and sets up indexes (HNSW or IVFFlat) optimized for cosine distance search.
* **`002_predefined_questions.sql`**: Creates the `predefined_questions` store containing the questions list displayed in Mode B audits, along with their active-state tracking columns.
* **`003_audit_log_rls.sql`**: Implements append-only policies on `audit_logs` table. Ensures that no application user or node can delete or alter existing log events, creating an immutable compliance trail.

---

## 3. Important to Remember
> [!CAUTION]
> - **Append-Only Auditing**: The security policies must enforce that only `INSERT` queries are permitted on `audit_logs` via the client role. Any attempts to perform `UPDATE` or `DELETE` operations must be rejected at the database engine level to maintain regulatory logging validity.
