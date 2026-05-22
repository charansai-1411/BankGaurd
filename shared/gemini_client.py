import os
import google.generativeai as genai

def get_gemini_model(model_name: str = "gemini-1.5-pro"):
    """
    Initializes and returns a Gemini generative model client.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key.startswith('"') and api_key.endswith('"'):
        api_key = api_key[1:-1]
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def get_embedding(text: str) -> list[float]:
    """
    Generates a 768-dimensional vector embedding for the input text using text-embedding-004.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key.startswith('"') and api_key.endswith('"'):
        api_key = api_key[1:-1]
        
    genai.configure(api_key=api_key)
    
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
        output_dimensionality=768
    )
    return result["embedding"]

