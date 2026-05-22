import os
import json
import yaml

from shared.gemini_client import get_embedding
from ingestion.embed_utils import recursive_character_split, store_embeddings

def resolve_ref(spec: dict, ref: str) -> dict:
    """
    Resolves local JSON references (e.g. #/components/schemas/User) in the OpenAPI spec.
    """
    if not ref.startswith("#/"):
        return {"$ref": ref}
    parts = ref.split("/")[1:]
    current = spec
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return {"$ref": ref}
    return current

def format_schema(spec: dict, schema: dict, depth: int = 0) -> str:
    """
    Recursively formats a JSON schema into a clean, human-readable outline.
    """
    if not schema:
        return "any"
    if "$ref" in schema:
        if depth > 4:  # Prevent infinite recursion in cyclical references
            return schema["$ref"].split("/")[-1]
        resolved = resolve_ref(spec, schema["$ref"])
        return format_schema(spec, resolved, depth + 1)
        
    schema_type = schema.get("type", "object")
    if schema_type == "object":
        properties = schema.get("properties", {})
        if not properties:
            return "{}"
        lines = []
        for prop, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "any")
            if "$ref" in prop_schema:
                prop_type = prop_schema["$ref"].split("/")[-1]
            elif prop_schema.get("type") == "array" and "items" in prop_schema:
                items_schema = prop_schema["items"]
                items_type = items_schema.get("type", "any")
                if "$ref" in items_schema:
                    items_type = items_schema["$ref"].split("/")[-1]
                prop_type = f"Array<{items_type}>"
            lines.append(f"{'  ' * (depth + 1)}{prop}: {prop_type}")
        return "\n" + "\n".join(lines)
    elif schema_type == "array":
        items = schema.get("items", {})
        items_type = items.get("type", "any")
        if "$ref" in items:
            items_type = items["$ref"].split("/")[-1]
        return f"Array<{items_type}>"
    else:
        return str(schema_type)

def ingest_openapi_spec(spec_path: str, document_id: str):
    """
    Parses an OpenAPI spec (JSON or YAML), chunks components (endpoints, security schemas),
    generates embeddings, and stores them in Supabase.
    """
    print(f"Ingesting OpenAPI spec: {spec_path}")
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"OpenAPI spec file not found: {spec_path}")
        
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Load spec based on file extension/content format
    if spec_path.endswith(".json"):
        spec = json.loads(content)
    else:
        # Fallback to YAML
        spec = yaml.safe_load(content)
        
    if not isinstance(spec, dict):
        return {"status": "error", "message": "Invalid OpenAPI spec format"}
        
    info = spec.get("info", {})
    spec_title = info.get("title", "Unknown API")
    spec_version = info.get("version", "1.0.0")
    
    chunks_to_insert = []
    metadata_list = []
    
    # 1. Ingest General Info
    general_text = f"API Title: {spec_title}\nVersion: {spec_version}\nDescription: {info.get('description', '')}"
    chunks_to_insert.append(general_text)
    metadata_list.append({
        "document_id": document_id,
        "spec_title": spec_title,
        "spec_version": spec_version,
        "type": "general_info"
    })
    
    # 2. Ingest Paths and Methods
    paths = spec.get("paths", {})
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                continue
                
            summary = operation.get("summary", "")
            description = operation.get("description", "")
            
            lines = [
                f"Endpoint: {method.upper()} {path}",
                f"Summary: {summary}",
                f"Description: {description}",
                "Parameters:"
            ]
            
            # Form parameters
            params = operation.get("parameters", [])
            # Also inherit path-level parameters
            params.extend(path_item.get("parameters", []))
            
            for param in params:
                p_name = param.get("name", "")
                p_in = param.get("in", "")
                p_required = "Required" if param.get("required", False) else "Optional"
                p_desc = param.get("description", "")
                p_schema = param.get("schema", {})
                p_type = p_schema.get("type", "string") if isinstance(p_schema, dict) else "string"
                lines.append(f"- {p_in}: {p_name} ({p_type}, {p_required}) - {p_desc}")
                
            # Request Body
            req_body = operation.get("requestBody", {})
            if req_body:
                lines.append("Request Body:")
                content_types = req_body.get("content", {})
                for ct, ct_obj in content_types.items():
                    schema = ct_obj.get("schema", {})
                    formatted = format_schema(spec, schema)
                    lines.append(f"  Content-Type: {ct}\n  Schema: {formatted}")
                    
            # Responses
            responses = operation.get("responses", {})
            if responses:
                lines.append("Responses:")
                for status_code, resp_obj in responses.items():
                    r_desc = resp_obj.get("description", "")
                    lines.append(f"  Status: {status_code} - {r_desc}")
                    r_content = resp_obj.get("content", {})
                    for ct, ct_obj in r_content.items():
                        schema = ct_obj.get("schema", {})
                        formatted = format_schema(spec, schema)
                        lines.append(f"    Content-Type: {ct}\n    Schema: {formatted}")
                        
            # Security Requirements
            security = operation.get("security", spec.get("security", []))
            if security:
                lines.append("Security Requirements:")
                for sec_req in security:
                    for scheme_name, scopes in sec_req.items():
                        lines.append(f"  - {scheme_name} (scopes: {', '.join(scopes)})")
                        
            endpoint_text = "\n".join(lines)
            
            # Split if too large
            sub_chunks = recursive_character_split(endpoint_text, chunk_size=800, chunk_overlap=100)
            for idx, sc in enumerate(sub_chunks):
                chunks_to_insert.append(sc)
                metadata_list.append({
                    "document_id": document_id,
                    "spec_title": spec_title,
                    "spec_version": spec_version,
                    "type": "endpoint",
                    "path": path,
                    "method": method.upper(),
                    "chunk_index": idx
                })
                
    # 3. Ingest Security Schemes
    components = spec.get("components", {})
    sec_schemes = components.get("securitySchemes", {})
    for scheme_name, scheme_obj in sec_schemes.items():
        lines = [
            f"Security Scheme: {scheme_name}",
            f"Type: {scheme_obj.get('type', '')}",
            f"In: {scheme_obj.get('in', '')}",
            f"Name: {scheme_obj.get('name', '')}",
            f"Scheme: {scheme_obj.get('scheme', '')}",
            f"Bearer Format: {scheme_obj.get('bearerFormat', '')}",
            f"Description: {scheme_obj.get('description', '')}"
        ]
        
        # Oauth2 flows
        flows = scheme_obj.get("flows", {})
        if flows:
            lines.append("Flows:")
            for flow_name, flow_obj in flows.items():
                lines.append(f"  - {flow_name}:")
                lines.append(f"    Authorization URL: {flow_obj.get('authorizationUrl', '')}")
                lines.append(f"    Token URL: {flow_obj.get('tokenUrl', '')}")
                lines.append(f"    Refresh URL: {flow_obj.get('refreshUrl', '')}")
                scopes = flow_obj.get("scopes", {})
                if scopes:
                    lines.append("    Scopes:")
                    for scope, scope_desc in scopes.items():
                        lines.append(f"      {scope}: {scope_desc}")
                        
        scheme_text = "\n".join(lines)
        chunks_to_insert.append(scheme_text)
        metadata_list.append({
            "document_id": document_id,
            "spec_title": spec_title,
            "spec_version": spec_version,
            "type": "security_scheme",
            "scheme_name": scheme_name
        })
        
    # Generate embeddings and store
    embeddings = [get_embedding(chunk) for chunk in chunks_to_insert]
    store_embeddings("api_specs", chunks_to_insert, embeddings, metadata_list)
    
    return {"status": "success", "endpoints_count": len(chunks_to_insert)}
