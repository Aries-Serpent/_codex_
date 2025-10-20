"""Minimal FastAPI application for health and echo endpoints."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from codex_ml.ingest import ingest_sample

app = FastAPI(title="Codex ML Reference API", version="0.1.0")


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Health indicator")
    service: str = Field(default="codex", description="Service identifier")


class PredictRequest(BaseModel):
    prompt: str = Field(..., description="Input text prompt")
    return_tokens: bool = Field(False, description="Whether to return whitespace tokens")


class PredictResponse(BaseModel):
    prompt: str
    reply: str
    tokens: List[str] = Field(default_factory=list)


@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
@app.get("/ping", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return service health information."""

    return HealthResponse()


@app.get("/sample")
def sample(sample_size: int = 4) -> Dict[str, Any]:
    """Expose a tiny dataset sample via the ingest facade."""

    result = ingest_sample(sample_size=sample_size)
    return {
        "metadata": result["metadata"],
        "records": result["records"],
    }


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    """Echo the prompt with a deterministic transformation.

    The endpoint keeps behaviour intentionally simple so it can be used as a
    smoke-test for API plumbing without pulling in large model dependencies.
    """

    text = payload.prompt.strip()
    if not text:
        raise HTTPException(status_code=400, detail="prompt must be non-empty")

    reply = text[::-1]
    tokens = text.split() if payload.return_tokens else []
    return PredictResponse(prompt=payload.prompt, reply=reply, tokens=tokens)
