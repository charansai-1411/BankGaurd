# OpenAPI spec ingestion
from ingestion.embed_utils import get_embedding
# import prance

def ingest_openapi_spec(spec_path: str, document_id: str):
    """
    1. Load spec using prance Parser to resolve $ref chains
    2. Iterate through endpoints (paths and methods)
    3. Flatten endpoint parameters, descriptions, and schemas into clean text blocks
    4. Generate embeddings and save to pgvector under namespace 'api_specs_bank_doc'
    5. Save endpoint_path and method to metadata
    """
    print(f"Ingesting OpenAPI spec: {spec_path}")
    # Stub execution
    return {"status": "success", "endpoints_count": 5}
