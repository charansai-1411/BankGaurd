from typing import List, Dict, Any

def chunk_file_with_ast(file_content: str, language: str) -> List[Dict[str, Any]]:
    """
    Parses code with tree-sitter and returns chunks corresponding to classes/functions.
    """
    # Stub AST parser
    return [
        {
            "name": "payment_client",
            "type": "function",
            "start_line": 30,
            "end_line": 60,
            "content": file_content
        }
    ]
