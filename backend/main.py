from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.diagnostics import router as diagnostics_router

app = FastAPI(
    title="Solar Underperformance Diagnosis API",
    description="API for explainable solar power underperformance diagnosis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "solar-diagnostic-api"}

app.include_router(diagnostics_router, prefix="/api/v1")
