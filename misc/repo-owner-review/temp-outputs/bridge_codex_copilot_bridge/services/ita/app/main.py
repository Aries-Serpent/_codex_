from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="ITA Bridge Stub", version="0.1.0")


class KBSearchReq(BaseModel):
    query: str
    top_k: int = 5


class HygieneReq(BaseModel):
    diff: str | None = None
    checks: List[str] | None = None


class TestsReq(BaseModel):
    pattern: str | None = None


class CreatePRReq(BaseModel):
    title: str
    body: str
    head: str
    base: str
    confirm: bool | None = None


@app.post("/kb/search")
def kb_search(req: KBSearchReq) -> Dict[str, Any]:
    # Deterministic stubbed results
    results = [
        {
            "title": f"KB match for: {req.query}",
            "url": "https://internal.example/kb/123",
            "snippet": "This is a stubbed KB snippet.",
        }
        for _ in range(max(1, min(req.top_k, 5)))
    ]
    return {"results": results}


@app.post("/repo/hygiene")
def repo_hygiene(req: HygieneReq) -> Dict[str, Any]:
    findings = []
    if req.diff and "TODO" in req.diff:
        findings.append({"type": "lint", "message": "Found TODO in diff"})
    return {"ok": len(findings) == 0, "findings": findings}


@app.post("/tests/run")
def tests_run(req: TestsReq | None = None) -> Dict[str, Any]:
    # Stubbed: always pass a small set
    return {"passed": 12, "failed": 0, "duration_s": 1.23}


@app.post("/git/create-pr")
def git_create_pr(req: CreatePRReq) -> Dict[str, Any]:
    dry = not bool(req.confirm)
    if dry:
        return {
            "dry_run": True,
            "message": f"[DRY RUN] Would create PR {req.head}->{req.base}: {req.title}",
            "pr_url": None,
        }
    # In a real implementation: call GitHub App flow. Here: stub URL.
    return {
        "dry_run": False,
        "message": "PR created",
        "pr_url": "https://github.com/owner/repo/pull/123",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
