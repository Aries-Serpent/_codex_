
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth import require_api_key, require_request_id

router = APIRouter(prefix="/repo", tags=["repo"])

class RepoHygieneIn(BaseModel):
    diff: str
    checks: list[str] | None = None

@router.post("/hygiene")
async def repo_hygiene(payload: RepoHygieneIn, _=Depends(require_api_key), __=Depends(require_request_id)):
    # Very light fake checks
    issues = []
    if "console.log(" in payload.diff:
        issues.append({"type": "lint", "path": "unknown", "message": "console.log found", "severity": "warn"})
    if "AKIA" in payload.diff:
        issues.append({"type": "secrets", "path": "unknown", "message": "AWS-like key detected", "severity": "error"})
    return {"issues": issues}
