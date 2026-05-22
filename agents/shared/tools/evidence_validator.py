import re
from shared.db import get_db_client
from shared.gemini_client import get_gemini_model

def normalize_text(text: str) -> str:
    """
    Cleans text by converting to lowercase, removing punctuation, and collapsing spacing.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return ' '.join(text.split())

def levenshtein_ratio(s1: str, s2: str) -> float:
    """
    Computes Levenshtein similarity ratio between two strings (0.0 to 1.0).
    """
    m, n = len(s1), len(s2)
    if m == 0 or n == 0:
        return 0.0
        
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(
                    dp[i-1][j] + 1,    # deletion
                    dp[i][j-1] + 1,    # insertion
                    dp[i-1][j-1] + 1   # substitution
                )
    distance = dp[m][n]
    max_len = max(m, n)
    return (max_len - distance) / max_len

def get_best_substring_match(chunk: str, citation: str) -> float:
    """
    Finds the best fuzzy match score of a citation within a larger chunk
    by sliding a window or analyzing sentences.
    """
    norm_chunk = normalize_text(chunk)
    norm_citation = normalize_text(citation)
    
    if not norm_citation:
        return 0.0
        
    # Fast path: direct containment
    if norm_citation in norm_chunk:
        return 1.0
        
    # Split citation into words
    cit_words = norm_citation.split()
    chunk_words = norm_chunk.split()
    
    if len(chunk_words) <= len(cit_words):
        return levenshtein_ratio(norm_chunk, norm_citation)
        
    # Sliding window of same word count
    best_score = 0.0
    window_size = len(cit_words)
    
    # We allow the window to expand slightly (up to +2 words) to catch minor word additions
    for w_size in [window_size, window_size + 1, window_size + 2]:
        if w_size > len(chunk_words):
            continue
        for i in range(len(chunk_words) - w_size + 1):
            sub_text = ' '.join(chunk_words[i:i + w_size])
            score = levenshtein_ratio(sub_text, norm_citation)
            if score > best_score:
                best_score = score
                if best_score >= 0.95: # Early stop
                    return best_score
                    
    return best_score

def check_semantic_support(chunk: str, citation: str) -> bool:
    """
    Calls Gemini to verify if the chunk text semantically supports the cited claim.
    """
    try:
        model = get_gemini_model("gemini-1.5-pro")
        prompt = (
            f"You are a compliance validator. Verify if the Cited Claim is semantically supported "
            f"by the Source Document Chunk (even if paraphrased or summarized).\n\n"
            f"Source Document Chunk:\n{chunk}\n\n"
            f"Cited Claim:\n{citation}\n\n"
            f"Respond with ONLY 'YES' if the source chunk fully supports the cited claim, "
            f"or 'NO' if the claim contains information not found in or supported by the source. "
            f"Do not output anything else."
        )
        response = model.generate_content(prompt)
        result = response.text.strip().upper()
        return "YES" in result
    except Exception as e:
        print(f"Error in check_semantic_support: {e}")
        return False

def validate(chunk_id: str, cited_text: str) -> dict:
    """
    Validates that the cited_text is supported by the chunk in the vector store.
    Uses substring fuzzy matching (ratio >= 0.85) with semantic fallback (0.65 to 0.85).
    """
    db = get_db_client()
    response = db.table("vector_store").select("content").eq("id", chunk_id).execute()
    if not response.data:
        return {"is_valid": False, "reason": "Chunk ID not found in database", "score": 0.0}
        
    chunk_content = response.data[0]["content"]
    
    # Calculate best fuzzy substring match
    score = get_best_substring_match(chunk_content, cited_text)
    
    is_valid = False
    status = "invalid"
    
    if score >= 0.85:
        is_valid = True
        status = "valid (fuzzy match)"
    elif score >= 0.65:
        # Fallback to semantic paraphrase check
        is_valid = check_semantic_support(chunk_content, cited_text)
        status = "valid (semantic paraphrase check)" if is_valid else "invalid (failed semantic check)"
    else:
        status = "invalid (score too low)"
        
    return {
        "is_valid": is_valid,
        "status": status,
        "score": score,
        "chunk_content": chunk_content
    }
