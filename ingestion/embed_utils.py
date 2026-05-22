import os
from shared.gemini_client import get_embedding
from shared.db import get_db_client

def recursive_character_split(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[str]:
    """
    Splits text recursively using different separators to keep chunks below chunk_size
    while maximizing cohesion.
    """
    separators = ["\n\n", "\n", " ", ""]
    
    def split_recurse(text_to_split: str, current_seps: list[str]) -> list[str]:
        if len(text_to_split) <= chunk_size:
            return [text_to_split]
        
        if not current_seps:
            # Force split by size
            return [text_to_split[i:i+chunk_size] for i in range(0, len(text_to_split), chunk_size - chunk_overlap)]
        
        sep = current_seps[0]
        remaining_seps = current_seps[1:]
        
        # Split text by separator
        if sep == "":
            parts = list(text_to_split)
        else:
            parts = text_to_split.split(sep)
            
        chunks = []
        current_chunk = []
        current_len = 0
        
        for part in parts:
            part_len = len(part)
            # If the single part exceeds chunk size, recursively split it with remaining separators
            if part_len > chunk_size:
                # Flush current_chunk if not empty
                if current_chunk:
                    joined = sep.join(current_chunk)
                    chunks.append(joined)
                    current_chunk = []
                    current_len = 0
                
                sub_chunks = split_recurse(part, remaining_seps)
                chunks.extend(sub_chunks)
            else:
                # Check if adding this part would exceed the chunk size
                # Account for separator length
                sep_len = len(sep) if current_chunk else 0
                if current_len + sep_len + part_len > chunk_size:
                    # Flush current_chunk
                    joined = sep.join(current_chunk)
                    if joined.strip():
                        chunks.append(joined)
                    
                    # Handle overlap by taking the last parts that fit into overlap size
                    overlap_chunk = []
                    overlap_len = 0
                    for rev_part in reversed(current_chunk):
                        rev_sep_len = len(sep) if overlap_chunk else 0
                        if overlap_len + rev_sep_len + len(rev_part) <= chunk_overlap:
                            overlap_chunk.insert(0, rev_part)
                            overlap_len += rev_sep_len + len(rev_part)
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_len = overlap_len
                    
                    # Add current part
                    current_chunk.append(part)
                    current_len += (len(sep) if current_len > 0 else 0) + part_len
                else:
                    current_chunk.append(part)
                    current_len += sep_len + part_len
                    
        if current_chunk:
            joined = sep.join(current_chunk)
            if joined.strip():
                chunks.append(joined)
                
        return chunks

    return split_recurse(text, separators)

def store_embeddings(namespace: str, chunks: list[str], embeddings: list[list[float]], metadata_list: list[dict] = None) -> list:
    """
    Stores chunks, embeddings, and metadata into Supabase vector_store in bulk.
    """
    if not chunks:
        return []
    
    if metadata_list is None:
        metadata_list = [{} for _ in chunks]
        
    db = get_db_client()
    records = []
    for chunk, embedding, metadata in zip(chunks, embeddings, metadata_list):
        records.append({
            "namespace": namespace,
            "content": chunk,
            "embedding": embedding,
            "metadata": metadata,
            "is_active": True,
            "version": 1
        })
        
    # Bulk insert using Supabase API
    # Since supabase-py uses postgrest, we can do insert(records)
    response = db.table("vector_store").insert(records).execute()
    return response.data
