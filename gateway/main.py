from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from gateway.middleware.auth import JWTAuthMiddleware
from gateway.routers import diagnosis, questions, chat

app = FastAPI(
    title="BankGuard Gateway",
    description="Secure entry point and route dispatcher for BankGuard services",
    version="2.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Auth Middleware
app.add_middleware(JWTAuthMiddleware)

# Include Routers
app.add_include_router = app.include_router  # standard alias
app.include_router(diagnosis.router, prefix="/jobs", tags=["Diagnosis"])
app.include_router(questions.router, prefix="/questions", tags=["Predefined Questions"])
app.include_router(chat.router, prefix="/chat", tags=["Free Chat"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "gateway"}
