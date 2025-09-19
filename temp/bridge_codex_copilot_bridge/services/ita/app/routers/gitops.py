
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from ..auth import require_api_key, require_request_id
from ..utils.security import enforce_confirmation
from ..utils.github_app import create_or_update_pr

router = APIRouter(prefix="/git", tags=["git"])

class CreatePrIn(BaseModel):
    repo: str
    title: str
    body: str
    base: str
    head: str
    labels: list[str] | None = None

@router.post("/create-pr")
async def git_create_pr(payload: CreatePrIn,
                        confirm: bool = Query(default=False),
                        dry_run: bool = Query(default=True),
                        _=Depends(require_api_key),
                        __=Depends(require_request_id)):
    enforce_confirmation(confirm, dry_run)
    if dry_run:
        return {"simulated": True, "pr_url": None, "message": "Dry-run: no PR created."}
    pr_url = await create_or_update_pr(payload.repo, payload.title, payload.body, payload.base, payload.head, payload.labels or [])
    return {"simulated": False, "pr_url": pr_url, "message": "PR created."}
