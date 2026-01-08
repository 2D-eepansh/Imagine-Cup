"""FastAPI entrypoint for the Portfolio Risk Intelligence backend.

Exposes deterministic, demo-safe endpoints that wrap the existing
risk scoring logic. Run locally with:

    uvicorn backend.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router

app = FastAPI(title="Portfolio Risk Intelligence API", version="1.0.0")

# CORS restricted to local/demo origins; expand for production as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
