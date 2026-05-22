# Shared SDK — Context & Specifications

This directory contains the central library shared by all services (Gateway, Agent instances, workers, and ingestion scripts).

---

## 1. Goal
To prevent code duplication, guarantee model uniformity, and establish a single source of configuration mappings for databases, caches, and AI APIs.

---

## 2. Shared Modules
* **`db.py`**: Exports client sessions for Supabase, query executors, and pgvector cosine search helpers.
* **`redis_client.py`**: Configures connection to Upstash Redis for caching active chat sessions and storing LangGraph checkpoints.
* **`r2_client.py`**: Leverages `boto3` to communicate with S3-compatible Cloudflare R2, generating pre-signed URLs.
* **`gemini_client.py`**: Sets up Google's Generative AI SDK, exposing helper wrappers for `Gemini 1.5 Pro` context execution.
* **`models.py`**: Declares Pydantic structures (`GapFinding`, `QuestionSchema`, `JobStatusResponse`, `DiagnoseRequest`, `ChatMessage`, `ChatResponse`).

---

## 3. Important to Remember
> [!IMPORTANT]
> - **Dependency Consistency**: Since this module is imported by five different services, changing any Pydantic scheme or connection parameter in `models.py` requires testing against all service endpoints to prevent serialization errors.
