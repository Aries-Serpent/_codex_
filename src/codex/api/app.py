"""Minimal FastAPI application for health and echo endpoints."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="codex", version="0.1.0")


class PredictRequest(BaseModel):
    """Request schema for the `/predict` endpoint."""

    prompt: str


class PredictResponse(BaseModel):
    """Response schema for the `/predict` endpoint."""

    output: str


@app.get("/health")
def health() -> dict:
    """Simple health endpoint returning a 200 response."""

    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    """Root endpoint mirroring the health payload."""

    return {"name": "codex", "status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    """Echo the provided prompt as the mock prediction output."""

    return PredictResponse(output=f"echo: {req.prompt}")
