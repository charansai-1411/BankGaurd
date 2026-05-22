# Async Worker Service — Context & Specifications

This component is a background task processor running ARQ, listening to jobs enqueued in Upstash Redis.

---

## 1. Goal
To run LangGraph agent execution loops asynchronously, format results into HTML via Jinja2, compile HTML to PDF using WeasyPrint, upload the reports to Cloudflare R2, and update the Supabase job status.

---

## 2. Operations & Architecture

```
[ARQ Queue] ---> [tasks.py] ---> [instantiate Agent Graph]
                                         |
                                         v
                                [Run State Machine]
                                         |
                                         v
[Cloudflare R2] <--- [Upload PDF] <--- [WeasyPrint] <--- [Jinja2 Template]
```

### Steps in worker loop
1. **Trigger**: ARQ fetches job context (`job_id`, `agent_type`, `mode`).
2. **Execute Agent**: Initiates the specific agent's LangGraph StateGraph pipeline, passing `call_depth=0`.
3. **HTML Compilation**: Passes findings list to `report_generator.py` which compiles `report.html.j2` with Jinja2.
4. **PDF Compilation**: Invokes WeasyPrint to render the HTML structure to PDF.
5. **R2 Upload**: Uploads the PDF file to Cloudflare R2 bucket.
6. **DB Complete**: Updates the `jobs` row status to `READY` and populates `report_url` with the pre-signed R2 URL.

---

## 3. Important to Remember
> [!TIP]
> - **WeasyPrint Dependencies**: WeasyPrint requires system libraries like `pango`, `cairo`, and `gobject`. These must be installed in the Docker container for the PDF generation tool to run without errors.
> - **State Resumability**: Ensure that the worker records checkpoint states. If the worker encounters a container restart, it can resume from the last saved state checkpoint in Upstash Redis.
