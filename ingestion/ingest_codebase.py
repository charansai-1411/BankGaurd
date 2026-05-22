# Codebase ingestion using tree-sitter
from ingestion.embed_utils import get_embedding
# from agents.codebase.tools.tree_sitter_chunker import chunk_file_with_ast

def ingest_code_repository(zip_path: str, document_id: str):
    """
    1. Unpack repository ZIP file
    2. Scan source files (*.py, *.java, *.js, *.go)
    3. Run tree-sitter parsing to isolate AST function/class blocks
    4. Generate embeddings and save to pgvector under namespace 'codebase_bank_doc'
    5. Save line range, file path, and language to metadata
    """
    print(f"Ingesting codebase zip: {zip_path}")
    # Stub execution
    return {"status": "success", "files_processed": 15}
