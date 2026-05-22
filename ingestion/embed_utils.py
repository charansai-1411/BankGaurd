# Gemini embedding utils
# import google.generativeai as genai

def get_embedding(text: str) -> list:
    """
    Calls Gemini API text-embedding-004 to fetch vector.
    """
    # Stub embedding vector (768 dimensions)
    return [0.0] * 768

def get_embeddings_batch(texts: list) -> list:
    """
    Batch embedding retrieval.
    """
    return [[0.0] * 768 for _ in texts]
