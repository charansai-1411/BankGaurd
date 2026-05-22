# BankGuard — LangGraph Multi-Agent Compliance Platform

BankGuard V1 is an enterprise-grade multi-agent compliance auditing engine. It leverages FastAPI, LangGraph, Gemini, pgvector (Supabase), Upstash Redis, and Cloudflare R2 to analyze bank regulatory compliance.

## Project Structure

```
.
├── gateway/                          # API Gateway (FastAPI, JWT Auth, Route Dispatcher)
├── agents/
│   ├── rbi_compliance/               # General Policy Audit Agent (LangGraph ReAct)
│   ├── api_compliance/               # API Audit Agent (LangGraph ReAct + OpenAPI)
│   └── codebase/                     # Source Code Audit Agent (LangGraph ReAct + Tree-Sitter)
├── worker/                           # Async ARQ Task Worker (Jinja2 + WeasyPrint PDF)
├── ingestion/                        # File parsing and pgvector embedding pipelines
├── shared/                           # Shared SDK for DB, Cache, R2, and Gemini clients
└── supabase/                         # Database schema migrations and RLS configurations
```

## Setup Instructions

1. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in the secrets:
   ```bash
   cp .env.example .env
   ```

2. **Database Setup**:
   Apply SQL migrations from `supabase/migrations/` to your Supabase PostgreSQL instance.

3. **Local Docker Orchestration**:
   Start all services (gateway, workers, redis) locally:
   ```bash
   docker-compose up --build
   ```

## Active Port Mapping
* **API Gateway**: `http://localhost:8000` (Swagger UI at `/docs`)
* **RBI Compliance Agent Service**: `http://localhost:8001`
* **API Compliance Agent Service**: `http://localhost:8002`
* **Codebase Agent Service**: `http://localhost:8003`

For detailed technical designs and flow diagrams, refer to [PROJECT_MEMORY.md](file:///C:/Users/chara/OneDrive/Desktop/BankGaurd/BankGaurd/PROJECT_MEMORY.md).
