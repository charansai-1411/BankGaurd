# PDF Ingestion pipeline
from ingestion.embed_utils import get_embeddings_batch
# from shared.db import supabase_client

def ingest_pdf(file_path: str, agent_domain: str, document_id: str):
    """
    1. Parse PDF text using PyPDF or PDFPlumber
    2. Split text recursively (size 800, overlap 100)
    3. Generate Gemini embeddings for each chunk
    4. Write chunks into vector_store table under namespace '{agent_domain}_regulation'
    5. Set is_active=true and archive raw PDF to Cloudflare R2
    """
    print(f"Ingesting PDF: {file_path} into namespace: {agent_domain}")
    # Stub execution
    return {"status": "success", "chunks_count": 10}
