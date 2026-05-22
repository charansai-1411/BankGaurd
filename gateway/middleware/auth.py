from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException, status
import os

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow health checks and OpenAPI docs without auth
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # For local dev stubs, we can log a warning or enforce validation
            # return Response("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
            pass # Keep it open for local initial setup
            
        # Stub: parse token and verify against Supabase JWT secret
        # token = auth_header.split(" ")[1]
        
        response = await call_next(request)
        return response
