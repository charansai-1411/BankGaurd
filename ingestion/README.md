# Document Ingestion Service — Context & Specifications

This component is responsible for parsing, splitting, embedding, versioning, and indexing raw documents, OpenAPI specifications, and code repositories.

---

## 1. Goal
To convert unstructured or semi-structured data into semantic vector search chunks under the correct database namespaces.

---

## 2. Ingestion Pipelines

```
[Raw PDF / YAML / ZIP] ---> [Document Ingestion]
                                  |
            +---------------------+---------------------+
            |                     |                     |
            v                     v                     v
      [PDF Loader]        [OpenAPI Parser]      [Tree-Sitter AST]
  (Recursive character)  (prance endpoints)    (Function-level code)
            |                     |                     |
            +---------------------+---------------------+
                                  |
                                  v
                       [text-embedding-004]
                                  |
                                  v
                    [Supabase pgvector Vector DB]
                     (Update is_active version)
```

### PDF Ingestion pipeline
* Loader: `RecursiveCharacterTextSplitter` (chunk_size=800, overlap=100).
* Target namespaces: `rbi_regulation`, `rbi_bank_doc`.

### OpenAPI Specification pipeline
* Engine: Uses `prance` parser to resolve external references (`$ref`).
* Output: Chunks mapped directly to endpoints with custom metadata (`endpoint_path`, `method`).
* Target namespace: `api_specs_bank_doc`.

### Codebase Ingestion pipeline
* Engine: `tree-sitter` AST parsers.
* Splitter: Extracts function and class scopes (AST chunks).
* Output: Captures file paths, line ranges, and programming language metadata.
* Target namespace: `codebase_bank_doc`.

---

## 3. Versioning & Atomicity
* When a document is re-ingested:
  1. Calculate the new version index.
  2. Write new chunks to the database with `is_active=true` and `version=N`.
  3. Mark all previous version chunks `is_active=false` within a single SQL transaction.
* Original files are archived in Cloudflare R2: `r2://bankguard/{agent_domain}/{doc_type}/{version}/`.

---

## 4. Important to Remember
> [!WARNING]
> - **Code Chunk boundaries**: Do not use character-offset chunking for source code. Traditional character chunking destroys AST relationships, resulting in fragments that LLMs cannot reason about. Always use tree-sitter AST queries to capture complete code units.
