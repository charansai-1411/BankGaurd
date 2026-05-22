import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from shared.gemini_client import get_embedding
from ingestion.embed_utils import recursive_character_split, store_embeddings

def clone_repository(repo_url: str, dest_dir: str) -> str:
    """
    Clones a remote git repository to the target destination directory.
    """
    print(f"Cloning repository: {repo_url} into: {dest_dir}")
    if os.path.exists(dest_dir):
        # Clear existing directory
        shutil.rmtree(dest_dir, ignore_errors=True)
        
    os.makedirs(dest_dir, exist_ok=True)
    
    # Run git clone command
    result = subprocess.run(
        ["git", "clone", repo_url, dest_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return dest_dir

def mask_comments_and_literals(content: str) -> str:
    """
    Replaces comments (// and /* */) and string/regex/template literals ("", '', and ``)
    with spaces (preserving newlines and length) to avoid counting braces
    or keywords inside comments/strings, while maintaining original line/char offsets.
    """
    chars = list(content)
    n = len(chars)
    i = 0
    state = "code" # code, line_comment, block_comment, str_single, str_double, str_template
    
    while i < n:
        c = chars[i]
        next_c = chars[i+1] if i + 1 < n else ""
        
        if state == "code":
            if c == "/" and next_c == "/":
                state = "line_comment"
                chars[i] = " "
                chars[i+1] = " "
                i += 2
                continue
            elif c == "/" and next_c == "*":
                state = "block_comment"
                chars[i] = " "
                chars[i+1] = " "
                i += 2
                continue
            elif c == '"':
                state = "str_double"
                chars[i] = " "
                i += 1
                continue
            elif c == "'":
                state = "str_single"
                chars[i] = " "
                i += 1
                continue
            elif c == "`":
                state = "str_template"
                chars[i] = " "
                i += 1
                continue
        elif state == "line_comment":
            if c == "\n":
                state = "code"
            else:
                chars[i] = " "
        elif state == "block_comment":
            if c == "*" and next_c == "/":
                state = "code"
                chars[i] = " "
                chars[i+1] = " "
                i += 2
                continue
            elif c != "\n":
                chars[i] = " "
        elif state == "str_double":
            if c == "\\" and next_c == '"':
                chars[i] = " "
                chars[i+1] = " "
                i += 2
                continue
            elif c == '"':
                state = "code"
                chars[i] = " "
            elif c != "\n":
                chars[i] = " "
        elif state == "str_single":
            if c == "\\" and next_c == "'":
                chars[i] = " "
                chars[i+1] = " "
                i += 2
                continue
            elif c == "'":
                state = "code"
                chars[i] = " "
            elif c != "\n":
                chars[i] = " "
        elif state == "str_template":
            if c == "\\" and next_c == "`":
                chars[i] = " "
                chars[i+1] = " "
                i += 2
                continue
            elif c == "`":
                state = "code"
                chars[i] = " "
            elif c != "\n":
                chars[i] = " "
                
        i += 1
        
    return "".join(chars)

def chunk_code_file(content: str, file_path: str) -> list[dict]:
    """
    Chunks source code files into logic blocks (classes, methods, functions)
    using syntactic indent or brace heuristics.
    """
    ext = os.path.splitext(file_path)[1].lower()
    lines = content.splitlines()
    
    # If the file is tiny, return as a single chunk
    if len(lines) <= 20:
        return [{
            "content": content,
            "start_line": 1,
            "end_line": len(lines),
            "name": os.path.basename(file_path),
            "type": "file"
        }]
        
    chunks = []
    
    if ext == ".py":
        # Python class/def indent tracker
        pattern = re.compile(r'^(\s*)(class|def|async def)\s+(\w+)')
        current_block = None
        block_indent = 0
        
        for idx, line in enumerate(lines):
            line_num = idx + 1
            stripped = line.strip()
            
            if not stripped:
                if current_block:
                    current_block["lines"].append(line)
                continue
                
            match = pattern.match(line)
            if match:
                indent = len(match.group(1))
                def_type = match.group(2)
                name = match.group(3)
                
                if current_block:
                    block_content = "\n".join(current_block["lines"])
                    chunks.append({
                        "content": block_content,
                        "start_line": current_block["start_line"],
                        "end_line": line_num - 1,
                        "name": current_block["name"],
                        "type": current_block["type"]
                    })
                
                current_block = {
                    "start_line": line_num,
                    "name": name,
                    "type": "class" if "class" in def_type else "function",
                    "lines": [line]
                }
                block_indent = indent
            else:
                if current_block:
                    current_indent = len(line) - len(line.lstrip())
                    # Indent closed or matches definition start
                    if current_indent <= block_indent and not stripped.startswith('#'):
                        block_content = "\n".join(current_block["lines"])
                        chunks.append({
                            "content": block_content,
                            "start_line": current_block["start_line"],
                            "end_line": line_num - 1,
                            "name": current_block["name"],
                            "type": current_block["type"]
                        })
                        current_block = None
                    else:
                        current_block["lines"].append(line)
                else:
                    current_block = {
                        "start_line": line_num,
                        "name": "module_level",
                        "type": "general",
                        "lines": [line]
                    }
                    block_indent = 0
                    
        if current_block:
            block_content = "\n".join(current_block["lines"])
            chunks.append({
                "content": block_content,
                "start_line": current_block["start_line"],
                "end_line": len(lines),
                "name": current_block["name"],
                "type": current_block["type"]
            })
            
    elif ext in [".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".cpp", ".c", ".h", ".cs", ".rs"]:
        masked_content = mask_comments_and_literals(content)
        masked_lines = masked_content.splitlines()
        
        # Check if braces are highly unbalanced
        total_open = masked_content.count('{')
        total_close = masked_content.count('}')
        
        if abs(total_open - total_close) > 10 or (total_open == 0 and len(lines) > 40):
            # Fallback to sliding window for unbalanced codebase
            step = 40
            for i in range(0, len(lines), step):
                block_lines = lines[i:i+50]
                block_content = "\n".join(block_lines)
                chunks.append({
                    "content": block_content,
                    "start_line": i + 1,
                    "end_line": min(i + 50, len(lines)),
                    "name": "fallback_window",
                    "type": "fallback"
                })
        else:
            # Curly brace matching heuristics on masked lines
            class_func_pattern = re.compile(
                r'(class\s+\w+|function\s+\w+|\w+\s*\([^)]*\)\s*\{|\w+\s+class\s+\w+|\w+\s+\w+\s*\([^)]*\)\s*\{|fn\s+\w+)'
            )
            
            current_block = None
            brace_count = 0
            in_braces = False
            
            for idx, line in enumerate(lines):
                line_num = idx + 1
                if idx >= len(masked_lines):
                    break
                masked_line = masked_lines[idx]
                open_braces = masked_line.count('{')
                close_braces = masked_line.count('}')
                
                match = class_func_pattern.search(masked_line)
                
                if match and not in_braces:
                    if current_block:
                        block_content = "\n".join(current_block["lines"])
                        chunks.append({
                            "content": block_content,
                            "start_line": current_block["start_line"],
                            "end_line": line_num - 1,
                            "name": current_block["name"],
                            "type": "block"
                        })
                    
                    current_block = {
                        "start_line": line_num,
                        "name": match.group(1).strip(),
                        "type": "declaration",
                        "lines": [line]
                    }
                    brace_count = open_braces - close_braces
                    in_braces = brace_count > 0
                else:
                    if current_block:
                        current_block["lines"].append(line)
                        brace_count += open_braces - close_braces
                        # Hard limit at 150 lines per block to avoid massive blocks
                        if (brace_count <= 0 and in_braces) or (len(current_block["lines"]) >= 150):
                            block_content = "\n".join(current_block["lines"])
                            chunks.append({
                                "content": block_content,
                                "start_line": current_block["start_line"],
                                "end_line": line_num,
                                "name": current_block["name"],
                                "type": "block"
                            })
                            current_block = None
                            in_braces = False
                    else:
                        current_block = {
                            "start_line": line_num,
                            "name": "general",
                            "type": "general",
                            "lines": [line]
                        }
                        brace_count = open_braces - close_braces
                        in_braces = brace_count > 0
                        
            if current_block:
                block_content = "\n".join(current_block["lines"])
                chunks.append({
                    "content": block_content,
                    "start_line": current_block["start_line"],
                    "end_line": len(lines),
                    "name": current_block["name"],
                    "type": "block"
                })
    else:
        # Fallback sliding window for config / text files
        step = 40
        for i in range(0, len(lines), step):
            block_lines = lines[i:i+50]
            block_content = "\n".join(block_lines)
            chunks.append({
                "content": block_content,
                "start_line": i + 1,
                "end_line": min(i + 50, len(lines)),
                "name": "text_block",
                "type": "fallback"
            })
            
    final_chunks = []
    for c in chunks:
        if not c["content"].strip():
            continue
        if len(c["content"]) > 1000:
            # Sub-split large logical blocks recursively
            sub_splits = recursive_character_split(c["content"], chunk_size=800, chunk_overlap=100)
            for s_idx, sub in enumerate(sub_splits):
                final_chunks.append({
                    "content": sub,
                    "start_line": c["start_line"],
                    "end_line": c["end_line"],
                    "name": f"{c['name']}_part_{s_idx}",
                    "type": c["type"]
                })
        else:
            final_chunks.append(c)
            
    return final_chunks

def should_process_file(file_path: str) -> bool:
    """
    Returns True if the file should be parsed and indexed.
    Excludes node_modules, .venv, git folders, images, and binary artifacts.
    """
    # Excluded directories
    parts = Path(file_path).parts
    exclude_dirs = {".git", ".venv", "node_modules", "__pycache__", "dist", "build", "env", "venv"}
    if any(p in exclude_dirs for p in parts):
        return False
        
    # Supported file extensions
    allowed_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go",
        ".c", ".cpp", ".h", ".cs", ".rs", ".json", ".yaml", ".yml",
        ".md", ".sh", ".sql"
    }
    
    ext = os.path.splitext(file_path)[1].lower()
    return ext in allowed_extensions

def ingest_codebase_dir(base_dir: str, document_id: str):
    """
    Indexes source files from a directory, chunks them, and uploads embeddings to Supabase.
    """
    chunks_to_insert = []
    metadata_list = []
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)
            
            if not should_process_file(rel_path):
                continue
                
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                if not content.strip():
                    continue
                    
                file_chunks = chunk_code_file(content, rel_path)
                
                for fc in file_chunks:
                    chunks_to_insert.append(fc["content"])
                    metadata_list.append({
                        "document_id": document_id,
                        "file_path": rel_path.replace("\\", "/"),
                        "start_line": fc["start_line"],
                        "end_line": fc["end_line"],
                        "block_name": fc["name"],
                        "type": fc["type"],
                        "language": os.path.splitext(rel_path)[1].lower()
                    })
            except Exception as e:
                print(f"Error reading file {full_path}: {e}")
                
    if chunks_to_insert:
        print(f"Indexing {len(chunks_to_insert)} code chunks...")
        embeddings = [get_embedding(chunk) for chunk in chunks_to_insert]
        store_embeddings("codebase", chunks_to_insert, embeddings, metadata_list)
        
    return {"status": "success", "chunks_indexed": len(chunks_to_insert)}

def ingest_code_repository(repo_url: str, document_id: str):
    """
    Clones a remote git repository, structures its source files, chunks classes/methods,
    and stores embeddings in Supabase under 'codebase' namespace.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = os.path.join(temp_dir, "repo")
        try:
            clone_repository(repo_url, clone_dir)
            return ingest_codebase_dir(clone_dir, document_id)
        except Exception as e:
            print(f"Error ingesting repository: {e}")
            return {"status": "error", "message": str(e)}
