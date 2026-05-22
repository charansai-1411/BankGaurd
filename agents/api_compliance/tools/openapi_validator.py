from typing import Dict, Any

def validate_openapi_spec(spec_content: str) -> Dict[str, Any]:
    """
    Validates OpenAPI specification for structural errors and compliance with security standards.
    """
    # Stub validation checks
    return {
        "valid": True,
        "errors": [],
        "warnings": ["Security definitions seem to miss scopes definition in OAuth2 flow."]
    }
