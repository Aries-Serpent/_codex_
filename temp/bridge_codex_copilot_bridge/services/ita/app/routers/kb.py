
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..auth import require_api_key, require_request_id

router = APIRouter(prefix="/kb", tags=["kb"])

class KbSearchIn(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)

@router.post("/search")
async def kb_search(payload: KbSearchIn, _=Depends(require_api_key), __=Depends(require_request_id)):
    # Stubbed RAG — replace with your vector store
    fake = [
        {"snippet": "Use feature flags to guard risky changes.", "source": "kb/engineering/flags.md", "score": 0.91},
        {"snippet": "PRs > 300 files tend to fail review.", "source": "kb/reviews/limits.md", "score": 0.84},
    ]
    return {"results": fake[: payload.top_k]}
